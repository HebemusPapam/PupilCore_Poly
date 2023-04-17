import math as mt

threshold_time = 0.04 # Seuil de temps pour définir une saccade minimum (en secondes)

#Fonction qui calcule la vitesse entre deux points, retourne un tableau de vitesse
def speed_calcul(x,y,time):
    """Fonction qui calcule la vitesse entre deux points"""
    speed_calcul = []
    for i in range(len(x)):
        speed_calcul.append(mt.sqrt(((x[i+1]-x[i])**2+(y[i+1]-y[i])**2))/(time[i+1]-time[i]))
    return speed_calcul #Liste en pixel par seconde

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

def Check_Fixation(threshold_speed, time, start, end, x, y):
    """Fonction qui vérifie si la fixation est valide"""
    speed = ((x[end] - x[start])**2 + (y[end] - y[start])**2) / (time[end] - time[start])
    if speed < threshold_speed:
        #On a une fixation
        return True
    else:
        #On a une saccade
        return False

def Check_micro_saccade(time, start, end, x, y):
    """Fonction qui vérifie si la micro-saccade est valide"""
    time = (time[end] - time[start])
    if time < threshold_time:
        #On a une micro_saccade
        
        return True, 
    else:
        #On a une fixation
        return False

def Velocity(threshold_speed, x, y, time): # Le tableau time est en secondes 
    """Fonction qui compare la vitesse entre deux points avec un seuil """
    All_Points_Not_Searched = True #Flag pour savoir si on a parcouru tous les points
    start = 0
    end = 0
    rayon_dispersion = 150

    tab_fixation = []
    tab_saccade = []
    middle_fix = [0,0]

    #Flag pour les différents évenements possible
    All_Points_Not_Searched = True
    Micro_Saccade = False
    Saccade = False

    while(All_Points_Not_Searched):
        if Micro_Saccade :
            #On a eu une micro saccade donc on doit recommencer à chercher les fixations depuis l'index où l'on s'est arrêté
            #car on a supprimé le point en dehors de la fixation du tableau de point gaze_x et gaze_y
            Micro_Saccade = False

        elif end < len(x)-2 : 
            end += 1

        else: 
            All_Points_Not_Searched = False
        
        if Check_Fixation(threshold_speed, time, start, end, x, y):
            #########Condition Temporel sur une fixation############

            if not Check_micro_saccade(time, start, end, x, y):
                #########Condition Temporel sur une fixation############
                #une fixation ne doit pas être confondu avec un blink donc t > 40ms
                
                print("Fixation : ",start," ",end," ",time[end]-time[start])
                middle_fix = middle_calcul(x[start:end],y[start:end])
                rayon_dispersion += rayon_dispersion * 0.001 * (end-start)
                tab_fixation.append((middle_fix[0],middle_fix[1],rayon_dispersion/3,time[start],time[end-1]-time[start]))  #The center of the fixation is saved

        else:
            #########Condition Temporel sur une saccade############
            
            #print("Saccade")
            tab_saccade.append(("Saccade",x[start],y[start],x[end],y[end],time[start],time[end],time[end]-time[start]))
            start = end - 1
            rayon_dispersion = 150
            Saccade = True
          
        
        while(not Saccade and All_Points_Not_Searched and not Micro_Saccade):
            start = end
            #########Condition Temporel sur une saccade############
            #une saccade ne doit pas être confondu avec un blink donc t > 40ms
            while((time[end]-time[start])<threshold_time and All_Points_Not_Searched):
                if end<(len(x)-2):
                    end+=1
                else:
                    All_Points_Not_Searched = False
            Saccade = True
            tab_saccade.append(("Saccade",x[start],y[start],x[end],y[end],time[start],time[end],time[end]-time[start]))
            start = end-1    

        Saccade = False   
        Micro_Saccade = False 


    return tab_fixation, tab_saccade
 

 