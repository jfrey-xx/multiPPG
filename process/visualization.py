"""
 Author: Kwasi Mensah (kmensah@andrew.cmu.edu)
 Date: 8/02/2005

 This is meant to be a simple example of how to draw a cube
 using Panda's new Geom Interface. Quads arent directly supported 
 since they get broken down to trianlges anyway.
 
 
 Oculus rift bindings for Python: https://github.com/wwwtyro/python-ovrsdk
"""

import numpy as np
import matplotlib.pyplot as plt

from direct.directbase import DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.task import Task

from panda3d.core import *

import time

#from panda3d.core import lookAt
#from panda3d.core import GeomVertexFormat, GeomVertexData
#from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
#from panda3d.core import Texture, GeomNode
#from panda3d.core import PerspectiveLens
#from panda3d.core import CardMaker
#from panda3d.core import Light, Spotlight
#from panda3d.core import TextNode
#from panda3d.core import Vec3, Vec4, Point3

import sys, os

import socket
import array
import struct



#base.disableMouse()
base.camera.setPos(0, -10, 0)


escapeEvent = OnscreenText( 
 			 text="Esc: Exit the game",
     			 style=1, fg=(1,1,1,1), pos=(-1.3, 0.95),
			 align=TextNode.ALeft, scale = .05)
title = OnscreenText(text="Demo - Physiological signals-controlled world",
                       style=1, fg=(1,1,1,1),
                        align=TextNode.ARight,
                       pos=(1.3,0.95), scale = .07)
#escapeEvent = OnscreenText( 
# 			 text="1: Set a Texture onto the Cube",
#     			 style=1, fg=(1,1,1,1), pos=(-1.3, 0.95),
#			 align=TextNode.ALeft, scale = .05)
#spaceEvent = OnscreenText( 
# 			 text="2: Toggle Light from the front On/Off",
#     			 style=1, fg=(1,1,1,1), pos=(-1.3, 0.90),
#			 align=TextNode.ALeft, scale = .05)
#upDownEvent = OnscreenText( 
# 			 text="3: Toggle Light from on top On/Off",
#     			 style=1, fg=(1,1,1,1), pos=(-1.3, 0.85),
#			 align=TextNode.ALeft, scale = .05)
                       
                       
def mesHeaderFormat(header):
    """Extracts important info from the mesHeader"""
    
    cellHeader = header.split(',')
    for field in cellHeader:
        if field.find('DEVICE') != -1:
            ind = field.find('DEVICE')
            mesDevice = field[ind+len('DEVICE='):]
        elif field.find('FS') != -1:
            ind = field.find('FS')
            mesFs = int(field[ind+len('FS='):])
        elif field.find('DATA') != -1:
            ind = field.find('DATA')
            mesTags = field[ind+len('DATA='):]
        elif field.find('#CH') != -1:
            ind = field.find('#CH')
            mesCh = int(field[ind+len('#CH='):])
    
    return mesDevice, mesFs, mesTags, mesCh
    

def mesDataFormat(mesData, mesTags):
    """Returns an array of cells with the data divided by tag"""
    sizeBytes = 4
    nCh = len(mesTags)
    nBytes = len(mesData);
    nSamples = (nBytes/sizeBytes)/nCh;
    #mesData = np.uint8(mesData) # Convert from binary to integers (not necessary pyton)
    
    #Changing mesData to a list, size (nBytes,1)
    #Reordering the List into a number (4bytes) matrix wise in
    #dataPerSample which has size: (4,nBytes/4)
    #FlipUP to correct the swap in bytes    
    dataPerSample = np.flipud(np.reshape(list(bytearray(mesData)), [sizeBytes,-1],order='F'));
    #swapMesData has size: (nBytes,1)    
    swapMesDataUint8 = np.uint8(np.reshape(dataPerSample,[nBytes,-1],order='F' ));
    tagsForPackage = mesTags*nSamples;
    swapMesData = "".join(map(chr,swapMesDataUint8));
        
    preData = struct.unpack(tagsForPackage,swapMesData);
    
    mesEEG = np.reshape(np.array(preData),[nSamples,nCh],order='C');
    return mesEEG

    
