import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pyrebase
from datetime import datetime


def sendToDB(email, MicroScore, MicroAcc, MacroScore, MacroAcc, AngleScore, AngleAcc, KDA, Feeling):
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
        "Accuracy": MicroAcc,
        "KDA": KDA,
        "Feeling": Feeling
    })
    db.child("Users").child(email).child("Sessions").child(datem).child("Macro").set({
        "Score": MacroScore,
        "Accuracy": MacroAcc,
        "KDA": KDA,
        "Feeling": Feeling
    })
    db.child("Users").child(email).child("Sessions").child(datem).child("Angle").set({
        "Score": AngleScore,
        "Accuracy": AngleAcc,
        "KDA": KDA,
        "Feeling": Feeling
    })

def getMLOutput(email):
    config = {
        "apiKey": "AIzaSyA19RqsNimyy0H9vEXPvtt-IKUR37ZXUSU",
        "authDomain": "warmuptestervalorant.firebaseapp.com",
        "databaseURL": "https://warmuptestervalorant-default-rtdb.firebaseio.com",
        "storageBucket": "warmuptestervalorant.appspot.com"
    }
    firebaseref = pyrebase.initialize_app(config)
    db = firebaseref.database()