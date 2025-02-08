import numpy as np
import csv
import os


def merge_csv_files1(input_folder, output_file, saclist):
    # 创建一个列表来存储所有的数据行
    all_rows = []

    # 遍历输入文件夹中的每个 CSV 文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            filepath = os.path.join(input_folder, filename)
            with open(filepath, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                # 获取操作类型，用于在输出中标识来源
                operation_type = os.path.splitext(filename)[0]
                first_row_skipped = False  # 用于跳过每个原始文件的首行（标题）
                for row in reader:
                    # 跳过每个原始文件的首行（标题）
                    if not first_row_skipped:
                        first_row_skipped = True
                        continue

                    # 添加操作类型作为第一列，其余内容保持不变
                    all_rows.append([operation_type] + row)

    # 按时间戳排序
    all_rows.sort(key=lambda x: x[1])
    # 处理同一时间多个动作的情况，只保存不为 "Move" 的版本
    unique_timestamps = set()
    filtered_rows = []
    for row in all_rows:
        timestamp = row[1]
        if timestamp not in unique_timestamps:
            unique_timestamps.add(timestamp)
            filtered_rows.append(row)
        elif row[0] != 'Move':
            for idx, existing_row in enumerate(filtered_rows):
                if existing_row[1] == timestamp and existing_row[0] == 'Move':
                    filtered_rows[idx] = row
                    break

    # 更新 all_rows
    all_rows = filtered_rows
    
    merged1 = []
    sac_index = 0
    for i in range(len(all_rows)):
        time = float(all_rows[i][1])
        if sac_index < len(saclist) and time >= float(saclist[sac_index][0]) and time <= float(saclist[sac_index][1]):
            if time == float(saclist[sac_index][0]):
                merged1.append(['Fast_move'] + [str(item) for item in saclist[sac_index]])  # Add fast movement information
            if time == float(saclist[sac_index][1]):  # If reaching the end time of the fast movement segment, move to the next segment
                sac_index += 1
        else:
            # Add original mouse movement data as is
            merged1.append(all_rows[i])
    

    # 写入到输出文件中
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'Starttime', 'Endtime', 'Duration', 'Startx', 'Starty', 'Endx', 'Endy'])
        writer.writerows(merged1)




def merge_csv_files2(filename, saclist):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头行
        data = list(reader)
        
    # 检查数据格式并处理
    max_columns = max(len(row) for row in data)
    for row in data:
        if len(row) < max_columns:
            row.extend([None] * (max_columns - len(row)))  # 填充缺失值
    
    
    merged1 = []
    sac_index = 0
    for i in range(len(data)):
        time = float(data[i][1])
        if sac_index < len(saclist) and time >= float(saclist[sac_index][0]) and time <= float(saclist[sac_index][1]):
            if time == float(saclist[sac_index][0]):
                merged1.append(['Slow_move'] + [str(item) for item in saclist[sac_index]])  # Add slow movement information
            if time == float(saclist[sac_index][1]):  # If reaching the end time of the fast movement segment, move to the next segment
                sac_index += 1
        else:
            # Add original mouse movement data as is
            merged1.append(data[i])
    

    # 写入到输出文件中
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'Starttime', 'Endtime', 'Duration', 'Startx', 'Starty', 'Endx', 'Endy'])
        writer.writerows(merged1)




