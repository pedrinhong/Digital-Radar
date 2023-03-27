import cv2 as cv
import numpy as np
from tracker import *

BOX_COLOR_OKAY = (0,255,0)
BOX_COLOR_OVER = (0,0,255)
BOX_THICKNESS = 2
RED = (255,0,0)

class Camera:

    def __init__(self,speed):
       self.ROAD_MASK = cv.imread(r"C:\Users\pedri\Downloads\RoadMask.jpg")[:,:,0]
       self.tracking = Tracker(60)
       self.exceedid = {}
       self.countf = 0
       self.exceed = 0
       self.area1 = [(340, 423), (587, 446), (555, 576), (142, 543)]
       self.area2 = [(697, 447), (921, 431), (1068, 531), (732, 576)]
       self.frame = None
    
    def run(self,capture:cv.VideoCapture):
        backgtroundSubtractor =  cv.bgsegm.createBackgroundSubtractorMOG()
        while(capture.isOpened()):
            self.countf += 1
            ret,self.frame = capture.read()
            
            if not ret:
                raise  Exception("Erro! Vídeo não pôde ser carregado apropriadamente.") 
            
            grayFrame = cv.cvtColor(self.frame,cv.COLOR_BGR2GRAY)
            blurredFrame = cv.GaussianBlur(grayFrame,(3,3),5)  # Testar outro filtros (se fizer diferença no resultado final)
            noBGFrame = backgtroundSubtractor.apply(blurredFrame) 
            
            np.bitwise_and(noBGFrame,self.ROAD_MASK,noBGFrame)
                
            kernelM = cv.getStructuringElement(cv.MORPH_ELLIPSE,(6,6))
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_CLOSE,kernelM,iterations=2)
            noBGFrame = cv.morphologyEx(noBGFrame,cv.MORPH_OPEN,kernelM,iterations=3)
            
            contours,_ = cv.findContours(noBGFrame, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                
            detected = self.getPoints(contours)
            
            out = self.tracking.update(detected,self.countf)
            
            self.display(out,detected)
            
            cv.imshow("Video:",self.frame)

            if cv.waitKey(1) == ord('q'):   
                break
            
        capture.release()
        cv.destroyAllWindows()
    
    def getPoints(self,contours):
        detected = []
        for objectCoords in contours:
            area = cv.contourArea(objectCoords)
            #If its area is less than 1000, its probably not a vehicule.
            if area < 1000:
                continue

            x,y,w,h = cv.boundingRect(objectCoords)
            #Pegar centro do objeto
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            #desenha polígonos no vídeo
            for a in [self.area1, self.area2]:
                cv.polylines(self.frame, [np.array(a, np.int32)], True, BOX_COLOR_OKAY,BOX_THICKNESS)
            
            #contorna o veiculo somente quando o centro dele cruza com o poligono
            inRoi = False
            testPoly = cv.pointPolygonTest(np.array(self.area1, np.int32), (cx,cy), False)
            testPoly2 = cv.pointPolygonTest(np.array(self.area2, np.int32), (cx,cy), False)
            if testPoly >= 0 or testPoly2 >= 0:
                inRoi = True
                
            #Vendo só os da pista direita.
            if (cy < LOW_POINT_RIGHT_POLY and cy > TOP_LINE_RIGHT) or (cy > HIGH_POINT_LEFT_POLY):
                detected.append((x,y,w,h,inRoi))
                
        return detected
        
    def display(self,out,detected):
        for i in range(len(out)):
            id,speed = out[i]
            
            if(id == -1 and speed == -1):
                continue
            
            x,y,w,h,_ = detected[i]
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            
            if self.tracking.overSpeed(speed):
                box_color = BOX_COLOR_OVER
                if self.exceedid.get(id) == None:
                    self.exceedid[id] = True
                    self.exceed += 1
            else:
                box_color = BOX_COLOR_OKAY
        
            self.frame = cv.rectangle(self.frame,(x,y),(x+w-10,y+h-10),box_color,BOX_THICKNESS)
            if(speed != 0):
                cv.putText(self.frame,str(id)+f" : {speed:.2f} km/h",(x,y-15),cv.FONT_HERSHEY_PLAIN,1,(255,255,0),2)
            else:
                cv.putText(self.frame,str(id),(x+30,y),cv.FONT_HERSHEY_PLAIN,1,(255,255,0),2)
            cv.circle(self.frame, (cx,cy),5,(255,255,255),BOX_THICKNESS)
                
        cv.putText(self.frame, f'Vehicles: {self.tracking.getAmount()}', (450, 70), cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        cv.putText(self.frame, f'Infractors: {self.exceed}', (40, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
video = cv.VideoCapture(r"C:\Users\pedri\Downloads\cars_video.mp4")
            
cam = Camera(60)
cam.run(video)