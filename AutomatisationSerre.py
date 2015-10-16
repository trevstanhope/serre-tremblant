"""
AutomatisationSerre.py

Bac 1
Valve/Humidity A,B
Lumiere A

Bac 2
Valve/Humidity C,D
Lumiere B

Nord
Valve/Humidity A,C

Sud
Valve/Humidity B,D
"""

import serial
import datetime
from tkinter import *
from tkinter import ttk
import os
import time
import json

#Texte pour le protocole de communication avec arduino. Utilisy pour la lecture de donnees du arduino -> raspberry pi
#R pour relais V pour valve
TexteRelaisValveA="RV_A"
TexteRelaisValveB="RV_B"
TexteRelaisValveC="RV_C"
TexteRelaisValveD="RV_D"

#R pour relais L pour lumiyre
TexteRelaisLumiereA="RL_A"
TexteRelaisLumiereB="RL_B"

#C pour capteur H pour Humidity
TexteCapteurHumiditeA="CH_A"
TexteCapteurHumiditeB="CH_B"
TexteCapteurHumiditeC="CH_C"
TexteCapteurHumiditeD="CH_D"

#L pour lumiyre
TexteCapteurLumiereA="CL_A"
TexteCapteurLumiereB="CL_B"

#Garde en memoire l'etat de chaque relais.
#0 off | 1 on
EtatRelaisValveA=0
EtatRelaisValveB=0
EtatRelaisValveC=0
EtatRelaisValveD=0
EtatRelaisLumiereA=0
EtatRelaisLumiereB=0

#Devient true lorsque les valeurs voulues par l'usage sont depassees par les donnees du capteurs
#Exemple: si l'usager veut un taux d'humidite de 60 et que l'humidite tombe a 59% la valve s'active
#Marque que l'ordinateur doit envoyer la commande de changement d'etat d'un relai a l'arduino
ChangementEtatRelaisValveA=False
ChangementEtatRelaisValveB=False
ChangementEtatRelaisValveC=False
ChangementEtatRelaisValveD=False
ChangementEtatRelaisLumiereA=False
ChangementEtatRelaisLumiereB=False

#valeur des capteurs
#capteur vegetronix vh400
#Garde en mémore les valeurs bruts directement envoyé du arduino.
ValeurCapteurHumiditeA=0.0
ValeurCapteurHumiditeB=0.0
ValeurCapteurHumiditeC=0.0
ValeurCapteurHumiditeD=0.0
ValeurCapteurLumiereA=0.0
ValeurCapteurLumiereB=0.0

# Voulue (Targets)
configpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Historique', 'Configuration')
with open(configpath, 'r') as configfile:
        config = json.loads(configfile.read())  
ValeurVoulueLumiereA	= config['LumiereA']
ValeurVoulueHumiditeA 	= config['HumiditeA']
ValeurVoulueHumiditeB 	= config['HumiditeB']
ValeurVoulueLumiereB 	= config['LumiereB']
ValeurVoulueHumiditeC 	= config['HumiditeC']
ValeurVoulueHumiditeD 	= config['HumiditeD']

#Sert à l'utilisation du module du lumière qui communique Série avec usb ttl-232 FTDI 
ModuleLumiereAEtat = False
ModuleLumiereBEtat = False
ModuleLumiereAMax = False
ModuleLumiereBMax = False

#Pour le repos des plantes la nuit. Sert à l'activation de l'éclairage de telle heure à telle heure.
#Initialisation à true pour que les lumières démarent fermées.
ArretEclairage = True

#Modifie la luminosité des modules de lumières en alternance, car chaque module affecte la luminosité détectée des capteurs des 2 bacs.
#Détermine quel module de lampe sera modifié.
AlternanceModuleLumiere = 'A'

#Protocole de communication du module de lampe qui communique série. Envoi la commande pour mettre le taux de lumière en %.
#CommandeAllumeLampes ="s LAMP.manual 100%"
#CommandeEteintLampes ="s LAMP.manual 0%"
CommandeModuleLumiere =" s lamp.manual "

#Garde en mémoire la puissance des LED en % des modules de lumière
ValeurModuleLumiereA = 0
ValeurModuleLumiereB = 0

#Sert pour l'écriture de l'historique et pour l'arrêt de l'éclairage la nuit
HeureActuelle = 0

#Pour écrire les valeurs des capteurs qu'une seule fois par heure dans l'historique
DerniereHeureEcritureHistorique = 0

#Utilisé pour initialiser les modules de lumière
PremierePasseLumiere = True

#Ouvre et initialise la communication série pour le arduino et les modules de lumière
ArduinoSerie = serial.Serial("/dev/ttyACM0",timeout =0.01,writeTimeout = None)
ModuleLampe = serial.Serial("/dev/ttyUSB0",115200)

#Sert à déterminer entre quelle heure et quelle heure l'éclairage est activé peu importe ce que l'usager a saisi dans l'interface.
#Sert à fournir une période de repos aux plantes.
HeureActivationEclairage = config['HeureActivationEclairage']
HeureArretEclairage = config['HeureArretEclairage']

#pour inverser la valeur des capteurs de lumière Bac 1 <-> Bac 2
InversionCapteurLumiere = True

#VR - Garde en mémoire les valeurs réelles des capteurs à partir des données bruts ajustés.
#L'Humidité est calculée en teneur en eau (volumetric water content)
VRHumA = 0
VRHumB = 0
VRHumC = 0
VRHumD = 0
VRLumA = 0
VRLumB = 0

