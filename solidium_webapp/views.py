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
from collections import OrderedDict

from solidium_webapp import fusioncharts

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
        sound_script_path = "./solidium_webapp/sound/start.mpeg"
        ear_script_path = "./solidium_webapp/ear_app/ear_test_change.py"
        call(["mplayer",sound_script_path])
        proc = subprocess.Popen(['python3', ear_script_path], stdout=subprocess.PIPE, env=my_env)
        result = []
        while proc.poll() is None:
            output = proc.stdout.readline()
            result.append((output).decode())
        for i in result:
            if "이동훈" in i:
                oldstr = result[2]
                newstr = oldstr.replace("\n", "")
                print("예측 횟수 : "+ newstr)
                dic = ast.literal_eval(newstr)
                dic_max = max(dic.values())
                predict =""
                for key,value in dic.items():
                    request.session[key]=value
                    if dic_max==value:
                        predict=key
                print("예측한 사람 : "+predict)
                print("로그인된 정보 : "+str(request.user))
        if str(request.user)=="AnonymousUser":
            needuid="needuid"
            return render(request,'run.html',{'predict': predict, 'newstr': newstr, 'needuid': needuid})
        elif predict==str(request.user):
            sound_script_path = "./solidium_webapp/sound/authentication_success.mpeg"
            call(["mplayer", sound_script_path])
            Authentication="Authentication"
            return render(request, 'run.html', {'predict': predict, 'newstr': newstr, 'Authentication': Authentication})
        else:
            sound_script_path = "./solidium_webapp/sound/authentication_fail.mpeg"
            call(["mplayer", sound_script_path])
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
        chartdic=chart(request)
        request.session['stream_complete']=False
        return render(request,'result.html',chartdic)

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




# Loading Data from a Ordered Dictionary
# Example to create a column 2D chart with the chart data passed as Dictionary format.
# The `chart` method is defined to load chart data from Dictionary.