def getEEGwindow(conn, mesFs, mesTags, windowSizeSeconds):
    nSamples = mesFs*windowSizeSeconds
    columns = len(mesTags)
    outputBuffer = np.zeros((nSamples,columns))

    while 1:
        nBytes_4B = array.array("B",conn.recv(4)) 
        nBytes = struct.unpack('i',nBytes_4B[::-1])[0]
        if nBytes <0:
            return 1
        mesData = conn.recv(nBytes)
        #Format data, and fill buffer
        mesEEG = mesDataFormat(mesData, mesTags)
        newRows = mesEEG.shape[0]
        outputBuffer = np.concatenate((outputBuffer[newRows:,:], mesEEG))
        if outputBuffer[0,0] != 0:
            break
    return outputBuffer



#you cant normalize in-place so this is a helper function
def myNormalize(myVec):
	myVec.normalize()
	return myVec
 
def getMeshGrid((nx, ny)):
    "Returns a meshgrid of size (nx, ny)"
    x = np.arange(nx) #np.linspace(0, 1, nx)
    y = np.arange(ny) #np.linspace(0, 1, ny)
    xv, yv = np.meshgrid(x, y)
    return xv, yv
    
def makeSurfVertexArray():
    """Helper function to create and fill a GeomVertexArray with the given data"""
    pass




def randSpectrogram(t):
    "Generates a random spectrogram"
    
    # Generate a random signal: sin + Offset + noise
    Fs = 256
    win = 1 # seconds
    freq = 10 # Hertz
    offset = 1
    x = np.linspace(t, t+1, num=Fs*win)
    y = np.sin(2*np.pi*freq*x) + np.sin(2*np.pi*2.5*freq*x) + np.sin(2*np.pi*10.5*freq*x) + np.sin(2*np.pi*3.7*freq*x) + np.sin(2*np.pi*2.2*freq*x) + np.sin(2*np.pi*7.3*freq*x) + offset + np.random.random_sample(size=x.shape)
    
    # Compute the spectrogram
    NFFT = Fs/8     # the length of the windowing segments
#    Pxx, freqs, bins, im = plt.specgram(y, NFFT=NFFT, Fs=Fs, noverlap=127)
    
#    plt.figure(figsize=(12,8))
#    plt.subplot(211)
#    plt.plot(x, y)
#    ax1 = plt.subplot(212)
    Pxx, freqs, bins, im = plt.specgram(y, NFFT=NFFT, Fs=Fs, noverlap=NFFT-1)
#    ax1.set_ylim((0,127))
#    plt.show()
    
    return Pxx# , freqs
    

def makeSurface(rand_array, surface=None, scale=15):
    """Helper function to make a surface of random points"""
    
    format=GeomVertexFormat.getV3n3cpt2()
    vdata=GeomVertexData('surface', format, Geom.UHDynamic)
    
    vertex=GeomVertexWriter(vdata, 'vertex')
    normal=GeomVertexWriter(vdata, 'normal')
