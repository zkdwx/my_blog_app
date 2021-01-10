from django.urls import path

from users.views import RegisterView, ImageCodeView, SmsCodeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # 图片验证码的路由
    path('imagecode/', ImageCodeView.as_view(), name='imagecode'),
    path('smscode/', SmsCodeView.as_view(), name='smscode'),

]
