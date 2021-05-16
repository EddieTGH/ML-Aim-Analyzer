import tkinter as tk
from tkinter.constants import *
import pyrebase
from requests.sessions import session
""" import firebase_admin
from firebase_admin import credentials, db
import firebase_admin.auth """
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
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
# 3. tracking - track the time that the user can follow the target with the mouse
# 4. peeking - track the time taken for the user to click the screen once a ball appears
# 5. angle hold

config = {
    "apiKey": "AIzaSyA19RqsNimyy0H9vEXPvtt-IKUR37ZXUSU",
    "authDomain": "warmuptestervalorant.firebaseapp.com",
    "databaseURL": "https://warmuptestervalorant-default-rtdb.firebaseio.com",
    "storageBucket": "warmuptestervalorant.appspot.com"
}
firebaseref = pyrebase.initialize_app(config)
db = firebaseref.database()
""" global auth_email, auth_password, auth_client
with open("config.json", "r+") as texthandle:
    text = texthandle.read()
    auth_email = dict(text)["password"]
    auth_password = dict(text)['email']

auth_client = firebase_admin.auth.Client()

if auth_email != "" and auth_password != "":
    auth_client.get_user_by_email(auth_email)

cred = credentials.Certificate("warmuptestervalorant-firebase-adminsdk-ynxs8-8d9f42b78f.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://warmuptestervalorant-default-rtdb.firebaseio.com"
})

databaseRoot = db.reference("/") """


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

global canvas, numClicks, goodClicks

def main():
    global canvas
    canvas = tk.Canvas(root, bg = "blue", width = 800, height = 700)
    canvas.place(relx = 0.5, rely = 0.5, anchor = CENTER)

    def click(event):
        clicked(event)
    root.bind('<Motion>', motion)
    root.bind("<Button-1>", click)
    root.bind('<Escape>', close)

    title_label = tk.Label(root, text = "AMAZING AIM ANALYZER", font = ("Robus", 30))
    title_label.place(relx = 0.5, rely = 0.1, anchor = CENTER)

    microFlex = tk.Button(root, text = "MicroFlex Task", height = 100, width= 600, command = lambda: openMicroTask())
    microFlex.place(relx= 0.2, rely = 0.3)
    
    spiderShot = tk.Button(root, text = "Spider Shot Task", height = 100, width= 600, command = lambda: openSpiderShot())
    spiderShot.place(relx= 0.2, rely = 0.4)

    tracking = tk.Button(root, text = "Tracking Task", height = 100, width= 600, command = lambda: openTrackingTask())
    tracking.place(relx= 0.2, rely = 0.5)

    angleHold = tk.Button(root, text = "Angle Hold Task", height = 100, width= 600, command = lambda: openAngleTask())
    angleHold.place(relx= 0.2, rely = 0.6) 


    root.mainloop()
    
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


def close(event):
    for child in root.winfo_children():
        child.destroy()
    main()
 
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

def spawnMacroTargets(taskCanvas):
    print("SPAWNING MACRO NOW")
    global currentTargetX, currentTargetY, taskRunning, lastTargetX, lastTargetY, lastMouseX, lastMouseY, ballID
    taskRunning = True
    """ taskCanvas = tk.Canvas(root, width=800, height = 800, bg="red")
    taskCanvas.place(relx = 0, rely = 0, anchor = 'nw')
    taskCanvas.create_text(23, 14, text=str(0), justify = CENTER) """
    
    try:
        velocityAnalyzer2()
    except:
        pass

    filename = tk.PhotoImage(file = "ball.png")
    root.filename = filename
    
    x = random.randint(0, 800)
    y = random.randint(0, 800)
    try:
        print("distance here!:" + str(findDistance((x, y), (currentTargetX, currentTargetY))))
    except:
        pass
    try:
        while findDistance((x, y), (currentTargetX, currentTargetY)) < 300:
            x = random.randint(0, 800)
            y = random.randint(0, 800)
            print("recreating")
    except:
        print("error")
    print("x: " + str(x))
    print("y: ", str(y))
    lastMouseX = currentMouseX
    lastMouseY = currentMouseY
    currentTargetX, currentTargetY = x, y
    try:
        taskCanvas.delete(ballID)
    except:
        pass
    ballID = taskCanvas.create_image(x,y, anchor='c', image=filename)
    root.update()
    taskCanvas.update_idletasks()
    # root.after(2000, spawnTargets)


def spawnTargets(taskCanvas):
    global currentTargetX, currentTargetY, taskRunning, lastTargetX, lastTargetY, lastMouseX, lastMouseY, ballID
    taskRunning = True
    """ taskCanvas = tk.Canvas(root, width=800, height = 800, bg="red")
    taskCanvas.place(relx = 0, rely = 0, anchor = 'nw')
    taskCanvas.create_text(23, 14, text=str(0), justify = CENTER) """
    
    try:
        velocityAnalyzer2()
    except:
        pass

    filename = tk.PhotoImage(file = "ball.png")
    root.filename = filename
    x = random.randint(300, 500)
    y = random.randint(300, 500)
    print("x: " + str(x))
    print("y: ", str(y))
    lastMouseX = currentMouseX
    lastMouseY = currentMouseY
    currentTargetX, currentTargetY = x, y
    try:
        taskCanvas.delete(ballID)
    except:
        pass
    ballID = taskCanvas.create_image(x,y, anchor='c', image=filename)
    root.update()
    taskCanvas.update_idletasks()
    # root.after(2000, spawnTargets)

