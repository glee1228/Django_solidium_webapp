import numpy as np
import cv2

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)

info = {'face':[800,500,10000,30]}

while 1:
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)


    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img,'Face',(x+w/2,y+h), font, 0.5, (11,255,255), 2, cv2.LINE_AA)
        cv2.putText(img,'Credit Score: '+str(info['face'][0]),(x-w/2,y+h), font, 0.5, (11,255,255), 2, cv2.LINE_AA)
        cv2.putText(img,'Current Balance: '+str(info['face'][2]),(x-w/2,y+h/227), font, 0.5, (11,255,255), 2, cv2.LINE_AA)
        print(x,y)
    cv2.imshow('img',img)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
