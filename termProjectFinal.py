from cmu_112_graphics import *
from tkinter import*
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import cv2
import numpy as np
# import random
import os
import pickle
import math
import shutil
from sklearn.cluster import KMeans

#This file contains all modes of the app
class SplashScreenMode(Mode):

    def drawBackground(mode, canvas):
        image = Image.open('combined.jpg')
        image = image.resize((mode.width, mode.height))
        image = ImageTk.PhotoImage(image)
        canvas.create_image(0,0, anchor=NW, image=image)
    
    def drawHelpButton(mode, canvas):
        font = 'Arial 26'
        canvas.create_rectangle(3*mode.width//8, mode.height/2+150, 5*mode.width//8, mode.height/2+200, fill='#B57EDC')
        canvas.create_text(mode.width/2, mode.height/2+175, text='Instructions', fill='white',font=font)

    def redrawAll(mode, canvas):
        mode.drawBackground(canvas)
        mode.drawHelpButton(canvas)
        font = 'Arial 60'
        canvas.create_text(mode.width/2, mode.height/2-100, text='FILTERLAB', fill='black', font=font)
        font = 'Arial 26'
        canvas.create_text(mode.width/2, mode.height/2+100, text='Press any key to begin editing!', fill='white',font=font)

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.editMode)

    def mousePressed(mode, event):
        if 3*mode.width//8< event.x <5*mode.width//8 and (mode.height/2+150)<event.y<(mode.height/2+200):
            mode.app.setActiveMode(mode.app.helpMode)
