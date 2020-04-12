import pandas as pd
import quandl, math, datetime
import numpy as np
import pandas as pd
from sklearn import preprocessing, svm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_validate
from sklearn import model_selection
import matplotlib.pyplot as plt
from matplotlib import style
import pickle

style.use('ggplot')

quandl.ApiConfig.api_key = "cywTtNArctgR6VxJTBZN"

df = quandl.get("WIKI/GOOGL")
df = df[['Adj. Open',  'Adj. High',  'Adj. Low',  'Adj. Close', 'Adj. Volume']]
df['HL_PCT'] = (df['Adj. High'] - df['Adj. Low']) / df['Adj. Low'] * 100.
df['PCT_change'] = (df['Adj. Close'] - df['Adj. Open']) / df['Adj. Open'] * 100.0

df = df[['Adj. Close', 'HL_PCT', 'PCT_change', 'Adj. Volume']]

print(df.tail())


forecast_col = 'Adj. Close'
df.fillna(-99999, inplace=True)

# predict 10% of the dataframe
forecast_out = int(math.ceil(0.1*len(df)))
#print(forecast_out)

df['label'] = df[forecast_col].shift(-forecast_out)


# features - dropping everything but label from df
x = np.array(df.drop(['label'],1))
x = preprocessing.scale(x)
x_lately = x[-forecast_out:]
x = x[:-forecast_out]

df.dropna(inplace=True)
# label
y = np.array(df['label'])

# splits data into training and testing data
x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, test_size=0.2)

# clf = LinearRegression(n_jobs=-1)
# clf.fit(x_train, y_train)
# with open('linearregression.pickle','wb') as f:
#     pickle.dump(clf, f)

pickle_in = open('linearregression.pickle', 'rb')
clf = pickle.load(pickle_in)


accuracy = clf.score(x_test,y_test)
forecast_set = clf.predict(x_lately)
#print(forecast_set, accuracy, forecast_out)

df['Forecast'] = np.nan

#can be simplified: get latest day and add new days, and adding dates to axis
last_date = df.iloc[-1].name
last_unix = last_date.timestamp()
one_day = 86400
next_unix = last_unix + one_day

for i in forecast_set:
    next_date = datetime.datetime.fromtimestamp(next_unix)
    next_unix += one_day
    df.loc[next_date] = [np.nan for _ in range(len(df.columns) - 1)] + [i]

print(df.tail())

df['Adj. Close'].plot()
df['Forecast'].plot()
plt.legend(loc=4)
plt.xlabel('Date')
plt.ylabel('Price')
plt.show(block=True)