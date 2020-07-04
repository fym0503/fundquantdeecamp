import numpy as np
import pandas as pd
import os
import re
from sklearn.cluster import KMeans

STANDPOINT = pd.to_datetime('2019-03-31') # 考察时点

# 先找出所有基金，和被持有的股
path = 'D:/Deecamp数据/holding_stocks/holding_stocks/'
holdings = set()
funds = []
files = os.listdir(path)
for f in files:
    ints = os.listdir(path+f)
    for i in ints:
        print("\r Now: "+i[:9], end="")
        hs = pd.read_csv(path+f+'/'+i, parse_dates=['period_start','period_end','pub_date'])
        hs['symbol'] = hs['symbol'].astype(str)
        hs['China'] = hs['symbol'].apply(lambda x:re.search('\D',x) is None)
        holdings = holdings|set(hs.drop(index=hs.loc[hs['China']==False].index)['symbol'].to_list())
        funds.append(i[:9])
holdings = list(set(map(int,holdings)))
holdings.sort()

# 构造矩阵，在STANDPOINT时间点的持股情况
matrix = pd.DataFrame(columns=holdings)
for f in funds:
    print("\r Now: "+f, end="")
    hs = pd.read_csv(path+f[4:6]+'/'+f+'.csv', parse_dates=['period_start','period_end','pub_date'])
    hs['symbol'] = hs['symbol'].astype(str)
    hs['China'] = hs['symbol'].apply(lambda x:re.search('\D',x) is None)
    hs.drop(index=hs.loc[hs['China']==False].index, inplace=True)
    hs['symbol'] = hs['symbol'].astype(int)
    res = hs.loc[(hs['period_start']<=STANDPOINT) & (hs['period_end']>=STANDPOINT)][['symbol','proportion']].groupby(['symbol']).max()
    matrix = matrix.append(res.to_dict()['proportion'], ignore_index=True)
matrix.index = funds

matrix.fillna(0,inplace=True)

N_CLUSTERS = 20 # 聚类数量
cluster = KMeans(n_clusters=N_CLUSTERS,random_state=0).fit(matrix)
cluster = model.predict(matrix)
cluster_result = pd.DataFrame(cluster, index=matrix.index, columns=['cluster'])