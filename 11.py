import numpy as np
import pandas as pd
from pandas import Series,DataFrame
import datetime
import statsmodels.api as sm

fastPercentage = 50 # top 50% of the total amounts -  fast item-store
mediumPercentage = 30 # 30% of the total sales - amounts item-store
slowPercentage = 20 # bottom 20% of the total sales - amounts item-store

# reading csv files and organizing the data
assign1raw = pd.read_csv('assignment4.1a.csv')
assign1raw['Date'] = assign1raw['Date'].astype('datetime64[ns]')
withInterval = DataFrame(assign1raw, columns=['Date', 'StoreCode', 'ProductCode', 'SalesQuantity', 'Week', 'Promotion'])
withInterval['Week'] = assign1raw['Date'].dt.week

promraw = pd.read_csv('PromotionDates.csv')
promotions = DataFrame(promraw, columns=['Period', 'StartDate', 'EndDate', 'StartWeek', 'EndWeek', 'Duration'])
promotions['StartDate'] = promotions['StartDate'].astype('datetime64[ns]')
promotions['EndDate'] = promotions['EndDate'].astype('datetime64[ns]')
promotions['Duration'] = (promotions['EndDate'] - promotions['StartDate'])
promotions = promotions.drop(promotions.index[4:6]) # using the first 4 promotions

futureraw = pd.read_csv('assignment4.1b.csv')
futureraw['Date'] = futureraw['Date'].astype('datetime64[ns]')
futureData = DataFrame(futureraw, columns=['Date', 'StoreCode', 'ProductCode', 'SalesQuantity', 'Week', 'Promotion'])
futureData['Week'] = futureData['Date'].dt.week

for index1, row1 in promotions.iterrows():
    withInterval.loc[(withInterval['Date'].isin(pd.date_range(row1['StartDate'],row1['EndDate']))), 'Promotion'] = row1['Period']
withInterval.loc[(pd.isnull(withInterval['Promotion'])), 'Promotion'] = 'non-Prom'

nonProm = withInterval.loc[withInterval['Promotion'] == 'non-Prom']
promotional = withInterval.loc[withInterval['Promotion'] != 'non-Prom']

# finding the promotion and non-promotion durations
promoWeeks =  len((withInterval.loc[withInterval['Promotion'] != 'non-Prom']).Date.value_counts().index) / 7
nonPromoWeeks = len((withInterval.loc[withInterval['Promotion'] == 'non-Prom']).Date.value_counts().index) / 7

# weekly sales amounts – each products total weekly sales
wProd=nonProm.groupby(['Week','ProductCode']).agg({'SalesQuantity':sum})
wProd=wProd.sort_values(by=['SalesQuantity'], ascending=[False])
wStore=nonProm.groupby(['Week','StoreCode']).agg({'SalesQuantity':sum})
wStore=wStore.sort_values(by=['SalesQuantity'], ascending=[False])
wProdPerStore=nonProm.groupby(['Week','StoreCode', 'ProductCode']).agg({'SalesQuantity':sum})
wProdPerStore=wProdPerStore.sort_values(by=['Week','SalesQuantity'], ascending=[True, False])
wProdPerStore.to_csv(r'WeeklyProductSalesPerStore.txt', header=True, index=True, sep='-', mode='a')

# total sales amounts
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

# product sales per store
tProdPerStore=nonProm.groupby(['StoreCode', 'ProductCode']).agg({'SalesQuantity':sum})
tProdPerStore=tProdPerStore.sort_values(by=['SalesQuantity'], ascending=[False])
tProdPerStore['Per'] = 100*tProdPerStore.SalesQuantity/tStore.SalesQuantity.sum()
tProdPerStore['CumSum'] = tProdPerStore.SalesQuantity.cumsum()
tProdPerStore['CumPer'] = 100*tProdPerStore.CumSum/tProdPerStore.SalesQuantity.sum()
tProdPerStore.to_csv(r'TotalSalesPerStoresNonProm.txt', header=True, index=True, sep='-', mode='a')

# total sales amounts for each promotion
promProd=promotional.groupby(['Promotion','ProductCode']).agg({'SalesQuantity':sum})
promProd=promProd.sort_values(by=['SalesQuantity'], ascending=[False])

promStore=promotional.groupby(['Promotion','StoreCode']).agg({'SalesQuantity':sum})
promStore=promStore.sort_values(by=['SalesQuantity'], ascending=[False])

