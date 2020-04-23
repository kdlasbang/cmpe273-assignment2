#pip3 install opencv-python
#pip3 install numpy
import numpy as np
import utlis
from flask import Flask, escape, request, jsonify, send_file
import json 
import cv2
import os.path
from os import path    

app = Flask(__name__)
test_id=1
myIndex=[]

DB={"test":[],
    "scantron":[]}
if(os.path.exists("./DB.txt")):
    with open('./DB.txt') as f:
        DB = json.load(f)


@app.route('/api/tests',methods=['POST'])
def create_test():
    global test_id
    req=request.json
    if len(DB["test"])==0:
        DB["test"].append({"test_id":test_id,"subject":req["subject"],"answer_keys":req["answer_keys"],"submissions":[]})
        saveFile()
        return (jsonify(test_id=test_id,subject=req["subject"],answer_key=req["answer_keys"], submission= [])),201
    else:
        test_id+=1
        DB["test"].append({"test_id":test_id,"subject":req["subject"],"answer_keys":req["answer_keys"],"submissions":[]})
        saveFile()
        return (jsonify(test_id=test_id,subject=req["subject"],answer_key=req["answer_keys"],submission= [])),201


@app.route('/api/tests/<int:get_id>/scantrons',methods=['POST'])
def getPDF(get_id):
    if request.files.get(""):
        image = request.files[""]
        strid= str(get_id)
        url= "http://localhost:5000/files/"+strid+".jpg"
        addr="./files/"+strid+".jpg"
        image.save(addr)
        readfile(addr)
        
        for x in range (len(myIndex)):
            if(myIndex[x]==-1):
                myIndex[x]=""
                continue
            
            elif(myIndex[x]==0):
                myIndex[x]="A"
                continue
            
            elif(myIndex[x]==1):
                myIndex[x]="B"
                continue
            
            elif(myIndex[x]==2):
                myIndex[x]="C"
                continue
            
            elif(myIndex[x]==3):
                myIndex[x]="D"
                continue
            
            elif(myIndex[x]==4):
                myIndex[x]="E"
                continue
            

        score =0
        subject ="Math"
        result=[]
        for i in range (len(myIndex)):
            result.append( {str(i+1) :{"actual":DB["test"][0]["answer_keys"][str(i+1)], "expected" : myIndex[i]} })
            if(DB["test"][0]["answer_keys"][str(i+1)]==myIndex[i]):
                score+=1
    DB["scantron"].append({"scantron_id":get_id,"scantron_url":url,"name":"Foo Bar","subject":subject,"Score":score,"result":result})

    for i in range(len(DB["test"])):
        if(DB["test"][i]["subject"]==subject):
            DB["test"][i]["submissions"].append({"scantron_id":get_id,"scantron_url":url,"name":"Foo Bar","subject":subject,"Score":score,"result":result})
    saveFile()
    
    return (jsonify(scantron_id=get_id,scantron_url=url,name="Foo Bar",subject= subject, Score=score , result=result)),201


@app.route('/api/tests/<int:get_id>',methods=['GET'])
def get_test(get_id):
    if(len(DB["test"])==0):
        return 'Currently no test, please POST first.'
    for i in range(len(DB["test"])):
        if DB["test"][i]['test_id']==get_id:
            return DB["test"][i]
    return 'No This test ID, sorry!'






@app.route('/')
def fileurl():
    get_id = 1
    addr="./files/"+str(get_id)+".jpg"
    return send_file(
            addr,
            mimetype='image/jpge',
            attachment_filename='snapshot.png',
            cache_timeout=0
        )


def saveFile():
    with open('./DB.txt', 'w') as json_file:
        json.dump(DB, json_file)





def readfile(path):
    #===============================
    #path = "scantron-100.jpg"
    widthImg = 1245
    heightImg=3000
    question =50
    choices = 5
    #===============================
    img = cv2.imread(path)

    #PREPROCESSING
    img = cv2.resize(img,(widthImg,heightImg))
    imgContours = img.copy()
    imgBiggestContours = img.copy()
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
    imgCanny = cv2.Canny(imgBlur,10,50)

    # FINDING ALL CONTOURS
    countours, hierarchy = cv2.findContours(imgCanny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(imgContours,countours,-1,(0,255,0),10)

    #FIND RECTANGLES
    rectCon = utlis.rectContour(countours)
    biggestContour = utlis.getCornerPoints(rectCon[0])
    gradePoints = utlis.getCornerPoints(rectCon[1])
    test = biggestContour.copy()
    test[0][0]=[333,2617]
    test[1][0]=[331,437]
    test[2][0]=[775,437]
    test[3][0]=[778,2617]
    #print("ttt:",test)
    #print("\n for contour\n",biggestContour )
    #print("\n for grade\n",gradePoints)
    biggestContour=test

    if biggestContour.size != 0 and gradePoints.size != 0:
        cv2.drawContours(imgBiggestContours,biggestContour,-1,(0,255,0),20)
        cv2.drawContours(imgBiggestContours,gradePoints,-1,(255,0,0),20)

        biggestContour= utlis.reorder(biggestContour)
        gradePoints = utlis.reorder(gradePoints)

        pt1 = np.float32(biggestContour)
        pt2= np.float32([[0,0],[widthImg,0],[0,heightImg],[widthImg,heightImg]])
        matrix = cv2.getPerspectiveTransform(pt1,pt2)
        imgWarpColored = cv2.warpPerspective(img,matrix,(widthImg,heightImg))

        ptG1 = np.float32(gradePoints)
        ptG2 = np.float32([[0,0],[325,0],[0,150],[325,150]])
        matrixG = cv2.getPerspectiveTransform(ptG1, ptG2)
        imgGradeDisplay = cv2.warpPerspective(img, matrixG,(325, 150))
        #cv2.imshow("Grade", imgGradeDisplay)

        imgWarpGray = cv2.cvtColor(imgWarpColored,cv2.COLOR_BGR2GRAY)
        imgThresh = cv2.threshold(imgWarpGray,150,255,cv2.THRESH_BINARY_INV)[1]
        #cv2.imshow("Grade", imgThresh)
        
        boxes = utlis.splitBoxes(imgThresh)
        #cv2.imshow("test", boxes[4])
        #print(cv2.countNonZero(boxes[2]),cv2.countNonZero(boxes[0]))


        #GETTING NO ZERO PIXEL VALUES OF EACH BOX
        myPixelVal = np.zeros((question,choices))
        countC = 0
        countR = 0

        for image in boxes:
            totalPixels = cv2.countNonZero(image)
            myPixelVal[countR][countC] = totalPixels
            countC +=1
            if (countC == choices):countR+=1; countC=0
        #print(myPixelVal)

        global myIndex
        localmyIndex = []
        for x in range(0, question):
            arrline = myPixelVal[x]
            arrmed= np.median(arrline)
            localmyIndex.append(-1)
            for y in range(0,choices):
                if(myPixelVal[x][y]/arrmed > 2):
                    localmyIndex[x]=y
        myIndex = localmyIndex




    imgBlank = np.zeros_like(img)
    imageArray = ([img,imgGray,imgBlur,imgCanny],
    [imgContours,imgBiggestContours,imgWarpColored,imgThresh])
    imgStacked = utlis.stackImages(imageArray,0.5)


    #cv2.imshow("stacked images",imgStacked)
    cv2.waitKey(0)
