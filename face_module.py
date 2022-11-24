#face_module.py
import gpiozero as gpio
import os
import time
import cv2
import numpy as np
from PIL import Image
from sensor_module import *


def face_recognition(): # 30번 연속 동일인(등록된)이면 신뢰도평균 출력 후 True 반환

    start1 = time.time()    # for no recognition
    start2 = time.time()    # for recognition

    count = 0

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    cascadePath = "/home/user/opencv/data/haarcascades/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)
    font = cv2.FONT_HERSHEY_SIMPLEX

    #initiate id counter
    id = 0
    id_ = [0] * 30

 
    # Initialize and start realtime video capture
    cam = cv2.VideoCapture(cv2.CAP_V4L2) 
    cam.set(3, 640) # set video width
    cam.set(4, 480) # set video height

    # Define min window size to be recognized as a face
    minW = 0.3*cam.get(3)   # initial : 0.1 / 0.1
    minH = 0.3*cam.get(4)

    sum = 0 # count if id is first recognized id && confidence < 50
    n = 0 # index of id array & loop count

    while True:
      
        ret, img = cam.read()
        img = cv2.flip(img, 1) # Flip horizontally
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.1, # initial : 1.2
            minNeighbors = 6, # 3 ~ 6, initial : 5 
            minSize = (int(minW), int(minH)),
        )

        for(x,y,w,h) in faces:
            start2 = time.time()    #face recognition ok
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
            # Check if confidence is less them 100 ==> "0" is perfect match
            confidence = 100 - (int)(confidence)
           
            print("face detected!")
            if (confidence > 50): # initial : 0, changed for better distinction
                
                while (n >= 0) & (n < 30):
                    print("n : ", n)
                    id_[n] = id  # first recognized id 

                    if (id_[0] != id_[n]):
                        id_[0] = id_[n]
                        n = 0
                        sum = 0
                        break

                    n += 1
                    sum += confidence   # to get average of confidences
                    print("n : ", n, "sum : ", sum)

                if (n == 30): # 평균 출력하고 True 반환
                    print("average is : ", (sum / 30),  "%") 
                    print(time.time() - start1, "sec")
                    cam.release()
                    cv2.destroyAllWindows() # end of program
                    return True
            else:
                id = "unknown"          
                count += 1
                                
                if (count == 30): # if unknown face for 10sec
                    print("***unknown face***")
                    cam.release()
                    cv2.destroyAllWindows()
                    return 0
                    
        else:
            if (time.time() - start1 > 8) | (time.time() - start2 > 8): # nothing recognized
                print("\n***false alarm***")
                cam.release()
                cv2.destroyAllWindows()  #end of program
                return 0


def face_recognition2(): # 연속 30번 등록된 얼굴로 확인되면 해당 얼굴의 id 반환

    start1 = time.time()    # for no recognition
    start2 = time.time()    # for recognition

    count = 0

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    cascadePath = "/home/user/opencv/data/haarcascades/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)
    font = cv2.FONT_HERSHEY_SIMPLEX

    #initiate id counter
    id = 0
    id_ = [0] * 30

 
    # Initialize and start realtime video capture
    cam = cv2.VideoCapture(cv2.CAP_V4L2) 
    cam.set(3, 640) # set video width
    cam.set(4, 480) # set video height

    # Define min window size to be recognized as a face
    minW = 0.3*cam.get(3)   # initial : 0.1 / 0.1
    minH = 0.3*cam.get(4)

    n = 0 # index of id array & loop count

    while True:
      
        ret, img = cam.read()
        img = cv2.flip(img, 1) # Flip horizontally
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.1, # initial : 1.2
            minNeighbors = 6, # 3 ~ 6, initial : 5 
            minSize = (int(minW), int(minH)),
        )

        for(x,y,w,h) in faces:
            start2 = time.time()    #face recognition ok
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
            # Check if confidence is less them 100 ==> "0" is perfect match
            confidence = 100 - (int)(confidence)
           
            if (confidence > 50): # initial : 0, changed for better distinction
                
                while (n >= 0) & (n < 30): # 30번 확인할 동안 동일인인지 확인
                    id_[n] = id  # first recognized id 

                    if (id_[0] != id_[n]): # 중간에 다른 사람으로 인식되면 카운트 초기화
                        id_[0] = id_[n]
                        n = 0
                        break

                    n += 1

                if (n == 30): #30번 동일인으로 판단되면 해당 인물의 id 반환
                    cam.release()
                    cv2.destroyAllWindows() # end of program
                    return id_[0]
            else:
                id = "unknown"          
                count += 1
                                
                if (count == 30): # if unknown face for 10sec
                    print("\nunknown face, face adding start")
                    cam.release()
                    cv2.destroyAllWindows()
                    return 0
                    
        else: #얼굴 미탐지인 상태로 8초 경과 시 종료
            if (time.time() - start1 > 8) | (time.time() - start2 > 8): # nothing recognized
                print("\n***false alarm***")
                cam.release()
                cv2.destroyAllWindows()  #end of program
                return 0



def face_add(face_id): #얼굴 등록

    if (face_id < 0) | (face_id > 10): # 예외처리
        print("invalid id")
        return 0
    
    
    idx = 0
    if (face_id != 1):
        idx = face_recognition2()        
    
    face_detector = cv2.CascadeClassifier('/home/user/opencv/data/haarcascades/haarcascade_frontalface_default.xml')
    
    print("\nLook at the camera and wait ...") 

    cam = cv2.VideoCapture(cv2.CAP_V4L2)
    cam.set(3, 640) # set video width
    cam.set(4, 480) # set video height

    minW = 0.3*cam.get(3)
    minH = 0.3*cam.get(4)

    # Initialize individual sampling face count
    count = 0
    while(True):
        ret, img = cam.read()
        img = cv2.flip(img, 1) #  flip video image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(
            gray, 
            scaleFactor = 1.1, 
            minNeighbors = 6,
            minSize = (int(minW), int(minH)),
        )

        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            count += 1
            # Save the captured image into the datasets folder
            if (idx != 0):
                cv2.imwrite("dataset/User." + str(idx) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
                cv2.imshow('image',img)
                time.sleep(0.5)
                
                if (count == 30):
                    return 0
            else:
                cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])

        if count == 30: # Take 30 face sample and stop
            face_id += 1
            with open("/home/user/Desktop/face_id.txt", "w") as f:
                f.write(str(face_id))
            break

    # Do a bit of cleanup
    print("\nExiting Program")
    cam.release()
    cv2.destroyAllWindows()
    return 0

def face_training(): #얼굴 학습

    # Path for face image database
    path = 'dataset'
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier("/home/user/opencv/data/haarcascades/haarcascade_frontalface_default.xml");

    # function to get the images and label data
    def getImagesAndLabels(path):
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
        faceSamples=[]
        ids = []
        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
            img_numpy = np.array(PIL_img,'uint8')
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = detector.detectMultiScale(img_numpy)
            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)
        return faceSamples,ids
    print ("\nTraining faces. It will take a few seconds. Wait ...")
    faces,ids = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))

    # Save the model into trainer/trainer.yml
    recognizer.write('trainer/trainer.yml') 

    # Print the number of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))

def remove_all(): #얼굴 전체 삭제
    os.system("rm -rf /home/user/Desktop/dataset/*.jpg")
    print("all data removed")
    with open("face_id.txt","w") as f:
        f.write("1")