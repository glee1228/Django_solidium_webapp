from django.shortcuts import render
from django.shortcuts import redirect
from .forms import UploadImageForm
from .forms import ScriptForm
from django.core.files.storage import FileSystemStorage
from .forms import ImageUploadForm
from django.conf import settings
from .opencv_dface import opencv_dface
# Create your views here.
import cv2
import ast
from django.http import HttpResponse,StreamingHttpResponse, HttpResponseServerError
import numpy as np
from django.views.decorators import gzip
from time import sleep
import subprocess
from subprocess import call
import os
from django.views import View
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from .forms import LoginForm,UserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
import glob
import shutil

class MainView(View):
    def get(self,request,*args,**kwargs):
        return render(request,'main.html')
    def post(self,request,*args,**kwargs):
        login_succ = "로그인 완료"
        login_fail = "로그인 실패"
        logout_succ = "성공적으로 로그아웃되었습니다"

        if request.POST['func']=='login':
            form = LoginForm(request.POST)
            username = request.POST['username']
            password = request.POST['password']
            print(username,password)
            user = authenticate(username = username,password=password)
            print(user)

            if user is not None and user.is_active:
                login(request, user)
                return render(request, 'main.html', {'logincheck': login_succ})
            else :
                return render(request,'main.html',{'logincheck':login_fail})
        elif request.POST['func']=='logout':
            logout(request)
            return render(request,'main.html',{'logout_succ':logout_succ})
        elif request.POST['func']=='signup':
            #print(request.POST['username'],request.POST['email'],request.POST['password'])
            form = UserForm(request.POST)
            print(form)
            if form.is_valid():
                new_user = User.objects.create_user(**form.cleaned_data)
                return render(request,'main.html')
            else :
                return render(request,'main.html')
        else:
            return render(request,'main.html')
class StartView(View):

    def get(self,request,*args,**kwargs):
        request.session['start_complete']=False
        request.session['run_complete']=False
        request.session['stream_complete']=False
        return render(request,'start.html')

    def post(self,request,*args,**kwargs):
        request.session['start_complete']=True
        after_pre=settings.EAR_IMAGE_ROOT+"/Test/After_preprocess/"
        before_pre=settings.EAR_IMAGE_ROOT+"/Test/Before_preprocess/"
        after_resize=settings.EAR_IMAGE_ROOT+"/Test/Before_preprocess/After_resize_pixel/"
        empty_directory(after_pre)
        empty_directory(before_pre)
        empty_directory(after_resize)
        make_directory(before_pre,"After_resize_pixel")
        #print(os.path.join(after_resize, '*'))
        #print(after_resize)
        return redirect(reverse('run'))

class RunView(View):

    def get(self,request,*args,**kwargs):
        #if not request.session.get('start_complete',False):
        #    raise PermissionDenied
        request.session['start_complete']=False
        my_env = { **os.environ, 'PATH': '/usr/sbin:/sbin:' + os.environ['PATH']}
        # print(my_env)
        sound_script_path = "./solidium_webapp/sound/Papago.mpeg"
        ear_script_path = "./solidium_webapp/ear_app/ear_test_change.py"
        call(["mplayer",sound_script_path])
        proc = subprocess.Popen(['python3', ear_script_path], stdout=subprocess.PIPE, env=my_env)
        result = []
        while proc.poll() is None:
            output = proc.stdout.readline()
            result.append((output).decode())
        oldstr = result[2]
        newstr = oldstr.replace("\n", "")
        print("예측 횟수 : "+ newstr)
        dic = ast.literal_eval(newstr)
        dic_max = max(dic.values())
        predict =""
        for key,value in dic.items():
            if dic_max==value:
                predict=key
        print("예측한 사람 : "+predict)
        print("로그인된 정보 : "+str(request.user))
        if predict==str(request.user):
            Authentication="Authentication"
            return render(request, 'run.html', {'predict': predict, 'newstr': newstr, 'Authentication': Authentication})
        else:
            unauthorized = "unauthorized"
            return render(request, 'run.html', {'predict': predict, 'newstr': newstr, 'unauthorized': unauthorized})



    def post(self,request,*args,**kwargs):
        if request.POST['auth']=='fail':
            return redirect(reverse('main'))
        elif request.POST['auth']=='succ':
            request.session['run_complete']=True
            return redirect(reverse('stream'))
        else :
            return redirect(reverse('main'))


class StreamView(View):
    def get(self,request,*args,**kwargs):
        #if not request.session.get('run_complete',False):
        #    raise PermissionDenied
        request.session['run_complete']=False
        streaming(request)
        return render(request,'stream.html')

    def post(self,request,*args,**kwargs):
        request.session['stream_complete']=True
        return redirect(reverse('result'))

class ResultView(View):

    def get(self,request,*args,**kwargs):
        #if not request.session.get('stream_complete',False):
        #    raise PermissionDenied
        request.session['stream_complete']=False
        return render(request,'result.html')

class UserView(View):
    def get(self,request,*args,**kwargs):
        request.session['stream_complete']=False
        return render(request,'user.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

class VideoCamera(object):
    def __init__(self,path):
        self.video = cv2.VideoCapture(path)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        #image = cv2.flip(image, -1)
        ret, jpeg = cv2.imencode('.jpg', image)
        sleep(0.07)
        return jpeg.tobytes()


@gzip.gzip_page
def streaming(request):
    stream_path = './media/video/123.mp4'
    return StreamingHttpResponse(gen(VideoCamera(stream_path)),
                                 content_type="multipart/x-mixed-replace;boundary=frame")

def remove_thing(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

def empty_directory(path):
    for i in glob.glob(os.path.join(path, '*')):
        remove_thing(i)

def make_directory(path,name):
    os.mkdir(path+name)

















# def run(request):
#
#     #print(form)
#     if request.method=='GET':
#          #if request.POST['value']=='authentication':
#
#             my_env = {**os.environ, 'PATH': '/usr/sbin:/sbin:' + os.environ['PATH']}
#             #print(my_env)
#             ear_script_path = "./solidium_webapp/ear_app/ear_test_change.py"
#
#             proc = subprocess.Popen(['python3',ear_script_path],stdout=subprocess.PIPE,env=my_env)
#             result=[]
#             while proc.poll() is None:
#                 output = proc.stdout.readline()
#                 result.append((output).decode())
#             #output = result.communicate()[0]
#             print(result[2])
#             return render(request, "run.html", {'result':result})
#
#          #else:
#          #   return render(request, 'run.html')
#     else:
#         return render(request,'run.html')
#



#def result(request):
#    if request.method=='POST':

# def uimage(request):
#     if request.method == 'POST':
#         form = UploadImageForm(request.POST, request.FILES)  # 이미지 업로드 폼
#         if form.is_valid():
#             myfile = request.FILES['image']
#             fs = FileSystemStorage()  # 이미지 저장 함수
#             filename = fs.save(myfile.name, myfile)
#             uploaded_file_url = fs.url(filename)
#             return render(request, 'uimage.html',
#                       {'form': form, 'uploaded_file_url': uploaded_file_url})
#     else:
#         form = UploadImageForm()
#         return render(request, 'uimage.html',
#                       {'form': form})
#
# def dface(request):
#     if request.method == 'POST':
#         form = ImageUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.save()
#
#             imageURL = settings.MEDIA_URL + form.instance.document.name
#             opencv_dface(settings.MEDIA_ROOT_URL + imageURL)
#
#             return render(request, 'dface.html', {'form': form, 'post': post})
#     else:
#         form = ImageUploadForm()
#     return render(request, 'dface.html', {'form': form})