promProdPerStore=promotional.groupby(['Promotion','StoreCode', 'ProductCode']).agg({'SalesQuantity':sum})
promProdPerStore=promProdPerStore.sort_values(by=['SalesQuantity'], ascending=[False])

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
gPromProdPerStore.to_csv(r'TotalSalesPerStorePromotion.txt', header=True, index=True, sep='-', mode='a')

#  products sales amounts per store during promotions
ppp=promotional.groupby(['StoreCode', 'ProductCode']).agg({'SalesQuantity':sum})
ppp1=promotional.groupby(['StoreCode']).agg({'SalesQuantity':sum})
ppp1.columns = ['StoreSales']
promProdPerStore=ppp.join(ppp1.set_index(ppp1.index), on='StoreCode')
promProdPerStore=promProdPerStore.sort_values(by=['StoreCode','SalesQuantity'], ascending=[True,False])
promProdPerStore['Per'] = 100*promProdPerStore.SalesQuantity/promProdPerStore.StoreSales
promProdPerStore['CumPer'] = promProdPerStore.Per.groupby(['StoreCode']).cumsum()
promProdPerStore.to_csv(r'SalesPerStorePromotion.txt', header=True, index=True, sep='-', mode='a')

#  separating products and stores during non-promo
tProd['Type'] = 'Slow'
tProd.loc[(tProd['CumPer']<=(fastPercentage+mediumPercentage)), 'Type'] = 'Medium'
tProd.loc[(tProd['CumPer']<=fastPercentage), 'Type'] = 'Fast'

tStore['Type'] = 'Slow'
tStore.loc[(tStore['CumPer']<=(fastPercentage+mediumPercentage)), 'Type'] = 'Medium'
tStore.loc[(tStore['CumPer']<=fastPercentage), 'Type'] = 'Fast'

tProdPerStore['Type'] = 'Slow'
tProdPerStore.loc[(tProdPerStore['CumPer']<=(fastPercentage+mediumPercentage)), 'Type'] = 'Medium'
tProdPerStore.loc[(tProdPerStore['CumPer']<=fastPercentage), 'Type'] = 'Fast'
tProdPerStore.to_csv(r'StoreProductPairTypes.txt', header=True, index=True, sep='-', mode='a')

# comparison of the product sales during non-promo, promo periods
compProd = tProd.join(promProd.set_index(promProd.index), on='ProductCode', lsuffix='_non-Promo', rsuffix='_Promo')
compProd['IncreaseRateInShare'] = 100*(compProd['Per_Promo']/compProd['Per_non-Promo'] - 1 ) # change in total share
compProd['IncreaseRateOfWeeklySales'] = 100*((compProd['SalesQuantity_Promo']/promoWeeks - compProd['SalesQuantity_non-Promo']/nonPromoWeeks)/(compProd['SalesQuantity_non-Promo']/nonPromoWeeks))
compProd=compProd.sort_values(by=['IncreaseRateOfWeeklySales'], ascending=[False])
compProd.to_csv(r'ComparisonOfNonPromo-PromobyProducts.txt', header=True, index=True, sep='-', mode='a')

# comparison of the stores during non-promo, promo periods
compStore = tStore.join(promStore.set_index(promStore.index), on='StoreCode', lsuffix='_non-Promo', rsuffix='_Promo')
compStore['IncreaseRateInShare'] = 100*(compStore['Per_Promo']/compStore['Per_non-Promo'] - 1 ) # change in total share
compStore['IncreaseRateOfWeeklySales'] = 100*((compStore['SalesQuantity_Promo']/promoWeeks - compStore['SalesQuantity_non-Promo']/nonPromoWeeks)/(compStore['SalesQuantity_non-Promo']/nonPromoWeeks))
compStore=compStore.sort_values(by=['IncreaseRateOfWeeklySales'], ascending=[False])

compStore.to_csv(r'ComparisonOfNonPromo-PromobyStores.txt', header=True, index=True, sep='-', mode='a')

#  product 218 store 331 with the greatest sales are chosen as sample
sample = promotional.loc[(promotional['ProductCode']==218) & (promotional['StoreCode']==331)]
sample = sample.set_index('Date')

# regression model try-out
X = list(sample.loc[(sample['Promotion']=='Promo1'), 'SalesQuantity'])
y = list(sample.loc[(sample['Promotion']=='Promo2'), 'SalesQuantity'])

model = sm.OLS(y, X).fit()
predictions = model.predict(X)
model.summary()
print(model.summary())






