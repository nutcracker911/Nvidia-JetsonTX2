#!/usr/bin/python3

import cv2
import jetson.inference
import jetson.utils
import argparse 
import sys
import numpy as np
import imutils
import serial
import time

######################################################

global centX # определение глобальных переменных чтобы считать разницу между центром картинки и центром квадрата который определяется qr-code
global centY

centX=640 # центр выводимого изображения
centY=360

x=[]
y=[]
xx=[]
yy=[]
X=0
Y=0
detect=[]
TT=0

deltaX=0
deltaY=0
degreex=0
degreey=0

line=0
lines=[]
lines1=[]
z=0

test=[]

######################################################

Karray=[110,60,100,100,100,100] # массив координат для сервоприводов
Aarray=[20,20,3,3,3,3] # массив ускорения для сервоприводов
Sarray=[600,600,200,200,200,200] # массив скорости для сервоприводов

ser=serial.Serial('/dev/ttyTHS2', 115200, timeout=None) # управление сервой через сериал порт

str1='K'
for i in range(6):
	str1=str1+','+str(Karray[i])
str1=str1+';'
ser.write(str1.encode())
ser.flushInput

str1='A'
for i in range(6):
	str1=str1+','+str(Aarray[i])
str1=str1+';'
ser.write(str1.encode())
ser.flushInput

str1='S'
for i in range(6):
	str1=str1+','+str(Sarray[i])
str1=str1+';'
ser.write(str1.encode())
ser.flushInput

ser.close()

######################################################

#parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage() +
                                 jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

#parser.add_argument("input_URI", type=str, default="", nargs='?', help="URI of the input stream")
#parser.add_argument("output_URI", type=str, default="", nargs='?', help="URI of the output stream")
parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
#parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")


is_headless = ["--headless"] if sys.argv[0].find('console.py') != -1 else [""]

try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)


net = jetson.inference.detectNet(opt.network, sys.argv, threshold=0.9)
camera = jetson.utils.videoSource("/dev/video0")      # '/dev/video0' for V4L2
display = jetson.utils.videoOutput("display://0") # 'my_video.mp4' for file
######################################################

while display.IsStreaming():
	
	ser=serial.Serial('/dev/ttyTHS2', 115200, timeout=None) # откравыем сериал порт для осуществелении переди данных
	img = camera.Capture()
	detections = net.Detect(img)
	display.Render(img)
	
	'''jetson.utils.cudaDeviceSynchronize()
	test=jetson.utils.cudaToNumpy(img)
	#jetson.utils.cudaNormalize(test (0.0,250.0), test (0.0,1.0))
	test2=test.copy()
	test2=cv2.cvtColor(test2.astype (np.uint8), cv2.COLOR_RGBA2BGR)
	
	print('1',test)
	print('2',test2)
	cv2.imshow('test', test2)'''
	
	display.SetStatus("Object Detection | Technopolis ERA {:.0f} FPS".format(net.GetNetworkFPS()))
	#net.PrintProfilerTimes()
	
	t=0
	detect.clear()
	
	for detection in detections:
		t=t+1
		detect.append(detection)
		detection=0
		
	Dold = 0
		
	if t!=0:
		for i in range(len(detections)):
			D = detect[i].Confidence
			#print(detect[i])
			if D > Dold:
				ii=i
				Dold = D
	
	if (len(detections)!=0):
		z = 1
		Center = detect[ii].Center
		#print(detect[ii].Center)
		x.append(Center[0])
		y.append(Center[1])
	
	else:
		z = 0
		x.clear()
		y.clear()
				
	if (len(x) == 1)&(len(y) == 1)&(len(detections)!= 0):
		#print('z=1 len x', x)
		#print('z=1 len y', y)
		X=int((sum(x))/1)
		Y=int((sum(y))/1)
		#print('X', X)
		#print('Y', Y)
		x.clear()
		y.clear()
		
	deltaX = int(centX-X)   #разница между центром области распознавания и центром общегй картинки
	deltaY = int(centY-Y)
	print('deltaX ', deltaX)
	print('deltaY ', deltaY)
	
	
	
	if (abs(deltaX)>50)&(abs(deltaY)>50):
		degreex= int(deltaX/5)
		degreey= int(deltaY/5)
	
	if (abs(deltaX)>20)&(abs(deltaY)>20):
		degreex= int(deltaX/10)
		degreey= int(deltaY/10)
		
	if (abs(deltaX)>10)&(abs(deltaY)>10):
		degreex= int(deltaX/100)
		degreey= int(deltaY/100)
	
	
	
	if (635<deltaX<645)&(355<deltaY<365)&(len(detections)!=0):
		degreex=0
		degreey=0
	
	if (len(detections) == 0):
		z = 0
		deltaX = 0
		deltaY = 0
		X = 0
		Y = 0
		
	'''if (Karray[0]>0):
		delt=0-Karray[0]
		for i in range (90):
			Karray[1]-=1
			Karray[0]-=1
			delt=0-Karray[0]
			ser.write(str1.encode())
		
	if (Karray[0]<179)&(Karray[1]<179):
		Karray[1]+=1
		Karray[0]+=1
		ser.write(str1.encode())
		
		if (Karray[0]==0)&(Karray[0]==0):
			for i in range(181):
				Karray[1]+=1
				ser.write(str1.encode())
				for i in range(181):
					Karray[0]+=1
					ser.write(str1.encode())	'''
			
		
	TT=TT+1
		
