import numpy as np
import math as mt

def Choix_Methode_Dispersion(methode,time,gaze_x,gaze_y,radius,duration):
    if methode=="Salvucci" :
        return dispersion_map_Salvucci(time,gaze_x,gaze_y,radius,duration)
    elif methode=="Eucl":
        return dispersion_map_Eucl(time,gaze_x,gaze_y,radius,duration)
    

def calcul_disp(Xs,Ys):
    dispersion = max((Xs[:])) - min((Xs[:])) + max((Ys[:])) - min ((Ys[:]))
    return float(dispersion)

def Check_Fixation_Salvucci(time,start,end,duration_limit,rayon_dispersion,dispersion,All_Points_Not_Searched,x,y,radius):
    #On cherche la dispersion sur une fenêtre de point, consistant au seuil de durée minimum d'une fixation
    while dispersion < rayon_dispersion and All_Points_Not_Searched:
        #########Condition Temporel############
        while((time[end]-time[start])<duration_limit and All_Points_Not_Searched ):
            if end<(len(x)-2):
                end+=1
            else:
                All_Points_Not_Searched = False
        ##########Tant que la dispersion est acceptable############
        #la condition temporel est respecté mais on continu d'ajouté des points tant que dispersion < rayon_dispersion
        #la dispersion est inférieur au seuil on recommence avec une fenêtre plus grande
        if end<(len(x)-2):
            end+=1
        else:
            All_Points_Not_Searched = False

        dispersion = calcul_disp(x[start:end],y[start:end])

        #On augment le seuil de dispersion si il y a de plus en plus de points
        if (All_Points_Not_Searched and dispersion < rayon_dispersion and rayon_dispersion < radius*2):
            rayon_dispersion = rayon_dispersion *1.001
    
    return rayon_dispersion,All_Points_Not_Searched,dispersion,start,end


def Check_Micro_Saccade_Salvucci(MicroS,t0,t1,x,y,microS_info,time,dispersion_max):
    
    MicroS_duration = 0.025 #Durée max d'une Micro saccade : 25ms
    All_Points_Not_Searched = True
    #On met de côté les points contenus dans la fixation
    x1 = x[t0:t1-1]
    y1 = y[t0:t1-1]

    #On n'utilise que l'index au début de la possible micro saccade 
    t0 = t1-1
    #on recule d'un point pour pouvoir repartir de t0 après 't1+=1' (t0 étant le premier point en dehors de la fixation)
    t1 -=2
    while(time[t1]-time[t0]<MicroS_duration and All_Points_Not_Searched and not MicroS):
        if t1<(len(x)-2):
                t1+=1
        else :
            All_Points_Not_Searched = False
        
        x2 = np.copy(x1)
        y2 = np.copy(y1)
        x2 = np.append(x2,x[t1])
        y2 = np.append(y2,x[t1])
        #On vérifie si la dispersion redevient sensiblement identique (l'utilisateur est revenu au point de départ)
        if t0!=t1 and abs(calcul_disp(x1,y1)-calcul_disp(x2,y2)) < 10 and calcul_disp(x2,y2)<dispersion_max and not MicroS :
            MicroS = True
            microS_info.append(("Micro",x[t0],y[t0],x[t1],y[t1],time[t0],time[t1],time[t1]-time[t0]))
            #On retire les points de la Micro saccade
            tem=[]
            for i in range(t0,t1,1):
                tem.append(i)
            x = np.delete(x,tem)
            y = np.delete(y,tem)
            time = np.delete(time,tem)
    
    return MicroS,x,y,time,All_Points_Not_Searched,microS_info

