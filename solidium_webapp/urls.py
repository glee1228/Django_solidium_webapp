from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns =[
    #url(r'^$',views.first_view,name='first_view'),
    url(r'^$',views.main_view,name='main_view'),
    url(r'^uimage/$',views.uimage, name='uimage'), # uimage라는 주소를 넣으면 uimage라는 함수에 내용을 전달하겠다는 뜻.
    url(r'^dface/$', views.dface, name='dface'),
    url(r'^run/$', views.run,name='run'),
    url(r'^stream/$',views.stream,name='stream'),
]
#이미지 파일을 업로드 하기위한 설정
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)