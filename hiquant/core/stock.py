# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from cycler import cycler

from .indicator_signal import gen_indicator_signal, signal_to_long, get_all_signal_indicators
from .lang import get_lang, LANG

class Stock:
    symbol = ''
    name = ''
    daily_df = None
    shares = 0
    cost = 0.0
    price = 0.0
    sellable = True

    def __init__(self, symbol, name = '', daily_df = None):
        self.symbol = symbol
        self.name = name
        self.daily_df = daily_df
        self.shares = 0
        self.cost = 0.0
        self.price = 0.0

    def calc_cum_return(self, df, signal, mix= False, order_cost = None):
        # Notice!!! Important !!!
        #
        # when calc signal, we used the close price of today,
        # to avoid "future data or function", it cannot be used for today's trading
        # the signal only impact next day, so here shift(1) to next day
        #
        # only for MFFI, we should catch the signal and buy/sell immediately
        #
        if signal.name == 'mffi':
            long_pos = signal_to_long(signal, time_factor=0.50)
        else:
            long_pos = signal_to_long(signal).shift(1).fillna(0)

        act_return = long_pos * df['daily_return']

        if mix:
            df['trade'] = signal.astype(int)
            df['long_pos'] = long_pos

        # use a column start with "." to store the performance data
        if order_cost is not None:
            buy_cost = signal.copy()
            buy_cost[ buy_cost < 0 ] = 0
            sell_cost = signal.copy()
            sell_cost[ sell_cost > 0 ] = 0
            buy_cost = buy_cost * (order_cost.open_commission)
            sell_cost = (-1) * sell_cost * (order_cost.close_commission + order_cost.close_tax)
            cost = (buy_cost + sell_cost)
        else:
            cost = 0
        cum_return = (1 + act_return - cost).cumprod() -1
        return cum_return.fillna(0)

    def add_indicator(self, indicators, mix = False, inplace = False, order_cost = None):
        # if only one indicator, we auto show trade & position
        if len(indicators) == 1:
            mix = True

        df = self.daily_df
        df['daily_return'] = df.close.pct_change().fillna(0)
        if mix:
            signal = gen_indicator_signal(df, indicators, inplace=inplace)
            if len(indicators) == 1:
                signal.rename(indicators[0], inplace= True)
            df['return.'] = self.calc_cum_return(df, signal, mix= True, order_cost= order_cost)
        else:
            for k in indicators:
                signal = gen_indicator_signal(df, [k], inplace=inplace).rename(k)
                df[k + '.'] = self.calc_cum_return(df, signal, mix= False, order_cost= order_cost)

    def rank_indicator(self, by = 'overall'):
        df = self.daily_df.copy()

        # fill NaN with 0
        df.fillna(0, inplace=True)

        # sort the indicators by overall performance
        table = []
        for k in df.columns:
            if k.endswith('.'):
                v = df[k]
                final = v.iloc[-1]
                overall = sum(v.tolist())
                table.append([k, final, overall])
        rank_df = pd.DataFrame(table, columns=['indicator', 'final', 'overall'])
        rank_df.sort_values(by=by, ascending=False, inplace=True)
        rank_df.reset_index(inplace=True, drop=True)

        return rank_df

    # Visualization
    # --------------------------------------------------------------------------------
    def plot(self, out_file = None):
        # China market candle color, red for up, green for down
        up_red = (get_lang() == 'zh')
        long_color = 'red' if up_red else 'green'
        short_color = 'green' if up_red else 'red'
        mc = mpf.make_marketcolors(
            up = long_color,
            down = short_color,
            edge = 'i',
            wick = 'i',
            volume = 'in',
            inherit = True
        )
        style = mpf.make_mpf_style(
            base_mpl_style = "ggplot",
            marketcolors = mc,
            rc = {
                # to correctly display Chinese text
                # download TTF files:
                # https://raw.githubusercontent.com/StellarCN/scp_zh/master/fonts/SimHei.ttf
                # https://raw.githubusercontent.com/StellarCN/scp_zh/master/fonts/SimKai.ttf
                # https://raw.githubusercontent.com/StellarCN/scp_zh/master/fonts/SimSun.ttf
                # copy to: /usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/
                'font.sans-serif': ['SimHei'], # Chinese font
                'font.family': 'sans-serif',
                'axes.unicode_minus': False,
                'axes.prop_cycle': cycler(color=['dodgerblue', 'deeppink', 'navy', 'teal', 'maroon', 'darkorange', 'indigo']),
                'lines.linewidth': 0.75,
            }
        )

        # we have panel 0 for main, panel 1 for volume by default
        next_panel = 2
        more_plot = []

        df = self.daily_df

        linestyles = dict(
            type = 'line',
            width = 1
        )
        panel_ratios = [1, 0.3]
        keys = [
            'ma5', 'ma10', 'ma20', 'ma30', 'ma60',
            'ema5', 'ema10', 'ema20', 'ema30', 'ema60',
            'hma5', 'hma10', 'hma20', 'hma30', 'hma60',
        ]
        cols = list(set(keys) & set(df.columns))
        if len(cols) > 0:
            more_plot.append(mpf.make_addplot(df[cols], panel=0, **linestyles))

        if 'mffi' in df.columns:
            mffi = df['mffi']
            trade_color = [long_color if v >= 0 else short_color for v in mffi]
            more_plot.append(mpf.make_addplot(mffi, type='bar', panel=next_panel, color=trade_color, ylabel='MFFI'))
            next_panel = next_panel +1
            panel_ratios.append(0.8)

        if 'macd_hist' in df.columns:
            macd = df.macd_hist
            macd_color = [long_color if v >= 0 else short_color for v in macd]
            more_plot.append(mpf.make_addplot(macd, type='bar', width=0.4, panel=next_panel, color=macd_color, ylabel='MACD'))
            cols = []
            for k in ['macd_dif', 'macd_dea']:
                if k in df.columns:
                    cols.append(k)
            if len(cols) > 0:
                more_plot.append(mpf.make_addplot(df[cols], panel=next_panel, secondary_y=False, **linestyles))
            next_panel = next_panel +1
            panel_ratios.append(0.3)

        indicators = get_all_signal_indicators()
        for key, values in indicators.items():
            if key in ['ma', 'macd', 'mffi']:
                continue
            ind_label = values['label']
            ind_cols = values['cols']

            if ind_cols[0] in df.columns:
                cols = list(set(ind_cols) & set(df.columns))
                more_plot.append(mpf.make_addplot(df[cols], panel=next_panel, ylabel=ind_label, secondary_y=False, **linestyles))
                next_panel = next_panel +1
                panel_ratios.append(0.3)

        if 'trade' in df.columns:
            # as the signal calculated with close price of today,
            # to avoid "future data", we can only trade before market close, or morning of next day
            trade_action = df['trade']

            trade_color = [long_color if v >= 0 else short_color for v in trade_action]
            more_plot.append(mpf.make_addplot(trade_action, type='bar', panel=next_panel, color=trade_color, ylabel=LANG('trade')))
            next_panel = next_panel +1
            panel_ratios.append(0.3)

        if 'long_pos' in df.columns:
            price_change = df['close'] - df['open']
            pos_color = [long_color if v >= 0 else short_color for v in price_change]
            long_pos = df['long_pos']
            more_plot.append(mpf.make_addplot(long_pos, type='bar', panel=next_panel, color=pos_color, ylabel=LANG('position')))
            next_panel = next_panel +1
            panel_ratios.append(0.15)

        # find the columns started with "." as performance data
        ret_cols = []
        for k in df.columns:
            if k.endswith('.'):
                ret_cols.append(k)
        if len(ret_cols) > 0:
            price_change_percent = (df['close']/df['close'].iloc[0]-1) * 100
            more_plot.append(mpf.make_addplot(price_change_percent, panel=next_panel, color='b', ylabel=LANG('return(%)'), **linestyles))
            more_plot.append(mpf.make_addplot(df[ret_cols] * 100, panel=next_panel, secondary_y=False, **linestyles))
            last_panel = next_panel
            next_panel = next_panel +1
            panel_ratios.append(1.0 if (len(ret_cols)>1) else 1.0)

        print(df)

        kwargs = dict(
            title = self.symbol + ' - ' + self.name,
            type = "candle",
            volume = True,
            datetime_format = '%Y-%m-%d',
            ylabel = LANG("price"),
            ylabel_lower = LANG("volume"),
            figratio = (10,6),
            figscale = 1.0,
            panel_ratios = panel_ratios,
            tight_layout = True,
            style = style,
            addplot = more_plot,
            returnfig = True,
            warn_too_much_data = 244 * 5,
        )
        if out_file is not None:
            kwargs[ 'savefig' ] = out_file

        fig, axes = mpf.plot(df[['open','close','high','low','volume']], **kwargs)

        # matplotlib subplot does not support legend, we do it by ourselves
        if(len(ret_cols) > 0):
            ret_cols.insert(0, 'price')
            axes[ last_panel * 2].legend(ret_cols, loc = 'best')

        plt.show()
