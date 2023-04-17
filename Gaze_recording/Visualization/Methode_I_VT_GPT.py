import math as mt
import numpy as np

threshold_time = 0.04 # Seuil de temps pour définir une saccade minimum (en secondes)

def middle_calcul(x,y):
    """Fonction qui calcule le centre de la fixation en utilisant la méthode du barycentre"""
    n = len(x)
    if n == 0:
        return [0, 0]
    else:
        sum_x = sum(x)
        sum_y = sum(y)
        barycenter_x = sum_x / n
        barycenter_y = sum_y / n
        return [barycenter_x, barycenter_y]

def Check_Fixation(threshold_speed, threshold_dispersion, start, end, x, y):
    """
    Fonction qui teste si les points entre start et end forment une fixation
    avec la méthode d'IVT (Intra-saccadic Velocity Threshold)
    """
    # Calcul de la vitesse moyenne
    speed = ((x[end] - x[start])**2 + (y[end] - y[start])**2) / (end - start)
    if speed > threshold_speed:
        # Si la vitesse est supérieure au seuil, ce n'est pas une fixation
        return False, None

    # Calcul du rayon de dispersion
    mean_x = np.mean(x[start:end+1])
    mean_y = np.mean(y[start:end+1])
    dispersion = np.max(np.sqrt((x[start:end+1]-mean_x)**2 + (y[start:end+1]-mean_y)**2))
    if dispersion > threshold_dispersion:
        # Si la dispersion est supérieure au seuil, ce n'est pas une fixation
        return False, None

    # Si la vitesse et la dispersion sont inférieures aux seuils, c'est une fixation
    return True, (mean_x, mean_y)


def Velocity(threshold_speed, x, y, time): 
    """Fonction qui utilise l'IVT pour détecter les fixations et les saccades"""
    
    # Définition du seuil de vitesse en pixels par seconde
    threshold_speed = threshold_speed
    
    # Initialisation des variables
    start = 0
    end = 0
    rayon_dispersion = 150
    tab_fixation = []
    tab_saccade = []
    middle_fix = [0,0]
    
    # Boucle principale de traitement des points de fixation
    while(end < len(x)):
        
        # Calcul de la vitesse moyenne entre deux points
        if time[end] == time[start]:
            speed = 0
        else:
            speed = ((x[end] - x[start])**2 + (y[end] - y[start])**2) / (time[end] - time[start])

        
        # Si la vitesse est inférieure au seuil, c'est une fixation
        if speed < threshold_speed:
            end += 1
            Test_Fixation, middle_fix = Check_Fixation(time, start, end, x, y)
            
            if Test_Fixation:
                
                # Calcul du rayon de dispersion de la fixation
                rayon_dispersion += rayon_dispersion * 0.001 * (end-start)
                tab_fixation.append((middle_fix[0],middle_fix[1],rayon_dispersion/3,time[start],time[end-1]-time[start]))  #The center of the fixation is saved
                
            else:
                # Si on n'a pas trouvé de fixation, on considère que c'est une saccade
                tab_saccade.append(("Saccade",x[start],y[start],x[end],y[end],time[start],time[end],time[end]-time[start]))
                start = end - 1
                rayon_dispersion = 150
            
        # Si la vitesse est supérieure au seuil, c'est une saccade
        else:
            # Si la saccade est suffisamment grande, on l'enregistre
            if end - start > 1:
                tab_saccade.append(("Saccade",x[start],y[start],x[end],y[end],time[start],time[end],time[end]-time[start]))
            start = end
        
        # Incrémentation de l'indice de fin
        end += 1
    
    # Si on a fini la boucle mais qu'on n'a pas enregistré la dernière saccade
    if end - start > 1:
        tab_saccade.append(("Saccade",x[start],y[start],x[end],y[end],time[start],time[end],time[end]-time[start]))
    
    return tab_fixation, tab_saccade
