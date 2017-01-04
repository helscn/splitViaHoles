#!/usr/bin/python

#### Last update: 2017/01/04 ####

#Compatible with python2 and python3
from __future__ import print_function
import sys,math,os,re,random,time
if sys.version_info[0] == 2:
    input=raw_input

#Check the environment
try:
    from genBasic import *
except ImportError:
    GENESIS_ENV=False
else:
    GENESIS_ENV=True

class BitOptions(object):
    '''Save the binary option data by bit'''
    def __init__(self,value=0):
        self.__value=value
        self.__updateCount()
    
    def __updateCount(self):
        self.__count=0
        for i in range(len(bin(self.__value))-2):
            self.__count += self.__value>>i & 1
            
    def __call__(self,val):
        self.__value=val
        self.__updateCount()
        return self
        
    def __len__(self):
        return len(bin(self.__value))-2

    def __str__(self):
        return bin(self.__value)[2:]

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__,self.__value)

    def __getitem__(self,bit):
        return self.__value>>bit & 1

    def __setitem__(self,bit,val):
        if self.__value>>bit & 1 == 0:
            if val:
                self.__value = 1<<bit | self.__value
                self.__count += 1
        else:
            if not val:
                self.__value = ~(1<<bit) & self.__value
                self.__count -= 1

    @property
    def count(self):
        return self.__count

    @property
    def value(self):
        return self.__value

class Via(object):
    '''Save the data about via hole'''
    def __init__(self,viaName='',posX=0,posY=0,viaDia=''):
        self.id=0
        self.name=viaName
        self.x=float(posX)
        self.y=float(posY)
        self.dia=viaDia
        self.stamp=BitOptions()
        self.state=0
        self.retryCount=0
        self.isNear=False

    def __sub__(self,v):
        return math.sqrt((self.x-v.x)**2+(self.y-v.y)**2)

    def __eq__(self,v):
        return (self.x==v.x and self.y==v.y)
        
    def __repr__(self):
        return "Via('{name}',{x},{y},'{dia}')".format(**self.__dict__)
        
    def __str__(self):
        return "{name} {x} {y} {dia}".format(**self.__dict__)
    
class Tool(object):
    def __init__(self,f=None):
        self.vias=[]
        if f:
            self.load(f)
            
    def __iter__(self):
        return iter(self.vias)
        
    def __len__(self):
        return len(self.vias)
        
    def __contain__(self,v):
        return v in self.vias
        
    def checkPitch(self,threshold):
        for v in self.vias:
            v.isNear=False
        ngCount=0
        i=0
        while i<len(self.vias):
            v1=self.vias[i]
            j=i+1
            while j<len(self.vias):
                v2=self.vias[j]
                if v2-v1<=threshold:
                    v1.isNear=True
                    v2.isNear=True
                elif v2.x-v1.x>threshold:
                    break
                elif v2.x<v1.x:
                    self.sortVias()
                    i=0
                    j=1
                    continue
                j+=1
            if v1.isNear:
                ngCount+=1
            i+=1
        return ngCount
        
    def addVia(self,v):
        if len(self.vias)==0 or v.id>self.vias[-1].id:
            self.vias.append(v)
            return len(self.vias)-1
        else:
            i=self.seek(v)
            self.vias.insert(i,v)
            return i

    def seek(self,v):
        if isinstance(v,Via):
            id=v.id
        else:
            id=v
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
        i=self.seek(v)
        j=i+1
        while i>=0:
            if self.vias[i]-v<=threshold:
                return True
            elif v.x-self.vias[i].x>threshold:
                break
            i-=1
        while j<len(self.vias):
            if self.vias[j]-v<=threshold:
                return True
            elif self.vias[j].x-v.x>threshold:
                break
            j+=1
        return False
        
    def getMinPitch(self,v,threshold):
        i=self.seek(v)
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
        
    def sortVias(self):
        self.vias.sort(key=lambda v:v.x)
        for i,v in enumerate(self.vias):
            v.id=i
        return self

    def load(self,f):
        self.vias=[]
        pattern=re.compile(r"^(#?\d+)?\s*(?:#[A-Z]+\s+)?(-?\d*\.?\d+)\s+(-?\d*\.?\d+)\s+(r\d+)")
        with open(f,'r') as f:
            for line in f:
                m=pattern.match(line)
                if m:
                    n,x,y,r=m.groups()
                    self.vias.append(Via(n or '',x,y,r))
        self.sortVias()
        return self
        
    def output(self,name='',f=None):
        for v in self.vias:
            n=random.choice(name) if type(name) in [list,tuple,set] else name
            if hasattr(f,'write'):
                f.write('{0} {1}\n'.format(str(v),n))
            else:
                print('{0} {1}'.format(str(v),n))

    def genselect(self,wkLayer='',prex='_xx'):
        prex=random.choice(prex) if type(prex) in [list,tuple,set] else prex
        for v in self.vias:
            COM('sel_layer_feat,operation=select,layer='+wkLayer+',index='+str(v.name[1:]))
        if int(COM('get_select_count')[-1]) != 0:
            COM('sel_copy_other,dest=layer_name,target_layer='+wkLayer+prex+',invert=no,dx=0,dy=0,size=0,x_anchor=0,y_anchor=0,rotation=0,mirror=none')

