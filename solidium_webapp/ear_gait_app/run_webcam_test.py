import argparse
import logging
import time
import cv2
import numpy as np
import math
import collections
from solidium_webapp.ear_gait_app.tf_pose.estimator import TfPoseEstimator
from solidium_webapp.ear_gait_app.tf_pose.networks import get_graph_path, model_wh
from math import exp
import tkinter
from tkinter import messagebox
import sklearn
from sklearn import svm
from collections import Counter
import pandas as pd
from solidium_site import settings

# Euclid = 두 점 사이의 유클리드 거리 반환

def Euclid(a, b) : 
    return (((a[0]-b[0])**2 + (a[1]-b[1])**2)**0.5)

logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0
timestart = time.time()
ifstart = 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--resize', type=str, default='0x0',
                        help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
    parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                        help='if provided, resize heatmaps before they are post-processed. default=1.0')
    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin')
    parser.add_argument('--show-process', type=bool, default=False,
                        help='for debug purpose, if enabled, speed for inference is dropped.')
    args = parser.parse_args()
    logger.debug('initialization %s : %s' % (args.model, get_graph_path(args.model)))
    w, h = model_wh(args.resize)
    if w > 0 and h > 0:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
    else:
        e = TfPoseEstimator(get_graph_path(args.model), target_size=(432, 368))
    logger.debug('cam read+')
    cam = cv2.VideoCapture(args.camera)
    ret_val, image = cam.read()
    logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))



    bf = open(settings.EAR_GAIT_URL+"body_features_test.txt", "w")  # 비율과 각도 쓸 파일 입력
    while True:
        ret_val, image = cam.read()
        logger.debug('image process+')
        humans = e.inference(image, resize_to_default=(w > 0 and h > 0), upsample_size=args.resize_out_ratio)
        logger.debug('postprocess+')
        image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
        logger.debug('show+')
        cv2.putText(image,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 10),  cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)


        if (len(humans)) != 0 :
            if ifstart == 0 :
                timestart = time.time()
                ifstart = 1

        coordi = np.zeros([18, 2])
        for human in humans:
            for k in human.body_parts.values():
                coordi[int(k.part_idx), 0] = k.x
                coordi[int(k.part_idx), 1] = k.y
        
        
        cv2.imshow('tf-pose-estimation result', image)
        fps_time = time.time()

        features = np.zeros(12)
        center = np.zeros([2])
        center[0] = (coordi[8][0] + coordi[11][0]) / 2
        center[1] = (coordi[8][1] + coordi[11][1]) / 2
        av_1 = np.zeros([5, 2])
        av_2 = np.zeros([5, 2])
        al = np.zeros([5])
        angle = np.zeros([5])

        # static features
        features[0] = Euclid(coordi[2], coordi[5])  # 어깨
        features[1] = Euclid(coordi[2], coordi[4])  # 팔
        features[2] = Euclid(coordi[1], center)  # 상체
        features[3] = Euclid(coordi[8], coordi[11])  # 엉덩이
        features[4] = Euclid(coordi[8], coordi[10])  # 다리
        features[5] = Euclid(coordi[10], coordi[13])  # 보폭

        # dynamic features
        av_1[0] = coordi[12] - center
        av_1[1] = coordi[1] - coordi[11]
        av_1[2] = coordi[1] - coordi[8]
        av_1[3] = coordi[11] - coordi[12]
        av_1[4] = coordi[8] - coordi[9]

        av_2[0] = coordi[9] - center
        av_2[1] = coordi[12] - coordi[11]
        av_2[2] = coordi[9] - coordi[8]
        av_2[3] = coordi[13] - coordi[12]
        av_2[4] = coordi[10] - coordi[9]

        dotproduct = np.dot(av_1, np.transpose(av_2))  # 벡터 내적

        for x in range(5):
            angle[x] = dotproduct[x][x]  # 각도 계산

        # 벡터 길이 계산

        al[0] = Euclid(coordi[12],center) * Euclid(coordi[9], center)
        al[1] = Euclid(coordi[1],coordi[11]) * Euclid(coordi[11], coordi[12])
        al[2] = Euclid(coordi[1],coordi[8]) * Euclid(coordi[8], coordi[9])
        al[3] = Euclid(coordi[11],coordi[12]) * Euclid(coordi[12], coordi[13])
        al[4] = Euclid(coordi[8],coordi[9]) * Euclid(coordi[9], coordi[10])

        # 최종 각도 계산
        angle = angle / al

        # 최종 각도 넣기
        for x in range(5):
            features[x + 6] = angle[x]

        for x in range(len(features)-1):
            if features[x] == 0:
                features[x] = float('nan')

        filedata = "%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" \
                    % ((features[0]), (features[1]), (features[2]), (features[3]), (features[4]), (features[5]), (features[6]), (features[7]), (features[8]), (features[9]), (features[10]))
        bf.write(filedata)


        if (cv2.waitKey(1) == 27) | ((time.time() - timestart > 4) & ifstart == 1):
            break

    bf.close()

    # CSV 받아오기

    train = pd.read_csv(settings.EAR_GAIT_URL+'body_features.txt', \
                        names=['shoulder', 'arm', 'upperbody', 'pelvis', 'leg', 'step', 'angle1', 'angle2',
                               'angle3', 'angle4', 'angle5', 'name'])
    train.dropna(inplace=True)
    x_train = train.drop('name', axis=1)
    x_train = x_train.drop('shoulder',axis=1)
    x_train = x_train.drop('pelvis',axis=1)
    x_train = x_train.drop('step',axis=1)
    y_train = train['name']


    test = pd.read_csv(settings.EAR_GAIT_URL+'body_features_test.txt', \
                       names=['shoulder', 'arm', 'upperbody', 'pelvis', 'leg', 'step', 'angle1', 'angle2', 'angle3',
                              'angle4', 'angle5'])
    test.dropna(inplace=True)
    x_test = test.drop('shoulder', axis=1)
    x_test = x_test.drop('pelvis',axis=1)
    x_test = x_test.drop('step',axis=1)


    from sklearn.svm import SVC

    #학습
    clf = SVC(kernel='rbf')
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)
    print(y_pred)

    #정확도 측정
    from sklearn.model_selection import train_test_split
    x_tn, x_tt, y_tn, y_tt = train_test_split(x_train, y_train, test_size=0.20)
    from sklearn.svm import SVC
    clf = SVC(kernel='rbf')
    clf.fit(x_tn, y_tn)
    y_pd = clf.predict(x_tt)
    from sklearn.metrics import classification_report, confusion_matrix
    y100=list(y_tt)
    y200=list(y_pd)
    #print("--------------------",y100)
    #print("=====================",y200)
    print(confusion_matrix(y_tt,y_pd))
    print(classification_report(y_tt,y_pd))

    # 결과 출력
    y_list = list(y_pred)
    cnt = [y_list.count(0), y_list.count(1), y_list.count(2), y_list.count(3), y_list.count(4)]
    print("예상 확률 : ", max(cnt) / len(y_list))
    z = cnt.index(max(cnt))
    print(z)

    logger.debug('finished+')

    cv2.destroyAllWindows()
        
