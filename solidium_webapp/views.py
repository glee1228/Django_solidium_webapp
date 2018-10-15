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
from django.http import HttpResponse,StreamingHttpResponse, HttpResponseServerError
import numpy as np
from django.views.decorators import gzip
from time import sleep
import subprocess
import os
def main_view(request):
    return render(request, 'main.html', {})


def uimage(request):
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)  # 이미지 업로드 폼
        if form.is_valid():
            myfile = request.FILES['image']
            fs = FileSystemStorage()  # 이미지 저장 함수
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            return render(request, 'uimage.html',
                      {'form': form, 'uploaded_file_url': uploaded_file_url})
    else:
        form = UploadImageForm()
        return render(request, 'uimage.html',
                      {'form': form})

def dface(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()

            imageURL = settings.MEDIA_URL + form.instance.document.name
            opencv_dface(settings.MEDIA_ROOT_URL + imageURL)

            return render(request, 'dface.html', {'form': form, 'post': post})
    else:
        form = ImageUploadForm()
    return render(request, 'dface.html', {'form': form})

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

class VideoCamera(object):
    def __init__(self,path):
        self.video = cv2.VideoCapture(path)
        #self.face_cascade = face
        #self.eye_cascade = eye

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        #image = cv2.flip(image, -1)
        ret, jpeg = cv2.imencode('.jpg', image)
        sleep(0.07)
        return jpeg.tobytes()

def video_feed(request):
    return HttpResponse(gen(VideoCamera()),
                    content_type='multipart/x-mixed-replace; boundary=frame')


def indexscreen(request):
    try:
        template = "screens.html"
        return render(request, template)
    except HttpResponseServerError:
        print("aborted")

def run(request):
    if request.method == 'POST':
        form = ScriptForm(request.POST)
        #print(form)
        if form.is_valid():

            my_env = {**os.environ, 'PATH': '/usr/sbin:/sbin:' + os.environ['PATH']}
            #print(my_env)
            ear_script_path = "./solidium_webapp/ear_app/ear_test_change.py"

            proc = subprocess.Popen(['python3',ear_script_path],stdout=subprocess.PIPE,env=my_env)
            result=[]
            while proc.poll() is None:
                output = proc.stdout.readline()
                result.append((output).decode())
            #output = result.communicate()[0]
            #print(output)
            return render(request,"run.html",{'result':result })

    else:
        form = ScriptForm()
    return render(request, 'run.html', {'form': form})


@gzip.gzip_page
def stream(request, num=0, stream_path="172.0.0.1"):
    stream_path = './media/video/123.mp4'
    return StreamingHttpResponse(gen(VideoCamera(stream_path)), content_type="multipart/x-mixed-replace;boundary=frame")




