## 웹 애플리케이션(Web Application) 

* 기능 소개

1. 1차 로그인, 회원가입

2. 걸음걸이 귀 인식 

3. 2차 로그인

4. 인식 결과와 불일치 시, 인증 불가

5. 인식 결과와 일치 시, feature을 담은 영상과 인식 최종 결과 차트로 열람 가능

6. 모든 페이지는 그 이전페이지에서만 순차적으로 접근 가능함(보안)

 

* 기술 소개
  * Django(Framework)
    *  Solidium_webapp
      * Ear_gait_app(보행,귀 전체 application)
        * Body_Feature_Extraction.py(tf-pose-estimation 오픈소스를 이용해 신체의 10개 특징좌표 추출)
        * Update_haarcascade_leftear.xml(Haar Algorithm 을 Adaboost로 학습한 xml)
        * Ear_detector.py(Opencv3.2, 귀를 검출하고 저장하는 python코드)
      * Urls
        * Main
          * Main.html 페이지 url
        * Start
          * 테스트 시작하는 start.html 페이지 url
        * Stream
          *  Stream.html 페이지 url
        * Streaming1
          *  귀 영상 스트리밍 url
        * Streaming2
          * 걸음걸이 영상 스트리밍 url
        * Result
          * 차트 및 그래프 시각화 url
      * Views
        *  MainView
          * Get
          *  Post
            *  로그인
            * 로그인 세션 생성
            * 회원가입
        * StartView
          * Get
          * Post
            * 이미지 데이터 삭제
        * RunView
          * Get
            * 안내 Sound 재생
            * 귀, 보행 인식 코드 재생
            * 인식 결과 가져오기
            * 1차 로그인 여부 확인 -> 인식 결과와 1차로그인 정보 일치 여부 확인
          * Post
            * 2차 인증 완료 시, StreamView로 이동
            * 2차 인증 실패 시, MainView로 이동
        * StreamView
          * Get
            * 귀를 검출한 이미지를 담은 영상 Streaming
            * 걸음걸이 feature 11개를 입힌 영상 Streaming
          * Post
        * ResultView
          * Get
            * FusionChart로 인식 결과 그래프로 시각화
          * Post
      * Templates
      * Main.html

![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image001.png)![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image002.png)![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image003.png)![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image004.png)

![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image005.png)![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image006.png)![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image007.png)![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image008.png)

l  Start.html![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image010.png)

l  Run.html![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image011.png)

l  Stream.html![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image013.png)

l  Result.html![img](file:////Users/donghoon/Library/Group%20Containers/UBF8T346G9.Office/TemporaryItems/msohtmlclip/clip_image015.png)

 