#    color=GeomVertexWriter(vdata, 'color')
#    texcoord=GeomVertexWriter(vdata, 'texcoord')
    
    # Random array
    nb_vertices = rand_array.shape[0] * rand_array.shape[1]
    nb_vertices_per_row = rand_array.shape[1]
    nb_vertices_per_col = rand_array.shape[0]
    #nb_triangles = (rand_array.shape[0]-1) * (rand_array.shape[1]-1) 
    
    # Create a coordinate grid
    xv, yv = getMeshGrid(rand_array.shape)
    xv = xv.T*scale
    yv = yv.T*scale

    # Create each vertex one by one
    for x_ind in range(rand_array.shape[0]):
        for y_ind in range(rand_array.shape[1]):
            x0 = xv[x_ind, y_ind]
            y0 = yv[x_ind, y_ind]
            z0 = rand_array[x_ind, y_ind]
            vertex.addData3f(x0, y0, z0)
            
            # Get two vectors linked to this vertex
            if (x_ind+1)%nb_vertices_per_col == 0 : # In the case where we are at the last voxel of a column
                if (y_ind+1)%nb_vertices_per_row == 0 : # In the case where we are at the last voxel of a row
                    x1 = xv[x_ind-1, y_ind]
                    y1 = yv[x_ind-1, y_ind]
                    z1 = rand_array[x_ind-1, y_ind]
                    
                    x2 = xv[x_ind, y_ind-1]
                    y2 = yv[x_ind, y_ind-1]
                    z2 = rand_array[x_ind, y_ind-1]
                else:
                    x1 = xv[x_ind, y_ind+1]
                    y1 = yv[x_ind, y_ind+1]
                    z1 = rand_array[x_ind, y_ind+1]
                    
                    x2 = xv[x_ind-1, y_ind+1]
                    y2 = yv[x_ind-1, y_ind+1]
                    z2 = rand_array[x_ind-1, y_ind+1]
            else:
                if (y_ind+1)%nb_vertices_per_row == 0 : # In the case where we are at the last voxel of a row
                    x1 = xv[x_ind+1, y_ind-1]
                    y1 = yv[x_ind+1, y_ind-1]
                    z1 = rand_array[x_ind+1, y_ind-1]
                    
                    x2 = xv[x_ind+1, y_ind]
                    y2 = yv[x_ind+1, y_ind]
                    z2 = rand_array[x_ind+1, y_ind]
                else:
                    x1 = xv[x_ind+1, y_ind]
                    y1 = yv[x_ind+1, y_ind]
                    z1 = rand_array[x_ind+1, y_ind]
                    
                    x2 = xv[x_ind, y_ind+1]
                    y2 = yv[x_ind, y_ind+1]
                    z2 = rand_array[x_ind, y_ind+1]
            
            x3, y3, z3 = np.cross([x1,y1,z1], [x2,y2,z2])

            normal.addData3f(myNormalize(Vec3(x3, y3, z3)))
            
            #print x0, y0, z0
    
    # Create the Geom for the surface
    if surface is None:
        surface = Geom(vdata)
    
        # Create each triangle one by one
        for i in range(nb_vertices - nb_vertices_per_row - 1 ): #range(10): # 
            if (i+1)%nb_vertices_per_row != 0 :        
                tri1 = GeomTriangles(Geom.UHDynamic)
                vertex1 = i
                vertex2 = i + 1
                vertex3 = i + nb_vertices_per_row
                tri1.addVertex(vertex1)
                tri1.addVertex(vertex2)
                tri1.addVertex(vertex3)
                tri1.closePrimitive()
                surface.addPrimitive(tri1)
            
                tri2 = GeomTriangles(Geom.UHDynamic)
                vertex4 = i + 1
                vertex5 = i + 1 + nb_vertices_per_row
                vertex6 = i + nb_vertices_per_row
                tri2.addVertex(vertex4)
                tri2.addVertex(vertex5)
                tri2.addVertex(vertex6)
                tri2.closePrimitive()
                surface.addPrimitive(tri2)
                
                
            
            print(vertex1, vertex2, vertex3)
            print(vertex4, vertex5, vertex6)
            
    else:
        # Update the data of the surface Geom
        surface.setVertexData(vdata)
 
    return surface
    

