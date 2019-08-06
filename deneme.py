import numpy as np
import pandas as pd
from pandas import Series,DataFrame
import datetime
import statsmodels.api as sm
import matplotlib.pyplot as pt
from sklearn import linear_model
import math

fastPercentage = 50 # 50% of the total sales -  fast items
mediumPercentage = 30 # 30% of the total amounts - medium items
slowPercentage = 20 # 20% of the total amounts - slow items

assign1raw = pd.read_csv('assignment4.1a.csv')
withInterval = DataFrame(assign1raw, columns=['Date', 'StoreCode', 'ProductCode', 'SalesQuantity', 'Week', 'Promotion'])
withInterval['Date'] = withInterval['Date'].astype('datetime64[ns]')
withInterval['Week'] = withInterval['Date'].dt.week

promraw = pd.read_csv('PromotionDates.csv')
promotions = DataFrame(promraw, columns=['Period', 'StartDate', 'EndDate', 'StartWeek', 'EndWeek', 'Duration'])
promotions['StartDate'] = promotions['StartDate'].astype('datetime64[ns]')
promotions['EndDate'] = promotions['EndDate'].astype('datetime64[ns]')
promotions['Duration'] = (promotions['EndDate'] - promotions['StartDate'])
promotions = promotions.drop(promotions.index[4:6]) # using the first 4 promotions

for index1, row1 in promotions.iterrows():
    withInterval.loc[(withInterval['Date'].isin(pd.date_range(row1['StartDate'],row1['EndDate']))), 'Promotion'] = row1['Period']
withInterval.loc[(pd.isnull(withInterval['Promotion'])), 'Promotion'] = 'non-Prom'
nonProm = withInterval.loc[withInterval['Promotion'] == 'non-Prom']
promotional = withInterval.loc[withInterval['Promotion'] != 'non-Prom']

promoWeeks =  len((withInterval.loc[withInterval['Promotion'] != 'non-Prom']).Date.value_counts().index) / 7
nonPromoWeeks = len((withInterval.loc[withInterval['Promotion'] == 'non-Prom']).Date.value_counts().index) / 7

# weekly sales amounts
wProd=nonProm.groupby(['Week','ProductCode']).agg({'SalesQuantity':sum})
wProd=wProd.sort_values(by=['SalesQuantity'], ascending=[False])
wStore=nonProm.groupby(['Week','StoreCode']).agg({'SalesQuantity':sum})
wStore=wStore.sort_values(by=['SalesQuantity'], ascending=[False])
wProdPerStore=nonProm.groupby(['Week','StoreCode', 'ProductCode']).agg({'SalesQuantity':sum})
wProdPerStore=wProdPerStore.sort_values(by=['Week','SalesQuantity'], ascending=[True, False])

# total sales amounts for non-promotion
tProd=nonProm.groupby(['ProductCode']).agg({'SalesQuantity':sum})
tProd=tProd.sort_values(by=['SalesQuantity'], ascending=[False])
tProd['Per'] = 100*tProd.SalesQuantity/tProd.SalesQuantity.sum()
tProd['CumSum'] = tProd.SalesQuantity.cumsum()
tProd['CumPer'] = 100*tProd.CumSum/tProd.SalesQuantity.sum()

tStore=nonProm.groupby(['StoreCode']).agg({'SalesQuantity':sum})
tStore=tStore.sort_values(by=['SalesQuantity'], ascending=[False])
tStore['Per'] = 100*tStore.SalesQuantity/tStore.SalesQuantity.sum()
tStore['CumSum'] = tStore.SalesQuantity.cumsum()
tStore['CumPer'] = 100*tStore.CumSum/tStore.SalesQuantity.sum()

tProdPerStore=nonProm.groupby(['StoreCode', 'ProductCode']).agg({'SalesQuantity':sum})
tProdPerStore=tProdPerStore.sort_values(by=['SalesQuantity'], ascending=[False])
tProdPerStore['Per'] = 100*tProdPerStore.SalesQuantity/tStore.SalesQuantity.sum()
tProdPerStore['CumSum'] = tProdPerStore.SalesQuantity.cumsum()
tProdPerStore['CumPer'] = 100*tProdPerStore.CumSum/tProdPerStore.SalesQuantity.sum()

# total sales amounts during promotion periods
promProd=promotional.groupby(['ProductCode']).agg({'SalesQuantity':sum})
promProd=promProd.sort_values(by=['SalesQuantity'], ascending=[False])
promProd['Per'] = 100*promProd.SalesQuantity/promProd.SalesQuantity.sum()
promProd['CumSum'] = promProd.SalesQuantity.cumsum()
promProd['CumPer'] = 100*promProd.CumSum/promProd.SalesQuantity.sum()

