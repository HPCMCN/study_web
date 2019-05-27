# coding=utf-8

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# EMAIL_USE_SSL = True

EMAIL_USE_TLS = True

# 发送邮件服务器
EMAIL_HOST = "smtp.qq.com"

# 发送邮件服务器端口
EMAIL_PORT = 465

# 发送人邮箱
EMAIL_HOST_USER = "hpcm@foxmail.com"

# 密码
EMAIL_HOST_PASSWORD = "oxsittmtxohxbbfe"

# 用户看到的发件人
EMAIL_FROM = "hpcmpc@qq.com"

# 激活url连接:
VERIFY_BASE_URL = "http://www.meiduo.site:8080/success_verify_email.html?token="
# 使用SSL的通用配置如下：
# 接收邮件服务器：pop.qq.com，使用SSL，端口号995
# 发送邮件服务器：smtp.qq.com，使用SSL，端口号465或587
# 账户名：您的QQ邮箱账户名（如果您是VIP帐号或Foxmail帐号，账户名需要填写完整的邮件地址）
# 密码：您的QQ邮箱密码
# 电子邮件地址：您的QQ邮箱的完整邮件地址