class Splitter(object):
    def __init__(self,tool,threshold,newToolsCount=3):
        self.orgTool=tool
        self.threshold=threshold
        self.newTools=[]
        self.stampVias=[]
        for i in range(newToolsCount):
            self.newTools.append(Tool())
            self.stampVias.append([])
        self.newToolsCount=newToolsCount
        self.__log=[]
        self.__testVia=Via()
        self.__ngVia=Via()
        self.__isRetry=False
        self.__retryCount=0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        for i in range(self.newToolsCount-1,-1,-1):
            if len(self.stampVias[i])>0:                  #Near with other tools
                j=self.orgTool.seek(self.stampVias[i].pop())
                via=self.orgTool.vias.pop(j)
                self.__log.append({ 'type':0,             #Get a neighboring hole
                                    'srcStampIndex':i,
                                    'srcViaIndex':j,
                                    'srcVia':via
                                })
                return via
        if len(self.orgTool)>0:
            self.__log=[]
            via=self.orgTool.vias.pop()
            self.__log.append({ 'type':-1,                #New area start
                                'srcVia':via
                            })
            return via
        else:
            raise StopIteration
    
    next=__next__
    
    def filter(self,threshold=None):
        threshold=threshold or self.threshold
        self.orgTool.checkPitch(threshold)
        okTool=Tool()
        vs=self.orgTool.vias
        i=len(vs)-1
        while i>=0:
            if not vs[i].isNear:
                okTool.vias.append(vs.pop(i))
            i-=1
        okTool.vias=okTool.vias[-1::-1]                  #Reverse the via list
        return okTool

    def splitVia(self,v,threshold=None):
        threshold=threshold or self.threshold
        if v.state<1 and v.stamp.count==self.newToolsCount:     #Found ng via hole
            self.__foundNGVia(v)
            return
        if v.state==0:          #Normal via hole
            for i in range(self.newToolsCount):
                if v.stamp[i]==0:
                    j=self.newTools[i].addVia(v)
                    self.__log.append({ 'type':1,
                                        'targetToolIndex':i,
                                        'targetViaIndex':j
                                    })
                    self.__updateStamp(v,i)
                    
                    if v is self.__ngVia:   #Fix a ng hole
                        self.__testVia.state=-2
                        self.__isRetry=False
                        self.__retryCount=0
                    break
        elif v.state==1:        #Insert this ng hole into the farthest tool
            maxPitch=0
            toolID=0
            for i in range(self.newToolsCount):
                currentPitch=self.newTools[i].getMinPitch(v,threshold)
                if currentPitch>maxPitch:
                    maxPitch=currentPitch
                    toolID=i
            j=self.newTools[toolID].addVia(v)
            self.__log.append({ 'type':1,
                                'targetToolIndex':toolID,
                                'targetViaIndex':j
                            })
        elif v.state == -1:       #It's a testVia
            retry=v.retryCount
            for i in range(self.newToolsCount):
                if v.stamp[i]==0:
                    if retry>0:
                        retry-=1
                    else:
                        j=self.newTools[i].addVia(v)
                        self.__log.append({ 'type':1,
                                            'targetToolIndex':i,
                                            'targetViaIndex':j
                                        })
                        self.__updateStamp(v,i)
                        v.retryCount+=1
                        return
            
        elif v.state == -2:       #It's a testVia that can fix the ng hole
            retry=v.retryCount
            for i in range(self.newToolsCount):
                if v.stamp[i]==0:
                    if retry>0:
                        retry-=1
                    else:
                        j=self.newTools[i].addVia(v)
                        self.__log.append({ 'type':1,
                                            'targetToolIndex':i,
                                            'targetViaIndex':j
                                        })
                        self.__updateStamp(v,i)
                        return
        
    def __updateStamp(self,v,toolID):
        threshold=self.threshold
        vs=self.orgTool.vias
        stampLog=[]
        i=self.orgTool.seek(v)
        j=i+1
        while i>=0:
            via=vs[i]
            if via-v<threshold:
                if via.stamp[toolID]==0:
                    via.stamp[toolID]=1
                    stampIndex=via.stamp.count-1
                    self.stampVias[stampIndex].append(via.id)
                    holeIndex=None
                    if stampIndex>0:
                        #Popup neighboring holes from previous stamp list
                        holeIndex=self.stampVias[stampIndex-1].index(via.id)
                        self.stampVias[stampIndex-1].pop(holeIndex)
                    stampLog.append((via,stampIndex,holeIndex))
            elif abs(vs[i].x-v.x)>threshold:
                break
            i-=1
        
        while j<len(vs):
            via=vs[j]
            if via-v<threshold:
                if via.stamp[toolID]==0:
                    via.stamp[toolID]=1
                    stampIndex=via.stamp.count-1
                    self.stampVias[stampIndex].append(via.id)
                    holeIndex=None
                    if stampIndex>0:
                        #Popup neighboring holes from previous stamp list
                        holeIndex=self.stampVias[stampIndex-1].index(via.id)
                        self.stampVias[stampIndex-1].pop(holeIndex)
                    stampLog.append((via,stampIndex,holeIndex))
            elif abs(vs[j].x-v.x)>threshold:
                break
            j+=1
            
        self.__log.append({ 'type':2,
                            'targetToolIndex':toolID,
                            'stampLog':stampLog
                        })


    def __goBack(self):
        flag = False if self.__retryCount>0 else True       #flag=True means to back to the first testVia
        while len(self.__log)>0:
            action=self.__log.pop()
            actionType=action['type']
            if actionType==-1:                              #Get via hole from orgTool
                self.orgTool.vias.append(action['srcVia'])
                continue
            elif actionType==0:                             #Get via hole from neighboring holes
                via=action['srcVia']
                self.stampVias[action['srcStampIndex']].append(via.id)
                self.orgTool.vias.insert(action['srcViaIndex'],via)
                if via.state==-1:                           #Last testVia
                    if via.retryCount>=self.newToolsCount-via.stamp.count:
                        flag=True
                        via.state=0
                        via.retryCount=0
                        self.__retryCount+=1
                        continue
                    else:
                        return
                elif (flag and 0<via.stamp.count<self.newToolsCount-1 and via.state==0):
                    via.state=-1                            #First retry
                    self.__testVia=via
                    return
                elif via.state==-2:     #A old test via for ng hole
                    continue
            elif actionType==1:                             #Split via hole
                self.newTools[action['targetToolIndex']].vias.pop(action['targetViaIndex'])
                continue
            elif actionType==2:                             #Update the stamps
                toolIndex=action['targetToolIndex']
                while len(action['stampLog'])>0:
                    via,stampIndex,holeIndex=action['stampLog'].pop()
                    via.stamp[toolIndex]=0
                    id=self.stampVias[stampIndex].pop()
                    if holeIndex is not None:
                        self.stampVias[stampIndex-1].insert(holeIndex,id)
        self.__isRetry=False
        self.__retryCount=0
        self.__ngVia.state=1
        self.__testVia.state=0
        self.__testVia.retryCount=0

    def __foundNGVia(self,v):
        if self.__isRetry:
            self.__retryCount+=1
        else:
            self.__ngVia=v
            self.__retryCount=0
            self.__isRetry=True
        self.__goBack()

