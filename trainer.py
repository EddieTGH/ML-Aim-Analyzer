import tkinter as tk
import pyrebase
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import _thread
import math
import random
from PIL import Image
import time

im1 = Image.open('ball.png').resize((100, 100))
im1.save("ball.png", "png")
# 5 tasks
# 1. micro adjustments
# 2. macro flicks
# 3. tracking
# 4. peeking
# 5. angle hold

config = {
    "apiKey": "AIzaSyA19RqsNimyy0H9vEXPvtt-IKUR37ZXUSU",
    "authDomain": "warmuptestervalorant.firebaseapp.com",
    "databaseURL": "https://warmuptestervalorant-default-rtdb.firebaseio.com",
    "storageBucket": "warmuptestervalorant.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

root = tk.Tk()
root.geometry("800x800")

global currentMouseX, currentMouseY, currentTargetX, currentTargetY, lastTargetX, lastTargetY, taskRunning, difference, inBetweenTargets, onTarget, timeOn, totalTime, percentageOn
global lastMouseX, lastMouseY
global lastHitTime, startTime
startTime = time.time()
onTarget = False
inBetweenTargets = False

sessionVelocitiesX = []
sessionVelocitiesY = []
sessionVelocities = {}

currentMouseX = root.winfo_pointerx() - root.winfo_rootx()
currentMouseY = root.winfo_pointery() - root.winfo_rooty()
lastMouseX = currentMouseX
lastMouseY = currentMouseY

global score, accuracy

def motion(event):
    global currentMouseX, currentMouseY, difference
    try:
        if event.x != currentMouseX or event.y != currentMouseY:
            difference = True
        else:
            difference = False
    except:
        pass
    currentMouseX = event.x
    currentMouseY = event.y
    # print('{}, {}'.format(currentMouseX, currentMouseY))

""" # go into a different thread since it'll be running in the background of tk
def velocityAnalyzer():
    global currentMouseX, currentMouseY, currentTargetX, currentTargetY, taskRunning, difference

    sessionVelocitiesX = []
    sessionVelocitiesY = []
    sessionVelocities = {}

    def findDistance(point1, point2):
        return math.sqrt((point2[1]-point1[1])**2 + (point2[0]-point1[0])**2)

    def findAccuracy():
        # return round(shotsHit/shotsTaken, 0)
        pass
    startTime = time.time()
    lastChecked = time.time()    
    lastPos = (currentMouseX, currentMouseY)
    while taskRunning:
        if currentMouseX != lastPos[0] or currentMouseY != lastPos[1]:
            newPos = (currentMouseX, currentMouseY)
            distance = findDistance(newPos, lastPos)
            timeDelta = time.time() - lastChecked
            totalTimeDelta = time.time() - startTime
            sessionVelocitiesX.append(timeDelta)
            sessionVelocitiesY.append(distance / timeDelta)
            sessionVelocities[totalTimeDelta] = distance / timeDelta
            lastPos = (currentMouseX, currentMouseY)
            lastChecked = time.time()
            print("Distance: {}, Time: {}, Velocity: {}".format(str(distance), str(timeDelta), str(distance / timeDelta)))
            time.sleep(0.020)
        else:
            time.sleep(0.020)
            continue """
 
def velocityAnalyzer2():
    global currentMouseX, currentMouseY, currentTargetX, currentTargetY, taskRunning, difference, lastMouseX, lastMouseY, lastHitTime, startTime
    print(currentMouseX, currentMouseY)
    print(lastMouseX, lastMouseY)
    print("Distance: {}".format(str(findDistance((currentMouseX, currentMouseY), (lastMouseX, lastMouseY)))))
    if findDistance((currentMouseX, currentMouseY), (currentTargetX, currentTargetY)) < 40:
        lastSuccessfulPos = (lastMouseX, lastMouseY)
        currentPos = (currentMouseX, currentMouseY)
        distance = findDistance(lastSuccessfulPos, currentPos)
        timeDelta = time.time() - lastHitTime
        totalTimeDelta = time.time() - startTime
        velocity = distance / (timeDelta)
        try:
            lastX = sessionVelocitiesX[len(sessionVelocitiesX)-1]
            sessionVelocitiesX.append(lastX + 1)
        except:
            sessionVelocitiesX.append(0)
        sessionVelocitiesY.append(velocity)
        sessionVelocities[totalTimeDelta] = velocity
        print("Distance: {}, Time: {}, Velocity: {}".format(str(distance), str(timeDelta), str(velocity)))
        lastHitTime = time.time()



def findDistance(point1, point2):
    return math.sqrt((point2[1]-point1[1])**2 + (point2[0]-point1[0])**2)

#Determines the state of the user:
    #Either between targets (moving towards one of them)
    #Either static, meaning that no position change is occurring and no targets are active
    #Or onTarget, meaning that the mouse is on a target
def detState():
    global inBetweenTargets, onTarget, static, currentMouseX, currentMouseY, currentTargetX, currentTargetY
    if findDistance((currentMouseX, currentMouseY), (currentTargetX, currentTargetY)) < 40:
        onTarget = True
        inBetweenTargets = False
    elif findDistance((currentMouseX, currentMouseY), (currentTargetX, currentTargetY)) > 40:
        inBetweenTargets = True
        onTarget = False
    root.after(20, detState)


def trackingAnalyzer2():
    global currentMouseX, currentMouseY, currentTargetX, currentTargetY, taskRunning, timeOn, totalTime, percentageOn
    
    timeOn = 0
    totalTime = 0
    if taskRunning:
        beg = time.time()
        start = time.time()
        offTarget = True
        if currentTargetX-40 < currentMouseX < currentTargetX + 40 and currentTargetY-40 < currentMouseY < currentTargetY+40:
            if offTarget:
                start = time.time()
                offTarget = False
        else:
            offTarget = True
            timeOn += time.time()-start
        totalTime += time.time()-beg
        percentageOn = round(timeOn/totalTime, 0)
        print("TotalTime:" + totalTime)
        print("percentageOn:" + percentageOn)

def angleHoldAnalyzer():
    pass
            
            
            
def move():
    pass
    # self.canvas.move(self.image,x,0)
    # self.master.update()

def spawnTargets():
    global currentTargetX, currentTargetY, taskRunning, lastTargetX, lastTargetY, lastMouseX, lastMouseY
    taskRunning = True
    taskCanvas = tk.Canvas(root, width=800, height = 800, bg="red")
    taskCanvas.place(relx = 0, rely = 0, anchor = 'nw')

    try:
        velocityAnalyzer2()
    except:
        pass

    filename = tk.PhotoImage(file = "ball.png")
    root.filename = filename
    x = random.randint(0, 800)
    y = random.randint(0, 800)
    print("x: " + str(x))
    print("y: ", str(y))
    lastMouseX = currentMouseX
    lastMouseY = currentMouseY
    currentTargetX, currentTargetY = x, y
    image = taskCanvas.create_image(x,y, anchor='c', image=filename)
    root.update()
    taskCanvas.update_idletasks()
    # root.after(2000, spawnTargets)

def clicked(event):
    global currentMouseX, currentMouseY, currentTargetX, currentTargetY, taskRunning, lastMouseX, lastMouseY, lastHitTime, startTime
    if taskRunning:
        if currentTargetX-40 < currentMouseX < currentTargetX + 40 and currentTargetY-40 < currentMouseY < currentTargetY+40:
            spawnTargets()
            # lastMouseX, lastMouseY = root.winfo_pointerx() - root.winfo_rootx(), root.winfo_pointery() - root.winfo_rooty()
            lastHitTime = time.time()
        else:
            pass

def mainMenu():
    pass
def microTask():
    global taskRunning, currentTargetX, currentTargetY
    taskRunning = True

def macroTask():
    global taskRunning, currentTargetX, currentTargetY
    taskRunning = True

def trackingTask():
    global taskRunning, currentTargetX, currentTargetY
    taskRunning = True

    
def reactionTimeTask():
    global taskRunning, currentTargetX, currentTargetY
    taskRunning = True

def angleHoldTask():
    global taskRunning, currentTargetX, currentTargetY
    taskRunning = True



if __name__ == "__main__":  
    def click(event):
        clicked(event)
    root.bind('<Motion>', motion)
    root.bind("<Button-1>", click)
    # _thread.start_new_thread(velocityAnalyzer, ())
    spawnTargets()
    # root.after(2000, spawnTargets)
    root.mainloop()
    fig = plt.figure()
    # Adding a subplot
    ax = fig.add_subplot(1,1,1)
    # Title
    ax.set_title("Cursor Velocity (px/s) vs Trial")
    # Y axis label
    ax.set_ylabel("Cursor Velocity")
    # X axis label
    ax.set_xlabel("Trial #")
    # Set y bounds to 0-1100
    ax.set_ylim([0, 2000])
    ax.set_xticks(sessionVelocitiesX)
    ax.plot(sessionVelocitiesX, sessionVelocitiesY, color = "red")
    plt.show()