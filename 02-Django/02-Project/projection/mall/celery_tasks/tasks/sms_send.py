# coding=utf-8
from celery_tasks.celery import app
from libs.yuntongxun.sms import CCP


@app.task(name='发送短信')
def send_sms_code(mobile, sms_code):
    """发送短信任务"""
    ccp = CCP()
    ccp.send_template_sms(mobile, [sms_code, 5], 1)
    return "短信发送成功!"