#Garde en mémoire les états des Valves et états des Lumières à partir des données bruts ajustés.
EtatValveA = False
EtatValveB = False
EtatValveC = False
EtatValveD = False
EtatLumiereA = False
EtatLumiereB = False

#Garde en mémoire les valeurs voulues par l'usager d'humidité et de luminosité.       
HumiditeVoulueA = config["HumiditeA"]
HumiditeVoulueB = config["HumiditeB"]
HumiditeVoulueC = config["HumiditeC"]
HumiditeVoulueD = config["HumiditeD"]
LumiereVoulueA = config["LumiereA"]
LumiereVoulueB = config["LumiereB"]

#Garde en mémoire les états des valves et des lumières que l'usager aimerait avoir. Cela est déterminé par le programme selon les valeurs que l'usager a entré.
EtatValveAVoulue = False
EtatValveBVoulue = False
EtatValveCVoulue = False
EtatValveDVoulue = False
EtatLumiereAVoulue = False
EtatLumiereBVoulue = False

#Écrit un fichier avec plus d'information que l'historique
LogDebug = False

#Combien de boucle de lecture et d'écrite est écrit dans le fichier debug
DebugNombreDentree=10

#Compteur pour calculer le nombre d'entrée écrite 
DebugCompteurNombreEntree=0

#L'heure de la dernière écriture dans le fichier debug
DebugHeureDerniereEntree=0
    
#Va chercher toutes les valeurs des capteurs et les états des relais du Arduino
def LitValeurArduino():
                #Lit une ligne du arduino contenant l'ensemble des états et des valeurs des capteurs
                #Exemple d'une ligne: RV_A:0 RV_B:1 RV_C:0 RV_D:0 RL_A:1 RL_B:0 CH_A:6525 CH_B:4536 CH_C:5814 CH_D:5454 CL_A:2005 CL_B:4102
                #Sépare et garde en mémoire chaque valeur que le arduino a envoyée
    
                ligneArduino = str(ArduinoSerie.readline())            
                #print(ligneArduino)
                if(ligneArduino!=-1):
                        mots = ligneArduino.split(" ")
                        for mot in mots:
                                var = mot.split(":")
                                if len(var)==2:
                                        try :
                                                
                                                if(var[0] == TexteRelaisValveA):
                                                        global EtatRelaisValveA
                                                        EtatRelaisValveA = int(var[1])
                                                        
                                                if(var[0] == TexteRelaisValveB):
                                                        global EtatRelaisValveB
                                                        EtatRelaisValveB = int(var[1])
                                                        
                                                if(var[0] == TexteRelaisValveC):
                                                        global EtatRelaisValveC
                                                        EtatRelaisValveC = int(var[1])
                                                        
                                                if(var[0] == TexteRelaisValveD):
                                                        global EtatRelaisValveD
                                                        EtatRelaisValveD = int(var[1])
                                                        
                                                if(var[0] == TexteRelaisLumiereA):
                                                        global EtatRelaisLumiereA
                                                        EtatRelaisLumiereA = int(var[1])
                                                        
                                                if(var[0] == TexteRelaisLumiereB):
                                                        global EtatRelaisLumiereB
                                                        EtatRelaisLumiereB = int(var[1])
                                                        
                                                if(var[0] == TexteCapteurHumiditeA):
                                                        global ValeurCapteurHumiditeA
                                                        ValeurCapteurHumiditeA = int(var[1])
                                                        
                                                if(var[0] == TexteCapteurHumiditeB):
                                                        global ValeurCapteurHumiditeB
                                                        ValeurCapteurHumiditeB = int(var[1])
                                                        
                                                if(var[0] == TexteCapteurHumiditeC):
                                                        global ValeurCapteurHumiditeC
                                                        ValeurCapteurHumiditeC = int(var[1])
                                                        
                                                if(var[0] == TexteCapteurHumiditeD):
                                                        global ValeurCapteurHumiditeD
                                                        ValeurCapteurHumiditeD = int(var[1])

                                                #Condition pour inverser les capteurs d'humidité(bac1<-->bac2), les fils on été inversés.         
                                                global ValeurCapteurLumiereA
                                                global ValeurCapteurLumiereB
                                                if(var[0] == TexteCapteurLumiereA):
                                                        if(InversionCapteurLumiere is False):
                                                            ValeurCapteurLumiereA = int(var[1])
                                                        else:
                                                            ValeurCapteurLumiereB = int(var[1])
                                                        
                                                if(var[0] == TexteCapteurLumiereB):
                                                        if(InversionCapteurLumiere is False):
                                                            ValeurCapteurLumiereB = int(var[1])
                                                        else:
                                                            ValeurCapteurLumiereA = int(var[1])

                                        except:
                                                pass

