DIST = 7.5

class Vehicule:
    def __init__ (self, cx, cy, id, frame):
        self.cx = cx
        self.cy = cy
        self.id = id
        self.firstFrame = frame
        self.lastFrame = -1
        self.speed = -1
    
    def update(self,newCx,newCy):
        self.cx = newCx
        self.cy = newCy
        
    def setFinal(self,finalPos):
        self.lastFrame = finalPos
        
    def setSpeed(self,fps):
        time = (self.lastFrame - self.firstFrame)/fps
        self.speed = 3.6*DIST/time