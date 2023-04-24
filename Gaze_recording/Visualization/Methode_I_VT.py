import math as mt

"""Fonction qui permet de passer au point suivant"""
def Suivant(x, end, FLAG_End):

    if end < (len(x)-2):
        end += 1
    else:
        FLAG_End = True
    
    return end, FLAG_End

"""Fonction qui calcule la vitesse entre deux points"""
def speed_calcul(x, y, time):

    speed_calcul = []
    for i in range(len(x)-1):
        speed_calcul.append(mt.sqrt(((x[i+1]-x[i])**2+(y[i+1]-y[i])**2))/(time[i+1]-time[i]))
    
    return speed_calcul

"""Fonction qui calcule le centre de la fixation en utilisant la méthode du barycentre"""
def middle_calcul(x,y):

    n = len(x)
    if n == 0:
        return [0, 0]
    else:
        sum_x = sum(x)
        sum_y = sum(y)
        barycenter_x = sum_x / n
        barycenter_y = sum_y / n
        return [barycenter_x, barycenter_y]

"""Fonction qui compare la vitesse entre deux points avec un seuil """
def Velocity(x, y, time, threshold_speed):

    #Initialisation des variables
    tab_fixation = []
    tab_saccade = []
    tab_speed = []
    start_sac = 0
    start_fix = 0
    end = 1
    rayon_dispersion = 150
    duration_micro_saccade = 0.035

    #Initialisation des flags
    FLAG_End = False
    FLAG_Micro_Saccade = True
    FLAG_Fixation = False

    #Calcul de la vitesse
    tab_speed = speed_calcul(x, y, time)

    #Début de la boucle
    while not FLAG_End:

        while FLAG_Micro_Saccade and not FLAG_End:

            #Début de la non-fixation
            start_sac = end
            #Tant qu'il n'y a pas de fixation
            while tab_speed[end] > threshold_speed and not FLAG_End:
                "Pas de fixation"
                end, FLAG_End = Suivant(x, end, FLAG_End)
            #Fin de la non-fixation

            #On regarde si la non-fixation est une saccade ou une micro-saccade
            if time[end] - time[start_sac] > duration_micro_saccade:
                "Saccade"
                #On ajoute la saccade dans le tableau
                FLAG_Micro_Saccade = False
                tab_saccade.append(("Saccade",x[start_sac],y[start_sac],x[end],y[end],time[start_sac],time[end],time[end]-time[start_sac]))
            else:
                "Micro_Saccade"
                #On continue la fixation

                if start_fix == -1:
                    #Début de la fixation
                    start_fix = end
                
                #Tant qu'il y a une fixation
                while tab_speed[end] <= threshold_speed and not FLAG_End:
                    "Fixation"
                    end, FLAG_End = Suivant(x, end, FLAG_End)
                #Fin de la fixation
                FLAG_Fixation = True

        #Si il y a eu une fixation
        if FLAG_Fixation:
            #On ajoute la fixation dans le tableau
            middle_fix = middle_calcul(x[start_fix:end],y[start_fix:end])
            rayon_dispersion += rayon_dispersion * 0.001 * (end-start_fix)
            tab_fixation.append((middle_fix[0],middle_fix[1],rayon_dispersion/3,time[start_fix],time[end-1]-time[start_fix]))

            #On réinitialise les flags et les variables
            FLAG_Fixation = False
            FLAG_Micro_Saccade = True
            start_fix = -1 #On met -1 pour dire qu'il n'y a pas de fixation
            rayon_dispersion = 150
        
    return tab_fixation, tab_saccade