def get_mouse_saccade(input_folder, minlen, maxvel, maxacc, minsamples):
    """
    Detects mouse saccades, defined as consecutive samples with an inter-sample
    velocity of over a velocity threshold or an acceleration threshold.

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
    for filename in os.listdir(input_folder):
        if 'move' in filename.lower() and filename.endswith('.csv'):
            filepath = os.path.join(input_folder, filename)
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
    
    time = data_array[:,0].astype(float)
    x = data_array[:,1].astype(float)
    y = data_array[:,2].astype(float)   
   
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





def get_mouse_hover(filepath, max_hover_time):
    """
    Detects mouse hover segments between consecutive movements, where the time
    between two consecutive movements exceeds the specified threshold.

    Arguments:
    tlist           -   numpy array of timestamps in seconds
    xlist           -   numpy array of x positions
    ylist           -   numpy array of y positions
    max_hover_time  -   maximum time in seconds to consider as hover

    Returns:
    hover_segments  -   list of lists, each containing [starttime, endtime, duration, startx, starty, endx, endy]
    """
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
    
    tlist = data_array[:,1].astype(float)

    hover_segments = []
    start_time = None
    for i in range(len(data_array) - 1):
        action_type = data_array[i, 0]
        end_time_col = 2 if action_type in ['Slow_move', 'Hover', 'Fast_move'] else 1
        end_time = float(data_array[i, end_time_col])

        next_start_time = float(data_array[i+1, 1])

        time_diff = next_start_time - end_time
        if time_diff >= max_hover_time:
            start_time = end_time + 0.01
            end_time = next_start_time - 0.01
            duration = end_time - start_time
            hover_segments.append([start_time, end_time, duration])
    return hover_segments



def get_mouse_slow(filepath):
    """
    Merges mouse movement and hover sequences with action types based on start time.

    Arguments:
    data                -   list of lists, each containing [time, x, y]
    saclist             -   list of lists, each containing [starttime, endtime, duration, startx, starty, endx, endy]
    hoverlist           -   list of lists, each containing [starttime, endtime, duration, startx, starty, endx, endy]
    slow_speed_threshold-   threshold in seconds to consider as slow-speed movement

    Returns:
    merged_list         -   merged list of all actions with action type sorted by start time
    """
    with open(filepath, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头行
        data = list(reader)
        
    # 检查数据格式并处理
    max_columns = max(len(row) for row in data)
    for row in data:
        if len(row) < max_columns:
            row.extend([None] * (max_columns - len(row)))  # 填充缺失值
    
    slow_speed_segments = []
    slow_speed_start_time = None
    slow_speed_end_time = None
    slow_speed_start_x = None
    slow_speed_start_y = None
    slow_speed_end_x = None
    slow_speed_end_y = None
    
    for action in data:   
        if action[0] != 'Move':
            if slow_speed_start_time is not None:
                slow_speed_duration = float(slow_speed_end_time) - float(slow_speed_start_time)
                slow_speed_segments.append([slow_speed_start_time, slow_speed_end_time, slow_speed_duration,
                                            slow_speed_start_x, slow_speed_start_y, slow_speed_end_x, slow_speed_end_y])
                slow_speed_start_time = None
                slow_speed_end_time = None
                slow_speed_start_x = None
                slow_speed_start_y = None
                slow_speed_end_x = None
                slow_speed_end_y = None
        else:
            if slow_speed_start_time is None:
                slow_speed_start_time = str(action[1])  # 将时间值转换为字符串
                slow_speed_start_x = str(action[2])  # 将坐标值转换为字符串
                slow_speed_start_y = str(action[3])  # 将坐标值转换为字符串
                slow_speed_end_time = str(action[1])  # 将时间值转换为字符串
                slow_speed_end_x = str(action[2])  # 将坐标值转换为字符串
                slow_speed_end_y = str(action[3])  # 将坐标值转换为字符串

            else:
                if prev_move_time is not None and float(action[1]) - float(prev_move_time) >= 0.1:
                    slow_speed_duration = float(slow_speed_end_time) - float(slow_speed_start_time)
                    slow_speed_segments.append([slow_speed_start_time, slow_speed_end_time, slow_speed_duration,
                                                slow_speed_start_x, slow_speed_start_y, slow_speed_end_x, slow_speed_end_y])
                    slow_speed_start_time = str(action[1])  # 将时间值转换为字符串
                    slow_speed_start_x = str(action[2])  # 将坐标值转换为字符串
                    slow_speed_start_y = str(action[3])  # 将坐标值转换为字符串
                    slow_speed_end_time = str(action[1])  # 将时间值转换为字符串
                    slow_speed_end_x = str(action[2])  # 将坐标值转换为字符串
                    slow_speed_end_y = str(action[3])  # 将坐标值转换为字符串

                slow_speed_end_time = str(action[1])
                slow_speed_end_x = str(action[2])
                slow_speed_end_y = str(action[3])
            
            prev_move_time = action[1]

    if slow_speed_start_time is not None:
        slow_speed_duration = float(slow_speed_end_time) - float(slow_speed_start_time)
        slow_speed_segments.append([slow_speed_start_time, slow_speed_end_time, slow_speed_duration,
                                    slow_speed_start_x, slow_speed_start_y, slow_speed_end_x, slow_speed_end_y])

    return slow_speed_segments


def merge_mouse_movement(input_folder, slowlist, saclist, hoverlist):
    # Assign action types
    saclist_with_type = [['Fast_move'] + [str(item) for item in sac] for sac in saclist]
    hoverlist_with_type = [['Hover'] + [str(item) for item in hover] for hover in hoverlist]
    slowlist_with_type = [['Slow_move'] + [str(item) for item in slow] for slow in slowlist]
    
    all_rows = []
    all_rows= saclist_with_type + hoverlist_with_type + slowlist_with_type
    
    # 遍历输入文件夹中的每个 CSV 文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv') and 'move' not in filename.lower():
            filepath = os.path.join(input_folder, filename)
            with open(filepath, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                # 获取操作类型，用于在输出中标识来源
                operation_type = os.path.splitext(filename)[0]
                first_row_skipped = False  # 用于跳过每个原始文件的首行（标题）
                for row in reader:
                    # 跳过每个原始文件的首行（标题）
                    if not first_row_skipped:
                        first_row_skipped = True
                        continue
                    # 添加操作类型作为第一列，其余内容保持不变
                    all_rows.append([operation_type] + row)

    # 按时间戳排序
    all_rows.sort(key=lambda x: x[1])
    return all_rows


def analyzer(input_folder, filepath2, output_file, minlen=0.2, maxvel=2000, maxacc=2000, minsamples=5, max_hover_time=0.1):
    Ssac, saclist = get_mouse_saccade(input_folder, minlen, maxvel, maxacc, minsamples)
    # 保存saccade
    with open('saccade.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'Starttime', 'Endtime', 'Duration', 'Startx', 'Starty', 'Endx', 'Endy'])
        for row in saclist:
            writer.writerow(['Fast_move'] + row)
            
    merge_csv_files1(input_folder, filepath2, saclist)        
            
    
    slowlist = get_mouse_slow(filepath2)
    # 保存slow
    with open('slow.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'Starttime', 'Endtime', 'Duration', 'Startx', 'Starty', 'Endx', 'Endy'])
        for row in slowlist:
            writer.writerow(['Slow_move'] + row)
    
    merge_csv_files2(filepath2,slowlist)               
            
    hover_segments = get_mouse_hover(filepath2, max_hover_time)
    # 保存hover
    with open('hover.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'Starttime', 'Endtime', 'Duration', 'Startx', 'Starty', 'Endx', 'Endy'])
        for row in hover_segments:
            writer.writerow(['Hover'] +row)

    merged_data = []
    merged_data = merge_mouse_movement(input_folder,slowlist, saclist, hover_segments)
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'Starttime', 'Endtime', 'Duration', 'Startx', 'Starty', 'Endx', 'Endy'])  # 写入表头
        for row in merged_data:
            writer.writerow(row)
    
    return merged_data

def main():
    # 指定输入文件夹和输出文件
    input_folder = 'simplified_folder'
    filepath2 = 'merged_mousekb_data.csv'
    output_file = 'mouse_actions.csv'
    analyzer(input_folder, filepath2, output_file)


if __name__ == "__main__":
    main()