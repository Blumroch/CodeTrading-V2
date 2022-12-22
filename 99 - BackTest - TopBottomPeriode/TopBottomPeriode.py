# 3EMA CROSSOVER & STOCHRSI
#Le programme peut prendre quelques minutes à s'exécuter car nous allons chercher
# beaucoup de données chez Binance. 

import pandas as pd # Librairy pour la manipulation et l'analyse de données
from binance.client import Client # L'exchage où on peut aller extraire les paires cryptos 
import ta # Librairy pour l'analyse technique


#Mettre la valeur courte et longue durée anisi que la très longue durée
emaTest1 = 217
emaTest2 = 291
emaTest3 = 2

#Paire(vérifier chez Binance)
paire = "THETABTC"
dateDebut = "1 january 2017"
#dateFin = "10 april 2021"
#dateFin = "10 december 2021" #Si on en a besoin, sinon jusqu'à Làlà. Ne pas oublier de l'ajouter au KlinesT

# On va chercher les données chez Binance paire,temps,date début
klinesT= Client().get_historical_klines(paire,Client().KLINE_INTERVAL_1HOUR,dateDebut)
# Les données qu'on va chercher séparées par colonnes
df = pd.DataFrame(klinesT,columns=['timestamp','open','high','low','close','volume','close_time','quote_av','trades','tb_base_av','tb_quote_av','ignore'])

# On affiche tout ça, si on veut.
#print(df)

#On fait du ménage en supprimant les colonnes inutiles
del df['ignore']
del df['close_time']
del df['quote_av']
del df['trades']
del df['tb_base_av']
del df['tb_quote_av']

# On affiche tout ça, si on veut.
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

#6 nouvelles colonnes avec les EMA et le StochRSI
df['EMAX1'] = ta.trend.ema_indicator(df['close'],emaTest1)
df['EMAX2'] = ta.trend.ema_indicator(df['close'],emaTest2)
df['EMAX3'] = ta.trend.ema_indicator(df['close'],emaTest3)
df["EMA_HISTO"] = df["EMAX1"] - df["EMAX2"]

df['%K'] = ta.momentum.stochrsi_k(df['close'],14,3)
df['%D'] = ta.momentum.stochrsi_d(df['close'],14,3)
#df['emaTest1'] = pd.to_numeric(df['emaTest1'])
#df['emaTest2'] = pd.to_numeric(df['emaTest2'])

# On affiche tout ça.
#print(df)

#BACKTESTING COMMENCE ENFIN ICITTE
#On fait semblant d'investir 1000 USDT à dateDebut
#Un nouveu tableau pour nos infos
dt = None
dt = pd.DataFrame(columns = ['date','position', 'prix', 'fee' ,'fiat', 'coins', 'wallet', 'drawBack'])

position = 0
ecartAthPrixPosition = 0
#datePosition = df.iloc[len(df)-1]['date']
datePosition = "NULLLLLLL"
prixPosition = 0
countPeriode = 0 
athPosition  = 0 


#On passe chacun des index du tableau ci-haut.
for index, row in df.iterrows() :
    #ACHAT smaTest1>smaTest2 et que j'ai au moins 10$
    if row['EMA_HISTO'] > 0 and row['EMAX3'] < row['close'] and row['%K'] > row['%D'] or position == 1 and row['EMA_HISTO'] > 0 :    
        if position == 0 :
            print("V ,",datePosition,",",prixPosition,"$ ,",countPeriode,",",athPosition,"$ ,",round(ecartAthPrixPosition,8),"$")
            datePosition = index
            countPeriode = 1
            prixPosition = row['close']
            athPosition = prixPosition
            ecartAthPrixPosition = 0            
            position = 1

        elif position == 1 :
            countPeriode = countPeriode + 1
            if row['close'] > athPosition :
                athPosition = row['close']
                ecartAthPrixPosition = row['close'] - prixPosition

        #print("A",datePosition,prixPosition,countPeriode,athPosition,ecartAthPrixPosition)  #Pour CSV  
    # VEND SMA200<SMA600 et que j'ai au moins 0,0001 coin
    elif row['EMA_HISTO'] <= 0 :
        if position == 1 :
            print("A ,",datePosition,",",prixPosition,"$ ,",countPeriode,",",athPosition,"$ ,",round(ecartAthPrixPosition,8),"$")  #Pour CSV  
            position = 0
            countPeriode = 0
            ecartAthPrixPosition = 0
            datePosition = index
            prixPosition = row['close']
            athPosition = prixPosition
        countPeriode = countPeriode + 1
        #athPosition = prixPosition
        if row['close'] < athPosition and position == 0 :
            athPosition = row['close']
            ecartAthPrixPosition = prixPosition - row['close']
        #print("V",datePosition,prixPosition,countPeriode,athPosition,ecartAthPrixPosition)

print("AV ,",datePosition,",",prixPosition,"$ ,",countPeriode,",",athPosition,"$ ,",round(ecartAthPrixPosition,8),"$")
