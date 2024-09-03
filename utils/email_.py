import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from utils.log import logger


def send_email(subject, body, attachment=None):
    sender_email = "automation_test_xiaozx@outlook.com"
    sender_password = "12345shangshandalaohu"
    receiver_email = "shawn.xiao@osl.com"
    # 设置邮件内容
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # 添加正文
    message.attach(MIMEText(body, "plain"))

    # 添加附件（如果有）
    if attachment:
        filename = os.path.basename(attachment)
        with open(attachment, "rb") as f:
            attach = MIMEApplication(f.read(), Name=filename)
            attach["Content-Disposition"] = f"attachment; filename={filename}"
            message.attach(attach)
    try:
        # 连接到 Outlook SMTP 服务器
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()  # 开启安全传输模式
            server.login(sender_email, sender_password)  # 登录邮箱

            # 发送邮件
            server.sendmail(sender_email, receiver_email, message.as_string())
        logger.log('Email sent successful')
    except Exception as e:
        print(f"发送电子邮件时出错: {e}")

# 示例用法
if __name__ == "__main__":
    subject = "Test Email from Python"
    body = "Hello,\n\nThis is a test email sent from Python."
    current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径所在目录
    file_path = os.path.join(current_dir, '..', 'utils', 'email_.py')
    send_email(subject, body, file_path)