#Fais la gestion du module de lumière. Ne gère pas les LED dans les bacs au sol, ils sont gérés par les relais et le temps d'éclairage.
def CommunicationModulesLampe():
    global ModuleLumiereAEtat
    global ModuleLumiereBEtat
    global ModuleLumiereAMax
    global ModuleLumiereBMax
    global ValeurModuleLumiereA
    global ValeurModuleLumiereB
    global PremierePasseLumiere
    global AlternanceModuleLumiere
    ModuleAEtatChange=False
    ModuleBEtatChange=False

    #Si le programme vient tout juste de démarrer, on initialise les modules de lumière en les éteingnants
    if(PremierePasseLumiere is True):
        try:
            ModuleLampe.write(('1:1'+CommandeModuleLumiere+str(0)+'%' +'\r').encode("ASCII"))
            ModuleLampe.write(('1:2'+CommandeModuleLumiere+str(0)+'%' +'\r').encode("ASCII"))
            ModuleLampe.write(('1:3'+CommandeModuleLumiere+str(0)+'%' +'\r').encode("ASCII"))
            ModuleLampe.write(('1:4'+CommandeModuleLumiere+str(0)+'%' +'\r').encode("ASCII"))
        except:
            ModuleLampe.close()
            ModuleLampe.open()
        PremierePasseLumiere = False

    #On ferme les lumières si c'est la nuit(ou les heures d'éclairage décidées)
    if (ArretEclairage is True):
        if(ValeurModuleLumiereA !=0) and (ValeurModuleLumiereB!=0):
            ModuleLumiereAEtat = False
            ModuleLumiereAMax = False
            try:
                ModuleLampe.write(('1:1'+CommandeModuleLumiere+str(0)+'%' +'\r').encode("ASCII"))
                ModuleLampe.write(('1:2'+CommandeModuleLumiere+str(0)+'%' +'\r').encode("ASCII"))
                ModuleLampe.write(('1:3'+CommandeModuleLumiere+str(0)+'%' +'\r').encode("ASCII"))
                ModuleLampe.write(('1:4'+CommandeModuleLumiere+str(0)+'%' +'\r').encode("ASCII"))
            except:
                ModuleLampe.close()
                ModuleLampe.open()
            ValeurModuleLumiereA = 0
            ValeurModuleLumiereB = 0

    #Sinon, on modifie la valeur des lampes afin d'atteindre la luminosité décidée par l'usager
    else:
        #Un à La fois à cause de l'interférence de lux entre les lampes et les capteurs
        if (AlternanceModuleLumiere == 'A'):
            if (LumiereVoulueA > VRLumA) and (ModuleLumiereAMax is False):
                ValeurModuleLumiereA+=1
                ModuleAEtatChange =True
            elif (LumiereVoulueA < VRLumA) and (ModuleLumiereAEtat is True):
                ValeurModuleLumiereA-=1
                ModuleAEtatChange =True
            AlternanceModuleLumiere = 'B'
        elif (AlternanceModuleLumiere == 'B'):    
            if (LumiereVoulueB > VRLumB) and (ModuleLumiereBMax is False):
                ValeurModuleLumiereB+=1
                ModuleBEtatChange =True
            elif (LumiereVoulueB < VRLumB) and (ModuleLumiereBEtat is True):
                ValeurModuleLumiereB-=1
                ModuleBEtatChange =True
            AlternanceModuleLumiere = 'A'
        
        if ValeurModuleLumiereA <=0:
            ModuleLumiereAEtat = False
            ModuleLumiereAMax = False
        else:
            ModuleLumiereAEtat = True
        
        # LumiereA
        if ValeurModuleLumiereA >=100:
            ModuleLumiereAEtat = True
            ModuleLumiereAMax = True
        else:
            ModuleLumiereAMax = False

        if ValeurModuleLumiereB <=0:
            ModuleLumiereBEtat = False
            ModuleLumiereBMax = False
        else:
            ModuleLumiereBEtat = True
            
        if ValeurModuleLumiereB >=100:
            ModuleLumiereBEtat = True
            ModuleLumiereBMax = True
        else:
            ModuleLumiereBMax = False

        #On envoie la commande aux lampes si l'on doit changer l'intensité des lumières.
        try:
            if (ModuleAEtatChange is True):
                ModuleLampe.write(('1:1'+CommandeModuleLumiere+str(ValeurModuleLumiereA)+'%' +'\r').encode("ASCII"))
                ModuleLampe.write(('1:2'+CommandeModuleLumiere+str(ValeurModuleLumiereA)+'%' +'\r').encode("ASCII"))
                ModuleAEtatChange = False
            if (ModuleBEtatChange is True):
                ModuleLampe.write(('1:3'+CommandeModuleLumiere+str(ValeurModuleLumiereB)+'%' +'\r').encode("ASCII"))
                ModuleLampe.write(('1:4'+CommandeModuleLumiere+str(ValeurModuleLumiereB)+'%' +'\r').encode("ASCII"))
                ModuleAEtatChange = False                
        except:
            ModuleLampe.close()
            ModuleLampe.open()
            
    #On se débarrasse de tous les retours que le module pourrait nous renvoyer
    ModuleLampe.flushInput()

