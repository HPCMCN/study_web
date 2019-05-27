# coding=utf-8
from django.core.mail import send_mail

from celery_tasks.celery import app
from contents.center.email import EMAIL_FROM, VERIFY_BASE_URL


@app.task(name="发送邮件")
def send_verify_email(user_email, token):
    """发送激活邮件"""
    verify_url = VERIFY_BASE_URL + token
    # 主题
    subject = "美多商城邮箱激活验证"
    # 内容
    message = "<p>尊敬的用户您好！</p>" \
              "<p>感谢您使用美多商城。</p>" \
              "<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>" \
              "<p><a href='%s'>%s<a></p>" % (user_email, token, verify_url)
    #                普通消息                         这里使用html消息
    send_mail(subject, "", EMAIL_FROM, [user_email], html_message=message)
    return "激活邮件发送成功!"
