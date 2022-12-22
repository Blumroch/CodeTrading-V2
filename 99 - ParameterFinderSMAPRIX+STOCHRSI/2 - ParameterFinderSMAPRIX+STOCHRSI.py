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

iSMAMax = 1000
iKDMax =14 
iLongueurMax = 28
iProfitMin = 115 #Profit minimum qu'on garde à la fin
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

#df['%K'] = ta.momentum.stochrsi_k(df['close'],14,3)
#df['%D'] = ta.momentum.stochrsi_d(df['close'],14,3)
 #if row['EMA_HISTO'] > 0 and row['%K'] > row['%D'] and usdt > 0 :


#Un nouveau tableau pour faire nos testes
dfTest = df.copy()

dResultat = None
dResultat = pd.DataFrame(columns = ['iIndiceSMA','iIndiceKD','iIndiceLongueur', 'fProfit'])

dfTest['%K'] = ta.momentum.stochrsi_k(dfTest['close'],14,3)
dfTest['%D'] = ta.momentum.stochrsi_d(dfTest['close'],14,3)
iIndiceLongueur = 14
iIndiceKD = 3
"""   for iIndiceLongueur in range(1,iLongueurMax+1,1):        
        for iIndiceKD in range(1,iKDMax+1,1):
            dfTest['%K'] = ta.momentum.stochrsi_k(dfTest['close'],iIndiceLongueur,iIndiceKD)
            dfTest['%D'] = ta.momentum.stochrsi_d(dfTest['close'],iIndiceLongueur,iIndiceKD)
    """
    
for iIndiceSMA in range(1,iSMAMax+1,1):
    dfTest["SMA"] = ta.trend.sma_indicator(dfTest['close'],iIndiceSMA)
    fUsd = 100
    fCrypto = 0
    fUsdTransaction = 0
    
    for index, row in dfTest.iterrows() :
        if row['close'] > row['SMA'] and row['%K'] > row['%D'] and fUsd > 0 :  #row['%K'] > row['%D'] and
                # ACHAT quand PRIX<SMA
            fCrypto = fUsd / row['close'] - fFrais * fUsd / row['close']
            fUsdTransaction = fUsd
            fUsd = 0            
                # VEND PRIX<SMA
        elif row['close'] <= row['SMA'] and fCrypto > 0 :
            fUsd = fCrypto * row['close'] - fFrais * fCrypto * row['close']
            if fUsd < 75 :
                fCrypto = 0
                break                
            fCrypto = 0           
            #On garde seulement ceux qui ont fait des profits     
    if fCrypto*row['close'] > iProfitMin or fUsd > iProfitMin :
        if fUsd == 0 :            
            myrow = {'iIndiceSMA':iIndiceSMA,'iIndiceKD':iIndiceKD, 'iIndiceLongueur':iIndiceLongueur,'fProfit': round(fUsdTransaction,2)}
        else :
            myrow = {'iIndiceSMA':iIndiceSMA,'iIndiceKD':iIndiceKD, 'iIndiceLongueur':iIndiceLongueur,'fProfit': round(fUsd,2)}

        dResultat = pd.concat([dResultat, pd.DataFrame.from_records([myrow])])

print ("Best indicator for the crossing of the simple moving average with the price fo " + paire)
print ("from " + str(df.index[0]) + " to " + str(df.index[len(df)-1]) + " for a time frame of 1 hour")

print(dResultat.sort_values(by=['fProfit']))
#dt.plot.scatter(x='i',y='j',c='result',s=50,xolormap='seismic')


"""
if usdt == 0 :
    myrow = {'i':i,'j':j,'result': usdtTransaction}
else :
    myrow = {'i':i,'j':j,'result': usdt + coin*dfTest.iloc[-1]['close']}
dt = pd.concat([dt, pd.DataFrame.from_records([myrow])])

for i in range(1,ema1Max,3):#25,50,3----------1,ema1Max,1
    dfTest["EMA1"] = ta.trend.ema_indicator(dfTest['close'],i)
    for j in range(i+2,ema2Max,3):#i+2,70,3--------1,ema2Max,1
        dfTest["EMA2"] = ta.trend.ema_indicator(dfTest['close'],j)
        dfTest["EMA_HISTO"] = dfTest["EMA1"] - dfTest["EMA2"]

        usdt = 1000
        coin = 0
        fee = 0.0007

        #On passe chacun des index du tableau ci-haut.
        for index, row in dfTest.iterrows() :
            #ACHAT EMA1>SM2 et que j'ai au moins 0$
            if row['EMA_HISTO'] > 0 and row['%K'] > row['%D'] and usdt > 0 :
                #Converti USDT en coin comme si on vendait et on enlève les fee
                coin = usdt / row['close'] - fee * usdt / row['close']
                #on a tout échanger nos USDT
                usdtTransaction = usdt
                usdt = 0
                #print("Achat de coin au prix de : ",df['close'][index],"||",df['timestamp'][index], "|| J'ai",fiat,"$ et ",btc,"btc")
        
            # VEND EMA200<SMA600 et que j'ai au moins 0,0001 coin
            elif row['EMA_HISTO'] <= 0 and coin > 0 :
                #Converti USDT en coin comme si on vendait
                usdt = coin * row['close'] - fee * coin * row['close']
                # on enlève les frais par principex
                if usdt < 250: 
                    break
                coin = 0
                #print("Vend de coin au prix de : ",df['close'][index],"||",df['timestamp'][index], "|| J'ai",fiat,"$ et ",btc,"btc")
     
        if usdt == 0 :
            myrow *= {'i':i,'j':j,'result': usdtTransaction}
        else :
            myrow = {'i':i,'j':j,'result': usdt + coin*dfTest.iloc[-1]['close']}
        
        dt = pd.concat([dt, pd.DataFrame.from_records([myrow])])
        #dt = dt.append(myrow,ignore_index=True) Ne semble plus fonctionner. Remplacer par concat
"""