#Appelle la fonction de lecture des états et des valeurs des capteurs du Arduino et envois une commande pour activer ou éteindre un relais.
def CommunicationArduino():
    global ChangementEtatRelaisValveA
    global ChangementEtatRelaisValveB
    global ChangementEtatRelaisValveC
    global ChangementEtatRelaisValveD
    global ChangementEtatRelaisLumiereA
    global ChangementEtatRelaisLumiereB
    #Exemple du protocole A1--> Active la valve du Bac 1 Nord E0-->éteint le ralais des lumière au sol du Bac 1
    try:
        #Lit 5 fois pour être certain d'avoir les bonnes données
        for x in range(0,5): 
            LitValeurArduino()
        #Envoi une seule commande à la fois pour le arduino pour ne pas le submerger de données
        if(ChangementEtatRelaisValveA is True):
            if EtatValveAVoulue is True:
                ArduinoSerie.write(("A"+str(1)+'\n').encode("ASCII"))
            if EtatValveAVoulue is False:
                ArduinoSerie.write(("A"+str(0)+'\n').encode("ASCII"))
            ChangementEtatRelaisValveA = False
        elif(ChangementEtatRelaisValveB is True):
            if EtatValveBVoulue is True:
                ArduinoSerie.write(("B"+str(1)+'\n').encode("ASCII"))
            if EtatValveBVoulue is False:
                ArduinoSerie.write(("B"+str(0)+'\n').encode("ASCII"))
            ChangementEtatRelaisValveB = False
        elif(ChangementEtatRelaisValveC is True):
            if EtatValveCVoulue is True:
                ArduinoSerie.write(("C"+str(1)+'\n').encode("ASCII"))
            if EtatValveCVoulue is False:
                 ArduinoSerie.write(("C"+str(0)+'\n').encode("ASCII"))
            ChangementEtatRelaisValveC = False
        elif(ChangementEtatRelaisValveD is True):
            if EtatValveDVoulue is True:
                ArduinoSerie.write(("D"+str(1)+'\n').encode("ASCII"))
            if EtatValveDVoulue is False:
                ArduinoSerie.write(("D"+str(0)+'\n').encode("ASCII"))
            ChangementEtatRelaisValveD = False
        elif(ChangementEtatRelaisLumiereA is True):
            if EtatLumiereAVoulue is True:
                ArduinoSerie.write(("E"+str(1)+'\n').encode("ASCII"))
            if EtatLumiereAVoulue is False:
                ArduinoSerie.write(("E"+str(0)+'\n').encode("ASCII"))
            ChangementEtatRelaisLumiereA = False
        #TODO One of these is not used    
        elif(ChangementEtatRelaisLumiereB is True):
            if EtatLumiereBVoulue is True:
                ArduinoSerie.write(("F"+str(1)+'\n').encode("ASCII"))
            if EtatLumiereBVoulue is False:
                ArduinoSerie.write(("F"+str(0)+'\n').encode("ASCII"))
            ChangementEtatRelaisLumiereB = False
    except:
        ArduinoSerie.close()
        ArduinoSerie.open()
    ArduinoSerie.flushInput()
    
#Sert à modifier les valeurs dans l'interface afin d'afficher les données entrées de l'usager lorsqu'il appuie sur un bouton    
def humA():
   global HumiditeVoulueA
   HumiditeVoulueA = int(HumA.get())
   config['HumiditeA'] = HumiditeVoulueA
   writeConfig()
   valeur = str(HumiditeVoulueA)
   selection = "Nord_teneur en eau voulue:" + valeur +'%'
   LHumA.config(text=selection, font=FonteTexte)
def humB():
   global HumiditeVoulueB
   HumiditeVoulueB = int(HumB.get())
   config['HumiditeB'] = HumiditeVoulueB
   writeConfig()
   valeur = str(HumiditeVoulueB)
   selection = "Sud_teneur en eau voulue:" + valeur +'%'
   LHumB.config(text=selection, font=FonteTexte)
def humC():
   global HumiditeVoulueC
   HumiditeVoulueC = int(HumC.get())
   config['HumiditeC'] = HumiditeVoulueC
   writeConfig()
   valeur = str(HumiditeVoulueC)  
   selection = "Nord_teneur en eau voulue:" + valeur +'%'
   LHumC.config(text=selection, font=FonteTexte)
def humD():
   global HumiditeVoulueD
   HumiditeVoulueD = int(HumD.get())
   config['HumiditeD'] = HumiditeVoulueD
   writeConfig()
   valeur = str(HumiditeVoulueD)
   selection = "Sud_teneur en eau voulue:" + valeur +'%'
   LHumD.config(text=selection, font=FonteTexte)
def lumA():
   global LumiereVoulueA
   LumiereVoulueA = int(LumA.get())
   config['LumiereA'] = LumiereVoulueA
   writeConfig()
   valeur = str(LumiereVoulueA)   
   selection = "Lumière Voulue:" + valeur +'%'
   LLumA.config(text = selection, font=FonteTexte)
def lumB():
   global LumiereVoulueB
   LumiereVoulueB = int(LumB.get())
   config['LumiereB'] = LumiereVoulueB
   writeConfig()
   valeur = str(LumiereVoulueB)   
   selection = "Lumière Voulue:" + valeur +'%'
   LLumB.config(text = selection, font=FonteTexte)
def writeConfig():
   with open(configpath, 'w') as configfile:
      configfile.write(json.dumps(config, indent=4))
def OnOFF(var):
   if var == 0:
      return "OFF"
   else:
      return "ON"
def LumiereKill():
    global HeureArretEclairage
    if ArretEclairage:
        HeureArretEclairage = config['HeureArretEclairage']
    else:
        HeureArretEclairage = HeureActuelle
    print("Lumiere Killed! %d" % HeureArretEclairage)

