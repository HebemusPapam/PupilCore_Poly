import math as mt

#Fonction qui calcule la vitesse entre deux points, retourne un tableau de vitesse
def speed_calcul(x,y,time):
    """Fonction qui calcule la vitesse entre deux points"""
    speed = []
    for i in range(len(x)-1):
        speed.append(mt.sqrt(((x[i+1]-x[i])**2+(y[i+1]-y[i])**2))/(time[i+1]-time[i]))
    return speed #Liste en pixel par seconde

#Fonction qui compare la vitesse entre deux points avec un seuil, et indique si le regard est fixé ou non 
def fixation_velocity(speed,threshold_speed,x): 
    """Fonction qui compare la vitesse entre deux points avec un seuil, et indique si le regard est fixé ou non"""
    tab_fixation = []
    #Conversion du seuil en seconde : 
    threshold_speed = threshold_speed*1000
    for i in range(len(x)-1):
        print('speed = ',speed[i])
        if speed[i] < threshold_speed : # On a une fixation 
            tab_fixation.append("Fixation")
            
        else : # On a un mouvement
            tab_fixation.append("Saccade")
            print('Saccade')
        print('Nature :',tab_fixation[i])
    return tab_fixation 
