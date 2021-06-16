# -*- coding: utf-8; py-indent-offset:4 -*-

import datetime as dt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .push_base import *

class EmailPush( PushBase ):
    mailto = ''
    sender = ''
    server = ''
    user = ''
    passwd = ''

    def __init__(self, conf):
        super().__init__(conf)

        self.mailto = conf['mailto']
        self.sender = conf['sender']
        self.server = conf['server']
        self.user = conf['user']
        self.passwd = conf['passwd']

    def send(self, subject = 'HELLO', content = 'hello, world'):
        msg = MIMEMultipart("alternative")
        msg['From'] = self.sender
        msg['To'] = self.mailto
        msg['Subject'] = subject
        msg.attach( MIMEText( content, 'plain', 'utf-8' ) )

        s = smtplib.SMTP(self.server)
        if len(self.user)>0 and len(self.passwd)>0:
            s.login(self.user, self.passwd)

        s.sendmail(self.sender, self.mailto, msg.as_string())
        s.quit()

    def flush(self):
        if not self.msg_queue:
            return

        subject = '[hiquant] ' + self.msg_queue[0]

        line = '-' * 40
        content = '\n\n'.join(self.msg_queue)
        content += '\n' + line + '\n' + dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n'

        self.send(subject, content)
        print('email sent')

        self.msg_queue = []