def dispersion_map_Salvucci(time,gaze_x,gaze_y,radius,duration):
    """
    Return a list of fixation : fixation (x,y,radius) if the conditions are respected
    A circle is created, if the dispersion and time between the points are contained in their respective threshold.
    Using method of Salvucci, D.D.; Goldberg, J.H. Identifying fixations and saccades in eye-tracking protocols.
    """
    rayon_dispersion = radius
    duration_limit = duration
    end=0
    start = 0
    dispersion = 0
    fixation = []
    saccade = []

    #Flag pour les différents évenements possible
    No_Saccade=True
    All_Points_Not_Searched = True
    Micro_Saccade = False

    while (All_Points_Not_Searched):
        if Micro_Saccade :
            #On a eu une micro saccade donc on doit recommencer à chercher les fixations depuis l'index où l'on s'est arrêté
            #car on a supprimé le point en dehors de la fixation du tableau de point gaze_x et gaze_y
            Micro_Saccade = False
        elif end<(len(gaze_x)-2):
            end+=1
            print(end)
        else :
            All_Points_Not_Searched = False        
        #On prend une fenêtre de point sur la durée mini d'une fixation et on vérifie sa dispersion
        rayon_dispersion,All_Points_Not_Searched,dispersion,start,end = Check_Fixation_Salvucci(time,start,end,duration_limit,rayon_dispersion,dispersion,All_Points_Not_Searched,gaze_x,gaze_y,radius)
        #end correspond à l'indice de x + 1 après que l'on soit sortie de la fixation (Ex : 0-55 -> fixation start = 0 end = 57)
        #La dispersion est trop importante, on vérifie que le rayon a changé et que ce n'est pas une microsaccade
        if rayon_dispersion!=radius:
            #On vérifie la présence d'une MicroSaccade, de plus on enlève de la liste des points les coordonnées de micro_saccade
            Micro_Saccade,gaze_x,gaze_y,time,All_Points_Not_Searched,saccade = Check_Micro_Saccade_Salvucci(Micro_Saccade,start,end,gaze_x,gaze_y,saccade,time,rayon_dispersion)
            
            if not Micro_Saccade :
                #Il y a une fixation mais pas de micro saccade
                middle_fix = middle_calcul(gaze_x[start:end-1],gaze_y[start:end-1])
                fixation.append((middle_fix[0],middle_fix[1],rayon_dispersion/3,time[start],time[end-1]-time[start]))  #The center of the fixation is saved
                rayon_dispersion = radius #The dispersion is reset to its default value

        #Si le rayon n'a pas changé alors on a une saccade (aucune fixation dans le laps de temps étudié)
        else:
            No_Saccade = False
            end = start
            #Notre saccade dure tous la durée de la fenêtre donc on la recalibre pour ne prendre en compte que les 80 premières ms de cette fenêtre
            while (time[end]-time[start]<0.08) and All_Points_Not_Searched:
                if end<(len(gaze_x)-2):
                    end+=1
                else :
                    All_Points_Not_Searched = False   
            saccade.append(("Normal",gaze_x[start],gaze_y[start],gaze_x[end],gaze_y[end],time[start],time[end],time[end]-time[start]))
            if start-end != -1 : 
                start = end-1
            else : 
                start = end
            dispersion = 0

        #On a besoin d'une saccade entre deux fixation (pas de saccade ou de Micro Saccades juste avant)
        while(No_Saccade and All_Points_Not_Searched and not Micro_Saccade):
            start = end
            #########Condition Temporel sur une saccade############
            #une saccade ne doit pas être confondu avec un blink donc t > 40ms
            while((time[end]-time[start])<0.04 and All_Points_Not_Searched):
                if end<(len(gaze_x)-2):
                    end+=1
                else:
                    All_Points_Not_Searched = False
            No_Saccade = False
            saccade.append(("Normal",gaze_x[start],gaze_y[start],gaze_x[end],gaze_y[end],time[start],time[end],time[end]-time[start]))
            start = end-1
            dispersion = 0      
        
        #On remet le flag Saccade à 1  
        No_Saccade=True    
        Micro_Saccade = False
      
    return fixation,saccade

def dispersion_map_Eucl(time,gaze_x,gaze_y,radius,duration):

    """
    Return a list of fixation : fixation (x,y,radius) if the conditions are respected
    A circle is created, if the dispersion and time between the points are contained in their respective threshold.
    The function first check if the distance between the point is longer than the radius and then if the time passed is sufficient.
    """
    rayon_dispersion = radius
    duration_limit = duration
    x_1 = gaze_x[0]
    y_1 = gaze_y[0]
    time_0 = time[0]
    fixation= []
    saccade=[]
    middle_fix = []
    #we search the distance between each point 
    for i in range(1,len(gaze_x)-2):
        if np.isnan(gaze_x[i])==False:
            x_2 = gaze_x[i]
            y_2 = gaze_y[i]
            time_1 = time[i]
            distance = mt.sqrt((x_1-x_2)**2 + (y_1-y_2)**2)
            #Event if the fixation is over (out of the circle)
            if distance > rayon_dispersion : 
                #The dispersion size must have evolved to be considered a fixation
                if rayon_dispersion != radius :
                    #The time between 2 points must be high enough
                    if time_1-time_0 >= duration_limit:
                        start = np.where(time == time_0)[0][0]
                        end = np.where(time == time_1)[0][0]
                        middle_fix = middle_calcul(gaze_x[start:end],gaze_y[start:end])
                        fixation.append((middle_fix[0],middle_fix[1],rayon_dispersion,time_0,time_1-time_0))  #The center of the fixation is saved
                        rayon_dispersion = radius #The dispersion is reset to its default value
                x_1 = x_2
                y_1 = y_2
                time_0=time_1

            elif rayon_dispersion < (radius*3):
                rayon_dispersion = rayon_dispersion * 1.01

    #Condition if the gaze stay in a circle and don't disperse at the end
    if time_1-time_0 >= duration_limit:
        start = np.where(time == time_0)[0][0]
        end = np.where(time == time_1)[0][0]
        middle_fix = middle_calcul(gaze_x[start:end],gaze_y[start:end])
        fixation.append((middle_fix[0],middle_fix[1],rayon_dispersion,time_0,time_1-time_0))  #The center of the fixation is saved
        fixation.append((middle_fix[0],middle_fix[1],rayon_dispersion,time_0,time_1-time_0))  #The center of the fixation is saved
    return fixation,saccade

def middle_calcul(x,y):
    """
    Fonction qui retourne les coordonées du centre d'une succession de points
    """
    sum_x = 0
    sum_y = 0
    for xp in x:
        sum_x += xp
    for yp in y:
        sum_y += yp
    return [sum_x/len(x),sum_y/len(y)]