class HelpMode(Mode):
    def appStarted(mode):
        pass
    
    def drawInstructions(mode, canvas):
        font = 'Times 28 bold'
        canvas.create_text(mode.width//2, mode.height/9, text = 'FILTERLAB Instructions', font = font, anchor = N)
        font = 'Times 24'
        canvas.create_text(mode.width//8, 2*mode.height/9, text = '1. Upload an image using the Upload Button', font = font, anchor = W)
        canvas.create_text(mode.width//8, 3*mode.height/9, text = '2. Add desired effect to image by pressing one of the buttons on the left', font = font, anchor = W)
        canvas.create_text(mode.width//8, 4*mode.height/9, text = '3. Adjust effect using the toolbar (if applicable) or press the button again\nto remove the effect currently being applied', font = font, anchor = W)
        canvas.create_text(mode.width//8, 5*mode.height/9, text = "4. Save the effect you've created using the 'Save Filter' button and apply it to\nother photos using the 'Apply Custom Filter' button! You can save multiple effects!", font = font, anchor = W)
        canvas.create_text(mode.width//8, 6*mode.height/9, text = "5. Once you've finished editing, press 'Save As' to save the enhanced image\nto your computer!", font = font, anchor = W)
        canvas.create_text(mode.width//8, 7*mode.height/9, text = "6. Continue editing or import a new photo to edit!", font = font, anchor = W)
        canvas.create_text(mode.width//2, 8*mode.height/9, text = "\tPress any key to go to editing mode\nNote: * features take a bit longer, so please be patient!", font = font, anchor = N)
    
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0,0,mode.width,mode.height, fill='#FADADD')
        mode.drawInstructions(canvas)

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.editMode)

class VideoHelpMode(Mode):
    def appStarted(mode):
        pass
    
    def drawInstructions(mode, canvas):
        font = 'Times 28 bold'
        canvas.create_text(mode.width//2, mode.height/9, text = 'Welcome to Video Mode!', font = font, anchor = N)
        font = 'Times 24'
        canvas.create_text(mode.width//8, 2*mode.height/9, text = "1. Upload a video from your computer or try the effects on your camera output!\n(Press 'Camera Mode' at any time to see the camera output)", font = font, anchor = W)
        canvas.create_text(mode.width//8, 3*mode.height/9, text = '2. Add desired effect to video by pressing one of the buttons on the left', font = font, anchor = W)
        canvas.create_text(mode.width//8, 4*mode.height/9, text = '3. Adjust effect using the toolbar (if applicable), press the button again\nto remove the effect currently being applied', font = font, anchor = W)
        canvas.create_text(mode.width//8, 5*mode.height/9, text = "4. Save the effect you've created using the 'Save Filter' button and apply it to\nother photos using the 'Apply Custom Filter' button! You can save multiple effects and\napply effects from previous uses!", font = font, anchor = W)
        canvas.create_text(mode.width//8, 6*mode.height/9, text = "5. Press start/stop recording to record the clips you want! You can change the\napplied effects while recording. Press 'Save As' to save to your computer!\nAnd take snapshots by pressing 'Capture Frame'", font = font, anchor = W)
        canvas.create_text(mode.width//8, 7*mode.height/9, text = "Please note that some effects may slow your video down a bit, or take a bit\nlonger to apply. Not all photo filters are available for videos.", font = font, anchor = W)
        canvas.create_text(mode.width//2, 8*mode.height/9, text = "Press any key to begin editing!", font = font, anchor = N)
    
    def redrawAll(mode, canvas):
        canvas.create_rectangle(0,0,mode.width,mode.height, fill='#CCFFFF')
        mode.drawInstructions(canvas)

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.videoMode)

# This mode contains all video mode features
class VideoMode(Mode):
    def appStarted(mode, fileName = 0):
        mode.fileName = fileName
        mode.effectsApplied = dict()
        mode.video = cv2.VideoCapture(mode.fileName)
        mode.ret, mode.frame = mode.video.read()
        mode.app.timerDelay=10
        mode.currentEffect=None
        width=int(mode.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height=int(mode.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        mode.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        mode.out=cv2.VideoWriter('output.mp4', mode.fourcc, 20, (width, height))
        if (os.path.isfile('Custom Filter 1') and os.path.isfile("Number of Custom Filters")):
            file = open(f'Number of Custom Filters', 'rb')
            mode.numCustomFilters= pickle.load(file)
            file.close()
        else:
            mode.numCustomFilters = 0
        mode.buttonWidth = 75
        mode.buttonHeight = 48

        mode.filterButtons =['Blur', 'Vignette', 'Sharpen', 'Cartoonize',
                        'Invert', 'Edges']
        mode.adjustmentButtons=['Saturate', 'Contrast', 'Brightness', '   Auto\nEnhance']
        mode.optionButtons=['Upload\n Video', 'Save As', 'Save\nFilter', '  Apply\nCustom\n  Filter', ' Remove\nCustom\n   Filter', '  Help\nScreen', '     Start\nRecording', '     Stop\nRecording']
        mode.buttonShadowColor = 'black'
        mode.buttonColor = '#93c572'
        mode.buttonDistance=5
        mode.customFilter = None
        mode.frameCount = 0

    def videoFinished(mode):
        return (not mode.ret)

    def sharpen(mode, param):
        image = mode.frame
        intensity = param/10
        image = cv2.detailEnhance(image, sigma_s=intensity, sigma_r=0.15)
        return image

    def updateValue(mode, event):
        image = mode.frame
        mode.effectParameter = mode.slider.get()
        mode.effectsApplied[mode.currentEffect]=mode.effectParameter
        
        if (mode.currentEffect=='Saturate'):
            image = mode.saturate(mode.effectParameter)

        elif (mode.currentEffect=='Brightness'):
            image = mode.brightness(mode.effectParameter)
        
        elif (mode.currentEffect=='Blur'):
            image = mode.blur(mode.effectParameter)

        elif (mode.currentEffect=='Sharpen'):
            image = mode.sharpen(mode.effectParameter)
        
        elif (mode.currentEffect=='Edges'):
            image = mode.edges(mode.effectParameter)

        elif (mode.currentEffect == 'Contrast'):
            image = mode.contrast(mode.effectParameter)

        elif (mode.currentEffect =='Color Reduction'):
            image = mode.colorReduction(mode.effectParameter)

        elif (mode.currentEffect=='Cluster Fill'):
            image = mode.clusterFill(mode.effectParameter)


    def getSliderValue(mode, start):
        master = Tk()
        mode.slider = Scale(master, from_=0, to=100, orient=HORIZONTAL)
        mode.slider.set(start)
        mode.slider.bind("<ButtonRelease-1>", mode.updateValue)
        mode.slider.pack()

    def saturate(mode, param):
        image = mode.frame
        hsvImg = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        saturation= param/75+0.1
        updatedImg = cv2.copyMakeBorder(hsvImg,0,0,0,0, cv2.BORDER_REPLICATE)
        updatedImg[...,1] = hsvImg[...,1]*saturation 
        image=cv2.cvtColor(updatedImg,cv2.COLOR_HSV2BGR)
        return image

    def contrast(mode, param):
        image = mode.frame
        contrast = param/50
        image = image*contrast
        return image

    def brightness(mode, param):
        image = mode.frame
        brightness = param-50
        image=cv2.convertScaleAbs(image, -1, 1, brightness)
        return image

##from http://www.askaswiss.com/2016/01/how-to-create-cartoon-effect-opencv-python.html
    def cartoonize(mode):
        numDownSamples = 2
        numBilateralFilters = 50 
        image = mode.frame
        imageColored = image
        for i in range(numDownSamples):
            imageColored = cv2.pyrDown(imageColored)
        for j in range(numBilateralFilters):
            imageColored = cv2.bilateralFilter(imageColored, 9, 9, 7)
        for k in range(numDownSamples):
            imageColored = cv2.pyrUp(imageColored)
        gray = cv2.cvtColor(imageColored, cv2.COLOR_RGB2GRAY)
        blur = cv2.medianBlur(gray, 3)
        edges = cv2.adaptiveThreshold(blur, 255,
                                         cv2.ADAPTIVE_THRESH_MEAN_C,
                                         cv2.THRESH_BINARY, 9, 2)
        (width,height,channels) = imageColored.shape
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        image =  cv2.bitwise_and(imageColored, edges)
        return image

    def edges(mode, param):
        edges = 100-param 
        image = cv2.Canny(mode.frame, edges, edges+100)
        return image

    def invertColors(mode):
        image = cv2.bitwise_not(mode.frame)
        return image

    def timerFired(mode):
        mode.ret, mode.frame = mode.video.read()
        if (mode.ret):
            mode.frame = cv2.cvtColor(mode.frame, cv2.COLOR_BGR2RGB)
            if ('Saturate' in mode.effectsApplied):
                param = mode.effectsApplied['Saturate']
                mode.frame = mode.saturate(param)
            if ('Brightness' in mode.effectsApplied):
                param = mode.effectsApplied['Brightness']
                mode.frame = mode.brightness(param)
            if ('Contrast' in mode.effectsApplied):
                param = mode.effectsApplied['Contrast']
                mode.frame = mode.contrast(param)
            if ('Cartoon' in mode.effectsApplied):
                mode.frame = mode.cartoonize()
            if ('Vignette' in mode.effectsApplied):
                param = mode.effectsApplied['Vignette']
                mode.frame = mode.vignette()
            if ('Edges' in mode.effectsApplied):
                param = mode.effectsApplied['Edges']
                mode.frame = mode.edges(param)
            if ('Invert' in mode.effectsApplied):
                mode.frame = mode.invertColors()
            if ('Auto Enhance' in mode.effectsApplied):
                mode.frame = mode.autoEnhance()
            if ('Sharpen' in mode.effectsApplied):
                param = mode.effectsApplied['Sharpen']
                mode.frame = mode.sharpen(param)
            if ('Blur' in mode.effectsApplied):
                param = mode.effectsApplied['Blur']
                mode.frame = mode.blur(param)
            saveFrame = cv2.cvtColor(mode.frame, cv2.COLOR_RGB2BGR)
            mode.out.write(saveFrame) 
        else:
            mode.video = cv2.VideoCapture(mode.fileName)
    
    def importVideo(mode):
        mode.effectsApplied = dict()
        mode.currentEffect = None
        path=filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("mp4 files","*.mp4"),("all files","*.*")))
        if path==None or path == '':
            path = 0
        mode.fileName = mode.originalFileName = path
        mode.video = cv2.VideoCapture(mode.fileName)
        ret, mode.frame = mode.video.read()

    def blur(mode, param):
        param//=10
        if param%2==0:
            param+=1
        image = mode.frame
        image = cv2.GaussianBlur(image, (param, param), 7)
        return image

    def autoEnhance(mode):
        image = mode.frame
        image = cv2.filter2D(image, -1, 1.1)
        return image

#from https://subscription.packtpub.com/book/application_development/9781785283932/2/ch02lvl1sec25/creating-a-vignette-filter
    def vignette(mode):
        image = mode.frame
        image = cv2.resize(image, (0,0), fx=0.3, fy=0.3)
        rows, cols = image.shape[:2]
        kernelX = cv2.getGaussianKernel(cols,200)
        kernelY = cv2.getGaussianKernel(rows,200)
        kernel = kernelY * kernelX.T
        mask = 255 * kernel / np.linalg.norm(kernel)
        for i in range(3):
            image[:,:,i] = image[:,:,i] * mask
        image = cv2.resize(image, (0,0), fx=3.333, fy=3.333)
        return image


    def saveVideo(mode):
        path = filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("mp4 files","*.mp4"),("all files","*.*")))
        if not path:
            return
        mode.out.release()
        shutil.move('output.mp4', path)

    def removeCustomFilter(mode):
        # if mode.customFilter==None:
        #     return
        mode.effectsApplied=dict()
        if (mode.fileName == 0):
            mode.video= cv2.VideoCapture(0)
        else:
            mode.video = cv2.VideoCapture(mode.originalFileName)
        mode.ret, mode.frame = mode.video.read()

    
    def saveFilter(mode):
        if None in mode.effectsApplied:
            mode.effectsApplied.pop(None)
        data = mode.effectsApplied
        file = open(f'Custom Filter {mode.numCustomFilters}', 'wb')
        pickle.dump(data, file)
        file.close()

        file = open(f'Number of Custom Filters', 'wb')
        pickle.dump(mode.numCustomFilters, file)
        file.close()

    def loadFilter(mode):
        # image = mode.frame
        filters = []
        filtersString = ''
        for i in range(1, mode.numCustomFilters+1):
            file = open(f'Custom Filter {i}', 'rb')
            filters.append(pickle.load(file))
            file.close()
        for j in range(len(filters)):
            filtersString+= f'{j+1}. {filters[j]}\n'
        ROOT = Tk()
        ROOT.withdraw() 
        inputVar = simpledialog.askstring(title="Choose Custom Filter",
                                  prompt=f"Enter only the number of the filter you'd like to apply: \n {filtersString}")
        if (inputVar == None or not inputVar.isdigit()):
            return
        filterIndex = int(inputVar)-1
        desiredFilter = filters[filterIndex]
        mode.effectsApplied.update(desiredFilter)

    def captureFrame(mode):
        img = mode.frame
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(f'Frame {mode.frameCount}.jpg', img)

    def startRecording(mode):
        width=int(mode.video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height=int(mode.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        mode.out=cv2.VideoWriter('output.mp4', mode.fourcc, 20, (width, height))

    def stopRecording(mode):
        if (mode.out==None):
            return
        mode.out.release()
        
    def keyPressed(mode, event):
        if event.key=='h':
            mode.app.setActiveMode(mode.app.videoHelpMode)

    def drawButtons(mode, canvas):
        startX, startY = mode.buttonDistance, mode.buttonHeight
        for k in range(len(mode.adjustmentButtons)):
            textX = startX + mode.buttonWidth//2
            textY = startY + mode.buttonHeight//2
            label=mode.adjustmentButtons[k]
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth+mode.buttonDistance, 
                startY+mode.buttonHeight+mode.buttonDistance, fill = mode.buttonShadowColor)
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth, startY+mode.buttonHeight, fill = mode.buttonColor)
            canvas.create_text(textX, textY, text=label, fill='black')
            startX+=mode.buttonWidth+mode.buttonDistance
            if k%2==1:
                startY +=mode.buttonHeight+mode.buttonDistance
                startX = mode.buttonDistance

        startY+=mode.buttonHeight+mode.buttonDistance
        startX=mode.buttonDistance

        for j in range(len(mode.filterButtons)):
            textX = startX + mode.buttonWidth//2
            textY = startY + mode.buttonHeight//2
            label=mode.filterButtons[j]
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth+mode.buttonDistance, 
                startY+mode.buttonHeight+mode.buttonDistance, fill = mode.buttonShadowColor)
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth, startY+mode.buttonHeight, fill = mode.buttonColor)
            canvas.create_text(textX, textY, text=label, fill='black')
            startX+=mode.buttonWidth+mode.buttonDistance
            if j%2==1:
                startY +=mode.buttonHeight+mode.buttonDistance
                startX = mode.buttonDistance
        
        startY+=mode.buttonHeight+mode.buttonDistance
        startX=mode.buttonDistance

        for i in range(len(mode.optionButtons)):
            textX = startX + mode.buttonWidth//2
            textY = startY + mode.buttonHeight//2
            label=mode.optionButtons[i]
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth+mode.buttonDistance, 
                startY+mode.buttonHeight+mode.buttonDistance, fill = mode.buttonShadowColor)
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth, startY+mode.buttonHeight, fill = mode.buttonColor)
            canvas.create_text(textX, textY, text=label, fill='black')
            startX+=mode.buttonWidth+mode.buttonDistance
            if i%2==1:
                startY +=mode.buttonHeight+mode.buttonDistance
                startX= mode.buttonDistance

        textX = startX + mode.buttonWidth
        textY = startY + mode.buttonHeight//2
        canvas.create_rectangle(startX, startY, startX+2*mode.buttonWidth+mode.buttonDistance, startY+mode.buttonHeight, fill = mode.buttonColor)
        canvas.create_text(textX, textY, text='Picture\n Mode', fill='black')

        startY +=mode.buttonHeight+mode.buttonDistance
        startX= mode.buttonDistance
        textX = startX + mode.buttonWidth//2
        textY = startY + mode.buttonHeight//2
        canvas.create_rectangle(startX, startY, startX+mode.buttonWidth, startY+mode.buttonHeight, fill = mode.buttonColor)
        canvas.create_text(textX, textY, text='Camera\n Mode', fill='black')
        startX+=mode.buttonWidth+mode.buttonDistance
        textX = startX + mode.buttonWidth//2 + mode.buttonDistance
        canvas.create_rectangle(startX, startY, startX+mode.buttonWidth, startY+mode.buttonHeight, fill = mode.buttonColor)
        canvas.create_text(textX, textY, text='Capture\n Frame', fill='black')
        startY +=mode.buttonHeight+mode.buttonDistance
        startX= mode.buttonDistance
        textX = startX + mode.buttonWidth
        textY = startY + mode.buttonHeight//2 
        canvas.create_rectangle(startX, startY, startX+2*mode.buttonWidth+mode.buttonDistance, startY+mode.buttonHeight, fill = mode.buttonColor)
        canvas.create_text(textX, textY, text='Restart', fill='black')
        
    def drawBackground(mode, canvas):
        canvas.create_rectangle(0,0, mode.width, mode.height, fill='grey')
        canvas.create_rectangle(0,0, 2*mode.buttonWidth+3*mode.buttonDistance, mode.height, fill='black')

    def drawLabels(mode, canvas):
        font = 'Arial 23 bold'
        startX=mode.buttonWidth+2*mode.buttonDistance
        startY = mode.buttonHeight//2
        canvas.create_text(startX, startY, text="Adjusments", fill='white', font = font)
        startY+=3*mode.buttonHeight+2*mode.buttonDistance
        canvas.create_text(startX, startY, text="Filters", fill='white', font = font)
        startY+=4*mode.buttonHeight+4*mode.buttonDistance
        canvas.create_text(startX, startY, text="Options", fill='white', font = font)

    def mousePressed(mode, event):
        if mode.buttonWidth+mode.buttonDistance<event.x<2*mode.buttonWidth+mode.buttonDistance and 10*mode.buttonHeight+9*mode.buttonDistance<event.y<11*mode.buttonHeight+9*mode.buttonDistance:
            mode.app.setActiveMode(mode.app.videoHelpMode)
        if (0<event.x<2*mode.buttonWidth+mode.buttonDistance and 12*mode.buttonHeight+11*mode.buttonDistance<event.y<13*mode.buttonHeight+11*mode.buttonDistance):
            mode.out.release()
            mode.video.release()
            mode.app.setActiveMode(mode.app.editMode)
        if (0<event.x<2*mode.buttonWidth+mode.buttonDistance and 14*mode.buttonHeight+13*mode.buttonDistance<event.y<15*mode.buttonHeight+13*mode.buttonDistance):
            if (mode.fileName == 0):
                mode.appStarted()
            else:
                path = mode.fileName
                mode.appStarted(mode.fileName)
        #first column of buttons
        if 0<event.x<mode.buttonWidth:
            if 13*mode.buttonHeight+12*mode.buttonDistance<event.y<14*mode.buttonHeight+12*mode.buttonDistance:
                mode.fileName = 0
                mode.video = cv2.VideoCapture(mode.fileName)
            if 8*mode.buttonHeight+7*mode.buttonDistance<event.y<9*mode.buttonHeight+7*mode.buttonDistance:
                mode.importVideo()
            if (mode.fileName!=None):
                if mode.buttonHeight<event.y<2*mode.buttonHeight:
                    if mode.currentEffect=='Saturate':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Saturate')
                    else:
                        mode.currentEffect='Saturate'
                        mode.getSliderValue(50)
                elif 2*mode.buttonHeight+mode.buttonDistance<event.y<3*mode.buttonHeight+mode.buttonDistance:
                    if mode.currentEffect=='Brightness':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Brightness')
                    else:
                        mode.currentEffect='Brightness'
                        mode.getSliderValue(50)
                elif 4*mode.buttonHeight+3*mode.buttonDistance<event.y<5*mode.buttonHeight+3*mode.buttonDistance:
                    if mode.currentEffect=='Blur':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Blur')
                    else:
                        mode.currentEffect='Blur'
                        mode.getSliderValue(0)
                elif 5*mode.buttonHeight+4*mode.buttonDistance<event.y<6*mode.buttonHeight+4*mode.buttonDistance:
                    if mode.currentEffect=='Sharpen':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Sharpen')
                    else:
                        mode.currentEffect='Sharpen'
                        mode.getSliderValue(0)
                elif 6*mode.buttonHeight+5*mode.buttonDistance<event.y<7*mode.buttonHeight+5*mode.buttonDistance:
                    if (mode.currentEffect=='Invert'):
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Invert')
                    else:
                        mode.currentEffect='Invert'
                    mode.invertColors()
                    mode.effectsApplied[mode.currentEffect]=None
                elif 9*mode.buttonHeight+8*mode.buttonDistance<event.y<10*mode.buttonHeight+8*mode.buttonDistance:
                    mode.numCustomFilters+=1
                    mode.saveFilter()
                elif 10*mode.buttonHeight+9*mode.buttonDistance<event.y<11*mode.buttonHeight+9*mode.buttonDistance:
                    mode.removeCustomFilter()
                elif 11*mode.buttonHeight+10*mode.buttonDistance<event.y<12*mode.buttonHeight+10*mode.buttonDistance:
                    mode.startRecording()
        #second column
        if (mode.buttonWidth+mode.buttonDistance<event.x<2*mode.buttonWidth+mode.buttonDistance):
            if 13*mode.buttonHeight+12*mode.buttonDistance<event.y<14*mode.buttonHeight+12*mode.buttonDistance:
                mode.frameCount+=1
                mode.captureFrame()
            if (mode.fileName!=None):
                if mode.buttonHeight<event.y<2*mode.buttonHeight:
                    if mode.currentEffect=='Contrast':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Contrast')
                    else:
                        mode.currentEffect='Contrast'
                        mode.getSliderValue(50)
                elif 2*mode.buttonHeight+mode.buttonDistance<event.y<3*mode.buttonHeight+mode.buttonDistance:
                    if mode.currentEffect=='Auto Enhance':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Auto Enhance')
                    else:
                        mode.currentEffect='Auto Enhance'
                        mode.effectsApplied[mode.currentEffect]=None
                        mode.autoEnhance()
                elif 4*mode.buttonHeight+3*mode.buttonDistance<event.y<5*mode.buttonHeight+3*mode.buttonDistance:
                    if mode.currentEffect=='Vignette':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Vignette')
                    else:
                        mode.currentEffect='Vignette'
                        mode.effectsApplied[mode.currentEffect]=None
                        mode.vignette()
                elif 5*mode.buttonHeight+4*mode.buttonDistance<event.y<6*mode.buttonHeight+4*mode.buttonDistance:
                    if mode.currentEffect=='Cartoon':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Cartoon')
                    else:
                        mode.currentEffect='Cartoon'
                        mode.effectsApplied[mode.currentEffect]=None
                        mode.cartoonize()
                elif 6*mode.buttonHeight+5*mode.buttonDistance<event.y<7*mode.buttonHeight+5*mode.buttonDistance:
                    if mode.currentEffect=='Edges':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Edges')
                    else:
                        mode.currentEffect='Edges'
                        mode.getSliderValue(0)

                if 8*mode.buttonHeight+7*mode.buttonDistance<event.y<9*mode.buttonHeight+7*mode.buttonDistance:
                    mode.saveVideo()
                elif 9*mode.buttonHeight+8*mode.buttonDistance<event.y<10*mode.buttonHeight+8*mode.buttonDistance:
                    mode.currentEffect='Loading'
                    mode.loadFilter()
                elif 11*mode.buttonHeight+10*mode.buttonDistance<event.y<12*mode.buttonHeight+10*mode.buttonDistance:
                    mode.stopRecording()
    
    def drawVideo(mode, canvas):
        if (mode.ret):
            image = Image.fromarray(mode.frame)
            width, height = image.size
            sideBarWidth = 2*mode.buttonWidth+3*mode.buttonDistance
            if (width>=height):
                ratio = height/width
                newWidth = int(3*mode.width/4-sideBarWidth)
                newHeight = int(newWidth*ratio)
            else:
                ratio = width/height
                newHeight = int(3*mode.height/4)
                newWidth = int(newHeight*ratio)
            image = image.resize((newWidth, newHeight))
            imageTk = ImageTk.PhotoImage(image)
            startPositionX = (mode.width-newWidth)//2 + sideBarWidth//2
            startPositionY = (mode.height-newHeight)//2 
            canvas.create_image(startPositionX,startPositionY, anchor=NW, image=imageTk)
        
    def redrawAll(mode, canvas):
        mode.drawBackground(canvas)
        mode.drawButtons(canvas)
        mode.drawLabels(canvas)
        mode.drawVideo(canvas)

#This mode contains all image mode features
class EffectsMode(Mode):
    def appStarted(mode):
        mode.img = None
        mode.effectsApplied = dict()
        mode.currentEffect=None

        mode.buttonWidth = 75
        mode.buttonHeight = 45

        mode.filterButtons =['Blur*', '   Color\nReduction', 'Sharpen', 'Cartoonize',
                        'Invert', 'Edges', 'Recolor', 'Vignette', 'Cluster\n  Fill*  ', 'Blockify*', 'Pen*', 'Combine*']
        mode.adjustmentButtons=['Saturate', 'Contrast', 'Brightness', '   Auto\nEnhance']
        mode.optionButtons=['Upload\n Image', 'Save As', 'Save\nFilter', '  Apply\nCustom\n  Filter', ' Remove\nCustom\n   Filter', '  Help\nScreen']
        mode.buttonShadowColor = 'black'
        mode.buttonColor = '#AFEEEE'
        mode.buttonDistance=5
        mode.importPressed = False
        mode.fileName = None
        mode.originalFileName = None
        mode.slider=None
        mode.effectParameter = None
        mode.recolorParam = 0
        mode.customFilter = None
        mode.clusters = None
        mode.originalImg = None
        if (os.path.isfile('Custom Filter 1') and os.path.isfile("Number of Custom Filters")):
            file = open(f'Number of Custom Filters', 'rb')
            mode.numCustomFilters= pickle.load(file)
            file.close()
        else:
            mode.numCustomFilters = 0

    #first section: Image Adjustments
    def updateValue(mode, event):
        image = cv2.imread(mode.fileName)
        mode.effectParameter = mode.slider.get()
        mode.effectsApplied[mode.currentEffect]=mode.effectParameter
        
        if (mode.currentEffect=='Saturate'):
            image = mode.saturate(mode.effectParameter)

        elif (mode.currentEffect=='Brightness'):
            image = mode.brightness(mode.effectParameter)
        
        elif (mode.currentEffect=='Blur'):
            image = mode.blur(mode.effectParameter)

        elif (mode.currentEffect=='Sharpen'):
            image = mode.sharpen(mode.effectParameter)
        
        elif (mode.currentEffect=='Edges'):
            image = mode.edges(mode.effectParameter)

        elif (mode.currentEffect == 'Contrast'):
            image = mode.contrast(mode.effectParameter)

        elif (mode.currentEffect =='Color Reduction'):
            image = mode.colorReduction(mode.effectParameter)

        elif (mode.currentEffect=='Cluster Fill'):
            image = mode.clusterFill(mode.effectParameter)

        mode.fileName = str(mode.effectsApplied)+'.jpg'
        cv2.imwrite(mode.fileName, image)
        # mode.img = image

#https://www.python-course.eu/tkinter_sliders.php
    def getSliderValue(mode, start):
        image = cv2.imread(mode.fileName)
        master = Tk()
        mode.slider = Scale(master, from_=0, to=100, orient=HORIZONTAL)
        mode.slider.set(start)
        mode.slider.bind("<ButtonRelease-1>", mode.updateValue)
        mode.slider.pack()

    def saturate(mode, param):
        image = cv2.imread(mode.fileName)
        hsvImg = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
        saturation= param/75+0.1
        updatedImg = cv2.copyMakeBorder(hsvImg,0,0,0,0, cv2.BORDER_REPLICATE)
        updatedImg[...,1] = hsvImg[...,1]*saturation #figure out parameter
        image=cv2.cvtColor(updatedImg,cv2.COLOR_HSV2BGR)
        return image
    
    def contrast(mode, param):
        image = cv2.imread(mode.fileName)
        contrast = param/50
        image = image*contrast
        return image

    def brightness(mode, param):
        image = cv2.imread(mode.fileName)
        brightness = param-50
        image=cv2.convertScaleAbs(image, -1, 1, brightness)
        return image
#converting from PIL to OpenCV from https://stackoverflow.com/questions/14134892/convert-image-from-pil-to-opencv-format
#self-implement for post MVP
    def blockify(mode):
        image = Image.open(mode.fileName)
        image = image.filter(ImageFilter.GaussianBlur())
        pixels = image.load()
        rows, cols = image.size
        pixels = mode.floodFillHelper(image, rows, cols, pixels, pixels[rows//2,cols//2])
        mode.fileName = str(mode.effectsApplied)+'.jpg'
        image = image.convert('RGB') 
        open_cv_image = np.array(image) 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        cv2.imwrite(mode.fileName, open_cv_image)
        return open_cv_image

    def floodFillHelper(mode, image, rows, cols, pixels, currColor):
        for row in range(rows):
            for col in range(1,cols-1):
                newColor = pixels[row,col]
                if (mode.similarColors(currColor, newColor, 50)):
                    pixels[row,col]=currColor
                else: 
                    currColor = newColor
        for col in range(cols):
            for row in range(rows):
                newColor = pixels[row,col]
                if (mode.similarColors(currColor, newColor, 50)):
                    pixels[row,col]=currColor
                else: 
                    currColor = newColor
        return pixels


    def sharpen(mode, param):
        image = cv2.imread(mode.fileName)
        intensity = param/10
        image = cv2.detailEnhance(image, sigma_s=intensity, sigma_r=0.15)
        return image

    def invertColors(mode):
        image = cv2.imread(mode.fileName)
        image= cv2.bitwise_not(image)
        mode.fileName = str(mode.effectsApplied)+'.jpg'
        cv2.imwrite(mode.fileName, image)
        return image

    #algorithm based on https://en.wikipedia.org/wiki/Gaussian_blur#Mathematics
    def gaussianEquation(mode, xDistance, yDistance, sigma):
        eExp = math.exp(- ( xDistance**2 + yDistance**2) / (2*(sigma**2)))
        base = 1/(2*math.pi * sigma**2)
        return base*eExp

    def getMatrixSum(mode, matrix, ints=False):
        rows, cols = len(matrix), len(matrix[0])
        totalSum = 0
        redSum, greenSum, blueSum = 0, 0, 0
        if (isinstance(matrix[0][0], tuple)):
            for row in range(rows):
                for col in range(cols):
                    redSum+=matrix[row][col][0]
                    greenSum+=matrix[row][col][1]
                    blueSum+=matrix[row][col][2]
            if (ints):
                return (int(redSum), int(greenSum), int(blueSum))
            else:
                return (redSum, greenSum, blueSum)
        else:
            for row in range(rows):
                totalSum += sum(matrix[row])
            return totalSum

    def getPixelRowAndCol(mode, matrix, pixelValue):
        rows, cols = len(matrix), len(matrix[0])
        pixelRow, pixelCol = -1, -1
        for row in range(rows):
            if (pixelValue in matrix[row]):
                pixelRow = row
                pixelCol = matrix[row].index(pixelValue)
        return pixelRow, pixelCol

    # from https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#creating2dLists
    def make2dList(mode, rows, cols):
        return [ ([0] * cols) for row in range(rows) ]

    def getWeightedMatrix(mode, sigma):
        weightedMatrix = mode.make2dList(3,3)
        for drow in [-1, 0, +1]:
            for dcol in [-1, 0, +1]:
                xDistance= abs(dcol) 
                yDistance= abs(drow)
                weightedMatrix[drow+1][dcol+1] = mode.gaussianEquation(xDistance, yDistance, sigma)
        matrixSum = mode.getMatrixSum(weightedMatrix)
        for row in range(len(weightedMatrix)):
            for col in range(len(weightedMatrix[0])):  
                weightedMatrix[row][col] /= matrixSum
        return weightedMatrix

    def newPixelMatrix(mode, matrix, pixelValue, sigma, isTuple):
        weightedMatrix = mode.getWeightedMatrix(sigma)
        pixelRow, pixelCol = mode.getPixelRowAndCol(matrix, pixelValue)
        rows, cols = len(weightedMatrix), len(weightedMatrix[0])
        for row in range(rows):
            for col in range(cols):
                drow, dcol = row-1, col-1
                newRow = pixelRow+drow
                newCol = pixelCol+dcol
                if newRow>len(matrix)-1:
                    newRow = len(matrix)-1
                if newCol>len(matrix[0])-1:
                    newCol = len(matrix[0]) -1
                currentPixelValue = matrix[newRow][newCol]
                if (isTuple):
                    currentRed, currentGreen, currentBlue = currentPixelValue
                    weightedVal = weightedMatrix[row][col]
                    weightedMatrix[row][col]=(currentRed*weightedVal, currentGreen*weightedVal, currentBlue*weightedVal)
                else:
                    weightedMatrix[row][col] *= currentPixelValue
        return weightedMatrix

    def getNewPixelValue(mode, matrix, pixelValue, sigma, isTuple=False):
        newPixMatrix = mode.newPixelMatrix(matrix, pixelValue, sigma, isTuple)
        newValue = mode.getMatrixSum(newPixMatrix, True)
        return newValue

    #from https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#printing
    def maxItemLength(mode, a):
        maxLen = 0
        rows = len(a)
        cols = len(a[0])
        for row in range(rows):
            for col in range(cols):
                maxLen = max(maxLen, len(str(a[row][col])))
        return maxLen

    def getPixelValuesRGB(mode, matrix, rgb, sigma):
        red, green, blue= rgb
        newTuple=mode.getNewPixelValue(matrix, rgb, sigma, True)
        return newTuple

    #from https://stackoverflow.com/questions/27371064/converting-a-1d-list-into-a-2d-list-with-a-given-row-length-in-python
    def convertTo2dList(mode, L, rows, cols):
        newList = [L[i:i+rows] for i in range(0, len(L), rows)]
        return newList
    
#converting from PIL to openCv at the end from https://stackoverflow.com/questions/14134892/convert-image-from-pil-to-opencv-format
    def blur(mode, param):
        img = Image.open(mode.fileName)
        originalSize = img.size
        img = img.convert('RGB')
        height, width = img.size
        param= param//5 + 1
        height//=param
        width//=param
        img = img.resize((height, width))
        pixels=img.load()
        rows, cols = img.size
        pixelsList = list(Image.Image.getdata(img))
        pixelsList2d = mode.convertTo2dList(pixelsList, rows, cols)
        for row in range(0, rows, 8):
            for col in range(0, cols, 8):
                color = pixels[row, col]
                if (isinstance(color, tuple)):
                    newPixelValue = mode.getPixelValuesRGB(pixelsList2d, color , 1.5)
                else:
                    newPixelValue = int(mode.getNewPixelValue(pixelsList2d, color , 1.5))
                pixels[row, col] = newPixelValue
        img = img.resize(originalSize)
        mode.fileName = str(mode.effectsApplied)+'.jpg'
        img = img.convert('RGB') 
        open_cv_image = np.array(img) 
        # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        # cv2.imwrite(mode.fileName, open_cv_image)
        return open_cv_image

  
    def similarColors(mode, rgb1, rgb2, x):
        red1, green1, blue1 = rgb1
        red2, green2, blue2 = rgb2
        redDiff, greenDiff, blueDiff = abs(red1-red2), abs(green1-green2), abs(blue1-blue2)
        return redDiff<x and greenDiff<x and blueDiff<x

    def getColorRegions(mode, x, newSize):
        img = Image.open(mode.fileName)
        img = img.resize(newSize)
        rows, cols = img.size
        colors = dict()
        for row in range(rows):
            for col in range(cols):
                added=False
                currColor = img.getpixel((row, col))
                for key in colors:
                    if mode.similarColors(currColor, key, x):
                        colors[key].add((row, col))
                        added=True
                if added==False:
                    if (colors.get(currColor)==None):
                        colors[currColor]=set()
                    colors[currColor].add((row, col))
        return colors

    def fillRegions(mode, x):
        newSize = (500, 300)
        colorRegions = mode.getColorRegions(x, newSize) 
        img = Image.open(mode.fileName)
        img = img.resize(newSize)
        rows, cols = img.size
        for key in colorRegions:
            for pixel in colorRegions[key]:
                row, col = pixel
                img.putpixel((row, col), key)
        return img

    def colorReduction(mode, param):
        if param<20:
            param = 20
        elif param>60:
            param =60
        img = Image.open(mode.fileName)
        size = img.size
        img = mode.fillRegions(param)
        img = img.resize(size)
        mode.fileName = str(mode.effectsApplied)+'.jpg'
        img = img.convert('RGB') 
        open_cv_image = np.array(img) 
        # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        # cv2.imwrite(mode.fileName, open_cv_image)
        return open_cv_image

#from http://www.askaswiss.com/2016/01/how-to-create-cartoon-effect-opencv-python.html
    def cartoonize(mode):
        image = cv2.imread(mode.fileName)
        numDownSamples = 2
        numBilateralFilters = 50 
        imageColored = image
        for i in range(numDownSamples):
            imageColored = cv2.pyrDown(imageColored)
        for j in range(numBilateralFilters):
            imageColored = cv2.bilateralFilter(imageColored, 9, 9, 7)
        for k in range(numDownSamples):
            imageColored = cv2.pyrUp(imageColored)
        gray = cv2.cvtColor(imageColored, cv2.COLOR_RGB2GRAY)
        blur = cv2.medianBlur(gray, 3)
        edges = cv2.adaptiveThreshold(blur, 255,
                                         cv2.ADAPTIVE_THRESH_MEAN_C,
                                         cv2.THRESH_BINARY, 9, 2)
        (width,height,channels) = imageColored.shape
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        image =  cv2.bitwise_and(imageColored, edges)
        mode.fileName = str(mode.effectsApplied)+'.jpg'
        cv2.imwrite(mode.fileName, image)
        return image

    def edges(mode, param):
        image = cv2.imread(mode.fileName)
        edges = 100-param 
        image = cv2.Canny(image, edges, edges+100)
        return image

    def recolor(mode):
        mode.recolorParam+=1
        if (mode.fileName=="{None: None}.jpg"):
            mode.effectsApplied = dict()
            mode.fileName = mode.originalFileName
        image = Image.open(mode.fileName)
        pixels = image.load()
        rows, cols = image.size
        for row in range(rows):
            for col in range(cols):
                red, green, blue = pixels[row, col]
                pixels[row, col]= (green, blue, red)
        mode.fileName = str(mode.effectsApplied)+'.jpg'
        image = image.convert('RGB') 
        cvimage = np.array(image)
        cvimage = cvimage[:, :, ::-1].copy() 
        cv2.imwrite(mode.fileName, cvimage)
        return cvimage 

#from https://subscription.packtpub.com/book/application_development/9781785283932/2/ch02lvl1sec25/creating-a-vignette-filter
    def vignette(mode):
        image = cv2.imread(mode.fileName)
        image = cv2.resize(image, (0,0), fx=0.3, fy=0.3)
        rows, cols = image.shape[:2]
        kernelX = cv2.getGaussianKernel(cols,200)
        kernelY = cv2.getGaussianKernel(rows,200)
        kernel = kernelY * kernelX.T
        mask = 255 * kernel / np.linalg.norm(kernel)
        for i in range(3):
            image[:,:,i] = image[:,:,i] * mask
        image = cv2.resize(image, (0,0), fx=3.333, fy=3.333)
        mode.fileName = str(mode.effectsApplied)+'.jpg'
        cv2.imwrite(mode.fileName, image)
        return image

    def autoEnhance(mode):
        image = cv2.imread(mode.fileName)
        image = cv2.filter2D(image, -1, 1.1)
        mode.fileName = str(mode.effectsApplied)+'.jpg'
        cv2.imwrite(mode.fileName, image)
        return image

# from https://buzzrobot.com/dominant-colors-in-an-image-using-k-means-clustering-3c7af4622036
    def dominantColors(mode, clusters, fileName = None):
        #read image
        if fileName!=None:
            img = cv2.imread(fileName)
        else:
            img = cv2.imread(mode.fileName)  
        #convert to rgb from bgr
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)            
        #reshaping to a list of pixels
        img = img.reshape((img.shape[0] * img.shape[1], 3))   
        #using k-means to cluster pixels
        kmeans = KMeans(n_clusters = clusters)
        kmeans.fit(img)    
        #the cluster centers are our dominant colors.
        colors = kmeans.cluster_centers_      
        #save labels
        labels = kmeans.labels_      
        #returning after converting to integer from float
        return colors.astype(int)

    def totuple(mode, a):
        try:
            return tuple(mode.totuple(i) for i in a)
        except TypeError:
            return a

#self-implemented
    def getClusteredColorKeys(mode, clusters, fileName = None):
        colors = mode.dominantColors(clusters)
        colorKeys=[]
        for color in colors:
            colorKeys.append(mode.totuple(color))
        mode.clusters = colorKeys
        return colorKeys
    
    def getClusteredRegions(mode, clusters, bound=30):
        colorKeys = mode.getClusteredColorKeys(clusters)
        img = Image.open(mode.fileName)
        img = img.resize((500, 300))
        rows, cols = img.size
        colors = dict()
        for color in colorKeys:
            colors[color]=set()
        for row in range(rows):
            for col in range(cols):
                currColor = img.getpixel((row, col))
                for key in colors:
                    if mode.similarColors(currColor, key, bound):
                        colors[key].add((row, col))
        return colors
        
    def clusterFill(mode, param):
        clusters = param//10
        colorRegions = mode.getClusteredRegions(clusters)
        img = Image.open(mode.fileName)
        height, width = img.size
        img = img.resize((500, 300))
        rows, cols = img.size
        for key in colorRegions:
            for pixel in colorRegions[key]:
                row, col = pixel
                img.putpixel((row, col), key)
        img = img.resize((height, width))
        img = img.convert('RGB') 
        cvimage = np.array(img)
        cvimage = cvimage[:, :, ::-1].copy() 
        return cvimage 
    
    def pen(mode):
        image = cv2.imread(mode.fileName)
        image =cv2.GaussianBlur(image, (3,3), 1)
        edges = cv2.Canny(image, 100, 200)
        edges = cv2.bitwise_not(edges)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        contour = cv2.cvtColor(edges, cv2.COLOR_BGR2RGB)
        contour = Image.fromarray(contour)
        contourP = contour.load()
        img = Image.fromarray(image)
        rows, cols = img.size
        pixels = img.load()
        currColor = pixels[rows//2, cols//2]
        contourP = mode.getContourHelper(contourP, pixels, rows, cols, currColor)
        img = contour.convert('RGB') 
        cvimage = np.array(img)
        cvimage = cvimage[:, :, ::-1].copy() 
        mode.fileName = str(mode.effectsApplied)+'.jpg'
        cv2.imwrite(mode.fileName, cvimage)
        return cvimage 

    def getContourHelper(mode, contourP, pixels, rows, cols, currColor):
        for row in range(rows):
            for col in range(cols):
                if (contourP[row, col]==(0,0,0)):
                    currColor = pixels[rows//4, cols//4]
                elif mode.similarColors(currColor, pixels[row, col], 70):
                    contourP[row,col]=currColor
        return contourP
            
    def combine(mode):
        path=filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        if (path==None or path==''):
            return
        colorKeys = mode.getClusteredColorKeys(5, path)
        img = Image.open(mode.fileName)
        currentSize = img.size
        img = img.resize((500, 300))
        rows, cols = img.size
        for row in range(rows):
            for col in range(cols):
                currColor = img.getpixel((row, col))
                for key in colorKeys:
                    if mode.similarColors(currColor, key, 70):
                        img.putpixel((row, col), key)
        img= img.resize((currentSize))
        img = img.convert('RGB') 
        cvimage = np.array(img)
        cvimage = cvimage[:, :, ::-1].copy() 
        mode.fileName = str(mode.effectsApplied)+'.jpg'
        cv2.imwrite(mode.fileName, cvimage)
        return cvimage  

    def checkForImage(mode):
        if (mode.fileName!=None and not os.path.exists(mode.fileName)):
            cv2.imwrite(mode.fileName, mode.originalImg)
    
#third section: options
    def importImage(mode):
        mode.importPressed=True
        mode.recolorParam=0
        mode.effectsApplied = dict()
        mode.currentEffect = None
        path=filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        if (path==None or path==''):
            path = mode.fileName
            mode.fileName = path
        else:
            mode.fileName = mode.originalFileName = path
            mode.originalImg = cv2.imread(mode.fileName)
            mode.removeIntermediates()

    def saveImage(mode):
        path = filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        if not path:
            return 
        image = Image.open(mode.fileName)
        image.save(path, 'JPEG')

    def saveFilter(mode):
        if None in mode.effectsApplied:
            mode.effectsApplied.pop(None)
        data = mode.effectsApplied
        file = open(f'Custom Filter {mode.numCustomFilters}', 'wb')
        pickle.dump(data, file)
        file.close()

        file = open(f'Number of Custom Filters', 'wb')
        pickle.dump(mode.numCustomFilters, file)
        file.close()
        
    def loadFilter(mode):
        image = cv2.imread(mode.fileName)
        filters = []
        filtersString = ''
        for i in range(1, mode.numCustomFilters+1):
            file = open(f'Custom Filter {i}', 'rb')
            filters.append(pickle.load(file))
            file.close()
        for j in range(len(filters)):
            filtersString+= f'{j+1}. {filters[j]}\n'
        ROOT = Tk()
        ROOT.withdraw()
        inputVar = simpledialog.askstring(title="Choose Custom Filter",
                                  prompt=f"Enter only the number of the filter you'd like to apply: \n {filtersString}")
        if (inputVar == None or not inputVar.isdigit()):
            return
        filterIndex = int(inputVar)-1
        desiredFilter = filters[filterIndex]
        mode.customFilter = desiredFilter
        for filter in desiredFilter:
            parameter=desiredFilter.get(filter)
            mode.effectsApplied[filter]=parameter
            #adjustables
            if (filter=='Saturate'):
                image = mode.saturate(parameter)
            if (filter=='Brightness'):
                image = mode.brightness(parameter)
            if (filter=='Blur'):
                image = mode.blur(parameter)
            if (filter=='Edges'):
                image = mode.edges(parameter)
            if (filter=='Contrast'):
                image = mode.contrast(parameter)
            if (filter=='Cartoon'):
                image = mode.cartoonize()
            if (filter=='Auto Enhance'):
                image = mode.autoEnhance()
            if (filter=='Vignette'):
                image = mode.vignette()
            if (filter=='Color Reduction'):
                image = mode.colorReduction(parameter)
            if (filter=='Recolor'):
                image = mode.recolor()
                if (mode.recolorParam==2):
                    image = mode.recolor()
            if (filter=='Sharpen'):
                image = mode.sharpen()
            if (filter=='Cluster Fill'):
                image = mode.clusterFill(parameter)
            if (filter =='Blockify'):
                image = mode.blockify()
            if (filter =='Pen'):
                image = mode.pen()
            mode.fileName = str(mode.effectsApplied)+'.jpg'
            cv2.imwrite(mode.fileName, image)
        if ('Invert' in desiredFilter):
            image = mode.invertColors()
            mode.fileName = str(mode.effectsApplied)+'.jpg'
            cv2.imwrite(mode.fileName, image)
        cv2.imwrite(mode.fileName, image)

    def removeCustomFilter(mode):
        if mode.customFilter==None:
            return
        mode.effectsApplied=dict()
        mode.fileName = mode.originalFileName

    def removeIntermediates(mode):
        for filename in os.listdir():
            if filename.startswith('{') and filename.endswith('.jpg'):
                os.unlink(filename)
                # print(filename)

    def mousePressed(mode, event):
        if mode.buttonWidth+mode.buttonDistance<event.x<2*mode.buttonWidth+mode.buttonDistance and 13*mode.buttonHeight+12*mode.buttonDistance<event.y<14*mode.buttonHeight+12*mode.buttonDistance:
            mode.app.setActiveMode(mode.app.helpMode)
        if (0<event.x<2*mode.buttonWidth+mode.buttonDistance and 14*mode.buttonHeight+13*mode.buttonDistance<event.y<15*mode.buttonHeight+13*mode.buttonDistance):
            mode.removeIntermediates()
            mode.app.setActiveMode(mode.app.videoHelpMode)
        if (0<event.x<2*mode.buttonWidth+mode.buttonDistance and 15*mode.buttonHeight+14*mode.buttonDistance<event.y<16*mode.buttonHeight+14*mode.buttonDistance): #restart
            mode.fileName = mode.originalFileName
            mode.effectsApplied=dict()
        #first column of buttons
        if 0<event.x<mode.buttonWidth:
            if 11*mode.buttonHeight+10*mode.buttonDistance<event.y<12*mode.buttonHeight+10*mode.buttonDistance:
                mode.importImage()
            if (mode.fileName!=None):
                if mode.buttonHeight<event.y<2*mode.buttonHeight:
                    if mode.currentEffect=='Saturate':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Saturate')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Saturate'
                        mode.getSliderValue(50)
                elif 2*mode.buttonHeight+mode.buttonDistance<event.y<3*mode.buttonHeight+mode.buttonDistance:
                    if mode.currentEffect=='Brightness':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Brightness')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Brightness'
                        mode.getSliderValue(50)
                elif 4*mode.buttonHeight+3*mode.buttonDistance<event.y<5*mode.buttonHeight+3*mode.buttonDistance:
                    if mode.currentEffect=='Blur':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Blur')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Blur'
                        mode.getSliderValue(0)
                elif 5*mode.buttonHeight+4*mode.buttonDistance<event.y<6*mode.buttonHeight+4*mode.buttonDistance:
                    if mode.currentEffect=='Sharpen':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Sharpen')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Sharpen'
                        mode.getSliderValue(0)
                elif 6*mode.buttonHeight+5*mode.buttonDistance<event.y<7*mode.buttonHeight+5*mode.buttonDistance:
                    if (mode.currentEffect=='Invert'):
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Invert')
                    else:
                        mode.currentEffect='Invert'
                    mode.invertColors()
                    mode.effectsApplied[mode.currentEffect]=None
                elif 7*mode.buttonHeight+6*mode.buttonDistance<event.y<8*mode.buttonHeight+6*mode.buttonDistance:
                    if mode.currentEffect=='Recolor' and mode.recolorParam == 2:
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Recolor')
                        mode.recolorParam=0
                        if (mode.effectsApplied==dict()):
                            mode.fileName=mode.originalFileName
                        else:
                            mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Recolor'
                        mode.effectsApplied[mode.currentEffect]=(mode.recolorParam+1)
                    mode.recolor()
                elif 8*mode.buttonHeight+7*mode.buttonDistance<event.y<9*mode.buttonHeight+7*mode.buttonDistance:
                    if mode.currentEffect=='Cluster Fill':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Cluster Fill')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Cluster Fill'
                        mode.getSliderValue(0)
                elif 9*mode.buttonHeight+8*mode.buttonDistance<event.y<10*mode.buttonHeight+8*mode.buttonDistance:
                    if mode.currentEffect=='Pen':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Pen')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Pen'
                        mode.effectsApplied[mode.currentEffect]=None
                        mode.pen()
                elif 12*mode.buttonHeight+11*mode.buttonDistance<event.y<13*mode.buttonHeight+11*mode.buttonDistance:
                    mode.numCustomFilters+=1
                    mode.saveFilter()
                elif 13*mode.buttonHeight+12*mode.buttonDistance<event.y<14*mode.buttonHeight+12*mode.buttonDistance:
                    mode.removeCustomFilter()
        #second column
        elif (mode.buttonWidth+mode.buttonDistance<event.x<2*mode.buttonWidth+mode.buttonDistance):
            if (mode.fileName!=None):
                if mode.buttonHeight<event.y<2*mode.buttonHeight:
                    if mode.currentEffect=='Contrast':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Contrast')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Contrast'
                        mode.getSliderValue(50)
                elif 2*mode.buttonHeight+mode.buttonDistance<event.y<3*mode.buttonHeight+mode.buttonDistance:
                    if mode.currentEffect=='Auto Enhance':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Auto Enhance')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Auto Enhance'
                        mode.effectsApplied[mode.currentEffect]=None
                        mode.autoEnhance()
                elif 4*mode.buttonHeight+3*mode.buttonDistance<event.y<5*mode.buttonHeight+3*mode.buttonDistance:
                    if mode.currentEffect=='Color Reduction':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Color Reduction')
                        mode.fileName=str(mode.effectsApplied) + '.jpg'
                    else:
                        mode.currentEffect='Color Reduction'
                        mode.getSliderValue(30)
                elif 5*mode.buttonHeight+4*mode.buttonDistance<event.y<6*mode.buttonHeight+4*mode.buttonDistance:
                    if mode.currentEffect=='Cartoon':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Cartoon')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Cartoon'
                        mode.effectsApplied[mode.currentEffect]=None
                        mode.cartoonize()
                elif 6*mode.buttonHeight+5*mode.buttonDistance<event.y<7*mode.buttonHeight+5*mode.buttonDistance:
                    if mode.currentEffect=='Edges':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Edges')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Edges'
                        mode.getSliderValue(0)
                elif 7*mode.buttonHeight+6*mode.buttonDistance<event.y<8*mode.buttonHeight+6*mode.buttonDistance:
                    if mode.currentEffect=='Vignette':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Vignette')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Vignette'
                        mode.effectsApplied[mode.currentEffect]=None
                        mode.vignette()
                elif 8*mode.buttonHeight+7*mode.buttonDistance<event.y<9*mode.buttonHeight+7*mode.buttonDistance:
                    if mode.currentEffect=='Blockify':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Blockify')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Blockify'
                        mode.effectsApplied[mode.currentEffect]=None
                        mode.blockify()
                elif 9*mode.buttonHeight+8*mode.buttonDistance<event.y<10*mode.buttonHeight+8*mode.buttonDistance:
                    if mode.currentEffect=='Combine':
                        mode.currentEffect=None
                        mode.effectsApplied.pop('Combine')
                        mode.fileName=str(mode.effectsApplied)+'.jpg'
                    else:
                        mode.currentEffect='Combine'
                        mode.effectsApplied[mode.currentEffect]=None
                        mode.combine()
                if 11*mode.buttonHeight+10*mode.buttonDistance<event.y<12*mode.buttonHeight+10*mode.buttonDistance:
                    mode.saveImage()
                elif 12*mode.buttonHeight+11*mode.buttonDistance<event.y<13*mode.buttonHeight+11*mode.buttonDistance:
                    mode.currentEffect='Loading'
                    mode.loadFilter()
        if mode.currentEffect==None and mode.effectsApplied==dict():
            mode.fileName = mode.originalFileName
        
    def keyPressed(mode, event):
        if (event.key == 'v'):
            mode.removeIntermediates()
            mode.app.setActiveMode(mode.app.videoMode)
        elif event.key == 'h':
            mode.app.setActiveMode(mode.app.helpMode)

    #view
    def displayImage(mode, canvas):
        if (mode.fileName==None or mode.fileName==''):
            return
        mode.checkForImage()
        img = Image.open(mode.fileName)
        width, height = img.size
        sideBarWidth = 2*mode.buttonWidth+3*mode.buttonDistance
        if (width>=height):
            ratio = height/width
            newWidth = int(3*mode.width/4-sideBarWidth)
            newHeight = int(newWidth*ratio)
        else:
            ratio = width/height
            newHeight = int(3*mode.height/4)
            newWidth = int(newHeight*ratio)
        img = img.resize((newWidth, newHeight))
        img = ImageTk.PhotoImage(img)  
        startPositionX = (mode.width-newWidth)//2 + sideBarWidth//2
        startPositionY = (mode.height-newHeight)//2 
        canvas.create_image(startPositionX,startPositionY, anchor=NW, image=img) 
        
    def drawButtons(mode, canvas):
        font = 'Arial 13'
        startX, startY = mode.buttonDistance, mode.buttonHeight
        for k in range(len(mode.adjustmentButtons)):
            textX = startX + mode.buttonWidth//2
            textY = startY + mode.buttonHeight//2
            label=mode.adjustmentButtons[k]
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth+mode.buttonDistance, 
                startY+mode.buttonHeight+mode.buttonDistance, fill = mode.buttonShadowColor)
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth, startY+mode.buttonHeight, fill = mode.buttonColor)
            canvas.create_text(textX, textY, text=label, fill='black', font = font)
            startX+=mode.buttonWidth+mode.buttonDistance
            if k%2==1:
                startY +=mode.buttonHeight+mode.buttonDistance
                startX = mode.buttonDistance

        startY+=mode.buttonHeight+mode.buttonDistance
        startX=mode.buttonDistance

        for j in range(len(mode.filterButtons)):
            textX = startX + mode.buttonWidth//2
            textY = startY + mode.buttonHeight//2
            label=mode.filterButtons[j]
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth+mode.buttonDistance, 
                startY+mode.buttonHeight+mode.buttonDistance, fill = mode.buttonShadowColor)
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth, startY+mode.buttonHeight, fill = mode.buttonColor)
            canvas.create_text(textX, textY, text=label, fill='black', font = font)
            startX+=mode.buttonWidth+mode.buttonDistance
            if j%2==1:
                startY +=mode.buttonHeight+mode.buttonDistance
                startX = mode.buttonDistance
        
        startY+=mode.buttonHeight+mode.buttonDistance
        startX=mode.buttonDistance

        for i in range(len(mode.optionButtons)):
            textX = startX + mode.buttonWidth//2
            textY = startY + mode.buttonHeight//2
            label=mode.optionButtons[i]
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth+mode.buttonDistance, 
                startY+mode.buttonHeight+mode.buttonDistance, fill = mode.buttonShadowColor)
            canvas.create_rectangle(startX, startY, startX+mode.buttonWidth, startY+mode.buttonHeight, fill = mode.buttonColor)
            canvas.create_text(textX, textY, text=label, fill='black', font = font)
            startX+=mode.buttonWidth+mode.buttonDistance
            if i%2==1:
                startY +=mode.buttonHeight+mode.buttonDistance
                startX= mode.buttonDistance

        textX = startX + mode.buttonWidth
        textY = startY + mode.buttonHeight//2
        canvas.create_rectangle(startX, startY, startX+2*mode.buttonWidth+mode.buttonDistance, startY+mode.buttonHeight, fill = mode.buttonColor)
        canvas.create_text(textX, textY, text='Video\nMode', fill='black', font = font)
        startY +=mode.buttonHeight+mode.buttonDistance
        startX= mode.buttonDistance
        textX = startX + mode.buttonWidth
        textY = startY + mode.buttonHeight//2
        canvas.create_rectangle(startX, startY, startX+2*mode.buttonWidth+mode.buttonDistance, startY+mode.buttonHeight, fill = mode.buttonColor)
        canvas.create_text(textX, textY, text='Restart', fill='black', font = font)
        
        
    def drawBackground(mode, canvas):
        canvas.create_rectangle(0,0, mode.width, mode.height, fill='dark grey')
        canvas.create_rectangle(0,0, 2*mode.buttonWidth+3*mode.buttonDistance, mode.height, fill='black')

    def drawLabels(mode, canvas):
        font = 'Arial 23 bold'
        startX=mode.buttonWidth+2*mode.buttonDistance
        startY = mode.buttonHeight//2
        canvas.create_text(startX, startY, text="Adjusments", fill='white', font = font)
        startY+=3*mode.buttonHeight+2*mode.buttonDistance
        canvas.create_text(startX, startY, text="Filters", fill='white', font = font)
        startY+=7*mode.buttonHeight+7*mode.buttonDistance
        canvas.create_text(startX, startY, text="Options", fill='white', font = font)
    
    def redrawAll(mode, canvas):
        mode.drawBackground(canvas)
        mode.drawButtons(canvas)
        mode.drawLabels(canvas)
        if (mode.importPressed):
            mode.displayImage(canvas)
  
class MyModalApp(ModalApp):
    def appStarted(app):
        app.splashScreenMode=SplashScreenMode()
        app.editMode = EffectsMode()
        app.helpMode = HelpMode() 
        app.videoMode = VideoMode()
        app.videoHelpMode = VideoHelpMode()
        app.setActiveMode(app.splashScreenMode)

app = MyModalApp(width=1000, height=800)

        












