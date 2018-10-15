#!/opt/local/bin/python
# -*- coding: utf-8 -*-
import cv2
import time
import numpy as np
#재생할 파일 
#VIDEO_FILE_PATH = '0'
left_ear_cascade = cv2.CascadeClassifier('./media/update_haarcascade_leftear.xml')

# 동영상 파일 열기
cap = cv2.VideoCapture(0)
if left_ear_cascade.empty():
  raise IOError('Unable to load the left ear cascade classifier xml file')


#print (cap)

#print (cv2.CAP_PROP_FRAME_WIDTH)
#print (cv2.CAP_PROP_FRAME_HEIGHT)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
#잘 열렸는지 확인
if cap.isOpened() == False:
    print ('Can not open the video ')
    exit()

titles = ['orig']
#윈도우 생성 및 사이즈 변경
for t in titles:
    cv2.namedWindow(t)

#재생할 파일의 넓이 얻기
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#재생할 파일의 높이 얻기
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#재생할 파일의 프레임 레이트 얻기
fps = cap.get(cv2.CAP_PROP_FPS)

print('width {0}, height {1}, fps {2}'.format(width, height, fps))

#XVID가 제일 낫다고 함.
#linux 계열 DIVX, XVID, MJPG, X264, WMV1, WMV2.
#windows 계열 DIVX
#저장할 비디오 코덱
fourcc = cv2.VideoWriter_fourcc(*'X264')
#저장할 파일 이름
#경로 :
filename = './media/video/123.mp4'

#파일 stream 생성
out = cv2.VideoWriter(filename, fourcc, fps, (int(width), int(height)))
#filename : 파일 이름
#fourcc : 코덱
#fps : 초당 프레임 수
#width : 넓이
#height : 높이
timestart = time.time()
start = 0

#left,right ear cropped image numbering
l_ear_num = 0

while(True):
    #파일로 부터 이미지 얻기
    ret, frame = cap.read()
    #더 이상 이미지가 없으면 종료
    #재생 다 됨
    if frame is None:
        break;

    #귀 영상 처리
    grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    left_ear = left_ear_cascade.detectMultiScale(grayframe, 1.3, 5)

    for (x, y, w, h) in left_ear:
        l_ear_path="./media/leftear/%04d.jpg"%l_ear_num
        cv2.rectangle(frame, (x-10, y-7), (x + w+13, y + h+7), (0, 255, 0), 1)
        crop_left_ear = frame[y-5:y+h+5, x-5:x + w+11]
        cv2.imwrite(l_ear_path, crop_left_ear)
        l_ear_num+=1


    # 얼굴 인식된 이미지 화면 표시
    cv2.imshow(titles[0],frame)

    # 인식된 이미지 파일로 저장
    out.write(frame)

    if len(left_ear) != 0:
        if start == 0:
            timestart = time.time()
            start = 1
    #1ms 동안 키입력 대기
    if (cv2.waitKey(1) & 0xFF == ord('q'))| ((time.time() - timestart > 5)& start==1):
        break

#재생 파일 종료
cap.release()
#저장 파일 종료
out.release()
#윈도우 종료
cv2.destroyAllWindows()
