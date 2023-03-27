import math as mt

#Fonction qui calcule la vitesse entre deux points, retourne un tableau de vitesse
def speed_calcul(x,y,time):
    """Fonction qui calcule la vitesse entre deux points"""
    speed = []
    for i in range(len(x)-1):
        speed.append(mt.sqrt(((x[i+1]-x[i])**2+(y[i+1]-y[i])**2))/(time[i+1]-time[i]))
    return speed #Liste en pixel par seconde

#Fonction qui compare la vitesse entre deux points avec un seuil, et indique si le regard est fixé ou non 
def fixation_velocity(threshold_speed,x,y,time): 
    """Fonction qui compare la vitesse entre deux points avec un seuil, et indique si le regard est fixé ou non"""
    speed = speed_calcul(x,y,time)
    tab_fixation = []
    fixation = []
    saccade = []
    rayon = []
    #Conversion du seuil en seconde : 
    threshold_speed = threshold_speed*1000
    for i in range(len(x)-1):
        print('speed = ',speed[i])
        if speed[i] < threshold_speed : # On a une fixation 
            tab_fixation.append("Fixation")
            
        else : # On a un mouvement
            tab_fixation.append("Saccade")
            print('Saccade')
        if tab_fixation[i] == "Fixation":
            fixation.append((x[i],y[i],time[i],speed[i],))
        else:
            saccade.append((x[i],y[i]))
        print('Nature = ',tab_fixation[i])
    return tab_fixation,fixation,saccade


def fixation_velocity(threshold_speed, x, y, time): # Le tableau time est en secondes 
    """Fonction qui compare la vitesse entre deux points avec un seuil """
    All_Points_Not_Searched = True #Flag pour savoir si on a parcouru tous les points
    threshold_time = 0.03 # Seuil de temps pour définir une saccade minimum (en secondes)
    threshold_speed = threshold_speed*1000 #Conversion du seuil en seconde :
    duration = 0 

    tab_fixation = []
    
    temps_start = time 
    temps_end = time 
    speed = speed_calcul(x,y,time)
    for i in range(len(x)-1):
        while(time[i+1]-time[i]< threshold_time and  All_Points_Not_Searched==True):
            if speed[i] < threshold_speed :
                tab_fixation.append("Fixation")
            else : 
                tab_fixation.append("Saccade")
            i+=1 # Condition pour ne pas dépasser la taille du tableau
            if i == len(x)-1:
                All_Points_Not_Searched = False
        # On sort de la boucle, on a un point qui n'est pas dans la saccade
        if tab_fixation == "Fixation":
            duration = time[i+1]-time[i] #Temps de fixation
            tab_fixation.append((x[i],y[i],temps_start[i],temps_end[i+1],duration))
        else :
            duration = time[i+1]-time[i]
            tab_fixation.append((x[i],y[i],temps_start[i],temps_end[i+1],duration)) 
    return tab_fixation

# On modifie le tableau tab_fixation de sorte à ne pas avoir plusieurs points de fixation consécutifs 
def tab_fixation_modification(tab_fixation):
    """Fonction qui modifie le tableau tab_fixation de sorte à ne pas avoir plusieurs points de fixation consécutifs """
    tab_fixation_modifie = []
    for i in range(len(tab_fixation)):
        if tab_fixation[i][0] == "Fixation" and tab_fixation[i+1][0] == "Fixation":
            # On ne garde que le premier point = début de fixation, on supprime les lignes redondantes et on fait le calcul de la durée de fixation totale 

        if tab_fixation[i][0] == "Saccade" and tab_fixation[i+1][0] == "Saccade":
            tab_fixation_modifie.append("Saccade")
        else:
            tab_fixation_modifie.append(tab_fixation[i])
    return tab_fixation_modifie 
 