def valid_input(prompt='',func=None,errorMessage='Invalid input!'):
    while True:
        s=input(prompt)
        if not func:
            return s
        try:
            if hasattr(func,'__call__'):
                if func(s):
                    return s
                else:
                    raise ValueError
            elif hasattr(func,'match'):
                if func.match(s):
                    return s
                else:
                    raise ValueError
        except ValueError:
            print(errorMessage)
            continue

if GENESIS_ENV:
    ##################
    toolsCount=int(sys.argv[1]) if len(sys.argv[1])>1 else 3        #The quantity of new tools should >=3
    ##################
    if 'JOB' not in os.environ or 'STEP' not in os.environ:
        PAUSE('Need to run this from within a job and step...')
        sys.exit()
    COM('open_job,job='+os.environ['JOB'])
    xs = COM('open_entity,job='+os.environ['JOB']+',type=step,name='+os.environ['STEP']+',iconic=no')
    AUX('set_group,group='+xs[-1])
    wkLayer = COM('get_work_layer')[-1]
    if wkLayer == '':
        PAUSE('Need to run this on a work layer...')
        sys.exit()
    VOF()
    for i in range(toolsCount):
        COM('delete_layer,layer={0}{1:02}'.format(wkLayer,i+1))
        COM('create_layer,layer={0}{1:02},context=misc,type=drill,polarity=positive,ins_layer='.format(wkLayer,i+1))
    VON()
    COM('sel_clear_feat')
    COM('clear_layers')
    COM('affected_layer,name=,mode=all,affected=no')
    COM('pan_center,x=99,y=99')
    COM('units,type=inch')

    COM('display_layer,name='+wkLayer+',display=yes,number=1')
    COM('work_layer,name='+wkLayer)

    xinfo = DO_INFO('-t layer -e '+os.environ['JOB']+'/'+os.environ['STEP']+'/'+wkLayer+' -d SYMS_HIST')
    threshold = float(xinfo['gSYMS_HISTsymbol'][0][1:]) * 25.4 / 1000.0
    inputFile = '/tmp/gen_'+str(os.getpid())+'.'+os.environ['USER']+'.input'
    COM('info, out_file='+inputFile+',units=mm,args= -t layer -e '+os.environ['JOB']+'/'+os.environ['STEP']+'/'+wkLayer+' -d FEATURES -o feat_index')