#########################################
	
	if TT==1:	
		if degreex>0:
			if deltaX>=2:
				Karray[1]-=1
				Karray[2]-=1
				Karray[3]+=1
				if Karray[1]>=180:
					Karray[1]=180
				
				if Karray[2]<=70:# ограничение работы элеронов 
					Karray[2]=70
				if Karray[3]>=120:
					Karray[3]=120# ограничение работы элеронов 
				
				if Karray[1]<=0:
					Karray[1]=0
				
			if deltaX<=2:
				Karray[2]=100
				Karray[3]=90
		
		if degreex<0:
			if deltaX<=-2:
				Karray[1]+=1
				Karray[2]+=1
				Karray[3]-=1
				if Karray[1]>=180:
					Karray[1]=180
					
					
				if Karray[2]>=130:# ограничение работы элеронов 
					Karray[2]=130
				if Karray[3]<=60:
					Karray[3]=60# ограничение работы элеронов
				
				if Karray[1]<=0:
					Karray[1]=0  

				
			if deltaX>=-2:
				Karray[2]=100
				Karray[3]=90
				
		
		if -2>deltaX>2:
			Karray[1]+=0
		
	if TT==1:
		if degreey>0:
			if deltaY>=2:
				Karray[0]-=1
				Karray[4]-=1
				Karray[5]+=1
				if Karray[0]>=180:
					Karray[0]=180
					
				if Karray[4]<=70:# ограничение работы элеронов 
					Karray[4]=70
				if Karray[5]>=130:
					Karray[5]=130# ограничение работы элеронов 
					
				if Karray[0]<=0:
					Karray[0]=0
			if deltaY<=2:
				Karray[4]=100
				Karray[5]=100
				
				
		if degreey<0:
			if deltaY<=-2:
				Karray[0]+=1
				Karray[4]+=1
				Karray[5]-=1
				if Karray[0]>=180:
					Karray[0]=180
				
				if Karray[4]>=130:# ограничение работы элеронов 
					Karray[4]=130
				if Karray[5]<=70:
					Karray[5]=70# ограничение работы элеронов
					
				if Karray[0]<=0:
					Karray[0]=0
			if deltaY>=-2:
				Karray[4]=100
				Karray[5]=100
				
					
		if -2>deltaY>2:
			Karray[0]+=0
	
		
		TT = 0
		deltaY = 0
		deltaX = 0
		degreex = 0
		degreey = 0
		
		
	ser.write('?;'.encode())
	


	for i in range(25): # читаем 25 знаков приходящих с ардуины (число 25 выбранно потому что это максимальное количество которое можно получить с ардуины при получении 6 значений по 3 знака)
		line=ser.read(1)# читаем один бит
		if line!=b'\n' or line!='\r':
			lines.append(chr(ord(line))) # передешифровка получаемых данных
		if line==b'\n' or line==' \r':# флаг прекращения чтения битов (отправляется ардуиной)
			break
	
	Mlines = ''.join(lines)
	Mlines = Mlines.split(',')# формирование удобоваримого формата чтения фалов (получаем разрозненные числа и состыковываем их)
	
	if ' \r\n' in Mlines:
		Mlines.remove(' \r\n')
	if ' ' in Mlines:
		Mlines.remove(' ') 
	print(Mlines)
	lines.clear()
	Mlines.clear()
	
	Karray[2]=100
	Karray[3]=100
	Karray[4]=100
	Karray[5]=100
	
	
	str1='K'
	for i in range(6):
		str1=str1+','+str(Karray[i])
	str1=str1+';'  

	if z==1:
		ser.write(str1.encode())
		ser.flushInput
		ser.close()
		z=0

