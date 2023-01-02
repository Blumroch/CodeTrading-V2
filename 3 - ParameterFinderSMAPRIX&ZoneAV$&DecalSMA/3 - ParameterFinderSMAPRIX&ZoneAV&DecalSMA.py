#Le programme peut prendre quelques minutes à s'exécuter car nous allons chercher
# beaucoup de données chez Binance. 
# 

import pandas as pd # Librairy pour la manipulation et l'analyse de données
from binance.client import Client # L'exchage où on peut aller extraire les paires cryptos 
import ta # Librairy pour l'analyse technique
import matplotlib.pyplot as plt

client = Client()

paire = "FLUXBTC"
dateDebut = "1 january 2017"
#dateFin = "10 april 2021"
pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
iMeilleureSMA = 325
iIndiceZoneAchat = 104
iIndiceZoneVente = 92
iDecalSMAMax = 50
iProfitMin = 50 #Profit minimum qu'on garde à la fin
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
dResultat = pd.DataFrame(columns = ['iDecalSMA', 'fProfit', 'iTradeBon','iTradePasBon','fRatioTradeBon'])

dfTest["SMA"] = ta.trend.sma_indicator(dfTest['close'],iMeilleureSMA)

for iIndiceDecalSMA in range(1,iDecalSMAMax+1,1):
    dfTest['SMAX'] = dfTest['SMA'].shift(iIndiceDecalSMA)
    dfTest['DECALSMA'] = dfTest['close']/dfTest['SMAX']*100
    fUsd = 100
    fCrypto = 0
    fUsdTransaction = 0
    itradeBon = 0
    itradePasBon = 0

    #print("iIndiceSMA=",iIndiceSMA)
    #print("iIndiceDT=",iIndiceDecalSMA)
    #print(dfTest)

    for index, row in dfTest.iterrows() :
        # ACHAT
        if row['DECALSMA'] < iIndiceZoneVente and fUsd > 0 :
            fCrypto = fUsd / row['close'] - fFrais * fUsd / row['close']
            fUsdTransaction = fUsd
            fUsd = 0            
        # VEND PRIX<SMA
        elif row['DECALSMA'] >= iIndiceZoneAchat and fCrypto > 0 :
            fUsd = fCrypto * row['close'] - fFrais * fCrypto * row['close']
            if fUsd < 50:
                fCrypto = 0
                break                
            fCrypto = 0  
            if fUsdTransaction < fUsd: # Comptons les plus bonnes et les plus moins bonnes
                itradeBon = itradeBon + 1
            else :
                itradePasBon = itradePasBon + 1
            #On garde seulement ceux qui ont fait des profits     
        
    if fCrypto*row['close'] > iProfitMin or fUsd > iProfitMin :
        fRatioTradeBon = itradeBon/(itradePasBon+itradeBon)
        if fUsd == 0 :            
            myrow = {'iDecalSMA':iIndiceDecalSMA,'fProfit': round(fUsdTransaction,2),'iTradeBon':itradeBon,'iTradePasBon':itradePasBon,'fRatioTradeBon':round(fRatioTradeBon,2)}
        else :
            myrow = {'iDecalSMA':iIndiceDecalSMA,'fProfit': round(fUsd,2),'iTradeBon':itradeBon,'iTradePasBon':itradePasBon,'fRatioTradeBon':round(fRatioTradeBon,2)}
        dResultat = pd.concat([dResultat, pd.DataFrame.from_records([myrow])])
            
            #print(dResultat)
        #del dfTest ['SMAX']
        #del dfTest['DT']

print ("Best indicator for the crossing of the simple moving average with the price fo " + paire)
print ("from " + str(df.index[0]) + " to " + str(df.index[len(df)-1]) + " for a time frame of 1 hour")

print("Tri par profit")
print(dResultat.sort_values(by=['fProfit']))
print("")
print("Tri par trade")
print(dResultat.sort_values(by=['fRatioTradeBon']))
#dt.plot.scatter(x='i',y='j',c='result',s=50,xolormap='seismic')