promStore=promotional.groupby(['StoreCode']).agg({'SalesQuantity':sum})
promStore=promStore.sort_values(by=['SalesQuantity'], ascending=[False])
promStore['Per'] = 100*promStore.SalesQuantity/promStore.SalesQuantity.sum()
promStore['CumSum'] = promStore.SalesQuantity.cumsum()
promStore['CumPer'] = 100*promStore.CumSum/promStore.SalesQuantity.sum()

gPromProdPerStore=promotional.groupby(['StoreCode', 'ProductCode']).agg({'SalesQuantity':sum})
gPromProdPerStore=gPromProdPerStore.sort_values(by=['SalesQuantity'], ascending=[False])
gPromProdPerStore['Per'] = 100*gPromProdPerStore.SalesQuantity/gPromProdPerStore.SalesQuantity.sum()
gPromProdPerStore['CumSum'] = gPromProdPerStore.SalesQuantity.cumsum()
gPromProdPerStore['CumPer'] = 100*gPromProdPerStore.CumSum/gPromProdPerStore.SalesQuantity.sum()

#  products sales amounts per store during promotions
ppp=promotional.groupby(['StoreCode', 'ProductCode']).agg({'SalesQuantity':sum})
ppp1=promotional.groupby(['StoreCode']).agg({'SalesQuantity':sum})
ppp1.columns = ['StoreSales']
promProdPerStore=ppp.join(ppp1.set_index(ppp1.index), on='StoreCode')
promProdPerStore=promProdPerStore.sort_values(by=['StoreCode','SalesQuantity'], ascending=[True,False])
promProdPerStore['Per'] = 100*promProdPerStore.SalesQuantity/promProdPerStore.StoreSales
promProdPerStore['CumPer'] = promProdPerStore.Per.groupby(['StoreCode']).cumsum()

#  cumulative'de yukarıdaki yüzdeleri alarak itemlerı bul non promo promo karşılaştır

#  separationg products and stores
tProd['Type'] = 'Slow'
tProd.loc[(tProd['CumPer']<=(fastPercentage+mediumPercentage)), 'Type'] = 'Medium'
tProd.loc[(tProd['CumPer']<=fastPercentage), 'Type'] = 'Fast'

tStore['Type'] = 'Slow'
tStore.loc[(tStore['CumPer']<=(fastPercentage+mediumPercentage)), 'Type'] = 'Medium'
tStore.loc[(tStore['CumPer']<=fastPercentage), 'Type'] = 'Fast'

tProdPerStore['Type'] = 'Slow'
tProdPerStore.loc[(tProdPerStore['CumPer']<=(fastPercentage+mediumPercentage)), 'Type'] = 'Medium'
tProdPerStore.loc[(tProdPerStore['CumPer']<=fastPercentage), 'Type'] = 'Fast'

# comparison of the product sales during non-promo, promo periods
compProd = tProd.join(promProd.set_index(promProd.index), on='ProductCode', lsuffix='_non-Promo', rsuffix='_Promo')
compProd['IncreaseRateInShare'] = 100*(compProd['Per_Promo']/compProd['Per_non-Promo'] - 1 ) # change in total share
compProd['IncreaseRateOfWeeklySales'] = 100*((compProd['SalesQuantity_Promo']/promoWeeks - compProd['SalesQuantity_non-Promo']/nonPromoWeeks)/(compProd['SalesQuantity_non-Promo']/nonPromoWeeks))
compProd=compProd.sort_values(by=['IncreaseRateOfWeeklySales'], ascending=[False])

# comparison of the stores during non-promo, promo periods
compStore = tStore.join(promStore.set_index(promStore.index), on='StoreCode', lsuffix='_non-Promo', rsuffix='_Promo')
compStore['IncreaseRateInShare'] = 100*(compStore['Per_Promo']/compStore['Per_non-Promo'] - 1 ) # change in total share
compStore['IncreaseRateOfWeeklySales'] = 100*((compStore['SalesQuantity_Promo']/promoWeeks - compStore['SalesQuantity_non-Promo']/nonPromoWeeks)/(compStore['SalesQuantity_non-Promo']/nonPromoWeeks))
compStore=compStore.sort_values(by=['IncreaseRateOfWeeklySales'], ascending=[False])

# compStore.to_csv(r'pandas.txt', header=True, index=True, sep='-', mode='a')


# regression
# nonProm
# promotional
print('**********')

#  product 218 store 331 with the greatest sales are chosen as sample
sample = promotional.loc[(promotional['ProductCode']==218) & (promotional['StoreCode']==331)]
sample = sample.set_index('Date')

