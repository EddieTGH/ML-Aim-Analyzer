import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

filepath = "USA_cars_datasets.csv"

price = pd.read_csv(filepath, usecols = ['price'], squeeze = True)
mileage = pd.read_csv(filepath, usecols = ['mileage'], squeeze = True)

print(price)
print(mileage)


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

price_train, price_testing, mil_train, mil_testing = train_test_split(price, mileage, test_size = 0.33, random_state = 42)

def reshape(data):
    return np.array(data).reshape(-1, 1)

priceInput = reshape(price_train)
mileageInput = reshape(mil_train)

reg = LinearRegression()
reg.fit(priceInput, mileageInput)

import matplotlib.pyplot as plt

plt.scatter(price_testing, mil_testing)

m = reg.coef_
b = reg.intercept_

priceTest = np.array([0,70000])
predictions = m * priceTest + b

plt.plot(priceTest, predictions[0], 'r')
plt.show()