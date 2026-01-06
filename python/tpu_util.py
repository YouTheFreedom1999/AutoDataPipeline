import os

def tpu_collect(output_dir):
    # 从 terminal.stdout 中 正则匹配 "TPU utilization: " 后面的数字
    with open(os.path.join(output_dir, "terminal.stdout"), 'r') as file:
        for line in file:
            if "TPU utilization: " in line:
                tpu_util = float(line.split("TPU utilization: ")[1])
                return tpu_util
    return None