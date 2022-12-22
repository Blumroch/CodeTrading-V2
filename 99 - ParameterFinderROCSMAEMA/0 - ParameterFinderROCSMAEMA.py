
#Le programme peut prendre quelques minutes à s'exécuter car nous allons chercher
# beaucoup de données chez Binance. 
# 

import pandas as pd # Librairy pour la manipulation et l'analyse de données
from binance.client import Client # L'exchage où on peut aller extraire les paires cryptos 
import ta # Librairy pour l'analyse technique
import matplotlib.pyplot as plt

client = Client()

paire = "BNBBTC"
dateDebut = "11 january 2017"
##dateFin = "10 april 2021"

rocMax = 96 #96 pour 4 jours ou inférieur à 100 périodes
smaMax = 28
emaMax = 28
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
#On fait semblant d'investir 100 BTC 
### = Vieux code à effacer quand pu de besoin
###df['%K'] = ta.momentum.stochrsi_k(df['close'],14,3)
###df['%D'] = ta.momentum.stochrsi_d(df['close'],14,3)

#ROCX est le 
#df['ROCX'] = ta.momentum.stochrsi_k(df['close'],14,3)
 

#Un nouveau tableau pour faire nos testes
"""
i = 0
for index, row in dfTest.iterrows() :
    if i >=4 :
        #row['EMA_HISTO'] > 0 and row['%K'] > row['%D'] and usdt > 0 :
        myrow = {'close':row['close'],'closeX': dfTest.iloc[i-4]['close']}
        pdROC = pd.concat([pdROC, pd.DataFrame.from_records([myrow])])
    i=i+1
       
pdROC['ROC'] = pdROC['close']/pdROC['closeX']*100
pdROC['SMA1'] = ta.trend.sma_indicator(pdROC['ROC'],5)
pdROC['EMA1'] = ta.trend.ema_indicator(pdROC['SMA1'],5)

print(pdROC)
"""

dfTest = df.copy()

fee = 0.001 # frais binance
count = 0


dt = None
dt = pd.DataFrame(columns = ['i', 'j','k','result'])
count = 0

for i in range(2,rocMax+1,1):
    pdROC = None
    pdROC = pd.DataFrame(columns = ['index','close', 'closeX'])
    x = 0 # corespond à l'indicateur du ROC
    for index, row in dfTest.iterrows() :
        if x>=i :
        #row['EMA_HISTO'] > 0 and row['%K'] > row['%D'] and usdt > 0 :
            myrow = {'index':index,'close':row['close'],'closeX': dfTest.iloc[x-i]['close']} # x-i c'Est pour le décalage entre maintenant et l'indicateur
            pdROC = pd.concat([pdROC, pd.DataFrame.from_records([myrow])])
        x=x+1
    
    pdROC['ROC'] = pdROC['close']/pdROC['closeX']*100
    
    for j in range(2,smaMax+1,1):
        pdROC['SMA1'] = ta.trend.sma_indicator(pdROC['ROC'],j)
        for k in range(2,emaMax+1,1):
            pdROC['EMA1'] = ta.trend.ema_indicator(pdROC['SMA1'],k)
            pdROC["HISTO"] = pdROC["SMA1"] - pdROC["EMA1"]
            #print("i=",i,"j",j,"k",k)
            #print (pdROC)
            # tout ce qui a avant fonctionne

            btc = 100
            coin = 0

            for index, row in pdROC.iterrows() :
                #ACHAT SMA1>EMA1 et qu'il me reste des BTC
                if row['HISTO'] > 0 and btc > 0 :
                    #Converti USDT en coin comme si on vendait et on enlève les fee
                    coin = (btc/row['close']) - (fee*btc/row['close'])
                    #on a tout échangé nos btc
                    btcTransaction = btc
                    btc = 0 

                 # VEND SMA1<EMA2 et que j'ai au moins 0,0001 coin
                elif row['HISTO'] <= 0 and coin > 0 :
                #Converti USDT en coin comme si on vendait et on enlève les fee
                    btc = (coin*row['close']) - (fee*coin*row['close'])
                    if btc < 50: 
                        break
                    coin = 0
            #### PU SÛR ICITTE À REFAIRE !!!!!!!!!!
            if btc == 0 :
                myrow = {'i':i,'j':j,'k':k,'result': btcTransaction}
            else :
                myrow = {'i':i,'j':j,'k':k,'result': btc+coin*dfTest.iloc[-1]['close']}
            dt = pd.concat([dt, pd.DataFrame.from_records([myrow])])
print(dt.sort_values(by=['result']))

   
            


    #print(pdROC)
    


"""        
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
            myrow = {'i':i,'j':j,'result': usdtTransaction}
        else :
            myrow = {'i':i,'j':j,'result': usdt + coin*dfTest.iloc[-1]['close']}
        
        dt = pd.concat([dt, pd.DataFrame.from_records([myrow])])
        #dt = dt.append(myrow,ignore_index=True) Ne semble plus fonctionner. Remplacer par concat
print(dt.sort_values(by=['result']))
#dt.plot.scatter(x='i',y='j',c='result',s=50,xolormap='seismic')









"""






