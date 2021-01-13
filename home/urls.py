from django.urls import path

from home.views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    # 图片验证码的路由
]
