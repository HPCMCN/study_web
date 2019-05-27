# coding=utf-8

BROKER_URL  = "redis://127.0.0.1/14"      # 任务队列
CELERY_RESULT_BACKEND  = "redis://127.0.0.1/15"  # 结果队列


CELERY_IMPORTS = (
    "celery_tasks.tasks.sms_send",
    "celery_tasks.tasks.email_send",
    "celery_tasks.tasks.html_reader",
)


