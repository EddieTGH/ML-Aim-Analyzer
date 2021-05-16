import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pyrebase


def makeRegression(email):
    config = {
        "apiKey": "AIzaSyA19RqsNimyy0H9vEXPvtt-IKUR37ZXUSU",
        "authDomain": "warmuptestervalorant.firebaseapp.com",
        "databaseURL": "https://warmuptestervalorant-default-rtdb.firebaseio.com",
        "storageBucket": "warmuptestervalorant.appspot.com"
    }
    firebaseref = pyrebase.initialize_app(config)
    db = firebaseref.database()

    VelocityJsonData = dict(db.child("Users").child(email).child("Velocity_Data").get().val())
    VelocityX = list(VelocityJsonData.keys())
    VelocityY = list(VelocityJsonData.values())
    