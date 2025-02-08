import numpy as np
import csv

def get_fixation(x, y, time, maxdist, mindur):
	
	"""Detects fixations, defined as consecutive samples with an inter-sample
	distance of less than a set amount of pixels (disregarding missing data)
	
	arguments

	x		-	numpy array of x positions
	y		-	numpy array of y positions
	time		-	numpy array of EyeTribe timestamps

	keyword arguments

	missing	-	value to be used for missing data (default = 0.0)
	maxdist	-	maximal inter sample distance in pixels (default = 25)
	mindur	-	minimal duration of a fixation in milliseconds; detected
				fixation cadidates will be disregarded if they are below
				this duration (default = 100)
	
	returns
	Sfix, Efix
				Sfix	-	list of lists, each containing [starttime]
				Efix	-	list of lists, each containing [starttime, endtime, duration, endx, endy]
	"""

	#x, y, time = remove_missing(x, y, time, missing)

	# empty list to contain data
	Sfix = []
	Efix = []

	
	# loop through all coordinates
	si = 0
	fixstart = False
	for i in range(1,len(x)):
		# calculate Euclidean distance from the current fixation coordinate
		# to the next coordinate
		squared_distance = ((x[si]-x[i])**2 + (y[si]-y[i])**2)
		dist = 0.0
		if squared_distance > 0:
			dist = squared_distance**0.5
		# check if the next coordinate is below maximal distance
		if dist <= maxdist and not fixstart:
			# start a new fixation
			si = 0 + i
			fixstart = True
			Sfix.append([time[i]])
		elif dist > maxdist and fixstart:
			# end the current fixation
			fixstart = False
			# only store the fixation if the duration is ok
			if time[i-1]-Sfix[-1][0] >= mindur:
				Efix.append([Sfix[-1][0], time[i-1], time[i-1]-Sfix[-1][0], x[si], y[si]])
			# delete the last fixation start if it was too short
			else:
				Sfix.pop(-1)
			si = 0 + i
		elif not fixstart:
			si += 1
	#add last fixation end (we can lose it if dist > maxdist is false for the last point)
	if len(Sfix) > len(Efix):
		Efix.append([Sfix[-1][0], time[len(x)-1], time[len(x)-1]-Sfix[-1][0], x[si], y[si]])
	return Sfix, Efix


def get_eye_saccade(x, y, time, minlen, maxvel, maxacc, minsamples):
    """
	Detects saccades, defined as consecutive samples with an inter-sample
	velocity of over a velocity threshold or an acceleration threshold

    Arguments:
    x       -   numpy array of x positions
    y       -   numpy array of y positions
    time    -   numpy array of timestamps in seconds

    Keyword arguments:
    minlen  -   minimal length of saccades in seconds; all detected
                saccades with len(sac) < minlen will be ignored
                (default = 0.005)
    maxvel  -   velocity threshold in pixels/second (default = 40)
    maxacc  -   acceleration threshold in pixels/second**2
                (default = 340)

    Returns:
    Ssac, Esac
            Ssac    -   list of lists, each containing [starttime]
            Esac    -   list of lists, each containing [starttime, endtime, duration, startx, starty, endx, endy]
    """
    # CONTAINERS
    Ssac = []
    Esac = []

    # INTER-SAMPLE MEASURES
    intdist = (np.diff(x)**2 + np.diff(y)**2)**0.5
    inttime = np.diff(time)

    # 输出总距离
    print('Total distance:', np.sum(intdist))
    
    
    # VELOCITY AND ACCELERATION
    vel = intdist / inttime
    acc = np.diff(vel)
    
    # 速度、加速度和的时间保存到新的 CSV 文件中
    with open('velocity.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Velocity'])
        # 写速度和对应时间到CSV文件中
        for i in range(len(vel)):
            writer.writerow([vel[i],time[i]])
            
        
    with open('acceleration.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Acceleration'])
        # 写加速度和对应时间到CSV文件中
        for i in range(len(acc)):
            writer.writerow([acc[i], time[i]])
            
    # DETECT SACCADES
    sac_start = None
    consecutive_below_threshold = 0
    for i in range(len(acc)):
        if vel[i] > maxvel or acc[i] > maxacc:
            if sac_start is None:
                sac_start = i
            consecutive_below_threshold = 0
            continue
        elif sac_start is not None:
            consecutive_below_threshold += 1
            if consecutive_below_threshold >= minsamples:
                sac_end = i
                duration = time[sac_end] - time[sac_start]
                if duration >= minlen:
                    Ssac.append([time[sac_start]])
                    Esac.append([time[sac_start], time[sac_end], duration, x[sac_start], y[sac_start], x[sac_end], y[sac_end]])
                sac_start = None
                consecutive_below_threshold = 0
    return Ssac, Esac


