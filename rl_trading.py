'''reinforcement learning for trading '''



'''
States - 
 - Up 1
 - Down 1
 - Flat

 -Cost to move is fee
 -Gain is value from holding
 -Try to maximize what to Do

 R(s) = (total reward we got in state s) / (#times we visited state s)
 P(s, a, s') = (#times we took action a in state s and we went to s') / (#times we took action a in state s)



'''

from sklearn import preprocessing, cross_validation, svm
from sklearn.cross_validation import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from pandas import *
import pandas as pd
import numpy as np
from numpy import array
import pickle, math, warnings
from operator import itemgetter, attrgetter, methodcaller

Hold_time = (1,5,10,30,60,120,240,480)

directory ='C:\\Code\\btc\\Trader\\Data\\'
'''
classified = 'gdax_60_fmt' +'.csv'
df = pd.DataFrame.from_csv(directory + classified)
df['time'] = pd.to_datetime(df['time'])
df = df.sort(['time'])
df = df.tail(50000)
df['price'] = (df.low + df.high)/2
df['pdelta'] = df.price - df.price.shift(1)
for i in Hold_time:
	n1 = 'take'+ str(i)
	n2 = 'prof'+ str(i)
	n3 = 'vol' + str(i)
	n4 = 'ma' + str(i)
	n5 = 'ma_diff' + str(i)
	n6 = 'volume' + str(i)
	df[n1] = df.price.shift(-i)-df.price -df.price*.005
	df[n2] = df.apply(lambda x : 1 if  x[n1] > 1 else 0,axis = 1)
	df[n3] = pd.rolling_std(df['pdelta'],i)**2
	df[n4] = pd.Series(df.price).rolling(window=i).mean()
	df[n5] = df.price -df[n4]
	df[n6] = pd.Series(df.Volume).rolling(window=i).mean()
df['ma'] = pd.rolling_mean(df.price,5)
df['ma_diff'] = df.price -df['ma']
df['volatility']=pd.rolling_std(df['pdelta'],20)**2
df['uband']=df['ma'] + pd.rolling_std(df.price,20)
df['bband']=df['ma'] - pd.rolling_std(df.price,20)
df['u_take']=df.apply(lambda x : 1 if  x['uband'] < x['price'] else 0,axis = 1)
df['b_take']=df.apply(lambda x : 1 if  x['bband'] > x['price'] else 0,axis = 1)
df.to_csv(directory + '_rl_'+classified)
'''
reward = 'take1'
gamma = 0.999 '''this is the decay factor for rewards'''
actions = ['buy','sell','hold']
iterations = 1000 '''how many rows to test (just to keep it do-able)'''

classified = '_rl_gdax_60_fmt.csv'
df = pd.DataFrame.from_csv(directory + classified)
df.dropna()
features = ['volatility','ma_diff','pdelta','u_take','b_take','volume']
for i in Hold_time:
	n1 = 'take'+ str(i)
	n2 = 'prof'+ str(i)
	n3 = 'vol' + str(i)
	n4 = 'ma' + str(i)
	n5 = 'ma_diff' + str(i)
	n6 = 'volume' + str(i)
	features.extend([n3,n4,n5,n6])
cols = np.array(features)
df2=df[cols]
MDP = np.array(df2)
R = np.array(df2[reward])



def play(policyPlayerFn, initialState=None, initialAction=None):
	choice = np.random.choice(range(0,len(df2)-1) '''each row is individual (MDP), picks random number'''
	initialAction = np.random.choice(actions)
	intialState = MDP[choice]

def monteCarloES(nEpisodes):
    sumOfImportanceRatio = [0]
    sumOfRewards = [0]
    for i in range(0, nEpisodes):
        _, reward, playerTrajectory = play(behaviorPolicyPlayer, initialState=initialState)

        # get the importance ratio
        importanceRatioAbove = 1.0
        importanceRatioBelow = 1.0
        for action, (usableAce, playerSum, dealerCard) in playerTrajectory:
            if action == targetPolicyPlayer(usableAce, playerSum, dealerCard):
                importanceRatioBelow *= 0.5
            else:
                importanceRatioAbove = 0.0
                break
        importanceRatio = importanceRatioAbove / importanceRatioBelow
        sumOfImportanceRatio.append(sumOfImportanceRatio[-1] + importanceRatio)
        sumOfRewards.append(sumOfRewards[-1] + reward * importanceRatio)
    del sumOfImportanceRatio[0]
    del sumOfRewards[0]


    sumOfRewards= np.asarray(sumOfRewards)
    sumOfImportanceRatio= np.asarray(sumOfImportanceRatio)