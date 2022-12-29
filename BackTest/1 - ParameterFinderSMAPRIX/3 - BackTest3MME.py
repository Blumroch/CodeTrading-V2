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
dateDebut = "14 april 2017"
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

count = 0
usdt = 1000
usdtDepart = usdt
coin = 0
fee = 0.0007
totalFee = 0 
tradeBon = 0
tradePasBon = 0
meilleureTransaction = 0
pireTransaction = 0
totalMeilleureTransaction = 0
totalPireTransaction = 0
athWallet = 0
drawBack = 0

#On passe chacun des index du tableau ci-haut.
for index, row in df.iterrows() :
    #ACHAT smaTest1>smaTest2 et que j'ai au moins 10$
    if row['EMA_HISTO'] > 0 and row['EMAX3'] < row['close'] and row['%K'] > row['%D'] and usdt > 10 :    
        usdtTransaction = usdt # Pour calculer la valeur de la transcation
        coin = usdt / row['close'] #Converti USDT en coin comme si on vendait et on enlève les fee
        tradeFee = usdt * fee # Calculer les frais par principe
        totalFee = totalFee + tradeFee # Calcul des frais total        
        coin = coin - (tradeFee/row['close']) # Enlèver les frais par principe
        usdt = 0 # on a tout échanger nos USDT
        #print("Achat de coin au prix de : ",row['close'],"||",index, "|| J'ai",usdt,"$ et ",coin,"btc")
        #print(index,",ACHAT,",coin,",BNB,",row['close'],",",tradeFee)  #Pour CSV  et autre chose que tu USDT
        print(index,",ACHAT,",coin,",FTT,",row['close'],",",tradeFee)  #Pour CSV  
    # VEND SMA200<SMA600 et que j'ai au moins 0,0001 coin
    elif row['EMA_HISTO'] <= 0 and coin > 0 :
        #Converti USDT en coin comme si on vendait                
        usdt = coin * row['close']  #Converti les coin en USDT comme si on vendait et on enlève les fee
        tradeFee = coin * row['close'] * fee # Calcul des frais total
        totalFee = totalFee + tradeFee # Calcul des frais total
        usdt = usdt - tradeFee # Enlèver les frais par principe

        #Refaire totl, ça ne marche pas.
        
        pourcentageTransaction = (usdt-usdtTransaction)/usdtTransaction*100 # Cherchons la plus meilleure ou pas transaction
        if pourcentageTransaction > meilleureTransaction :
            meilleureTransaction = pourcentageTransaction
            indexMeilleur = index
        if pourcentageTransaction < pireTransaction :
            pireTransaction = pourcentageTransaction            
            indexPire = index

        if usdtTransaction < usdt: # Comptons les plus bonnes et les plus moins bonnes
            tradeBon = tradeBon + 1
            totalMeilleureTransaction = totalMeilleureTransaction + pourcentageTransaction
        else :
            tradePasBon = tradePasBon + 1
            totalPireTransaction = totalPireTransaction + pourcentageTransaction

        if usdt > athWallet: # ATH du wallet
            athWallet = usdt

        if drawBack > (usdt-athWallet)/athWallet * 100 : # calcul du Drawback
            drawBack = (usdt-athWallet)/athWallet * 100       
        coin = 0  # on a tout échanger nos coin
        dernierPrixValide = row['close']
        #print("Vend de coin au prix de : ",row['close'],"||",index, "|| J'ai",usdt,"$ et ",coin,"btc")
        #print(index,",VEND,",usdt,",BTC,",row['close'],",",tradeFee)  #Pour CSV pour autre chose que USD 
        print(index,",VEND,",usdt,",$,",row['close'],",",tradeFee)  #Pour CSV  

if usdt == 0 :
    print("Ne pas tenir compte du dernière achat")
    montantFinalWallet = usdtTransaction
    
else :
    montantFinalWallet = usdt # Montal final dans le Wallet

pourcentageBot = ((montantFinalWallet - usdtDepart)/usdtDepart) * 100 # Performance du wallet
pourcentageMaintien = ((df.iloc[len(df)-1]['close'] - df.iloc[0]['close'])/df.iloc[0]['close']) * 100 # Performence du maintien
gainMoyenPositif = totalMeilleureTransaction/tradeBon
gainMoyenNegatif = totalPireTransaction/tradePasBon


print("")
print("Période : [" + str(df.index[0]) + "] -> [" +str(df.index[len(df)-1]) + "]")
print("Montant Départ dans le wallet :",usdtDepart,"$")
print("Montant final dans le wallet :", round(montantFinalWallet,2),"$")
print("Performance du wallet avec le Bot",round(pourcentageBot,2),"%")
print("Performance du wallet avec maintien seulement",round(pourcentageMaintien,2),"%")
print("Nombre de transactions positives:",tradeBon)
print("Nombre de transactions négatives:",tradePasBon)
print("Gain moyen par transaction positive:",round(gainMoyenPositif,2),"%")
print("Perte moyenne par transaction négative:",round(gainMoyenNegatif,2),"%")
print("La plus meilleure transaction",round(meilleureTransaction,2),"% ->",indexMeilleur)
print("La plus pire transaction",round(pireTransaction,2),"% ->",indexPire)
print("Le pire drawback:", round(drawBack,2),"%")
print ("Frais total :",round(totalFee,2),"$")


print("")
print("")
print("Période : [" + str(df.index[0]) + "] -> [" +str(df.index[len(df)-1]) + "]")
print(usdtDepart)
print(montantFinalWallet) # Montal final dans le Wallet
print(round(pourcentageBot,2)) # Performance du wallet
print(round(pourcentageMaintien,2)) # Performence du maintien
print(tradeBon) # Nombre de bonne transaction
print(tradePasBon) #Nombre de pas bonne transaction
#print("----")
print(round(gainMoyenPositif,2)) # Pourcentage moyen par transaction positive
print(round(gainMoyenNegatif,2)) # Pourcentage moyen par transaction négative
#print("----")
print(round(meilleureTransaction,2),"% ->",indexMeilleur)
print(round(pireTransaction,2),"% ->",indexPire)
#print("----")
print(round(drawBack,2)) # Le pire drawback
print (totalFee) # Frais total
