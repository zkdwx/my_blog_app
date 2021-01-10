from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import HttpResponse
from utils.response_code import RETCODE
import logging
from random import randint
from libs.yuntongxun.sms import CCP
import re
from users.models import Users
from django.db import DatabaseError

logger = logging.getLogger('django')

# 注册视图
from django.views import View


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        smscode = request.POST.get("sms_code")
        if not all([mobile, password, password2, smscode]):
            return HttpResponseBadRequest("缺少必要的参数")
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest("手机号码不符合规则")
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest("请输入8-20位密码，密码是数字，字母")
        if password != password2:
            return HttpResponseBadRequest("两次密码不一致")
        redis_conn = get_redis_connection("default")
        redis_sms_code = redis_conn.get("sms:%s" % mobile)
        if redis_sms_code is None:
            return HttpResponseBadRequest("短信验证码已过期")
        if smscode != redis_sms_code.decode():
            return HttpResponseBadRequest("短信验证码不一致")
        try:
            user = Users.objects.create_user(username=mobile, mobile=mobile, password=password)
        except DatabaseError as e:
            logger.error(e)
            return HttpResponseBadRequest("注册失败")
        return HttpResponse("注册成功，重定向到首页")


class ImageCodeView(View):
    def get(self, request):
        # 1.接收前端传递过来的uuid
        uuid = request.GET.get('uuid')
        # 2.判断uuid是否获取到
        if uuid is None:
            return HttpResponseBadRequest("没有传递uuid")
        # 3.通过调用captcha来生成图片验证码（图片二进制和图片内容）
        text, image = captcha.generate_captcha()
        # 将图片内容保存到redis中
        # uuid作为一个key,图片内容作为一个value同时我们需要设置一个时效
        redis_conn = get_redis_connection('default')
        # key设置为uuid
        # second 过期秒数 300秒  5分钟过期时间
        # value text
        redis_conn.setex('img:%s' % uuid, 300, text)
        # 5.返回图片二进制
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):
    def get(self, request):
        mobile = request.GET.get('mobile')
        image_code = request.GET.get('image_code')
        uuid = request.GET.get("uuid")
        if not all([mobile, image_code, uuid]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必要的参数'})
        redis_conn = get_redis_connection('default')
        redis_image_code = redis_conn.get('img:%s' % uuid)
        if redis_image_code is None:
            return JsonResponse({"code": RETCODE.IMAGECODEERR, 'errmsg': '图片验证码过期'})
        try:
            redis_conn.delete('img:%s' % uuid)
        except Exception as e:
            logger.error(e)
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({"code": RETCODE.IMAGECODEERR, 'errmsg': '图片验证码错误'})
        sms_code = '%06d' % randint(0, 999999)
        logger.info(sms_code)
        redis_conn.setex('sms:%s' % mobile, 300, sms_code)
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        return JsonResponse({"code": RETCODE.OK, 'errmsg': '短信发送成功'})
