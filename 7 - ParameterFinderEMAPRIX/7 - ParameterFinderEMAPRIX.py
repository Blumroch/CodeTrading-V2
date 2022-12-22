 #Le programme peut prendre quelques minutes à s'exécuter car nous allons chercher
# beaucoup de données chez Binance. 
# 

import pandas as pd # Librairy pour la manipulation et l'analyse de données
from binance.client import Client # L'exchage où on peut aller extraire les paires cryptos 
import ta # Librairy pour l'analyse technique
import matplotlib.pyplot as plt

client = Client()

paire = "BTCUSDT"
dateDebut = "1 january 2017"
#dateFin = "10 april 2021"

iEMAMax = 1000
iProfitMin = 100 #Profit minimum qu'on garde à la fin
fFrais = 0.001 #Frais de Binance

# On va chercher les données chez Binance paire,temps,date début
klinesT= Client().get_historical_klines(paire,Client().KLINE_INTERVAL_1HOUR,dateDebut)
# Les données qu'on va chercher séparées par colonnes
df = pd.DataFrame(klinesT,columns=['timestamp','open','high','low','close','volume','close_time','quote_av','trades','tb_base_av','tb_quote_av','ignore'])

# On affiche tout ça.
#print(df)

#On fait du ménage en supprimant les colonnes inutiles
del df['ignore']
del df['close_time']
del df['quote_av']
del df['trades']
del df['tb_base_av']
del df['tb_quote_av']

# On affiche tout ça.
#print(df)

#On converti les autres colonnes pour que la donnée soit de format numérique
df['close'] = pd.to_numeric(df['close'])
df['high'] = pd.to_numeric(df['high'])
df['low'] = pd.to_numeric(df['low'])
df['open'] = pd.to_numeric(df['open'])
df['volume'] = pd.to_numeric(df['volume'])
#On converti timestam en date lisible UTC Time
df = df.set_index(df['timestamp'])
df.index = pd.to_datetime(df.index,unit='ms')
del df['timestamp']

# On affiche tout ça, si on veut.
#print(df)

#BACKTESTING COMMENCE ENFIN ICITTE

#Un nouveau tableau pour faire nos testes
dfTest = df.copy()

dResultat = None
dResultat = pd.DataFrame(columns = ['iIndiceEMA', 'fProfit'])
count = 0

for iIndiceEMA in range(1,iEMAMax+1,1):
    dfTest["EMA"] = ta.trend.ema_indicator(dfTest['close'],iIndiceEMA)
    fUsd = 100
    fCrypto = 0
    fUsdTransaction = 0

    for index, row in dfTest.iterrows() :
        if row['close'] > row['EMA'] and fUsd > 0 :
        # ACHAT quand PRIX<EMA
            fCrypto = fUsd / row['close'] - fFrais * fUsd / row['close']
            fUsdTransaction = fUsd
            fUsd = 0
        # VEND PRIX<EMA
        elif row['close'] <= row['EMA'] and fCrypto > 0 :
            fUsd = fCrypto * row['close'] - fFrais * fCrypto * row['close']
            if fUsd < 50:
                fCrypto = 0
                break
            fCrypto = 0
    #On garde seulement ceux qui ont fait des profits  
    if fCrypto * row['close'] > iProfitMin or fUsd > iProfitMin :
        if fUsd == 0 :
            myrow = {'iIndiceEMA':iIndiceEMA,'fProfit': round(fUsdTransaction,2)}
        else :
            myrow = {'iIndiceEMA':iIndiceEMA,'fProfit': round(fUsd,2)}
        dResultat = pd.concat([dResultat, pd.DataFrame.from_records([myrow])])

print ("Best indicator for the crossing of the simple moving average with the price fo " + paire)
print ("from " + str(df.index[0]) + " to " + str(df.index[len(df)-1]) + " for a time frame of 1 hour")

print(dResultat.sort_values(by=['fProfit']))
#dt.plot.scatter(x='i',y='j',c='result',s=50,xolormap='seismic')