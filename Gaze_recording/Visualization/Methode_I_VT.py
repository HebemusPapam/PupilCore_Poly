import math as mt

#Fonction qui calcule la vitesse entre deux points, retourne un tableau de vitesse
def speed_calcul(x,y,time):
    """Fonction qui calcule la vitesse entre deux points"""
    speed = []
    for i in range(len(x)-1):
        speed.append(mt.sqrt(((x[i+1]-x[i])**2+(y[i+1]-y[i])**2))/(time[i+1]-time[i]))
    return speed #Liste en pixel par seconde

def fixation_velocity(threshold_speed, x, y, time): # Le tableau time est en secondes 
    """Fonction qui compare la vitesse entre deux points avec un seuil """
    All_Points_Not_Searched = True #Flag pour savoir si on a parcouru tous les points
    threshold_time = 0.03 # Seuil de temps pour définir une saccade minimum (en secondes)
    threshold_speed = threshold_speed*1000 #Conversion du seuil en seconde :
    duration = 0 
    start = 0
    end = 0
    faux_positif = 0

    tab_fixation = []
    tab_saccade = []


    speed = speed_calcul(x,y,time)
    while(All_Points_Not_Searched):
        if end < len(x)-2 : 
            end += 1
        else: 
            All_Points_Not_Searched = False
        
        if speed[end] < threshold_speed : 
            duration += time[end] - time[start]
 
        else : 
            if faux_positif > 3:
                if duration > 0.20 : 
                    print("start : ", start)
                    print("end : ", end-1)
                    print("duration : ", duration)
                start = end - 1
                duration = 0
                faux_positif = 0
            else:
                faux_positif += 1
                duration += time[end] - time[start]
                print("faux positif : ", faux_positif)
                print("end : ", end)
            
    return tab_fixation, tab_saccade
 

 