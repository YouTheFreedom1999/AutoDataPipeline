

################## user define vector util plot
import numpy as np  
import matplotlib.pyplot as plt  
import os
from os import path

# user_out_dir = "/home/sjh/emu1/gem5/m5out_debug"

def vector_util_plot(user_out_dir):

    if not os.path.exists(user_out_dir+"/vector_util.txt"):
        return False
    columns = []  
    for _ in range(1, 4):  # 跳过第一列，只初始化2-4列  
        columns.append([])  
    
    # 读取文件并解析数据  
    with open(path.join(user_out_dir, "vector_util.txt"), 'r') as file:  
        for line in file:  
            data = line.strip().split(';')  
            assert(len(data) == 4)
            for i in range(1, 4):  # 跳过第一列（索引为0），只处理2-4列  
                columns[i-1].append(float(data[i]))  
    
    columns = [np.array(col) for col in columns]  
    
    plt.figure(figsize=(32, 6))  
    legand_name = ["vsu" , "veu" , "vlsu"]
    for i, col in enumerate(columns): 
        plt.plot(col, label=f'{legand_name[i]}')
    
    # 添加标题和轴标签  
    plt.title('Vector Execute Unit util')  

    plt.xlabel('Cycle')  
    plt.ylabel('Rate')  

    plt.legend()  
    plt.savefig(path.join(user_out_dir, "vector_util.png"))  
    return True

################## user define 

# stats_find_list = [
# "system.cpu.commit.kernelCycles::0",
# "system.cpu.commit.kernelCycles::1",
# "system.cpu.commit.kernelCycles::2",
# "system.cpu.commit.kernelCycles::3",
# "system.cpu.vsu.utilization" , 
# "system.cpu.veu.utilization" , 
# "system.cpu.vlsu_load.utilization" , 
# "system.cpu.vlsu_store.utilization" , 
# "system.cpu.vlsu0.utilization" , 
# "system.cpu.vlsu1.utilization" , 
# "system.cpu.vlsu.utilization"]

# stats_dict = {}

# with open(os.path.join(user_out_dir, "stats.txt"), "r") as file:
#     for line in file:
#         if "End Simulation Statistics" in line:
#             break
#         line = line.strip()  # 去除行首尾的空格或换行符
#         if line and not line.startswith("#"):  # 忽略空行和以 "#" 开头的注释行
#             key, value = line.split("#")[0].split()[:2]  # 使用空格分割行，并获取前两个元素
#             if key in stats_find_list:
#                 stats_dict[key] = value  # 将键值对添加到字典中

# for key in stats_find_list:
#     if key in stats_dict:
#         print(key, ":", stats_dict[key])