X = list(sample.loc[(sample['Promotion']=='Promo1'), 'SalesQuantity'])
y = list(sample.loc[(sample['Promotion']=='Promo2'), 'SalesQuantity'])
print(X)
print(y)

model = sm.OLS(y, X).fit()
predictions = model.predict(X)
model.summary()
print(model.summary())





# df = pd.DataFrame({"A": promotional.loc[(promotional['Promotion']=='Promo1')], "B": promotional.loc[(promotional['Promotion']=='Promo2')], "C": promotional.loc[(promotional['Promotion']=='Promo3')], "D": promotional.loc[(promotional['Promotion']=='Promo4')]})
# result = sm.ols(formula="D ~ A + B + C", data=df).fit()
# print(result.params)
# print(result.summary())

# tProd.to_csv(r'pandas1.txt', header=True, index='ProductCode', sep='-', mode='a')
# tStore.to_csv(r'pandas2.txt', header=True, index='StoreCode', sep='-', mode='a')
# print('/**********************')

# pProd = promotional
# pProd['Mean']=pProd.groupby(['ProductCode'])['SalesQuantity'].mean()
# pProd=pProd.sort_values(by=['SalesQuantity'], ascending=[False])
#
# print(pProd)

# pProd=promotional.groupby(['ProductCode']).agg({'SalesQuantity':sum})
# pProd=pProd.sort_values(by=['SalesQuantity'], ascending=[False])
#
# pProd=promotional.groupby(['ProductCode']).agg({'SalesQuantity':sum})
# pProd=pProd.sort_values(by=['SalesQuantity'], ascending=[False])

# tProd=promotional.groupby(['ProductCode'])['SalesQuantity'].mean()
# tProd=tProd.sort_values(['SalesQuantity'], ascending=[False])
# print(tProd)
# #
# pStore=promotional.groupby(['StoreCode'])['SalesQuantity'].agg({'SalesQuantity':sum})
# pStore=pStore.sort_values(by=['SalesQuantity'], ascending=[False])
#
# print(pStore.dtypes)
# print('rst**********************')
# rStore=promotional.groupby(['StoreCode'])['SalesQuantity'].sum()
# print(rStore)
# print('zst**********************')
# zstore=promotional.sort_values(['SalesQuantity'],ascending=False).groupby(['StoreCode'])['SalesQuantity'].sum()
# print(zstore)



# print(pProd)
# print('****************')
# print(pStore)
# print('****************')
# print(pProdPerStore)




# print(assign1raw.dtypes)
# assign1raw['Date'].dt.week
# print(datetime.date(assign1raw['Date'].dt).isocalendar()[1])
# print(assign1raw['Date'].dt.dayofweek)
# print(datetime.date(assign1raw['DateTime']).isocalendar()[1])
# print(assign1raw.dtypes)
# test1 = prom.read(50)
# asspiv = assign1.pivot('Date', 'ProductCode', 'SalesQuantity')
# group1 = assign1['SalesQuantity'].groupby(assign1['Date'])
# print(group1.mean())
# interval = assign1['SalesQuantity'].groupby(assign1['StoreCode'])
# print(assign1.values())
# group1 = assign1raw['SalesQuantity'].groupby(assign1raw['StoreCode'])
# print(group1.mean())
# print(assign1raw.columns)
# print(withInterval['Date'].dtype)
# np.arange()
# print(withInterval[withInterval['Date'].isin(['2015-01-01','2015-01-05'])])
# withInterval[(withInterval['Date'].isin(pd.date_range('2015-01-02','2015-01-05')))]['Promo']

# print(withInterval['SalesQuantity'].groupby(withInterval['Promotion']).mean())
# print(assign1.groupby('StoreCode').size())

# df = nonProm.sort_values(['SalesQuantity'],ascending=False).groupby('Week')


# print(tProd)
# print('**************************')
# print(tStore)
# print('**************************')
# print(tProdPerStore)



"""
store = nonProm['SalesQuantity'].groupby(nonProm['StoreCode']).mean()
store['CumSum'] = store.StoreCode.cumsum()
prod = nonProm['SalesQuantity'].groupby(nonProm['ProductCode']).mean()

print(list(store))

store=store.sort_values(ascending=False)
store['CumSum'] = store.StoreCode.cumsum()
store['CumPers'] = 100*store.CumSum/store.StoreCode.sum()

list(store.columns.values)
prod=prod.sort_values(ascending=False)
prod['CumSum'] = prod.ProductCode.cumsum()
prod['CumPers'] = 100*prod.CumSum/prod.ProductCode.sum()

# store = store.sort_values(by=['StoreCode'])
# prod = prod.sort_values(by=['ProductCode'])

print(store)
print(prod)




# nonProm.to_csv(r'pandas.txt', header=True, index=True, sep='-', mode='a')


"""