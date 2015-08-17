#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The module is used to varify email address.

Reference:
    http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000
Protocol:
    http://blog.csdn.net/bripengandre/article/details/2191048
"""

import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


SMTP_SERVER = 'smtp.163.com'
SIGNUP_SUBJECT = 'Chat Verification'
FINDPW_SUBJECT = 'Chat Password Settings'
SIGNUP_MESSAGE = """<html><body>
<h2>{name}，感谢您注册Chat！</h2>
<p>确认是你本人操作后<a href="{url}">点击链接</a>完成注册。</p>
<br/><p>若无法点击，请复制以下链接粘贴在浏览器地址栏：</p>
<p>{url}</p>
</body></html>
"""
FINDPW_MESSAGE = """<html><body>
<h2>{name}，我们收到了您的密码修改请求！</h2>
<p>请确认是您本人操作后<a href="{url}">点击链接</a>修改密码。</p>
<br/>若无法点击，请复制以下链接粘贴在浏览器地址栏：</p>
<p>{url}</p>
</body></html>
"""

def send_email(from_addr, from_pwd, to_name, to_addr, message,
               subject=SIGNUP_SUBJECT, smtp_server=SMTP_SERVER, smtp_port=25):
    msg = MIMEText(message, 'html', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8').encode()
    msg['From'] = _format_addr("管理员<{0}>".format(from_addr))
    msg['To'] = _format_addr(to_name + " <" + to_addr + ">")

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.set_debuglevel(1)
    server.login(from_addr, from_pwd)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()


def _format_addr(email_addr):
    name, addr = parseaddr(email_addr)
    return formataddr((
        Header(name, 'utf-8').encode(),
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))
