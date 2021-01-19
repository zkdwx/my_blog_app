from django.urls import path

from users.views import RegisterView, ImageCodeView, SmsCodeView, LoginView, LogoutView,ForgetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # 图片验证码的路由
    path('imagecode/', ImageCodeView.as_view(), name='imagecode'),
    path('smscode/', SmsCodeView.as_view(), name='smscode'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forget_password/', ForgetPasswordView.as_view(), name='forget_password'),

]
