import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
cred = credentials.Certificate("serviceAccountkey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendence1576-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendence1576.appspot.com"
})

#importing the student images
folderPath='Images'
PathList=os.listdir(folderPath)
imgList=[]
studentIds=[]

# print(PathList)
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentIds.append(os.path.splitext(path)[0])# partition the image name and extension and the getting the name only

    fileName=f'{folderPath}/{path}'#uplaoding images to storage
    bucket=storage.bucket()
    blob=bucket.blob(fileName)
    blob.upload_from_filename(fileName)


    # print(path)
    # print(os.path.splitext(path)[0]) # partition the image name and extension and the getting the name only
# print(len(imgList))
# print(studentIds)


def findEncodings(imagesList):
    encodeList=[]
    for img in imagesList:
        # step 1 BGR to RGB
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        #step 2 finding the encoding
        encode =face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# calling fuction to encode
print("Encoding Stated...")
encodeListKnown=findEncodings(imgList)
encodeListKnownWithIds=[encodeListKnown,studentIds]
print("Encoding Successfull...")


file=open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownWithIds,file)
file.close()

print("file saved")
