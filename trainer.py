from collections import UserString
import tkinter as tk
from tkinter.constants import *
import pyrebase
import pandas as pd
from pyrebase.pyrebase import Database
import sklearn
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import _thread
import math
import random
from PIL import Image
import time

def removePeriods(input):
    while input.__contains__("."):
        input = input.replace(".", "_()")
    return input

def addPeriods(input):
    while input.__contains__("_()"):
        input = input.replace("_()", ".")
    return input

im1 = Image.open('ball.png').resize((100, 100))
im1.save("ball.png", "png")
# 5 tasks
# 1. micro adjustments - score and accuracy
# 2. macro flicks - score and accuracy
# 3. tracking - percentage on target
# 5. angle hold - score and accuracy

""" Users
    PlayerEmail
        Sessions
            Datetime
                Micro
                    Score: score
                    Accuracy: accuracy
                    KDA: KDA
                    Feeling: feeling
                Macro
                    Score: score
                    Accuracy: accuracy
                    KDA: KDA
                    Feeling: feeling
                Tracking
                    Percentage: percentage
                    KDA: KDA
                    Feeling: feeling
                Angle
                    Score: score
                    Accuracy: accuracy
                    KDA: KDA
                    Feeling: feeling """
                    

config = {
    "apiKey": "AIzaSyA19RqsNimyy0H9vEXPvtt-IKUR37ZXUSU",
    "authDomain": "warmuptestervalorant.firebaseapp.com",
    "databaseURL": "https://warmuptestervalorant-default-rtdb.firebaseio.com",
    "storageBucket": "warmuptestervalorant.appspot.com"
}
firebaseref = pyrebase.initialize_app(config)
db = firebaseref.database()
global auth_email
with open("config.json", "r+") as texthandle:
    text = texthandle.read()
    try:
        auth_email = removePeriods(dict(text)["email"])
    except:
        auth_email = ""

""" auth_client = firebase_admin.auth.Client()

if auth_email != "" and auth_password != "":
    auth_client.get_user_by_email(auth_email)

cred = credentials.Certificate("warmuptestervalorant-firebase-adminsdk-ynxs8-8d9f42b78f.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://warmuptestervalorant-default-rtdb.firebaseio.com"
})

databaseRoot = db.reference("/") """

root = tk.Tk()
root.geometry("800x800")

def makeSignInToplevel():
    SignIn = tk.Toplevel(root)

    email = tk.StringVar()
    entry = tk.Entry(SignIn, textvariable = email)
    entry.place(relx = 0.5, rely = 0.5, anchor = CENTER)

    label = tk.Label(SignIn, text = "Sign In to your Account or Create an Account", font = ("Helvetica", 18))
    label.place(relx = 0.5, rely = 0.4, anchor = CENTER)

    def SubmitEmail(input):
        global auth_email
        email = removePeriods(input)
        auth_email = email
        dictionary = {'email': email}
        with open("config.json", "w+") as texthandle:
            texthandle.write(str(dictionary))
        texthandle.close()
        SignIn.destroy()

    submit = tk.Button(SignIn, text = "Submit", command = lambda: SubmitEmail(email.get()))
    submit.place(relx = 0.5, rely = 0.6, anchor = CENTER)

if auth_email != "":
    makeSignInToplevel()



global currentMouseX, currentMouseY, currentTargetX, currentTargetY, lastTargetX, lastTargetY, taskRunning, difference, inBetweenTargets, onTarget, timeOn, totalTime, percentageOn
global lastMouseX, lastMouseY
global lastHitTime, startTime
startTime = time.time()
onTarget = False
inBetweenTargets = False
global sessionVelocities, sessionVelocitiesX, sessionVelocitiesY, sessionTimesAngle
sessionTimesAngle = []
sessionVelocitiesX = []
sessionVelocitiesY = []
sessionVelocities = {}

currentMouseX = root.winfo_pointerx() - root.winfo_rootx()
currentMouseY = root.winfo_pointery() - root.winfo_rooty()
lastMouseX = currentMouseX
lastMouseY = currentMouseY

taskRunning = False

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
    global auth_email, sessionVelocitiesY, sessionVelocities, sessionVelocitiesX, taskRunning
    for child in root.winfo_children():
        child.destroy()
    taskRunning = False
    # Sending to firebase
    sum = 0
    for velocity in sessionVelocitiesY:
        sum += velocity
    avg_velocity = sum / len(sessionVelocitiesY)
    db.child("Users").child(auth_email).child("Velocity_Data").set(sessionVelocities)
    sessionVelocities = {}
    sessionVelocitiesX = []
    sessionVelocitiesY = []
    main()
 
