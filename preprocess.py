import pandas as pd
import os
import glob
import csv
from collections import defaultdict


def process_click_csv(input_file):
    df = pd.read_csv(input_file, header=1)

    if df.shape[1] < 3:
        print("click.csv文件格式不正确，请检查！")
        return None

    # 找到第二列出现正数的时间
    invalid_index = df[df.iloc[:, 1] > 0].index.min()
    # 上一次为最后一次负数的时间
    invalid_index = invalid_index - 1

    # 如果没有找到正数，保留全部数据
    if pd.isna(invalid_index):
        print("未找到正数，保留所有数据。")
        return df, None

    # 过滤出有效数据
    valid_data = df.iloc[:invalid_index]
    print(invalid_index)

    # 返回有效数据和无效数据的时间节点
    return valid_data, df.iloc[invalid_index, 0]


def process_other_csv_files(input_folder, time_threshold, output_folder):
    # 获取所有CSV文件
    other_files = glob.glob(os.path.join(input_folder, '*.csv'))

    for file in other_files:
        file_name = os.path.basename(file)
        if file_name == 'KB.csv':
            # 如果是KB.csv文件，只读取前两列
            df = pd.read_csv(file, usecols=[0, 1])
        else:
            # 其他文件读取所有列
            df = pd.read_csv(file)

        # 保留时间之前的数据
        valid_data = df[df.iloc[:, 0] <= time_threshold]

        # 保存处理后的数据到新文件
        output_file = os.path.join(output_folder, os.path.basename(file))
        valid_data.to_csv(output_file, index=False)
        print(f"处理后的数据已保存至 {output_file}")



def simplify_mouse_movement(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            input_file = os.path.join(input_folder, filename)
            if filename == 'eye_tracking.csv':
                output_file =  filename
            else:
                output_file = os.path.join(output_folder, filename)

            unique_timestamps = set()
            timestamp_data = defaultdict(list)
            header = []
            with open(input_file, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                for row in reader:
                    timestamp = "{:.2f}".format(float(row[0]))
                    if timestamp not in unique_timestamps:
                        unique_timestamps.add(timestamp)
                        # 将时间戳后面的所有数据保存为一个列表
                        timestamp_data[timestamp] = [val for val in row[1:]]

            sorted_timestamps = sorted(unique_timestamps)

            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                for timestamp in sorted_timestamps:
                    row_data = [timestamp] + timestamp_data[timestamp]
                    writer.writerow(row_data)


# 主程序
def main():
    input_folder = 'data'  # 所有CSV文件所在的文件夹
    click_file = os.path.join(input_folder, 'click.csv')
    output_folder = 'simplified_folder'
    
    valid_data, invalid_time = process_click_csv(click_file)
    
    if invalid_time is not None:
        print(f"第一次出现正数的时间为: {invalid_time}")
        # 创建输出文件夹
        if not os.path.exists('processed_data'):
            os.makedirs('processed_data')
        
        process_other_csv_files(input_folder, invalid_time, 'processed_data')

    # 简化行为数据
    simplify_mouse_movement('processed_data', output_folder)

if __name__ == "__main__":
    main()