def chart(request):
    # Chart data is passed to the `dataSource` parameter, as dictionary in the form of key-value pairs.
    dataSource = OrderedDict()

    # The `chartConfig` dict contains key-value pairs data for chart attribute
    chartConfig = OrderedDict()
    chartConfig["caption"] = "Top 5 High Ear's Similarity"
    chartConfig["subCaption"] = "images = Number of ear images"
    chartConfig["xAxisName"] = "사람 이름"
    chartConfig["yAxisName"] = "예측 횟수(images)"
    chartConfig["numberSuffix"] = "P"
    chartConfig["theme"] = "fusion"

    # The `chartData` dict contains key-value pairs data
    chartData = OrderedDict()
    chartData["오윤석"] = request.session.get('오윤석')
    chartData["이동훈"] = request.session.get('이동훈')
    chartData["임혜진"] = request.session.get('임혜진')
    chartData["이동준"] = request.session.get('이동준')
    chartData["손정효"] = request.session.get('손정효')
    chartData["Unknown"] = 0


    dataSource["chart"] = chartConfig
    dataSource["data"] = []

    # Convert the data in the `chartData` array into a format that can be consumed by FusionCharts.
    # The data for the chart should be in an array wherein each element of the array is a JSON object
    # having the `label` and `value` as keys.

    # Iterate through the data in `chartData` and insert in to the `dataSource['data']` list.
    for key, value in chartData.items():
        data = {}
        data["label"] = key
        data["value"] = value
        dataSource["data"].append(data)

    # Create an object for the column 2D chart using the FusionCharts class constructor
    # The chart data is passed to the `dataSource` parameter.
    column2D = fusioncharts.FusionCharts("column2d", "ex1", "480", "360", "chart-1", "json", dataSource)

    chartObj2 = fusioncharts.FusionCharts(
        'heatmap',
        'ex2',
        '480',
        '360',
        'chart-2',
        'json',
        {
            "chart": {
                "theme": "fusion",
                "caption": "Gait Pattern by Feature",
                "subcaption": "Source: 5 Static Features & 5 Dynamic Features in Gait",
                "showvalues": "1",
                "plottooltext": "<div><b>$rowLabel</b><br/>$columnLabel Rating: <b>$datavalue</b>/183</div>"
            },
            "rows": {
                "row": [
                    {
                        "id": "오윤석",
                        "label": "오윤석"
                    },
                    {
                        "id": "이동훈",
                        "label": "이동훈"
                    },
                    {
                        "id": "임혜진",
                        "label": "임혜진"
                    },
                    {
                        "id": "손정효",
                        "label": "손정효"
                    },
                    {
                        "id": "이동준",
                        "label": "이동준"
                    }
                ]
            },
            "columns": {
                "column": [
                    {
                        "id": "오윤석",
                        "label": "오윤석"
                    },
                    {
                        "id": "이동훈",
                        "label": "이동훈"
                    },
                    {
                        "id": "임혜진",
                        "label": "임혜진"
                    },
                    {
                        "id": "손정효",
                        "label": "손정효"
                    },
                    {
                        "id": "이동준",
                        "label": "이동준"
                    }
                ]
            },
            "dataset": [
                {
                    "data": [
                        {
                            "rowid": "오윤석",
                            "columnid": "오윤석",
                            "value": "5"
                        },
                        {
                            "rowid": "오윤석",
                            "columnid": "이동훈",
                            "value": "0"
                        },
                        {
                            "rowid": "오윤석",
                            "columnid": "임혜진",
                            "value": "0"
                        },
                        {
                            "rowid": "오윤석",
                            "columnid": "손정효",
                            "value": "155"
                        },
                        {
                            "rowid": "오윤석",
                            "columnid": "이동준",
                            "value": "1"
                        },
                        {
                            "rowid": "이동훈",
                            "columnid": "오윤석",
                            "value": "0"
                        },
                        {
                            "rowid": "이동훈",
                            "columnid": "이동훈",
                            "value": "0"
                        },
                        {
                            "rowid": "이동훈",
                            "columnid": "임혜진",
                            "value": "0"
                        },
                        {
                            "rowid": "이동훈",
                            "columnid": "손정효",
                            "value": "156"
                        },
                        {
                            "rowid": "이동훈",
                            "columnid": "이동준",
                            "value": "6"
                        },
                        {
                            "rowid": "임혜진",
                            "columnid": "오윤석",
                            "value": "0"
                        },
                        {
                            "rowid": "임혜진",
                            "columnid": "이동훈",
                            "value": "0"
                        },
                        {
                            "rowid": "임혜진",
                            "columnid": "임혜진",
                            "value": "149"
                        },
                        {
                            "rowid": "임혜진",
                            "columnid": "손정효",
                            "value": "15"
                        },
                        {
                            "rowid": "임혜진",
                            "columnid": "이동준",
                            "value": "5"
                        },
                        {
                            "rowid": "손정효",
                            "columnid": "오윤석",
                            "value": "0"
                        },
                        {
                            "rowid": "손정효",
                            "columnid": "이동훈",
                            "value": "0"
                        },
                        {
                            "rowid": "손정효",
                            "columnid": "임혜진",
                            "value": "0"
                        },
                        {
                            "rowid": "손정효",
                            "columnid": "손정효",
                            "value": "183"
                        },
                        {
                            "rowid": "손정효",
                            "columnid": "이동준",
                            "value": "3"
                        },
                        {
                            "rowid": "이동준",
                            "columnid": "오윤석",
                            "value": "18"
                        },
                        {
                            "rowid": "이동준",
                            "columnid": "이동훈",
                            "value": "0"
                        },
                        {
                            "rowid": "이동준",
                            "columnid": "임혜진",
                            "value": "4"
                        },
                        {
                            "rowid": "이동준",
                            "columnid": "손정효",
                            "value": "19"
                        },
                        {
                            "rowid": "이동준",
                            "columnid": "이동준",
                            "value": "128"
                        }
                    ]
                }
            ],
            "colorrange": {
                "gradient": "1",
                "minvalue": "0",
                "maxvalue": "183",
                "mapbypercent": "0",
                "code": "#67CDF2",
                "startlabel": "Poor",
                "endlabel": "Outstanding"
            }
        })
    chartdic =  {'output': column2D.render(), 'output2':chartObj2.render(), 'chartTitle1': '귀 인식 결과','chartTitle2':'걸음걸이 Confusion Matrix'}
    return chartdic













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