def velocityAnalyzer2():
    global currentMouseX, currentMouseY, currentTargetX, currentTargetY, taskRunning, difference, lastMouseX, lastMouseY, lastHitTime, startTime, sessionTimesAngle
    print(currentMouseX, currentMouseY)
    print(lastMouseX, lastMouseY)
    print("Distance: {}".format(str(findDistance((currentMouseX, currentMouseY), (lastMouseX, lastMouseY)))))
    if findDistance((currentMouseX, currentMouseY), (currentTargetX, currentTargetY)) < 40:
        lastSuccessfulPos = (lastMouseX, lastMouseY)
        currentPos = (currentMouseX, currentMouseY)
        distance = findDistance(lastSuccessfulPos, currentPos)
        timeDelta = time.time() - lastHitTime
        sessionTimesAngle.append(timeDelta)
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

def clicked2(event):
    global currentMouseX, currentMouseY, currentTargetX, currentTargetY, taskRunning, lastMouseX, lastMouseY, lastHitTime, canvas, goodClicks, numClicks, microRunning, macroRunning
    if taskRunning:
        numClicks += 1
        if currentTargetX-40 < currentMouseX < currentTargetX + 40 and currentTargetY-40 < currentMouseY < currentTargetY+40:
            if microRunning:
                spawnTargets(canvas)
            elif macroRunning:
                spawnMacroTargets(canvas)
            elif angleRunning:
                spawnAngleTargets(canvas)
            goodClicks += 1

            # lastMouseX, lastMouseY = root.winfo_pointerx() - root.winfo_rootx(), root.winfo_pointery() - root.winfo_rooty()
            lastHitTime = time.time()
        else:
            pass