else:
    inputFile = valid_input(prompt='Input the data file path: ',func=os.path.isfile,errorMessage='The file not exist!')
    outputFile = valid_input(prompt='Input the output file name: ',func=re.compile(r'^([^":\*\?]{1,254})$'),errorMessage='Invalid file name!')
    threshold = float(valid_input(prompt='Input the threshold value: ',func=float,errorMessage='Invalid threshold value!'))
    toolsCount = int(valid_input(prompt='Input the new tools count: ',func=int,errorMessage='Invalid tools count.'))

try:
    startTime=time.clock()
    viaHoles=Tool(inputFile)
    viaHolesCount=len(viaHoles)

    job=Splitter(viaHoles,threshold,toolsCount)
    okHolesTool=job.filter()
    okHolesCount=len(okHolesTool)

    print(  '\nTotal holes: {viaHolesCount}\n'
            'Threshold: {threshold}\n'
            'New tools count: {toolsCount}\n'
            '\nExclude {okHolesCount} via holes that pitch>{threshold}'
            .format(**locals())
        )

except:
    print('\nOpenging source data file error!')
    sys.exit()

try:
    for via in job:
        job.splitVia(via)
except:
    print('\nUnexpected errors, please contact the programmer.')
    sys.exit()

try:
    ngHolesCount=0
    for t in job.newTools:
        ngHolesCount+=t.checkPitch(threshold)
    print('\nTotal failed holes: {0}'.format(ngHolesCount))

    if GENESIS_ENV:
        toolNames=['{0:02}'.format(v+1) for v in range(toolsCount)]
        for v in range(toolsCount):
            job.newTools[v].genselect(wkLayer,'{0:02}'.format(v+1))
            COM('zoom_back')
        okHolesTool.genselect(wkLayer,toolNames)     #Random tool name
    else:
        with open(outputFile,'w') as f:
            toolNames=['T{0:02}'.format(v+1) for v in range(toolsCount)]
            for i in range(toolsCount):
                job.newTools[i].output(toolNames[i],f)
            okHolesTool.output(toolNames,f)     #Random tool name
except:
    print("\nCan't write the hole data!")
else:
    print('Job finished in {0:.2f} second(s).'.format(time.clock()-startTime))
    
sys.exit()
