import numpy as np

def Velocity(threshold_speed, x, y, time):
    """
    Calculates fixations and saccades using the I-VT method.
    
    Parameters:
        threshold_speed (float): Velocity threshold in pixels/second.
        x (ndarray): Array of x-coordinates.
        y (ndarray): Array of y-coordinates.
        time (ndarray): Array of time stamps in seconds.
        
    Returns:
        fixations (list): List of tuples (start_time, end_time, x_mean, y_mean)
                          representing fixations.
        saccades (list): List of tuples (start_time, end_time, start_x, start_y,
                          end_x, end_y, amplitude) representing saccades.
    """
    # Compute distances between consecutive samples
    dx = np.diff(x)
    dy = np.diff(y)
    dt = np.diff(time)
    distances = np.sqrt(dx**2 + dy**2)
    velocities = distances / dt
    
    # Initialize fixations and saccades lists
    fixations = []
    saccades = []
    
    # Initialize fixation parameters
    start_time = time[0]
    end_time = time[0]
    x_sum = x[0]
    y_sum = y[0]
    n_samples = 1
    
    # Iterate over samples
    for i in range(len(velocities)):
        # If velocity is below threshold, add sample to current fixation
        if velocities[i] < threshold_speed:
            end_time = time[i+1]
            x_sum += x[i+1]
            y_sum += y[i+1]
            n_samples += 1
        # If velocity is above threshold, end current fixation and add it to list
        else:
            if n_samples > 1:
                x_mean = x_sum / n_samples
                y_mean = y_sum / n_samples
                #fixations.append((start_time, end_time, x_mean, y_mean))
                fixations.append((x_mean, y_mean, 150, start_time, end_time-start_time))
            # Reset fixation parameters
            start_time = time[i+1]
            end_time = time[i+1]
            x_sum = x[i+1]
            y_sum = y[i+1]
            n_samples = 1
            
            # Add saccade to list
            start_x = x[i]
            start_y = y[i]
            end_x = x[i+1]
            end_y = y[i+1]
            amplitude = distances[i]
            #saccades.append((start_time, end_time, start_x, start_y, end_x, end_y, amplitude))
            saccades.append(("Saccade",start_x, start_y, end_x, end_y, start_time, end_time, (end_time-start_time)))
    
    # Add last fixation to list
    if n_samples > 1:
        x_mean = x_sum / n_samples
        y_mean = y_sum / n_samples
        #fixations.append((start_time, end_time, x_mean, y_mean))
        fixations.append((x_mean, y_mean, 150, start_time, end_time-start_time))
    
    return fixations, saccades