def clicked(event):
    global currentMouseX, currentMouseY, currentTargetX, currentTargetY, taskRunning, lastMouseX, lastMouseY, lastHitTime, canvas, goodClicks, numClicks, microRunning, macroRunning
    if taskRunning:
        numClicks += 1
        if microRunning:
            if currentTargetX-40 < currentMouseX < currentTargetX + 40 and currentTargetY-40 < currentMouseY < currentTargetY+40:
                spawnTargets(canvas)
                goodClicks += 1
        elif macroRunning:
            if currentTargetX-40 < currentMouseX < currentTargetX + 40 and currentTargetY-40 < currentMouseY < currentTargetY+40:
                spawnMacroTargets(canvas)
                goodClicks += 1
        elif angleRunning:
            print("angleRunning is true")
            if currentTargetX-40 < currentMouseX < currentTargetX + 40 and currentTargetY-40 < currentMouseY < currentTargetY+40:
                print("ball clicked")
                spawnAngleTargets(canvas)
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
    global taskRunning, currentTargetX, currentTargetY, canvas, goodClicks, numClicks, microRunning, macroRunning, angleRunning
    goodClicks = 0
    numClicks = 0
    microRunning = True
    macroRunning = False
    angleRunning = False
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
    sum = 0
    for velocity in sessionVelocitiesY:
        sum += velocity
        score += (velocity // 250) + 1  
    avg_velocity = sum / len(sessionVelocitiesY)
    
    score_label = tk.Label(scoreLevel, text = "Score: " + str(score))
    score_label.place(relx = 0.66, rely = 0.8, anchor = CENTER)

    score_label = tk.Label(scoreLevel, text = "Average Cursor Velocity: " + str(avg_velocity))
    score_label.place(relx = 0.8, rely = 0.8, anchor = CENTER)

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
    global taskRunning, currentTargetX, currentTargetY, canvas, goodClicks, numClicks, macroRunning, microRunning, angleRunning
    goodClicks = 0
    numClicks = 0
    macroRunning = True
    microRunning = False
    angleRunning = False
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
 

def openAngleTask():
    global taskRunning, currentTargetX, currentTargetY, canvas, goodClicks, numClicks, macroRunning, microRunning, angleRunning
    goodClicks = 0
    numClicks = 0
    macroRunning = False
    microRunning = False
    angleRunning = True
    for child in canvas.winfo_children():
        child.destroy()
    taskRunning = True
    canvas = tk.Canvas(root, width=800, height = 800, bg="red")
    canvas.place(relx = 0, rely = 0, anchor = 'nw')
    canvas.create_rectangle(0, 0, 300, 800, fill='yellow')
    canvas.create_rectangle(500, 0, 800, 800, fill='yellow')
    canvas.create_rectangle(0, 0, 200, 800, fill='green')
    canvas.create_rectangle(600, 0, 800, 800, fill='green')
    canvas.create_rectangle(0, 0, 100, 800, fill='pink')
    canvas.create_rectangle(700, 0, 800, 800, fill='pink')


    upper_text = canvas.create_text(23, 14, text=str(0), justify = LEFT)
    initialTime = time.time()
    updateTimer(canvas, initialTime, upper_text)
    root.bind("<Return>", displayResultsAngle)
    root.after(60000, lambda: close(0))
    spawnAngleTargets(canvas)
    


def spawnAngleTargets(canvas):
    print("SPAWNING Angle NOW")
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

    possibleX = [160, 210, 260, 540,590, 640]
    y = random.randint(0, 800)
    xIndex = random.randint(0,5)
    x = possibleX[xIndex]
 
    print("x: ", str(x))
    print("y: ", str(y))
    try:
        print("distance here!:" + str(findDistance((x, y), (currentTargetX, currentTargetY))))
    except:
        pass

    lastMouseX = currentMouseX
    lastMouseY = currentMouseY
    currentTargetX, currentTargetY = x, y
    try:
        canvas.delete(ballID)
    except:
        pass

    ballID = canvas.create_image(x, y, anchor='c', image=filename)
    if xIndex == 0:
        distance = 640
    elif xIndex == 1:
        distance = 590
    elif xIndex == 2:
        distance = 540
    elif xIndex == 3:
        distance = -540
    elif xIndex == 4:
        distance = -590
    elif xIndex == 5:
        distance = -640

    divider = 50
    counter = 0
    while counter<divider:
        time.sleep(0.05)
        canvas.move(ballID,distance / divider,0)
        x += distance / divider
        currentTargetX = x
        canvas.update() 
        root.update()
        counter += 1
        if x < 0 or x > 800:
            break
    root.update()
    canvas.update_idletasks()
    print('one spawned done')
    
    root.after(1000, spawnAngleTargets(canvas))


def displayResultsAngle(event):
    global sessionTimesAngle, sessionVelocitiesX, goodClicks, numClicks
    print("displayingangleresults")
    scoreLevel = tk.Toplevel(root)
    scoreLevel.geometry("600x600")
    scoreLevel.resizable(0,0)

    accuracy = round((goodClicks / numClicks), 2)
    
    acc_label = tk.Label(scoreLevel, text = "Accuracy: " + str(accuracy))
    acc_label.place(relx = 0.33, rely = 0.8, anchor = CENTER)

    score = 0
    sum = 0
    for times in sessionTimesAngle:
        sum += times
        score += (10-times)  
    avg_time = sum / len(sessionTimesAngle)
    
    score_label = tk.Label(scoreLevel, text = "Score: " + str(round(score,2))
    score_label.place(relx = 0.33, rely = 0.8, anchor = CENTER)

    score_label = tk.Label(scoreLevel, text = "Average Time Taken Per Ball: " + str(round(avg_time,2)))
    score_label.place(relx = 0.66, rely = 0.8, anchor = CENTER)

    fig = mpl.figure.Figure()
    # Adding a subplot
    ax = fig.add_subplot(1,1,1)
    # Title
    ax.set_title("Time Taken To Click On Target (s) vs Trial")
    # Y axis label
    ax.set_ylabel("Time Taken To Click Target")
    # X axis label
    ax.set_xlabel("Trial #")
    # Set y bounds to 0-1100
    ax.set_ylim([0, 5])
    # Create a matplotlib / tkinter canvas object
    canvas = FigureCanvasTkAgg(fig, master=scoreLevel)
    # Render the canvas
    canvas.draw()
    # place on tkinter gui
    canvas._tkcanvas.place(relx = 0.02, rely = 0.03, relwidth = 1, relheight = 0.70)
    toolbar = NavigationToolbar2Tk(canvas, scoreLevel)
    toolbar.update()
    # Plot the data
    line, = ax.plot(sessionVelocitiesX, sessionTimesAngle, color = "red", label = "EMG Value (V)")


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