import math as mt

#Fonction qui calcule la vitesse entre deux points, retourne un tableau de vitesse
def speed_calcul(x,y,time):
    """Fonction qui calcule la vitesse entre deux points"""
    speed_calcul = []
    for i in range(len(x)-1):
        speed_calcul.append(mt.sqrt(((x[i+1]-x[i])**2+(y[i+1]-y[i])**2))/(time[i+1]-time[i]))
    return speed_calcul #Liste en pixel par seconde

def middle_calcul(x,y):
    """Fonction qui retourne les coordonées du centre d'une succession de points"""
    sum_x = 0
    sum_y = 0
    for xp in x:
        sum_x += xp
    for yp in y:
        sum_y += yp
    return [sum_x/len(x),sum_y/len(y)]

def Check_Fixation(time, start, end, x, y, threshold_time):
    """Fonction qui vérifie si la fixation est valide"""
    if (time[end]-time[start]) > threshold_time:
        #On a une fixation
        middle_fix = middle_calcul(x[start:end],y[start:end])
        return True, middle_fix
    else:
        #On a une saccade
        return False, [0,0]

def Check_micro_saccade(time, start, end, x, y, threshold_time):
    """Fonction qui vérifie si la micro-saccade est valide"""
    if (time[end]-time[start]) > threshold_time:
        #On a une fixation
        middle_fix = middle_calcul(x[start:end],y[start:end])
        return True, middle_fix
    else:
        #On a une saccade
        return False, [0,0]

def Velocity(threshold_speed, x, y, time): # Le tableau time est en secondes 
    """Fonction qui compare la vitesse entre deux points avec un seuil """
    All_Points_Not_Searched = True #Flag pour savoir si on a parcouru tous les points
    threshold_time = 0.04 # Seuil de temps pour définir une saccade minimum (en secondes)
    threshold_speed = threshold_speed*1000 #Conversion du seuil en seconde :
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
    Test_Fixation = False

    speed = speed_calcul(x,y,time)
    while(All_Points_Not_Searched):
        if Micro_Saccade :
            #On a eu une micro saccade donc on doit recommencer à chercher les fixations depuis l'index où l'on s'est arrêté
            #car on a supprimé le point en dehors de la fixation du tableau de point gaze_x et gaze_y
            Micro_Saccade = False

        elif end < len(x)-2 : 
            end += 1

        else: 
            All_Points_Not_Searched = False
        
        
        Test_Fixation, middle_fix = Check_Fixation(time, start, end, x, y, threshold_time)
        
        if Test_Fixation:
            
            #Micro_Saccade, middle_fix = Check_micro_saccade(time, start, end, x, y, threshold_time)

            if not Micro_Saccade:
                #########Condition Temporel sur une fixation############
                
                print("Fixation")
                rayon_dispersion += rayon_dispersion * 0.001 * (end-start)
                tab_fixation.append((middle_fix[0],middle_fix[1],rayon_dispersion/3,time[start],time[end-1]-time[start]))  #The center of the fixation is saved

        else:
            #########Condition Temporel sur une saccade############
            
            print("Saccade")
            tab_saccade.append(("Saccade",x[start],y[start],x[end],y[end],time[start],time[end],time[end]-time[start]))
            start = end - 1
            rayon_dispersion = 150
            Saccade = True
          
        
        while(not Saccade and All_Points_Not_Searched):
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
 

 