#Regarde si l'heure à changé et note l'heure actuelle.
#Appel les fonctions pour l'historique et celle de la fonction de repos des plantes pour la nuit.
def MiseAJourHeureActuelle():
   LeTemps = str(datetime.datetime.time(datetime.datetime.now()))
   LeTempsSepare=LeTemps.split(":")
   Heure= LeTempsSepare[0]
   global HeureActuelle
   HeureActuelle =int(Heure)
   print("Current Hour/OFF Hour : %d/%d" % (HeureActuelle, HeureArretEclairage)
   VerifieHeure()
   Historique()
   #Pour des tests seulement.
   if(LogDebug is True):
       Debug() 

#Écrit un historique à toutes les heures des valeurs des capteurs.
def Historique():
    global DerniereHeureEcritureHistorique
    if(DerniereHeureEcritureHistorique != HeureActuelle):
        filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Historique', 'Donnees')
        file = open(filepath, 'a+')
        if(HeureActuelle == 0):
            date = str(datetime.datetime.now().date())
            file.write('\n'+date+'\n')
        file.write(str(HeureActuelle)+'H ')
        file.write('Bac1:Humidité Nord:'+str(VRHumA)+'%'+' Humidité Sud:'+str(VRHumB)+'%'+' Luminosité:'+str(VRLumA)+'% ')
        file.write('Bac2:Humidité Nord:'+str(VRHumC)+'%'+' Humidité Sud:'+str(VRHumD)+'%'+' Luminosité:'+str(VRLumB)+'%'+'\n')
        file.close()
        DerniereHeureEcritureHistorique = HeureActuelle

#Marque toutes les données des capteurs et des relais ainsi que les valeurs brutes que le arduino envoie.        
def Debug():
    global DebugFile
    global DebugCompteurNombreEntree
    global DebugHeureDerniereEntree
    DebugFile = open('Debug/Log', 'a+')
    if(DebugHeureDerniereEntree != HeureActuelle):
        if(DebugCompteurNombreEntree < DebugNombreDentree):
            if(HeureActuelle == 0):
                date = str(datetime.datetime.now().date())
                DebugFile.write('\n'+date+'\n')
            DebugFile.write(str(HeureActuelle)+'H ')
            DebugFile.write('Bac1:Humidité Nord:'+str(VRHumA)+'%'+' Humidité Sud:'+str(VRHumB)+'%'+' Luminosité:'+str(VRLumA)+'% ')
            DebugFile.write('Bac2:Humidité Nord:'+str(VRHumC)+'%'+' Humidité Sud:'+str(VRHumD)+'%'+' Luminosité:'+str(VRLumB)+'%'+'\n')
            DebugFile.write('Bac1Arduino:ValeurCapteurHumiditeANord:'+str(ValeurCapteurHumiditeA)+'%'+' ValeurCapteurHumiditeBSud:'+str(ValeurCapteurHumiditeB)+'%'+' ValeurCapteurLumiereA:'+str(ValeurCapteurLumiereA)+'% ')
            DebugFile.write('Bac2Arduino:ValeurCapteurHumiditeCNord:'+str(ValeurCapteurHumiditeC)+'%'+' ValeurCapteurHumiditeDSud:'+str(ValeurCapteurHumiditeD)+'%'+' ValeurCapteurLumiereB:'+str(ValeurCapteurLumiereB)+'%'+'\n')
            DebugFile.write('Bac1ArduinoRelais:EtatRelaisValveANord:'+str(EtatRelaisValveA)+'%'+' EtatRelaisValveBSud:'+str(EtatRelaisValveB)+'%'+' EtatRelaisLumiereA:'+str(EtatRelaisLumiereA)+'% ')
            DebugFile.write('Bac2ArduinoRelais:EtatRelaisValveCNord:'+str(EtatRelaisValveC)+'%'+' EtatRelaisValveDSud:'+str(EtatRelaisValveD)+'%'+' EtatRelaisLumiereB:'+str(EtatRelaisLumiereB)+'%'+'\n')
            DebugCompteurNombreEntree += 1
        else:
            DebugHeureDerniereEntree = HeureActuelle
            DebugCompteurNombreEntree =0
    DebugFile.close()

#Définie le temps d'éclairage pour le repos des plantes la nuit.
#s'occupe de vérifier s'il faut éteindre les lumières selon l'heure.
def VerifieHeure():
    global ArretEclairage
    global HeureArretEclairage
    if (HeureActuelle<HeureActivationEclairage) or (HeureActuelle>HeureArretEclairage):      
        ArretEclairage = True
    else:
        ArretEclairage = False
        HeureArretEclairage = config['HeureArretEclairage']

#Détermine s'il faut activer ou éteindre un relais selon la valeur des capteurs et les données que l'usager a saisies.
def MiseAJourEtatEtValeurReel():
   global EtatValveAVoulue
   global EtatValveBVoulue
   global EtatValveCVoulue
   global EtatValveDVoulue
   global EtatLumiereAVoulue
   global EtatLumiereBVoulue
   MiseAJourHeureActuelle()
   ChangeEtat()
   if (HumiditeVoulueA > VRHumA):
      EtatValveAVoulue = True
   else:
      EtatValveAVoulue = False
   if (HumiditeVoulueB > VRHumB):
      EtatValveBVoulue = True
   else:
      EtatValveBVoulue = False
   if (HumiditeVoulueC > VRHumC):
      EtatValveCVoulue = True
   else:
      EtatValveCVoulue = False   
   if (HumiditeVoulueD > VRHumD):
      EtatValveDVoulue = True
   else:
      EtatValveDVoulue = False
   if (ArretEclairage is True):
      EtatLumiereAVoulue = False
      EtatLumiereBVoulue = False
   else:
      EtatLumiereAVoulue = True
      EtatLumiereBVoulue = True
   
#Détermine s'il y a un changement qui doit être effectué au niveau de l'activation des relais.
#Met à jour les états dans l'interface.
def ChangeEtat():
   global EtatValveA
   global EtatValveB
   global EtatValveC
   global EtatValveD
   global EtatLumiereA
   global EtatLumiereB
   global ChangementEtatRelaisValveA
   global ChangementEtatRelaisValveB
   global ChangementEtatRelaisValveC
   global ChangementEtatRelaisValveD
   global ChangementEtatRelaisLumiereA
   global ChangementEtatRelaisLumiereB
   
   if(EtatRelaisValveA==0):
       EtatValveA=False
   if(EtatRelaisValveA==1):
       EtatValveA=True
   if(EtatRelaisValveB==0):
       EtatValveB=False
   if(EtatRelaisValveB==1):
       EtatValveB=True
   if(EtatRelaisValveC==0):
       EtatValveC=False
   if(EtatRelaisValveC==1):
       EtatValveC=True
   if(EtatRelaisValveD==0):
       EtatValveD=False
   if(EtatRelaisValveD==1):
       EtatValveD=True    
   if(EtatRelaisLumiereA==0):
       EtatLumiereA=False
   if(EtatRelaisLumiereA==1):
       EtatLumiereA=True    
   if(EtatRelaisLumiereB==0):
       EtatLumiereB=False
   if(EtatRelaisLumiereB==1):
       EtatLumiereB=True
       
   if(EtatValveA!=EtatValveAVoulue):
       ChangementEtatRelaisValveA =True  
   if(EtatValveB!=EtatValveBVoulue):
       ChangementEtatRelaisValveB =True 
   if(EtatValveC!=EtatValveCVoulue):
       ChangementEtatRelaisValveC =True 
   if(EtatValveD!=EtatValveDVoulue):
       ChangementEtatRelaisValveD =True 
   if(EtatLumiereA!=EtatLumiereAVoulue):
       ChangementEtatRelaisLumiereA =True 
   if(EtatLumiereB!=EtatLumiereBVoulue):
       ChangementEtatRelaisLumiereB =True 

#Fonction principale qui appelle toutes les autres fonctions et met à jour l'interface
#Cette fonction est appelée toutes les 2 secondes
def MiseAjourInterface():
   MiseAJourEtatEtValeurReel()
   
   global VRHumA
   global VRHumB
   global VRHumC
   global VRHumD
   global VRLumA
   global VRLumB
   
   #Division par cent parce que arduino fait la valeur du capteur multiplié par cent pour envoyer un entier et garder 2 décimales.
   VRHumA=(ValeurCapteurHumiditeA/100.0)
   VRHumB=(ValeurCapteurHumiditeB/100.0)
   VRHumC=(ValeurCapteurHumiditeC/100.0)
   VRHumD=(ValeurCapteurHumiditeD/100.0)

   #134 détermine l'amplitude des valeurs à aller chercher et donne environ 97.5% le jour en juillet et 30% à 60% la nuit avec de la lumière ambiante. 
   if(ValeurCapteurLumiereA < 0):
       VRLumA = 0
   else:
       VRLumA=100.0-(ValeurCapteurLumiereA/134.0)
          
   if(ValeurCapteurLumiereB < 0):
       VRLumB = 0
   else:
       VRLumB=100.0-(ValeurCapteurLumiereB/134.0)

   #S'assure que les valeurs ne sont pas négatives ou ne dépassent pas 100%
   #Si les valeurs sont au dessus de 100% ou en dessous de 0, c'est probablement un débordement de tableau
   #On les initialise donc à 0.    
   if(VRLumA>=100):
       VRLumA=0
   if(VRLumB>=100):
       VRLumB=0
   if(VRLumA<0):
       VRLumA=0
   if(VRLumB<0):
       VRLumB=0
   #Arrondie à 2 décimal, les valeurs des capteurs.
   VRLumA=round(VRLumA,2)
   VRLumB=round(VRLumB,2)     

   #Les états
   #Affiche en rouge si la valve ou les lumières sont fermées ou en Vert si elles sont allumées.
   texte = 'Valve nord:'+ str(OnOFF(EtatValveA))
   if(EtatValveA is False):     
      LEtatValveA.configure(text = texte,background="red",relief ="raised")
   else:
      LEtatValveA.configure(text = texte,background="green",relief ="raised")
      
   texte = 'Valve sud:'+ str(OnOFF(EtatValveB))
   if(EtatValveB is False):
      LEtatValveB.configure(text = texte,background="red",relief ="raised")
   else:
      LEtatValveB.configure(text = texte,background="green",relief ="raised")
      
   texte = 'Valve nord:'+ str(OnOFF(EtatValveC))     
   if(EtatValveC is False):
      LEtatValveC.configure(text = texte,background="red",relief ="raised")
   else:
      LEtatValveC.configure(text = texte,background="green",relief ="raised")
      
   texte = 'Valve sud:'+ str(OnOFF(EtatValveD))  
   if(EtatValveD is False):
      LEtatValveD.configure(text = texte,background="red",relief ="raised")
   else:
      LEtatValveD.configure(text = texte,background="green",relief ="raised")

   texte = 'Lumière:'+ str(ValeurModuleLumiereA)+'%'   
   if(ModuleLumiereAEtat is False):
      LEtatLumiereA.configure(text = texte,background="red",relief ="raised")
   else:
      LEtatLumiereA.configure(text = texte,background="green",relief ="raised")
      
   texte = 'Lumière:'+ str(ValeurModuleLumiereB)+'%'   
   if(ModuleLumiereBEtat is False):
      LEtatLumiereB.configure(text = texte,background="red",relief ="raised")
   else:
      LEtatLumiereB.configure(text = texte,background="green",relief ="raised")

   #Affiche les valeurs des capteurs dans l'interface.
   LVRHumA.configure(text='Nord_teneur en eau réelle:'+str("%.2f" % VRHumA)+'%', font =FonteTexte)
   LVRHumB.configure(text='Sud_teneur en eau réelle:'+str("%.2f" % VRHumB)+'%', font =FonteTexte)
   LVRHumC.configure(text='Nord_teneur en eau réelle:'+str("%.2f" % VRHumC)+'%', font =FonteTexte)
   LVRHumD.configure(text='Sud_teneur en eau réelle:'+str("%.2f" % VRHumD)+'%', font =FonteTexte)
   LVRLumA.configure(text ='Lumière Réelle:'+str("%.2f" % VRLumA)+'%',font =FonteTexte)
   LVRLumB.configure(text='Lumière Réelle:'+str("%.2f" % VRLumB)+'%',font =FonteTexte)

   #Appel les modules de communication externe comme le arduino et les modules de lumière
   CommunicationArduino()
   CommunicationModulesLampe()

   #Fais rouler le programme en boucle afin d'être actif tant que le programme n'est pas fermé par l'usager.
   root.after(2000,MiseAjourInterface)

#Crée l'interface et l'initialise. 
root = Tk()
root.title("Automatisation De Serre")
root.geometry("1200x600")

#Place les colones et les lignes dans l'interface qui afficheront les contrôles de l'interface
i=1
while i!=4:
   root.columnconfigure(i,weight=1)
   i+=1
i=1
while i!=13:
   root.rowconfigure(i,weight=1)
   i+=1

#La police de caractères de l'interface
FonteTexte = "Arial 11 bold"

#Initalise les variables en double tkinter
HumA = DoubleVar()
HumB = DoubleVar()
HumC = DoubleVar()
HumD = DoubleVar()
LumA = DoubleVar()
LumB = DoubleVar()

#Affiche les curseurs dans l'interface et les boutons
#On peut changer la résolution des curseurs avec resolution = 0.1 ou resolution = x
scaleA = Scale(root, from_=0.0, to=100.0, length=200,orient=HORIZONTAL,variable = HumA, font =FonteTexte)
scaleA.grid(column=1, row=2,ipady=20)
scaleA.set(config['HumiditeA'])
labelblanc = ttk.Separator(root, orient=VERTICAL,)
labelblanc.grid(column=3, row=1,sticky="nsw", rowspan=12)
buttonA = Button(root, text="Régler la teneur en eau nord", command=humA, font =FonteTexte)
buttonA.grid(column=1, row=3)

# HumiditeB
scaleB = Scale( root, from_=0.0, to=100.0, length=200,orient=HORIZONTAL,variable = HumB , font =FonteTexte)
scaleB.grid(column=2, row=2,ipady=20)
scaleB.set(config['HumiditeB'])
buttonB = Button(root, text="Régler la teneur en eau sud", command=humB, font =FonteTexte)
buttonB.grid(column=2, row=3)

# HumiditeC
scaleC = Scale( root, from_=0, to=100,length=200,orient=HORIZONTAL, variable = HumC , font =FonteTexte)
scaleC.grid(column=3, row=2,ipady=20)
scaleC.set(config['HumiditeC'])
buttonC = Button(root, text="Régler la teneur en eau nord", command=humC, font =FonteTexte)
buttonC.grid(column=3, row=3)

# HumiditeD
scaleD = Scale( root, from_=0, to=100,length=200,orient=HORIZONTAL,variable = HumD, font =FonteTexte )
scaleD.grid(column=4, row=2,padx=30,ipady=20)
scaleD.set(config['HumiditeD'])         
buttonD = Button(root, text="Régler la teneur en eau sud", command=humD, font =FonteTexte)
buttonD.grid(column=4, row=3)

# LumiereA
scaleE = Scale( root, from_=0, to=100,length=200,orient=HORIZONTAL,variable = LumA, font =FonteTexte )
scaleE.grid(column=1, row=8, columnspan =2,ipady=20)
scaleE.set(config['LumiereA'])
buttonE = Button(root, text="Régler Lumière", command=lumA, font =FonteTexte)
buttonE.grid(column=1, row=9, columnspan =2)

# LumiereB
scaleF = Scale( root, from_=0, to=100,length=200,orient=HORIZONTAL,variable = LumB, font =FonteTexte )
scaleF.grid(column=3, row=8, columnspan=2,ipady=20)
scaleF.set(config['LumiereB'])
buttonF = Button(root, text="Régler Lumière", command=lumB, font =FonteTexte)
buttonF.grid(column=3, row=9,columnspan =2)

#Affiche les valeurs des capteurs, ainsi que les textes descriptifs.
BacA =  Label(root, text='Bac 1:',font = "Arial 16 bold")
BacA.grid(column=1, row=1,columnspan=2)
BacA =  Label(root, text='Bac 2:',font = "Arial 16 bold")
BacA.grid(column=3, row=1,columnspan=2)

KillSwitch = Button(root, text="Kill Switch", command=LumiereKill, font = FonteTexte)
KillSwitch.grid(column=3, row=1,columnspan=2)

TVRHumA= str(VRHumA)
TVRHumB= str(VRHumB)
TVRHumC= str(VRHumC)
TVRHumD= str(VRHumD)

LVRHumA = Label(root, text='Nord_teneur en eau réelle:'+TVRHumA+'%', font =FonteTexte)
LVRHumA.grid(column=1, row=5)
LVRHumB = Label(root, text='Sud_teneur en eau réelle:'+TVRHumB+'%', font =FonteTexte)
LVRHumB.grid(column=2, row=5)
LVRHumC= Label(root, text='Nord_teneur en eau réelle:'+TVRHumC+'%', font =FonteTexte)
LVRHumC.grid(column=3, row=5)
LVRHumD = Label(root, text='Sud_teneur en eau réelle:'+TVRHumD+'%', font =FonteTexte)
LVRHumD.grid(column=4, row=5)
LVRLumA = Label(root, text='Lumière Réelle:'+str(VRLumA)+'%',font =FonteTexte)
LVRLumA.grid(column=1, row=10,columnspan =2)
LVRLumB = Label(root, text='Lumière Réelle:'+str(VRLumB)+'%',font =FonteTexte)
LVRLumB.grid(column=3, row=10,columnspan =2)

LHumA = Label(root)
LHumB = Label(root)
LHumC = Label(root)
LHumD = Label(root)
LLumA = Label(root)
LLumB = Label(root)

#Initialise tout à 0 dans l'interface.
LHumA = Label(root, text='Nord_teneur en eau voulue:'+str(config["HumiditeA"])+'%',font =FonteTexte)
LHumA.grid(column=1, row=6)
LHumB = Label(root, text='Sud_teneur en eau voulue:'+str(config["HumiditeB"])+'%',font =FonteTexte)
LHumB.grid(column=2, row=6)
LHumC = Label(root, text='Nord_teneur en eau voulue:'+str(config["HumiditeC"])+'%',font =FonteTexte)
LHumC.grid(column=3, row=6)
LHumD = Label(root, text='Sud_teneur en eau Voulue:'+str(config["HumiditeD"])+'%',font =FonteTexte)
LHumD.grid(column=4, row=6)
LLumA = Label(root, text='Lumière Voulue:'+str(config["LumiereA"])+'%',font =FonteTexte)
LLumA.grid(column=1, row=11,columnspan =2)
LLumB = Label(root, text='Lumière Voulue:'+str(config["LumiereB"])+'%',font =FonteTexte)
LLumB.grid(column=3, row=11,columnspan =2)

#Affichage des états des Valves et Lumière dans l'interface.
LEtatValveA = Label(root, text='ValveA:'+str(OnOFF(EtatValveA)),font =FonteTexte)
if(EtatValveA == 0):
   LEtatValveA.configure(background="red",relief ="raised")
else:
   LEtatValveA.configure(background="green",relief ="raised")   
LEtatValveA.grid(column=1, row=7,ipady=10)

LEtatValveB = Label(root, text='ValveB:'+str(OnOFF(EtatValveB)),font =FonteTexte)
if(EtatValveB == 0):
   LEtatValveB.configure(background="red",relief ="raised")
else:
   LEtatValveB.configure(background="green",relief ="raised") 
LEtatValveB.grid(column=2, row=7,ipady=10)

LEtatValveC= Label(root, text='ValveC:'+str(OnOFF(EtatValveC)),font =FonteTexte)
if(EtatValveC == 0):
   LEtatValveC.configure(background="red",relief ="raised")
else:
   LEtatValveC.configure(background="green",relief ="raised") 
LEtatValveC.grid(column=3, row=7,ipady=10)

LEtatValveD = Label(root, text='ValveD:'+str(OnOFF(EtatValveD)),font =FonteTexte)
if(EtatValveD == 0):
   LEtatValveD.configure(background="red",relief ="raised")
else:
   LEtatValveD.configure(background="green",relief ="raised") 
LEtatValveD.grid(column=4, row=7,ipady=10)

LEtatLumiereA = Label(root, text='LumiereA:'+str(OnOFF(EtatLumiereA)),font =FonteTexte)
if(EtatLumiereA == 0):
   LEtatLumiereA.configure(background="red",relief ="raised")
else:
   LEtatLumiereA.configure(background="green",relief ="raised") 
LEtatLumiereA.grid(column=1, row=12,columnspan =2,ipady=10)

LEtatLumiereB = Label(root, text='LumiereB:'+str(OnOFF(EtatLumiereB)),font =FonteTexte)
if(EtatLumiereB == 0):
   LEtatLumiereB.configure(background="red",relief ="raised")
else:
   LEtatLumiereB.configure(background="green",relief ="raised") 
LEtatLumiereB.grid(column=3, row=12, columnspan =2,ipady=10)

#Appel la fonction principal du programme.
MiseAjourInterface()

#Appelle le programme en boucle.
root.mainloop()
