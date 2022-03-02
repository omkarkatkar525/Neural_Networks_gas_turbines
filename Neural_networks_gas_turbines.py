# -*- coding: utf-8 -*-
"""Assignment_16_(Neural Networks)_gas_turbines.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EBc4dlfwzWZ8shY7kr55M53eJmqjdO-O
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split,GridSearchCV,KFold
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
import seaborn as sns
import matplotlib.pyplot as plt

turbine_data = pd.read_csv('/content/gas_turbines.csv')
turbine_data

turbine_data.isna().sum()

turbine_data.dtypes

correlation =turbine_data.corr()

plt.figure(figsize=(12,10))
sns.heatmap(correlation,annot=True)
plt.show()

"""## Feature Selection by using Mutual Information Feature Selection"""

from sklearn.feature_selection import SelectKBest,mutual_info_regression

X=turbine_data.drop(columns='TEY')
y=turbine_data.loc[:,['TEY']]

X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.2, random_state=5)

def select_features(X_train, y_train, X_test):
    fs = SelectKBest(score_func=mutual_info_regression, k='all')
    fs.fit(X_train, y_train)
    X_train_fs = fs.transform(X_train)
    X_test_fs = fs.transform(X_test)
    return X_train_fs, X_test_fs, fs

X_train_fs, X_test_fs, fs = select_features(X_train, y_train, X_test)

for i in range(len(fs.scores_)):
    print('Feature %d: %f' % (i, fs.scores_[i]))
fig, ax = plt.subplots(figsize=(10, 6))
plt.bar([i for i in range(len(fs.scores_))], fs.scores_)
plt.show()

X=turbine_data.drop(columns=['TEY','AT','AP','AH','CO','NOX'])
X

stand_scale=StandardScaler()

stand_X=stand_scale.fit_transform(X)
stand_X=pd.DataFrame(stand_X,columns=list(X.columns.values))
stand_X

X=stand_X

stand_y=stand_scale.fit_transform(y)
stand_y=pd.DataFrame(stand_y,columns=list(y.columns.values))
stand_y

y=stand_y

X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.3, random_state=1)
X_train.shape, X_test.shape, y_train.shape, y_test.shape

model=Sequential()
model.add(Dense(10, input_dim=5,kernel_initializer='he_uniform', activation='tanh'))
model.add(Dense(6, kernel_initializer='he_uniform', activation='tanh'))
model.add(Dense(1, kernel_initializer='he_uniform', activation='linear'))

model.compile(loss='mean_squared_error',optimizer='adam',metrics=['mse'])

model.fit(X_train,y_train, epochs=100, batch_size=40)

model.evaluate(X_test,y_test)

"""## Tuning of Hyperparameters:- Activation Function and Kernel Initializer"""

import tensorflow.keras.optimizers
from keras.layers import Dropout
from keras.optimizers import adam_v2

X = X.iloc[0:500,:]

y = y.iloc[0:500]

X_train_1, X_test_1, y_train_1, y_test_1 = train_test_split(X,y, test_size=0.3, random_state=1)
X_train_1.shape, X_test_1.shape, y_train_1.shape, y_test_1.shape



def create_model(learning_rate,dropout_rate,activation_function,init,neuron1,neuron2):
    model = Sequential()
    model.add(Dense(neuron1,input_dim = 5,kernel_initializer = init,activation = activation_function))
    model.add(Dropout(dropout_rate))
    model.add(Dense(neuron2,input_dim = neuron1,kernel_initializer = init,activation = activation_function))
    model.add(Dropout(dropout_rate))
    model.add(Dense(1,activation = 'linear'))
    
    adam=adam_v2.Adam(learning_rate = learning_rate)
    model.compile(loss = 'mean_squared_error',optimizer = adam,metrics = ['mse'])
    return model

# Create the model

model = KerasRegressor(build_fn = create_model,verbose = 0)

# Define the grid search parameters

batch_size = [20,40]
epochs = [50,100]
learning_rate = [0.01,0.1]
dropout_rate = [0.1,0.2]
activation_function = ['relu','linear']
init = ['uniform','normal']
neuron1 = [4,8]
neuron2 = [2,4]

# Make a dictionary of the grid search parameters

param_grids = dict(batch_size = batch_size,epochs = epochs,learning_rate = learning_rate,dropout_rate = dropout_rate,
                   activation_function = activation_function,init = init,neuron1 = neuron1,neuron2 = neuron2)

# Build and fit the GridSearchCV

grid = GridSearchCV(estimator = model,param_grid = param_grids,cv = KFold(),verbose = 10, scoring='neg_mean_squared_error')
grid_result = grid.fit(X_train_1, y_train_1)

# Summarize the results
print('Best : {}, using {}'.format(grid_result.best_score_,grid_result.best_params_))

"""## Applying best parameters values to the final model"""

final_model = Sequential()
final_model.add(Dense(4,input_dim = 5,kernel_initializer = 'uniform',activation = 'linear'))
final_model.add(Dense(2,input_dim = 4,kernel_initializer = 'uniform',activation = 'linear'))
final_model.add(Dense(1,activation = 'linear'))

final_model.compile(loss='mean_squared_error',optimizer='adam',metrics=['mse'])

final_model.fit(X_train,y_train, epochs=100, batch_size=20)

final_model.evaluate(X_test,y_test)

