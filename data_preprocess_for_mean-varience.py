import numpy as np
import pandas as pd
import os
import datetime

def realizedVolatility(series): # 计算波动率
    series = series.set_index('date')
    resampled = series.resample('W').last().ffill()
    resampled['log_ret'] = np.log(resampled['adjust_net_value']/resampled['adjust_net_value'].shift(1))
    vola = resampled['log_ret'].std()*np.sqrt(52)
    return vola

STANDPOINT = pd.datetime.today()
instruments = pd.read_csv(r'D:\Deecamp数据\instruments.csv')
instruments.drop(columns={'advisor','trustee'}, inplace=True)
instruments['revenue'] = 0
instruments['volatility'] = 0

path = r'D:/Deecamp数据/nav/nav/'
files = os.listdir(path)
for f in files:
    ints = os.listdir(path+f)
    for i in ints:
        code = i[:9]
        print("\r Now at "+code, end="")
        infos = instruments.loc[instruments['code']==code].iloc[0]
        if not pd.isnull(infos['delist_date']): # 该基金已经delist，不再考虑
            continue
        nav = pd.read_csv(path+f+'/'+i, parse_dates=['date'])
        if nav.iloc[-1]['date'] - nav['date'][0]<datetime.timedelta(days=365): # 上市不足一年，从起售起算
            revenue = nav.iloc[-1]['adjust_net_value']/nav.iloc[0]['adjust_net_value']-1
            series = nav[['date','adjust_net_value']]
        else: # 寻找一年前的时间点
            revenue = nav.iloc[-1]['adjust_net_value']/nav.loc[nav['date']>=nav.iloc[-1]['date']-datetime.timedelta(days=365)].iloc[0]['adjust_net_value']-1
            series = nav.loc[nav['date']>=nav.iloc[-1]['date']-datetime.timedelta(days=365)][['date','adjust_net_value']]
        instruments.loc[instruments['code']==code,'revenue'] = revenue
        instruments.loc[instruments['code']==code,'volatility'] = realizedVolatility(series)

instruments['list_date'] = pd.to_datetime(instruments['list_date'])
# 基金过滤
instruments.drop(index=instruments.loc[instruments['operate_mode']!='开放式基金'].index, inplace=True) #不买封闭式
instruments = instruments.loc[pd.isnull(instruments['delist_date'])] #不买中止发行的
instruments.drop(index=instruments.loc[instruments['list_date']>STANDPOINT-datetime.timedelta(days=365)].index, inplace=True) #不买发行不到一年的
instruments.drop(index=instruments.loc[instruments['revenue']>2].index, inplace=True) # 不买收益率高于2的狗屎运
instruments.drop(index=instruments.loc[instruments['volatility']==0].index, inplace=True) # 波动率为0的认为是净值数据缺失

# 做一个简单的基金挑选
high_revenue = set(instruments.groupby(['underlying_asset_type']).apply(lambda x:x.sort_values('revenue', ascending=False).head(5))['code']) #每一类基金收益高的
low_volatility = set(instruments.groupby(['underlying_asset_type']).apply(lambda x:x.sort_values('volatility', ascending=False).head(5))['code']) #每一类基金风险小的
selected_funds = high_revenue|low_volatility #求个并集

# 构造对数收益率序列矩阵
rets = pd.DataFrame()
for sf in selected_funds:
    nav = pd.read_csv(path+sf[4:6]+'/'+sf+'.csv', parse_dates=['date'])
    series = nav.loc[nav['date']>=nav.iloc[-1]['date']-datetime.timedelta(days=365)][['date','adjust_net_value']]
    series = series.set_index('date').resample('W').last().ffill()
    series['log_ret'] = np.log(series['adjust_net_value']/series['adjust_net_value'].shift(1))
    rets[sf] = series['log_ret']
rets.drop(index=rets.index[0],inplace=True)
rets.fillna(method='bfill',inplace=True)

covs = np.array(rets.cov())
means = np.array(rets.mean())
