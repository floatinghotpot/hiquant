# -*- coding: utf-8; py-indent-offset:4 -*-

import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from cycler import cycler

from .indicator_signal import gen_indicator_signal, long_to_signal, signal_to_long, get_all_signal_indicators

class Stock:
    symbol = ''
    name = ''
    daily_df = None
    shares = 0
    cost = 0.0
    price = 0.0

    def __init__(self, symbol, name = '', daily_df = None):
        self.symbol = symbol
        self.name = name
        self.daily_df = daily_df
        self.shares = 0
        self.cost = 0.0
        self.price = 0.0

    def calc_cum_return(self, df, signal, mix= False, order_cost = None):
        long_trend = signal_to_long(signal)
        long_pos = long_trend.fillna(0)
        act_return = long_pos * df['daily_return']

        if mix:
            df['trade_signal'] = signal
            df['long_pos'] = long_pos
            df['act_return'] = act_return

        # use a column start with "." to store the performance data
        if order_cost is not None:
            sell_cost = signal.copy()
            sell_cost[ sell_cost > 0 ] = 0
            buy_cost = signal.copy()
            buy_cost[ buy_cost < 0 ] = 0
            sell_cost = (-1) * sell_cost * (act_return * 0.75 + order_cost.close_commission + order_cost.close_tax)
            buy_cost = buy_cost * (act_return * 0.75 + order_cost.open_commission)
            cost = (buy_cost + sell_cost)
        else:
            cost = 0
        cum_return = (1 + act_return - cost).cumprod() -1
        return cum_return

    def add_indicator(self, indicators, mix = False, inplace = False, order_cost = None):
        df = self.daily_df
        df['daily_return'] = df.close.pct_change()
        if mix:
            signal = gen_indicator_signal(df, indicators, inplace=inplace)
            df['return.'] = self.calc_cum_return(df, signal, mix= True, order_cost= order_cost)
        else:
            for k in indicators:
                signal = gen_indicator_signal(df, [k], inplace=inplace)
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
    def plot(self, red_up = True, out_file = None):
        # China market candle color, red for up, green for down
        mc = mpf.make_marketcolors(
            up = 'red' if red_up else 'green',
            down = 'green' if red_up else 'red',
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
            trade_color = ['r' if v >= 0 else 'g' for v in mffi]
            more_plot.append(mpf.make_addplot(mffi, type='bar', panel=next_panel, color=trade_color, ylabel='MFFI'))
            next_panel = next_panel +1
            panel_ratios.append(0.8)

        if 'macd_hist' in df.columns:
            macd = df.macd_hist
            macd_color = ['r' if v >= 0 else 'g' for v in macd]
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

        if 'trade_signal' in df.columns:
            trade_signal = df['trade_signal']
            trade_color = ['r' if v >= 0 else 'g' for v in trade_signal]
            more_plot.append(mpf.make_addplot(trade_signal, type='bar', panel=next_panel, color=trade_color, ylabel='trade'))
            next_panel = next_panel +1
            panel_ratios.append(0.3)

        if 'long_pos' in df.columns:
            long_pos = df['long_pos']
            short_pos = 1 - long_pos
            more_plot.append(mpf.make_addplot(long_pos, type='bar', panel=next_panel, color='r', ylabel='position'))
            more_plot.append(mpf.make_addplot(short_pos, type='bar', panel=next_panel, color='g', secondary_y=False))
            next_panel = next_panel +1
            panel_ratios.append(0.3)

        if False: #'act_return' in df.columns:
            if 'daily_return' in df.columns:
                more_plot.append(mpf.make_addplot(df['daily_return'], panel=next_panel, color='b', ylabel='return', **linestyles))
            more_plot.append(mpf.make_addplot(df['act_return'], panel=next_panel, color='r', secondary_y=False, **linestyles))
            next_panel = next_panel +1
            panel_ratios.append(0.3)

        # find the columns started with "." as performance data
        ret_cols = []
        for k in df.columns:
            if k.endswith('.'):
                ret_cols.append(k)
        if len(ret_cols) > 0:
            more_plot.append(mpf.make_addplot(df['close']/df['close'].iloc[0]-1, panel=next_panel, color='b', ylabel='return', **linestyles))
            more_plot.append(mpf.make_addplot(df[ret_cols], panel=next_panel, secondary_y=False, **linestyles))
            last_panel = next_panel
            next_panel = next_panel +1
            panel_ratios.append(1.0 if (len(ret_cols)>1) else 1.0)

        kwargs = dict(
            title = self.symbol + ' - ' + self.name,
            type = "candle",
            volume = True,
            datetime_format = '%Y-%m-%d',
            ylabel = "price",
            ylabel_lower = "volume",
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
        if(len(ret_cols) > 1):
            ret_cols.insert(0, 'price')
            axes[ last_panel * 2].legend(ret_cols, loc = 'upper left')

        plt.show()
