#!/usr/bin/python

import sys,math

class Via:
    def __init__(self,viaName="",posX=0,posY=0,viaDia=""):
        self.id=0
        self.x=posX
        self.y=posY
        self.name=viaName
        self.dia=viaDia
        self.stamp=[0,0,0]
        self.state=0

    def __sub__(self,v):
        return math.sqrt((self.x-v.x)**2+(self.y-v.y)**2)

    def __eq__(self,v):
        return (self.x==v.x and self.y==v.y)
        
    def stampCount(self):
        return self.stamp[0]+self.stamp[1]+self.stamp[2]

class Tool:
    def __init__(self,f=""):
        self.vias=[]
        if f!="":
            self.load(f)

    def addVia(self,v):
        if len(self.vias)==0 or v.id>self.vias[len(self.vias)-1].id:
            self.vias.append(v)
            return len(self.vias)-1
        else:
            i=self.seek(v.id)
            self.vias.insert(i,v)
            return i
    def count(self):
        return len(self.vias)
        
    def seek(self,id):
        if len(self.vias)==0:
            return -1
        
        iMin=0
        iMax=len(self.vias)-1
        iNow=0
        while iMax-iMin>1:
            iNow=(iMin+iMax)//2
            if self.vias[iNow].id<id:
                iMin=iNow
            else:
                iMax=iNow

        if self.vias[iMin].id>=id:
            return iMin
        else:
            return iMax
    
    def isNear(self,v,threshold):
        i=self.seek(v.id)
        j=i+1
        while i>=0:
            if self.vias[i]-v<threshold:
                return True
            elif v.x-self.vias[i].x>threshold:
                break
            i-=1
        while j<len(self.vias):
            if self.vias[j]-v<threshold:
                return True
            elif self.vias[j].x-v.x>threshold:
                break
            j+=1
        return False
        
    def getMinPitch(self,v,threshold):
        i=self.seek(v.id)
        j=i+1
        minPitch=threshold
        while i>=0:
            currentPitch=self.vias[i]-v
            if currentPitch<minPitch:
                minPitch=currentPitch
            elif v.x-self.vias[i].x>threshold:
                break
            i-=1
        while j<len(self.vias):
            currentPitch=self.vias[j]-v
            if currentPitch<minPitch:
                minPitch=currentPitch
            elif self.vias[j].x-v.x>threshold:
                break
            j+=1
        return minPitch

    def load(self,f):
        ofile=open(f,"r")
        self.vias=[]
        for line in ofile:
            if len(line) > 5 :
                s=line.strip("\n").split(" ")
                self.vias.append(Via(s[0],float(s[1]),float(s[2]),s[3]))
        ofile.close()
        self.vias.sort(key=lambda v:v.x)
        for i,v in enumerate(self.vias):
            v.id=i
        return self
        
    def output(self,f="",memo="",isWriteMode=True):
        if f=="":
            for v in self.vias:
                 print v.x,v.y,v.dia,memo
        else:
            if isWriteMode:
                fo=open(f,"w")
            else:
                fo=open(f,"a")
            for v in self.vias:
                 fo.write(v.name+" "+str(v.x)+" "+str(v.y)+" "+str(v.dia)+" "+memo+"\n")
            fo.close()
    