def merge_actions(fixlist, saclist, slow_speed_threshold=0.1):
    """
    Merges fixation and saccade sequences with action types based on start time.

    Arguments:
    fixlist - list of lists, each containing [starttime, endtime, duration, endx, endy]
    saclist - list of lists, each containing [starttime, endtime, duration, startx, starty, endx, endy]

    Returns:
    merged_list - merged list of all actions with action type sorted by start time
    """
    # Assign action types
    fixlist_with_type = [['Fixation'] + fix for fix in fixlist]
    saclist_with_type = [['Fast_saccade'] + sac for sac in saclist]

    # Merge and sort by start time
    all_actions = fixlist_with_type + saclist_with_type
    all_actions = sorted(all_actions, key=lambda x: x[1])
    merged_list = []
    # Insert slow-speed movements between actions if the time gap exceeds the threshold
    for i in range(len(all_actions)):
        merged_list.append(all_actions[i])  # Add the current action to the merged list
        if i < len(all_actions) - 1:
            current_end_time = all_actions[i][2]
            next_start_time = all_actions[i + 1][1]
            time_gap = next_start_time - current_end_time
            if time_gap >= slow_speed_threshold:
                # Insert slow-speed movement
                slow_speed_start_time = current_end_time + 0.01
                slow_speed_end_time = next_start_time - 0.01
                slow_speed_duration = slow_speed_end_time - slow_speed_start_time
                slow_speed_start_x = all_actions[i][3]  # Use end x of current action as start x for slow-speed
                slow_speed_start_y = all_actions[i][4]  # Use end y of current action as start y for slow-speed
                slow_speed_end_x = all_actions[i + 1][3]  # Use start x of next action as end x for slow-speed
                slow_speed_end_y = all_actions[i + 1][4]  # Use start y of next action as end y for slow-speed
                slow_speed_action = ['Slow_saccade',slow_speed_start_time, slow_speed_end_time, slow_speed_duration,
                                     slow_speed_start_x, slow_speed_start_y, slow_speed_end_x, slow_speed_end_y]
                merged_list.append(slow_speed_action)

    return merged_list    

def analyzer(filepath, maxdist=50, mindur=0.3,  minlen=0.5, maxvel=1000, maxacc=1000, minsamples=2):
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头行
        data = list(reader)
        
    # 检查数据格式并处理
    max_columns = max(len(row) for row in data)
    for row in data:
        if len(row) < max_columns:
            row.extend([None] * (max_columns - len(row)))  # 填充缺失值
    
    data_array = np.array(data)
    
    tlist = data_array[:,0].astype(float)
    xlist = data_array[:,1].astype(float)
    ylist = data_array[:,2].astype(float)
    
    _, saclist = get_eye_saccade(xlist, ylist, tlist, minlen, maxvel, maxacc, minsamples)
    _, fixlist = get_fixation(xlist, ylist, tlist, maxdist, mindur)
    
    return fixlist, saclist

def main():
    filepath = 'eye_tracking.csv'  
    fixlist, saclist = analyzer(filepath)
        
    with open('fixation.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Starttime', 'Endtime', 'Duration', 'Endx', 'Endy'])
        for row in fixlist:
            writer.writerow(row)
            
    with open('saccade.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Starttime', 'Endtime', 'Duration', 'Startx', 'Starty', 'Endx', 'Endy'])
        for row in saclist:
            writer.writerow(row)
    # Merge fixation and saccade sequences
    merged_list = merge_actions(fixlist, saclist)

    # Save merged actions to CSV file
    with open('eye_actions.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'Starttime', 'Endtime', 'Duration', 'Startx', 'Starty', 'Endx', 'Endy'])
        for row in merged_list:
            writer.writerow(row)

if __name__ == "__main__":
    main()
