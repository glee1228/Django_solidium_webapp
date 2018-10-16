from django.conf.urls import url
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns =[
    url(r'^$',MainView.as_view(),name='main'),
    url(r'^start/$',StartView.as_view(),name='start'),
    url(r'^run/$', RunView.as_view(),name='run'),
    url(r'^stream/$',StreamView.as_view(),name='stream'),
    url(r'^streaming/$',streaming,name='streaming'),
    url(r'^result/$',ResultView.as_view(),name='result'),
    url(r'^user/$',UserView.as_view(),name='user'),

]
#이미지 파일을 업로드 하기위한 설정
#urlpatterns += static(settings.MEDIA_URL,
#                      document_root=settings.MEDIA_ROOT)