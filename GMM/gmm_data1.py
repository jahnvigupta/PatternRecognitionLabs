# -*- coding: utf-8 -*-
"""GMM_data1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1HURgFQigPv9vz2-apiv60TNaQiTA1Q0z
"""

#importing required libraries
import warnings
warnings.simplefilter("ignore")
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal as mvn
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split

#Function to read data on given path into a dataframe
def read_data(file_path):
  data = pd.read_csv(file_path, sep=',', header=None)
  #Make list of empty columns
  empty_cols = [col for col in data.columns if data[col].isnull().all()]
  # Drop these columns from the dataframe
  data.drop(empty_cols, axis=1, inplace=True) 
  #Return dataframe
  return data

def loss_function(data, means, sigmas, pi):
  loss = 0
  for i in range(len(data)):
    temp = 0
    for j in range(n_clusters):
      temp = temp + pi[j]*mvn.pdf(data.iloc[i], means[j], sigmas[j])
    loss = loss+np.log(temp)
  return loss

def init_GMM(data, n_clusters):

  dim = len(data.columns)
  means = np.zeros((n_clusters, dim))
  sigmas = np.zeros((n_clusters, dim, dim))
  pi = np.zeros(n_clusters)
  
  kmeans = KMeans(init="random", n_clusters=n_clusters, max_iter=300)
  kmeans.fit(data)
  predictions = kmeans.predict(data)

  for i in range(n_clusters):
    means[i] = data.iloc[np.where(predictions==i)].mean()
    idx = np.where(predictions==i)
    x = data.iloc[idx] - means[i]
    sigmas[i,:, :] = np.dot((x).T, (x)) / len(idx)
    pi[i] = len(data.iloc[np.where(predictions==i)])/len(data)
  return means, sigmas, pi

def e_step(data, means, sigmas, pi):
  n_clusters = len(means)
  gamma = np.zeros((len(data),n_clusters))
  for i in range(n_clusters):
    sum = 0
    for j in range(len(data)):
      gamma[j][i] = pi[i]*mvn.pdf(data.iloc[j], means[i], sigmas[i])
      sum = sum+gamma[j][i]
    gamma[:,i] = gamma[:,i]/sum
  return gamma

def m_step(data, gamma, means, sigmas, pi):
  n_clusters = len(means)
  for i in range(n_clusters):
    nk = np.sum(gamma[:,i])
    pi[i] = nk/len(data)
    means[i] = (1/nk)*(np.dot(gamma[:,i].T,data.iloc[:]))
    
    temp = np.matrix(np.array(data) - means[i, :])
    sigmas[i] = temp.T * np.diag(gamma[:,i]) * temp

  return means, sigmas, pi

def gmm(n_clusters, data, iters):
  means, sigmas, pi = init_GMM(data, n_clusters)
  cost = loss_function(data, means, sigmas, pi)
  cost_prev = 0
  iter = 0
  while(abs(cost-cost_prev)>0.00001 and iter<iters):
    cost_prev = cost
    gamma = e_step(data, means, sigmas, pi)
    means, sigmas, pi = m_step(data, gamma, means, sigmas, pi)
    cost = loss_function(data, means, sigmas, pi)
    iter = iter+1
  return means, sigmas, pi

def predict(means1, sigmas1, pi1, means2, sigmas2, pi2, x):
  p1 = 0
  p2 = 0
  for i in range(2):
    p1 = p1+pi1[i]*mvn.pdf(x, means1[i], sigmas1[i])
    
  for i in range(2):
    p2 = p2+pi2[i]*mvn.pdf(x, means2[i], sigmas2[i])  

  if(p1>p2):
    return 0
  else:
    return 1

if __name__ == '__main__':
  df1 = read_data("Class1.txt")
  df2 = read_data("Class2.txt")
  
  df1_train, df1_test = train_test_split(df1, test_size=0.33, random_state=42)
  df2_train, df2_test = train_test_split(df2, test_size=0.33, random_state=42)

  plt.figure()
  plt.scatter(df1_train[[0]],df1_train[[1]],label="Class1")
  plt.scatter(df2_train[[0]],df2_train[[1]],label="Class2")
  plt.title("Original Distribution of training data")

  plt.figure()
  plt.scatter(df1_test[[0]],df1_test[[1]],label="Class1")
  plt.scatter(df2_test[[0]],df2_test[[1]],label="Class2")
  plt.title("Original Distribution of test data")

  n_clusters = 2
  iters = 200

  means1, sigmas1, pi1 = gmm(n_clusters, df1_train, iters)
  means2, sigmas2, pi2 = gmm(n_clusters, df2_train, iters)

  plt.figure()
  plt.scatter(df2_train[[0]],df2_train[[1]],label="Class1")
  plt.scatter(means2[0][0],means2[0][1])
  plt.scatter(means2[1][0],means2[1][1])

  accuracy = 0
  for i in range(len(df1_test)):
    x = np.array(df1_test.iloc[i])
    if(predict(means1, sigmas1, pi1, means2, sigmas2, pi2, x)==0):
      accuracy = accuracy+1

  for i in range(len(df2_test)):
    x = np.array(df2_test.iloc[i])
    if(predict(means1, sigmas1, pi1, means2, sigmas2, pi2, x)==1):
      accuracy = accuracy+1
  accuracy = accuracy/(len(df1_test)+len(df2_test))
  print("Accuracy on test data is : ",accuracy)