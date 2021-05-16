import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pyrebase
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

def sendToDB(email, MicroScore, MacroScore, AngleScore, KDA, Feeling):
    config = {
        "apiKey": "AIzaSyA19RqsNimyy0H9vEXPvtt-IKUR37ZXUSU",
        "authDomain": "warmuptestervalorant.firebaseapp.com",
        "databaseURL": "https://warmuptestervalorant-default-rtdb.firebaseio.com",
        "storageBucket": "warmuptestervalorant.appspot.com"
    }
    firebaseref = pyrebase.initialize_app(config)
    db = firebaseref.database()
    today = datetime.today()
    datem = str(today.replace(microsecond=0))
    db.child("Users").child(email).child("Sessions").child(datem).child("Micro").set({
        "Score": MicroScore,
        "KDA": KDA,
        "Feeling": Feeling
    })
    db.child("Users").child(email).child("Sessions").child(datem).child("Macro").set({
        "Score": MacroScore,
        "KDA": KDA,
        "Feeling": Feeling
    })
    db.child("Users").child(email).child("Sessions").child(datem).child("Angle").set({
        "Score": AngleScore,
        "KDA": KDA,
        "Feeling": Feeling
    })

def getMLOutput(email, microScore, macroScore, angleScore):
    config = {
        "apiKey": "AIzaSyA19RqsNimyy0H9vEXPvtt-IKUR37ZXUSU",
        "authDomain": "warmuptestervalorant.firebaseapp.com",
        "databaseURL": "https://warmuptestervalorant-default-rtdb.firebaseio.com",
        "storageBucket": "warmuptestervalorant.appspot.com"
    }
    firebaseref = pyrebase.initialize_app(config)
    db = firebaseref.database()

    SessionDict = dict(db.child("Users").child(email).child("Sessions").get().val())
    Scores = []
    KDAs = []
    Feelings =[]
    for i in SessionDict:
        Session = SessionDict[i]
        sumOfScores = 0
        KDAs.append(SessionDict[i]["Macro"]["KDA"])
        Feelings.append(SessionDict[i]["Macro"]['Feeling'])
        for j in Session:
            sumOfScores += Session[j]["Score"]
        Scores.append(sumOfScores / 3)
    


    def reshape(data):
        return np.array(data).reshape(-1, 1)
    
    scoresInput = reshape(Scores)
    KDAInput = reshape(KDAs)

    reg = LinearRegression()
    reg.fit(scoresInput, KDAInput)

    m = reg.coef_
    print(m)
    b = reg.intercept_
    print(b)

    priceTest = np.array([0,max(Scores)])
    predictions = m * priceTest + b

    return m[0][0] * ((microScore + macroScore + angleScore) / 3) + b[0]

    """SessionDict:
        DateTime1
            Micro
            Macro
            Angle
        DateTime2
            Micro
            Macro
            Angle
    """

    """ x = avg 3 scores 
    y = KDA

    x = avg 3 accuracies
    y = KDA

    x = avg 3 scores 
    y = how they feel

    x = avg 3 accuracies 
    y = how they feel """
 
    
