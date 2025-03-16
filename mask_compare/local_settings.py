from .settings import *

DEBUG = True

# 开发环境禁用一些安全设置
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False