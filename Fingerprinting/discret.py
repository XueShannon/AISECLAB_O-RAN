#!/usr/bin/env python
# coding: utf-8

# In[3]:


#import sys
#if sys.maxunicode > 65535:
 #  print('wide-unicode')
#else:
#        print('narrow unicode')


# In[1]:


#import matlab.engine
#eng = matlab.engine.start_matlab()


# In[1]:


#get_ipython().run_line_magic('matplotlib', 'inline')
#from IPython.core.interactiveshell import InteractiveShell
#InteractiveShell.ast_node_interactivity = "all"
import scipy.io as sio
import numpy as np
from keras.utils import np_utils


# In[2]:


TempList = []
split_size=20
for i in range(14):
    data = sio.loadmat('./ChangedHometest2/Card'+str(i+1)+'.mat')
    #data = sio.loadmat('./mov_series_aug24/NIC'+str(i+1)+'.mat')
    data = data['Diff'].T
    data = data[:,0:80000]
    #np.split(data,10)
    print(data.shape)
    np.random.shuffle(data)
    data = np.reshape(data,(-1,split_size,3))
    TempList.append(data)
x = np.concatenate(TempList,0)
print(x.shape)


# In[3]:


from scipy import stats
data = []
for i in range(len(x)):
    temp = x[i]
    _,_,mean,var,skew,kur = stats.describe(temp)
    data.append(np.concatenate([mean,var,skew,kur],0))
print(data[0:10])


# In[4]:


data = np.asarray(data)
print(data.shape)
print(data[0:5])


# In[5]:


sample_size = int(len(data)/14)
y = []
for i in range(14):
    y.append([i]*sample_size)
y = np.asarray(y)
y=y.flatten()
y = np_utils.to_categorical(y, 14)
print(y[4000])
print(y.shape)
x= data
print(x.shape)


# In[6]:


from sklearn import preprocessing
x = preprocessing.scale(x)
print(x[0:5])


# In[7]:


from keras.models import Sequential
from keras.layers import Dense

model = Sequential()
model.add(Dense(14, input_shape=(12,),activation="relu"))
model.add(Dense(20,activation="relu"))
model.add(Dense(30,activation="relu"))
model.add(Dense(20,activation="relu"))
model.add(Dense(2,activation="softmax"))
model.add(Dense(20,activation="softmax"))
model.add(Dense(14,activation="softmax"))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['categorical_accuracy'],)
model.summary()


# In[8]:


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.15)
print("X_train original shape", X_train.shape)
print("y_train original shape", y_train.shape)
print("X_test original shape", X_test.shape)
print("y_test original shape", y_test.shape)


# In[9]:


history = model.fit(X_train, y_train, batch_size=128, nb_epoch=50,validation_data=(X_test, y_test))


# In[15]:


import matplotlib.pyplot as plt
history_dict = history.history

loss_values = history_dict['categorical_accuracy']
val_loss_values = history_dict['val_categorical_accuracy']
epochs = range(1,len(history_dict['categorical_accuracy'])+1)
plt.rcParams.update({'font.size': 16})
plt.figure(figsize=(10,10))
plt.plot(epochs, loss_values, 'b^-', label='Training acc')
plt.plot(epochs, val_loss_values, 'rs-', label='Validation acc')
plt.title('Training and validation loss: mobile',size=30)
plt.xlabel('Epochs',size=30)
plt.ylabel('Accuracy',size=30)
plt.legend(fontsize = 30 )
plt.savefig("./res_1.pdf", bbox_inches='tight', pad_inches=0)
plt.show();

score = model.evaluate(X_test, y_test)
print(score)
print('Test accuracy: ', score[1])


# In[ ]:





# In[11]:


predb = model.predict_classes(X_test)
y_test = y_test.argmax(axis=-1)
print(predb)
print(y_test)
indices = []
for i in range(len(y_test)):
    if y_test[i] != predb[i]:
        indices.append(i)
count = np.zeros((14,14),dtype=int)
for i in indices:
    count[y_test[i]][predb[i]] = count[y_test[i]][predb[i]]+1
print(count)


# In[12]:


print(len(indices)/len(predb))


# In[ ]:




