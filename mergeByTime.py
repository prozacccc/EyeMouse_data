import csv
import math
import pandas as pd

def merge_csv_files(mouse_file, eye_file, output_file):
    mouse_data = pd.read_csv(mouse_file, header=None)
    eye_data = pd.read_csv(eye_file, header=None)

    if mouse_data.shape[1] < 4 or eye_data.shape[1] < 4:
        print("输入的CSV文件格式不正确，请检查！")
        return

   # 排序数据
    mouse_data = mouse_data.sort_values(by=0)
    eye_data = eye_data.sort_values(by=0)

    # 找到重合的时间部分
    merged_data = []
    for _, mouse_row in mouse_data.iterrows():
        mouse_time = mouse_row[0]
        # 查找眼动数据中与当前键鼠时间重合的行
        eye_rows = eye_data[(eye_data.iloc[:, 0] == mouse_time)]
        if not eye_rows.empty:
            for _, eye_row in eye_rows.iterrows():
                merged_data.append([mouse_time, 
                                    mouse_row[1], 
                                    mouse_row[2], 
                                    mouse_row[3], 
                                    eye_row[1], 
                                    eye_row[2], 
                                    eye_row[3]])

    # 创建合并后的DataFrame
    result_data = pd.DataFrame(merged_data, columns=['Timestamp', 'Ation_m', 'Time_m', 'Object_m', 'Action_e', 'Time_e', 'Object_e'])

    # 保存为CSV文件
    result_data.to_csv(output_file+".csv", index=False)

    print(f"重合部分已保存至 {output_file}.csv")
    
    
    
def read_csv(filename):
    data = []
    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader, None)
        for row in reader:
            data.append(row)
    return data

def interpolate_mouse_actions(actions):
    interpolated_data = {}
    current_index = 0

    while current_index < len(actions):
        action = actions[current_index]
        if action[0] in ['Slow_move', 'Hover', 'Fast_move']:
            start_time = round(float(action[1]), 1)
            end_time = round(float(action[2]), 1)
            current_time = start_time
            if len(action) > 4:
                text = [action[0], action[1:4], action[4:]]
            else:
                text = [action[0], action[1:4]]
            while current_time <= end_time:
                current_time_str = "{:.1f}".format(current_time)  # 保留一位小数并转换为字符串
                current_time = float(current_time_str)  # 转换为浮点数
                if current_time not in interpolated_data:
                    interpolated_data[current_time] = text
                current_time += 0.1
            current_index += 1
        else:
            text = [action[0], action[1], action[2:]]
            time_point = round(float(action[1]), 1)
            time_point_str = "{:.1f}".format(time_point)  # 保留一位小数并转换为字符串
            time_point = float(time_point_str)  # 转换为浮点数
            if time_point not in interpolated_data:
                interpolated_data[time_point] = text
            elif interpolated_data[time_point][0] in ['Slow_move', 'Hover', 'Fast_move']:
                interpolated_data[time_point] = text  # 覆盖之前的动作
            else:
                pre = interpolated_data[time_point]
                text = [pre[0], pre[1], pre[2] + text[2]]
                interpolated_data[time_point] = text
                # print(interpolated_data[time_point])
            current_index += 1

    interpolated_list = [[key] + value for key, value in interpolated_data.items()]
    # for list in interpolated_list:
    #     print(list)
        
    return interpolated_list



def interpolate_eye_actions(actions):
    interpolated_data = []
    current_index = 0
    processed_times = set()  # 用于记录已处理的时间点

    while current_index < len(actions):
        action = actions[current_index]
        start_time = round(float(action[1]), 1)
        end_time = round(float(action[2]), 1)
        current_time = start_time
        while current_time <= end_time:
            current_time_str = "{:.1f}".format(current_time)  # 保留一位小数并转换为字符串
            current_time = float(current_time_str)  # 转换为浮点数
            if current_time not in processed_times:
                text = [current_time, action[0], action[1:4], action[4:]]
                interpolated_data.append(text)
                processed_times.add(current_time)
            current_time += 0.1
        current_index += 1
    # for list in interpolated_data:
    #     print(list)
    return interpolated_data


def complete_time_points(interpolated_data):
    completed_data = []
    max_time = max(interpolated_data)[0]
    current_time = min(interpolated_data)[0]
    interval = 0.1

    while current_time <= max_time:
        found = False
        for row in interpolated_data:
            if row[0] == current_time:
                completed_data.append(row)
                found = True
                break
        if not found:
            completed_data.append([current_time] + [''] * (len(interpolated_data[0]) - 1))
        current_time = round(current_time + interval, 1)

    return completed_data


def write_csv(filename, data):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


if __name__ == "__main__":
    input_filename = "eye_actions.csv"
    output_filename = "devided_eye_actions.csv"
    data = read_csv(input_filename)
    interpolated_data = interpolate_eye_actions(data)
    write_csv(output_filename, interpolated_data)    
    
    
    input_filename = "mouse_actions.csv"
    output_filename = "devided_mouse_actions.csv"
    data = read_csv(input_filename)
    interpolated_data = interpolate_mouse_actions(data)
    write_csv(output_filename, interpolated_data)

    mouse_file = 'devided_mouse_actions.csv'  # 键鼠数据文件
    eye_file = 'devided_eye_actions.csv'      # 眼动数据文件
    output_file = 'merged_eye&mouse_actions'  # 输出的Excel文件
    
    merge_csv_files(mouse_file, eye_file, output_file)
    
