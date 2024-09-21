import os
import pickle
import cvzone
import cv2
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
from datetime import datetime
import numpy as np

cred = credentials.Certificate("serviceAccountkey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendence1576-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendence1576.appspot.com"
})
bucket=storage.bucket()

cap= cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

imgBackground=cv2.imread("Resources/Attendence System.png")

#importing the modes images into list
folderModePath='Resources/Modes'
modePathList=os.listdir(folderModePath)
imgModeList=[]
# print(modePathList)
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
# print(len(imgModeList))

#load the encoding file
print("Loading Encode Files.....")
file=open('EncodeFile.p','rb')
encodeListKnownWithIds=pickle.load(file)
file.close()
encodeListKnown,studentIds=encodeListKnownWithIds
# print(studentIds)
print("Encode Files Loaded.....")

modeType=0 #means active
counter=0
id=0
imgStudent=[]


while True:
    success,img =cap.read()
    #reducing the size of image
    imgS=cv2.resize(img,(0,0),None,0.25,0.25)
    imgS=cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    #now feeding face
    faceCurFrame=face_recognition.face_locations(imgS)
    encodeCurFrame=face_recognition.face_encodings(imgS,faceCurFrame)


    # cv2.imshow("WebCam",img)
    # #overlay image background and webcam
    imgBackground[0:0+480,1:1+640]=img
    imgBackground[62:62+402,678:678+246]=imgModeList[modeType]
    if faceCurFrame:
        #now looping through encodings to check wether feed is matched
        for encodeFace,faceLoc in zip(encodeCurFrame,faceCurFrame):
            matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis=face_recognition.face_distance(encodeListKnown,encodeFace)
            # print("matches",matches)
            # print("facedis",faceDis)

            #getting index of min facedis in vector/array
            matchIndex=np.argmin(faceDis)
            # print("match Index",matchIndex)

            #now coparing the matches with the min distance (matchIndex)
            #if matchindex and matches vector index is true then face match found
            if matches[matchIndex]: # means true
                # print("known face detecte")
                # print(studentIds[matchIndex])
                #drawing rectangle around face
                y1,x2,y2,x1=faceLoc
                y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4 #becouse we reduce the size of image earlier to 25% so to get full we need to *4
                bbox=0+x1,1+y1,x2-x1,y2-y1 #adding 0 and one becase webcam is slightly shifted
                imgBackground=cvzone.cornerRect(imgBackground,bbox,rt=0)
                id=studentIds[matchIndex]
                if counter==0:
                    cvzone.putTextRect(imgBackground,"Loading",(240,400),2)
                    cv2.imshow("Face Attendence", imgBackground)
                    counter=1
                    modeType=3 

        if counter!=0:
            if counter==1:

                #getting the data
                studentInfo=db.reference(f'Students/{id}').get()
                print(studentInfo)

                #get the image _frommethod the storage
                blob=bucket.get_blob(f'Images/{id}.png')
                array=np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent=cv2.imdecode(array,cv2.COLOR_BGRA2BGR)#array to bgr

                # updating data of attendence
                # Convert the string to a datetime object
                last_attendence_time = studentInfo['last_attendence_time']
                dt_object = datetime.strptime(last_attendence_time, "%Y-%m-%d %H:%M:%S")
                # time before which you cannot mark attendence
                secondsElapsed=(datetime.now()-dt_object).total_seconds()
                print(secondsElapsed)
                if secondsElapsed>20:
                    ref=db.reference(f'Students/{id}')
                    studentInfo['total_attendence']+=1
                    ref.child('total_attendence').set(studentInfo['total_attendence'])
                    ref.child('last_attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType=2
                    counter=0
                    imgBackground[62:62 + 402, 678:678 + 246] = imgModeList[modeType]
            if modeType!=2:
                if 10<counter<20:
                   modeType=1
                imgBackground[62:62 + 402, 678:678 + 246] = imgModeList[modeType]

                if counter<=10:
                    # Extract and format the day and month
                    day_month = dt_object.strftime("%d-%m")


                    cv2.putText(imgBackground,str(studentInfo['total_attendence']),(678+140,62+45),cv2.FONT_HERSHEY_DUPLEX,0.5,(0,0,0),1)
                    #centring name
                    (w,h), _=cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_DUPLEX,1,1)
                    offset=(345-w)//2
                    # print(offset)
                    cv2.putText(imgBackground,str(studentInfo['name']),(678+offset,62+227),cv2.FONT_HERSHEY_DUPLEX,0.5,(0,0,0),1)
                    cv2.putText(imgBackground,str(id),(678+120,62+269),cv2.FONT_HERSHEY_DUPLEX,0.5,(0,0,0),1)
                    cv2.putText(imgBackground,str(studentInfo['Branch']),(678+125,62+306),cv2.FONT_HERSHEY_DUPLEX,0.5,(0,0,0),1)
                    cv2.putText(imgBackground,day_month,(678+55,62+361),cv2.FONT_HERSHEY_DUPLEX,0.35,(0,0,0),1)
                    cv2.putText(imgBackground,str(studentInfo['year']),(678+125,62+361),cv2.FONT_HERSHEY_DUPLEX,0.35,(0,0,0),1)
                    cv2.putText(imgBackground,str(studentInfo['Starting_year']),(678+193,62+361),cv2.FONT_HERSHEY_DUPLEX,0.35,(0,0,0),1)
                    resized_img = cv2.resize(imgStudent, (108, 108))
                    imgBackground[142:142+108,747:747+108]=resized_img
                counter+=1

                if counter>=20:
                    counter=0
                    modeType=0
                    studentInfo=[]
                    imgStudent=[]
                    imgBackground[62:62 + 402, 678:678 + 246] = imgModeList[modeType]

    else:
        modeType=0;
        counter=0;
        imgBackground[62:62 + 402, 678:678 + 246] = imgModeList[modeType]

    cv2.imshow("Face Attendence",imgBackground)
    cv2.waitKey(1)
#boiler plate template for running webcam oin python