def clicked(event):
    global currentMouseX, currentMouseY, currentTargetX, currentTargetY, taskRunning, lastMouseX, lastMouseY, lastHitTime, canvas, goodClicks, numClicks, microRunning, macroRunning
    if taskRunning:
        numClicks += 1
        if currentTargetX-40 < currentMouseX < currentTargetX + 40 and currentTargetY-40 < currentMouseY < currentTargetY+40:
            if microRunning:
                spawnTargets(canvas)
            elif macroRunning:
                spawnMacroTargets(canvas)
            goodClicks += 1

            # lastMouseX, lastMouseY = root.winfo_pointerx() - root.winfo_rootx(), root.winfo_pointery() - root.winfo_rooty()
            lastHitTime = time.time()
        else:
            pass

def mainMenu():
    pass

def updateTimer(canvas, initialTime, upper_text):
    canvas.delete(upper_text)
    upper_text = canvas.create_text(23, 14, text=str(round((time.time() - initialTime), 2)), justify = LEFT)
    root.after(5, lambda: updateTimer(canvas, initialTime, upper_text))

def openMicroTask():
    global taskRunning, currentTargetX, currentTargetY, canvas, goodClicks, numClicks, microRunning, macroRunning
    goodClicks = 0
    numClicks = 0
    microRunning = True
    macroRunning = False
    for child in canvas.winfo_children():
        child.destroy()
    taskRunning = True
    canvas = tk.Canvas(root, width=800, height = 800, bg="red")
    canvas.place(relx = 0, rely = 0, anchor = 'nw')
    upper_text = canvas.create_text(23, 14, text=str(0), justify = LEFT)
    initialTime = time.time()
    spawnTargets(canvas)
    updateTimer(canvas, initialTime, upper_text)
    root.bind("<Return>", displayResults)
    root.after(60000, lambda: close(0))
    
def calcAccuracy(shotsHit, shotsTaken): 
    return round(shotsHit/shotsTaken, 2)

def displayResults(event):
    global sessionVelocities, sessionVelocitiesX, sessionVelocitiesY, goodClicks, numClicks
    scoreLevel = tk.Toplevel(root)
    scoreLevel.geometry("600x600")
    scoreLevel.resizable(0,0)

    accuracy = round((goodClicks / numClicks), 2)
    
    acc_label = tk.Label(scoreLevel, text = "Accuracy: " + str(accuracy))
    acc_label.place(relx = 0.33, rely = 0.8, anchor = CENTER)

    score = 0
    for velocity in sessionVelocitiesY:
        score += (velocity // 250) + 1  
    
    score_label = tk.Label(scoreLevel, text = "Score: " + str(score))
    score_label.place(relx = 0.66, rely = 0.8, anchor = CENTER)

    fig = mpl.figure.Figure()
    # Adding a subplot
    ax = fig.add_subplot(1,1,1)
    # Title
    ax.set_title("Cursor Velocity (px/s) vs Trial")
    # Y axis label
    ax.set_ylabel("Cursor Velocity (px/s)")
    # X axis label
    ax.set_xlabel("Trial #")
    # Set y bounds to 0-1100
    ax.set_ylim([0, 2500])
    # Create a matplotlib / tkinter canvas object
    canvas = FigureCanvasTkAgg(fig, master=scoreLevel)
    # Render the canvas
    canvas.draw()
    # place on tkinter gui
    canvas._tkcanvas.place(relx = 0.02, rely = 0.03, relwidth = 1, relheight = 0.70)
    toolbar = NavigationToolbar2Tk(canvas, scoreLevel)
    toolbar.update()
    # Plot the data
    line, = ax.plot(sessionVelocitiesX, sessionVelocitiesY, color = "red", label = "EMG Value (V)")

def openSpiderShot():
    global taskRunning, currentTargetX, currentTargetY, canvas, goodClicks, numClicks, macroRunning, microRunning
    goodClicks = 0
    numClicks = 0
    macroRunning = True
    microRunning = False
    for child in canvas.winfo_children():
        child.destroy()
    taskRunning = True
    canvas = tk.Canvas(root, width=800, height = 800, bg="red")
    canvas.place(relx = 0, rely = 0, anchor = 'nw')
    upper_text = canvas.create_text(23, 14, text=str(0), justify = LEFT)
    initialTime = time.time()
    spawnMacroTargets(canvas)
    updateTimer(canvas, initialTime, upper_text)
    root.bind("<Return>", displayResults)
    root.after(60000, lambda: close(0))

def openTrackingTask():
    global taskRunning, currentTargetX, currentTargetY
    taskRunning = True


def openAngleTask():
    global taskRunning, currentTargetX, currentTargetY
    taskRunning = True



if __name__ == "__main__":  
    main()
    
    
    """ fig = plt.figure()
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
    plt.show() """