class MyTapper(DirectObject):
    def __init__(self, arrayIn):
        
        self.base = base
        self.base.setBackgroundColor(0.05,0.05,0.05)        
        
        self.base.disableMouse()
        #self.base.useDrive()
        
        self.updatePeriod = 0.5 # seconds
        
        self.keyMap = {"left":0, "right":0, "forward":0, "up":0, "down":0, "backward":0, "cam-left":0, "cam-right":0}
        #self.accept("1", self.toggleText)
        #self.accept("2", self.toggleLightsSide)
        #self.accept("3", self.toggleLightsUp)   
        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])     
        self.accept("arrow_down", self.setKey, ["backward",1]) 
        self.accept("space", self.setKey, ["up",1])
        self.accept("b", self.setKey, ["down",1])# Initialize the TCP/IP connection #######################
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-right",1])
        
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("arrow_down-up", self.setKey, ["backward",0]) 
        self.accept("space-up", self.setKey, ["up",0])
        self.accept("b-up", self.setKey, ["down",0])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-right",0])

        self.LightsOn=True
        self.LightsOn1=True
        slight = Spotlight('slight')# Initialize the TCP/IP connection #######################
        slight.setColor(Vec4(1, 0.8, 0.8, 1))
        lens = PerspectiveLens()
        slight.setLens(lens)
        self.slnp = render.attachNewNode(slight)
        self.slnp1= render.attachNewNode(slight)
        
        
        self.HRtext = OnscreenText(text = 'HR', style=1, fg=(1,1,1,1), pos = (1, -0.95), scale = 0.07)
        self.arrayIn = arrayIn
        
        
        # Create the surface
        self.scale = 30
        #time.sleep(0.1)
        self.surf = makeSurface(self.arrayIn, None)
        print('Surface successfully created.')
        snode = GeomNode('surface')
        snode.addGeom(self.surf)
        
        # It's called "cube" just so I don't have to rename everythin below
        self.cube = render.attachNewNode(snode)
        self.cube.setTwoSided(True)
                      
        # Lighting
        # Create Ambient Lightpanda3d show wire
        self.ambientLight = AmbientLight('ambientLight')
        self.ambientLight.setColor(Vec4(0.1, 0.1, 0.1, 1))
        ambientLightNP = render.attachNewNode(self.ambientLight)
        render.setLight(ambientLightNP)
         
        # Directional light 01
        directionalLight = DirectionalLight('directionalLight')
        #directionalLight.setColor(Vec4(0.1, 0.1, 0.1, 1)) 
        directionalLight.setColor(Vec4(0.8, 0.1, 0.1, 0.5))
        directionalLightNP = render.attachNewNode(directionalLight)
        # This light is facing backwards, towards the camera.
        directionalLightNP.setHpr(180, -20, 0)
        render.setLight(directionalLightNP)
         
        # Directional light 02
        directionalLight = DirectionalLight('directionalLight')
        #directionalLight.setColor(Vec4(0.6, 0.6, 0.6, 1)) 
        directionalLight.setColor(Vec4(0.1, 0.1, 0.8, 1))
        directionalLightNP = render.attachNewNode(directionalLight)
        # This light is facing forwards, away from the camera.
        directionalLightNP.setHpr(0, -20, 0)
        render.setLight(directionalLightNP)  
        
        #taskMgr.add(self.change_terrain,"moveTask")
        #self.cube.setRenderModeWireframe()
        
        # Health bar
        # Create a frame
        frame = DirectFrame(text = "main", scale = 0.001)
        # Add button
        
        self.oldTaskTime = 0.0
        taskMgr.add(self.updateSurface, name="updateSurface")
        taskMgr.add(self.move, name="moveCamera")
        
        
    def step(self):
        #print('STEP')
        taskMgr.step()
        
    
    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value    
    
    def updateSurface(self, task): # Also, update the bar
        diff = task.time - self.oldTaskTime
        if diff > self.updatePeriod:
            makeSurface(self.arrayIn, self.surf, scale=self.scale)
            
            hrInValue = 60
            lightScale = (hrInValue - 50.)/(110.-50.)
            #print('Light scale: %f'%lightScale)
            #self.ambientLight.setColor(Vec4(lightScale, lightScale, lightScale, 1))
            self.base.setBackgroundColor(lightScale,lightScale,lightScale)
            
            self.oldTaskTime = task.time
            
        return Task.cont            
        
    
    
    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        # If a move-key is pressed, move in the specified direction.
        #print(base.camera.getPos())

        dd = 5
        
        if (self.keyMap["left"]!=0):
            base.camera.setPos(base.camera.getPos() - (dd,0,0))
        if (self.keyMap["right"]!=0):
            base.camera.setPos(base.camera.getPos() + (dd,0,0))
        if (self.keyMap["forward"]!=0):
            base.camera.setPos(base.camera.getPos() + (0,dd,0))
        if (self.keyMap["backward"]!=0):
            base.camera.setPos(base.camera.getPos() - (0,dd,0))
        if (self.keyMap["up"]!=0):
            base.camera.setPos(base.camera.getPos() + (0,0,dd))
            #self.scale += 1
            #self.incBar(0.1)
        if (self.keyMap["down"]!=0):
            base.camera.setPos(base.camera.getPos() - (0,0,dd))
            #self.scale -= 1
            #self.incBar(-0.1)
            
            
        if (self.keyMap["cam-left"]!=0):
            #base.camera.setX(base.camera, -20 * globalClock.getDt())
            base.camera.setH(base.camera.getH() + dd)
        if (self.keyMap["cam-right"]!=0):
            base.camera.setH(base.camera.getH() -dd)
            
        return task.cont
        
			
			

#t=MyTapper()
#
#run()

#t.conn.close()





