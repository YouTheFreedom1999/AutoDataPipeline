
import os
import re
import json5
from k800_tma import *
from vector_util_plot import vector_util_plot
pattern0 = r"Exiting @ tick \d+ because Normal Stop!"
pattern1 = r"Exiting @ tick \d+ because m5_exit instruction encountered"
pattern2 = r"Exiting @ tick \d+ because m5_fail instruction encountered"
pattern3 = r"Exiting @ tick \d+ because Error Stop!"
pattern4 = r"Exiting @ tick \d+ because all threads have halted"
pattern5 = r"Exiting @ tick \d+ because simulation finished"

decimal_num_pattern = r'\d+'


def update_stats(stats_list):
    append_list = []
    if "coremarkScore" in stats_list:
        append_list.append("system.cpu.numCycles")
    if "TMA" in stats_list or "TMAPlot" in stats_list:
        append_list.extend(TMA_statas(stats_list))
    return append_list


def parse_statfile(config, stats_find_list):

    output_dir = config["output_path"]
    stats_dict = {}

    TMA_find_list = []
    TMA_stats_dict = {}
    if "TMA" in stats_find_list or "TMAPlot" in stats_find_list:
        TMA_find_list = TMA_additional_find(output_dir)

    with open(os.path.join(output_dir, "terminal.stdout"), 'r') as file:
        for line in file:
            if re.search(pattern0, line) or re.search(pattern1 , line) or re.search(pattern4, line) or re.search(pattern5, line):
                stats_dict["processStatus"] = "NormalStop"
                break
            elif 'gem5 has encountered a segmentation fault!' in line:
                stats_dict["proce   ssStatus"] = "*SegMentFault"
                break
            elif "panic" in line:
                stats_dict["processStatus"] = "***Panic"
                break
            elif re.search(pattern2, line) or re.search(pattern3, line):
                stats_dict["processStatus"] = "*ErrorStop"
                break
            else:
                # print(line)
                stats_dict["processStatus"] = "**NotStop"

    if stats_dict["processStatus"] != "NormalStop":
        return stats_dict

    with open(os.path.join(output_dir, "stats.txt"), "r") as file:
        for line in file:
            if "End Simulation Statistics" in line:
                break
            line = line.strip()  # 去除行首尾的空格或换行符
            if line and not line.startswith("#"):  # 忽略空行和以 "#" 开头的注释行
                key, value = line.split("#")[0].split()[:2]  # 使用空格分割行，并获取前两个元素
                if key in stats_find_list:
                    stats_dict[key] = value  # 将键值对添加到字典中
                if key in TMA_find_list:
                    TMA_stats_dict[key] = float(value)  # 将键值对添加到字典中

        if "coremarkScore" in stats_find_list and "coremark" in config["kernel"].lower():
            coremark_exe_name = config["kernel"].split("/")[-1]
            coremark_iteration_times = int(re.findall(
                decimal_num_pattern, coremark_exe_name)[-1])
            # print("coremark_iteration_times: ", coremark_iteration_times)
            stats_dict["coremarkScore"] = 1e6 / (int(stats_dict["system.cpu.numCycles"]) /
                                                 coremark_iteration_times)
        elif "coremarkScore" in stats_find_list:
            stats_dict["coremarkScore"] = -1

        if "TMA" in stats_find_list or "TMAPlot" in stats_find_list:
            for key in TMA_find_list:
                if key not in TMA_stats_dict:
                    TMA_stats_dict[key] = 0
            compute_TMA(stats_dict, TMA_stats_dict)

            output_path = os.path.join(output_dir, "TMA.png")
            TMA_plot(config, stats_dict, output_path)

        if "trace" in stats_find_list:
            parse_trace_log(os.path.join(output_dir, "trace.log"),config['numThreads'])
    
    if "vector.util" in stats_find_list:
        stats_dict["vector.util"] = vector_util_plot(output_dir)

    return stats_dict


# file_path="/project/Develop/CPU/design/sunjiahao/gem5_work/gem5_public/mutil_run/m5out/Sweep0_13"
# stats_find_list=["finalTick" , "simTicks" , "simFreq" , "hostTickRate"]

# print(parse_statfile(file_path , stats_find_list ))