class Splitter():
    def __init__(self,tool):
        self.orgTool=tool
        self.newTools=[Tool(),Tool(),Tool()]
        self.stampVias=[[],[]]
        self.log=[]
        self.testVia=Via()
        self.ngVia=Via()
        self.isRetry=False
        self.retryCount=0
    
    def updateStamp(self,v,toolID,threshold):
        vs=self.orgTool.vias
        stampLog=[]
        stampViasLog=[]
        i=self.orgTool.seek(v.id)
        j=i+1
        while i>=0:
            via=vs[i]
            if via-v<threshold:
                if via.stamp[toolID]==0:
                    via.stamp[toolID]=1
                    stampLog.append(via)
                    if via.stampCount()==1:
                        self.stampVias[0].append(via.id)
                        stampViasLog.append(-2)
                    elif via.stampCount()==2:
                        index=self.stampVias[0].index(via.id)
                        self.stampVias[0].pop(index)
                        stampViasLog.append(index)
                        self.stampVias[1].append(via.id)
                        stampViasLog.append(-1)
            elif v.x-vs[i].x>threshold:
                break
            i-=1
        while j<len(vs):
            via=vs[j]
            if via-v<threshold:
                if via.stamp[toolID]==0:
                    via.stamp[toolID]=1
                    stampLog.append(via)
                    if via.stampCount()==1:
                        self.stampVias[0].append(via.id)
                        stampViasLog.append(-2)
                    elif via.stampCount()==2:
                        index=self.stampVias[0].index(via.id)
                        self.stampVias[0].pop(index)
                        stampViasLog.append(index)
                        self.stampVias[1].append(via.id)
                        stampViasLog.append(-1)
            elif vs[j].x-v.x>threshold:
                break
            j+=1
            
        self.log.append({   "type":2,
                            "targetToolIndex":toolID,
                            "viaList":stampLog,
                            "stampList":stampViasLog
                        })
        
    def nextVia(self):
        if len(self.stampVias[1])>0:
            i=self.orgTool.seek(self.stampVias[1].pop())
            via=self.orgTool.vias.pop(i)
            self.log.append({   "type":0,
                                "srcStampIndex":1,
                                "srcViaIndex":i,
                                "srcVia":via
                            })
            return via
        elif len(self.stampVias[0])>0:
            i=self.orgTool.seek(self.stampVias[0].pop())
            via=self.orgTool.vias.pop(i)
            self.log.append({   "type":0,
                                "srcStampIndex":0,
                                "srcViaIndex":i,
                                "srcVia":via
                            })
            return via
        else:
            self.log=[]
            via=self.orgTool.vias.pop()
            self.log.append({   "type":-1,
                                "srcVia":via
                            })
            return via
            
    def splitVia(self,v,threshold):
        if v.state<1 and v.stampCount()==3:
            v.state=0
            self.foundNGVia(v,threshold)
            return
        if v.state<0:
            for i in [2,1,0]:
                if v.stamp[i]==0:
                    j=self.newTools[i].addVia(v)
                    self.log.append({   "type":1,
                                        "targetToolIndex":i,
                                        "targetViaIndex":j
                                    })
                    self.updateStamp(v,i,threshold)
                    break
            
        elif v.state==0:
            for i in range(0,3):
                if v.stamp[i]==0:
                    j=self.newTools[i].addVia(v)
                    self.log.append({   "type":1,
                                        "targetToolIndex":i,
                                        "targetViaIndex":j
                                    })
                    self.updateStamp(v,i,threshold)
                    if v is self.ngVia:
                        self.testVia.state=-2
                        self.isRetry=False
                    break
        elif v.state==1:
            maxPitch=0
            toolID=0
            for i in range(0,3):
                currentPitch=self.newTools[i].getMinPitch(v,threshold)
                if currentPitch>maxPitch:
                    maxPitch=currentPitch
                    toolID=i
            j=self.newTools[toolID].addVia(v)
            self.log.append({   "type":1,
                                "targetToolIndex":toolID,
                                "targetViaIndex":j
                            })
        else:
            pass
        
    def goBack(self):
        if self.retryCount>0:
            flag=False
        else:
            flag=True
        while len(self.log)>0:
            action=self.log.pop()
            actionType=action["type"]
            if actionType==-1:
                self.orgTool.vias.append(action["srcVia"])
            elif actionType==0:
                via=action["srcVia"]
                self.stampVias[action["srcStampIndex"]].append(via.id)
                self.orgTool.vias.insert(action["srcViaIndex"],via)
                if via.state==-1:
                    via.state=0
                    flag=True
                elif (flag and via.stampCount()==1 and via.state==0):
                    via.state=-1
                    self.testVia=via
                    return
            elif actionType==1:
                self.newTools[action["targetToolIndex"]].vias.pop(action["targetViaIndex"])
                
            elif actionType==2:
                for via in action["viaList"]:
                    via.stamp[action["targetToolIndex"]]=0
                
                li=action["stampList"]
                while len(li)>0:
                    v=li.pop()
                    if v<0:
                        id=self.stampVias[v+2].pop()
                    elif v>=0:
                        self.stampVias[0].insert(v,id)
        self.isRetry=False
        self.ngVia.state=1
        self.testVia.state=0

    def foundNGVia(self,v,threshold):
        if self.isRetry:
            self.retryCount+=1
        else:
            self.ngVia=v
            self.retryCount=0
            self.isRetry=True
        self.goBack()

        
threshold=0.182
if len(sys.argv)>3:
    inputFile=sys.argv[1]
    outputFile=sys.argv[2]
    threshold=float(sys.argv[3])
elif len(sys.argv)==3:
    inputFile=sys.argv[1]
    outputFile=sys.argv[2]
elif len(sys.argv)==2:
    inputFile=sys.argv[1]
    inputFile=sys.argv[1]
    outputFile=sys.argv[1]+".splited"
else:
    print "You should give a data file name at least."
    sys.exit()

try:
    viaHoles=Tool(inputFile)
    job=Splitter(viaHoles)
except:
    print "Openging source data file error!"
    sys.exit()

print "Source file:",inputFile
print "Target file:",outputFile
print "Threshold =",threshold,"\n"

try:
    while viaHoles.count()>0:
        job.splitVia(job.nextVia(),threshold)
except:
    print "Unexpected errors, please contact the programmer."
    sys.exit()

try:
    job.newTools[0].output(outputFile,"A",True)
    job.newTools[1].output(outputFile,"B",False)
    job.newTools[2].output(outputFile,"C",False)
except:
    print "Can't write the data to",outputFile,"!"
else:
    print "Job finished."
sys.exit()
