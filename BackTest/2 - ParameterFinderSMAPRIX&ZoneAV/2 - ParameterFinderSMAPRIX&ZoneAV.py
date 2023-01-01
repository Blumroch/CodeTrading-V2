# 3EMA CROSSOVER & STOCHRSI
#Le programme peut prendre quelques minutes à s'exécuter car nous allons chercher
# beaucoup de données chez Binance. 

import pandas as pd # Librairy pour la manipulation et l'analyse de données
from binance.client import Client # L'exchage où on peut aller extraire les paires cryptos 
import ta # Librairy pour l'analyse technique

client = Client()
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

#Paire(vérifier chez Binance)
paire = "BTCUSDT"
dateDebut = "01 january 2017"
#dateFin = "10 april 2021"

#Mettre la valeur du ParameterFin3der
iBestSma = 672
iZoneAchat = 1.13
iZoneVente = 0.92

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
df['SMA'] = ta.trend.sma_indicator(df['close'],iBestSma)

# On affiche tout ça.
#print(df)

#BACKTESTING COMMENCE ENFIN ICITTE
#On fait semblant d'investir 1000 fBTC à dateDebut
#Un nouveu tableau pour nos infos
dt = None
dt = pd.DataFrame(columns = ['date','position', 'prix', 'Frais' ,'fiat', 'coins', 'wallet', 'drawBack'])

fBTC = 1000
fBTCDepart = fBTC
fCrypto = 0
fFrais = 0.001 #frais pour binance
fTotalFrais = 0 
iTradeBon = 0
iTradePasBon = 0
fMeilleureTransaction = 0
fPireTransaction = 0
fPourcentageTransaction = 0
dtIndexMeilleur = 0
dtIndexPire = 0
fTotalMeilleureTransaction = 0
fTotalPireTransaction = 0
fAthWallet = 0

#On passe chacun des index du tableau ci-haut.
for index, row in df.iterrows() :
    #ACHAT
    if row['close'] < row['SMA']*iZoneAchat and fBTC>0 :    
        fBTCTransaction = fBTC # Pour calculer la valeur de la transcation
        fCrypto = fBTC / row['close'] #Converti BTC en Coin comme si on vendait et on enlève les frais
        fFraisTransaction = fBTC * fFrais # Calculer les frais par principe
        fTotalFrais = fTotalFrais + fFraisTransaction # Calcul des frais total        
        fCrypto = fCrypto - (fFraisTransaction/row['close']) # Enlèver les frais par principe
        fBTC = 0 # on a tout échanger nos fBTC
        print(index,",ACHAT,",fCrypto,",FLUX,",row['close'],",",fFraisTransaction)  #Pour CSV  
    # VEND
    elif row['close'] >= row['SMA']*iZoneVente and fCrypto>0 :            
        fBTC = fCrypto * row['close']  #Converti les Coin en fBTC comme si on vendait et on enlève les frais
        fFraisTransaction = fCrypto * row['close'] * fFrais # Calcul des frais total
        fTotalFrais = fTotalFrais + fFraisTransaction # Calcul des frais total
        fBTC = fBTC - fFraisTransaction # Enlèver les frais par principe
        fCrypto = 0  # on a tout échanger nos fCrypto
        print(index,",VEND,",fBTC,",BTC,",row['close'],",",fFraisTransaction)  #Pour CSV  
       
        fPourcentageTransaction = (fBTC-fBTCTransaction)/fBTCTransaction*100 # Cherchons la plus meilleure ou pas transaction
        if fPourcentageTransaction > fMeilleureTransaction :
            fMeilleureTransaction = fPourcentageTransaction
            dtIndexMeilleur = index

        if fPourcentageTransaction < fPireTransaction :
            fPireTransaction = fPourcentageTransaction
            dtIndexPire = index
      
        if fBTCTransaction < fBTC: # Comptons les plus bonnes et les plus moins bonnes
            iTradeBon = iTradeBon + 1
            fTotalMeilleureTransaction = fTotalMeilleureTransaction + fPourcentageTransaction
        else :
            iTradePasBon = iTradePasBon + 1
            fTotalPireTransaction = fTotalPireTransaction + fPourcentageTransaction

        if fBTC > fAthWallet: # ATH du wallet
            fAthWallet = fBTC
            
if fBTC == 0 :
    print("Ne pas tenir compte du dernière achat")
    fMontantFinalWallet = fBTCTransaction
    
else :
    fMontantFinalWallet = fBTC # Montal final dans le Wallet

fPourcentageBot = ((fMontantFinalWallet - fBTCDepart)/fBTCDepart) * 100 # Performance du wallet
fPourcentageMaintien = ((df.iloc[len(df)-2]['close'] - df.iloc[0]['close'])/df.iloc[0]['close']) * 100 # Performence du maintien

if iTradeBon>0 :
    fPourcentageMoyenPositif = fTotalMeilleureTransaction/iTradeBon
else: 
    fPourcentageMoyenPositif = 0

if iTradePasBon>0 :    
    fPourcentageMoyenNegatif = fTotalPireTransaction/iTradePasBon
else :
    fPourcentageMoyenNegatif = 0


print("")
print("Période : [" + str(df.index[0]) + "] -> [" +str(df.index[len(df)-1]) + "]")
print("Montant Départ dans le wallet :",fBTCDepart,"BTC")
print("Montant final dans le wallet :", round(fMontantFinalWallet,2),"BTC")
print("Performance du wallet avec le Bot",round(fPourcentageBot,2),"%")
print("Performance du wallet avec maintien seulement",round(fPourcentageMaintien,2),"%")
print("Nombre de transactions positives:",iTradeBon)
print("Nombre de transactions négatives:",iTradePasBon)
print("Gain moyen par transaction positive:",round(fPourcentageMoyenPositif,2),"%")
print("Perte moyenne par transaction négative:",round(fPourcentageMoyenNegatif,2),"%")
print("La plus meilleure transaction",round(fMeilleureTransaction,2),"% ->",dtIndexMeilleur)
print("La plus pire transaction",round(fPireTransaction,2),"% ->",dtIndexPire)
print ("Frais total :",round(fTotalFrais,2),"BTC")


print("")
print("")
print("Période : [" + str(df.index[0]) + "] -> [" +str(df.index[len(df)-1]) + "]")
print(fBTCDepart)
print(fMontantFinalWallet) # Montal final dans le Wallet
print(round(fPourcentageBot,2)) # Performance du wallet
print(round(fPourcentageMaintien,2)) # Performence du maintien
print(iTradeBon) # Nombre de bonne transaction
print(iTradePasBon) #Nombre de pas bonne transaction
#print("----")
print(round(fPourcentageMoyenPositif,2)) # Pourcentage moyen par transaction positive
print(round(fPourcentageMoyenNegatif,2)) # Pourcentage moyen par transaction négative
#print("----")
print(round(fMeilleureTransaction,2),"% ->",dtIndexMeilleur)
print(round(fPireTransaction,2),"% ->",dtIndexPire)
#print("----")
print (fTotalFrais) # Frais total
