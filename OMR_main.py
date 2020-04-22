#pip3 install opencv-python
#pip3 install numpy
import cv2
import numpy as np
import utlis

#===============================
path = "scantron-100.jpg"
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

    myIndex = []
    for x in range(0, question):
        arrline = myPixelVal[x]
        arrmed= np.median(arrline)
        myIndex.append(-1)
        for y in range(0,choices):
            if(myPixelVal[x][y]/arrmed > 2):
                myIndex[x]=y
    print(myIndex)




imgBlank = np.zeros_like(img)
imageArray = ([img,imgGray,imgBlur,imgCanny],
[imgContours,imgBiggestContours,imgWarpColored,imgThresh])
imgStacked = utlis.stackImages(imageArray,0.5)


#cv2.imshow("stacked images",imgStacked)
cv2.waitKey(0)
