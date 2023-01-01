import pandas as pd
from binance.client import Client # L'exchage où on peut aller extraire les paires cryptos 
import ta # Librairy pour l'analyse technique
import matplotlib.pyplot as plt
from datetime import datetime,timedelta,timezone

client = Client()
pd.set_option('display.max_columns', None) # Affichera toutes les colones
pd.set_option('display.max_rows', None) # Affichera toutes les lignes

ijoursLimits = 45 # Nbre de jours avant aujourd'hui où on va chercher des données

dtMaintenant = datetime.now(timezone.utc)
dtLautreJour = dtMaintenant - timedelta(ijoursLimits)
dtLala = dtMaintenant.strftime("%Y-%m-%d %H:%M:%S")
# Affiche le moment de qu'est-ce qu'on est
print("Il est présentement (UTC) :", dtLala)
dateDebut = dtLautreJour.strftime("%Y-%m-%d %H:%M:%S")
# Affiche le moment où la cueillette de données commencera
print("Les données commenceront (UTC) : ",dateDebut)

strPaire = "BTCUSDT"
dateDebut = dtLautreJour.strftime("%d %B %Y")
#dateFin = "10 april 2021"

aDonneBinance= Client().get_historical_klines(strPaire,Client().KLINE_INTERVAL_1HOUR,dateDebut)
# Les données qu'on va chercher séparées par colonnes
df = pd.DataFrame(aDonneBinance,columns=['timestamp','open','high','low','close','volume','close_time','quote_av','trades','tb_base_av','tb_quote_av','ignore'])

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

#SCANSTRATEGIE comme icitte

iMeilleureSMA = 672
df['SMA'] = ta.trend.sma_indicator(df['close'],iMeilleureSMA)

dfLigne = df.iloc[-2]  #Dernière valeur de la chandelle précédentee
print("")
print("Stratégie Scan pour : ",strPaire)
print("")
#Scan SMA
print ("Croissement prix/moyenne mobile : SMA = ", iMeilleureSMA)
if dfLigne['close'] < dfLigne['SMA']:
    for i in range (2,ijoursLimits*24,1) :
        if df.iloc[-i]['close'] > df.iloc[-i]['SMA'] :
            print("ZONE ACHAT DEPUIS (UTC) : ", df.index[-i])
            break

elif dfLigne['close'] >= dfLigne['SMA'] :
    for i in range (2,ijoursLimits,1) :
        if df.iloc[-i]['close'] < df.iloc[-i]['SMA'] :
            print("ZONE VENTE DEPUIS (UTC) : ", df.index[-i])
            break
else :
    print ("augmenter le ijoursLimits")

#dfTest = df.copy()
#print(dfTest)