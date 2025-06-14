import os, shutil
import csv
import subprocess
import argparse
import signal

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from parse_statfile import *
from command_gen import *

COLORS = {
    'default': '\033[0m',
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m'
}

def print_color_text(text, color):
    colored_text = f"{COLORS[color]}{text}{COLORS['default']}"
    print(colored_text , end='')

# print_color_text("Hello, World!", 'red')
# print_color_text("Hello, World!", 'green')
# print_color_text("Hello, World!", 'blue')


def execute_command(command):
    subprocess.run(command, shell=True)
    return True

gem_bin = "../build/RISCV/gem5.fast"

def handler(signum, frame):
    print('Ctrl+C signal received')
    os.system("stty echo")
    exit(0)
    
def push_thread_cmd(cmd_list , skip_run):
    if skip_run:
        return
    task_list = []
    for idx in range(len(cmd_list)):
        executor = ThreadPoolExecutor(max_workers=64) 
        print_color_text("[pa-dev]" ,'red')
        print_color_text(f" PUSH task({idx}/{len(cmd_list)}) to execute \r" ,'magenta')
        # task_list.append(executor.submit(execute_command , cmd_list[idx]))
        print(cmd_list[idx])
        print()

    finish = 1
    for task in as_completed(task_list):
        result = task.result()
        if result:
            print_color_text("[pa-dev]" ,'red')
            print_color_text(f" FINISH task({finish}/{len(cmd_list)})\r" ,'magenta')
            finish+=1
    print("\r")

    executor.shutdown()
def report_process(stats_list , config_list , csvfilename):
    stats_list.extend(update_stats(stats_list))
    csv_header = ["processStatus"]
    csv_header.extend(list(config_list[0]))
    csv_header.extend(stats_list)

    # print(csv_header)
    if not os.path.exists(report_file):
        os.makedirs(report_file)

    normal_stdout_path = os.path.join(report_file , "normal_stdout_files")
    error_stdout_path = os.path.join(report_file , "error_stdout_files")
    if not os.path.exists(normal_stdout_path):
        os.mkdir(normal_stdout_path)
    if not os.path.exists(error_stdout_path):
        os.mkdir(error_stdout_path)

    with open(os.path.join(report_file , csvfilename), 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=csv_header)
        writer.writeheader()
        normalCounter = 0
        errorCounter  = 0

        for config in config_list:
            config.update(parse_statfile(config, stats_list))
            writer.writerow(config)
            if config['processStatus'] == "NormalStop" :
                normalCounter += 1
                shutil.copy(
                    os.path.join(config["output_path"], "terminal.stdout"),
                    os.path.join(normal_stdout_path , f"stdout{config['scan_number']}"),
                )
            else:
                errorCounter += 1
                shutil.copy(
                    os.path.join(config["output_path"], "terminal.stdout"),
                    os.path.join(error_stdout_path , f"stdout{config['scan_number']}"),
                )
    print_color_text(f"[pa-dev] " ,'red')
    print_color_text(f"WRITE  {csvfilename} " , 'magenta')
    print(" ")
    return (errorCounter, normalCounter)

if __name__ == "__main__":
    
    signal.signal(signal.SIGINT, handler)
    parser = argparse.ArgumentParser()

    parser.add_argument( "--configFile" , type=str , help="input json file to config sim")
    parser.add_argument( "--reportPath" , type=str , help="report output dir , must dir")
    parser.add_argument( "--collection" , action="store_true" , help="only collect data")
    
    args = parser.parse_args()

    sweep_config_file = args.configFile
    report_file       = args.reportPath
    isonlyColl        = args.collection
    skip_run = isonlyColl
    if skip_run:
        csvfilename = "coll_report.csv"
    else:
        csvfilename = "run_report.csv"

    ret_list = gen_cmd(sweep_config_file)

    cmd_list = ret_list[0]
    config_list = ret_list[1]

    config_json = json5.load(open(sweep_config_file, 'r', encoding='utf-8'))
    stats_list = config_json["stats"]

    assert len(cmd_list) == len(config_list)

    print_color_text(f"[pa-dev]" ,'red')
    print_color_text(f" process {len(cmd_list)}" , 'magenta')
    print(" ")

    push_thread_cmd(cmd_list , skip_run)

    errorCounter , normalCounter= report_process(stats_list , config_list , csvfilename)
                
    print_color_text(f"[pa-dev] " ,'red')
    print_color_text(f"Normal stop task({normalCounter}/{len(cmd_list)}) | ", 'yellow') 
    print_color_text(f"Error stop task({errorCounter}/{len(cmd_list)}) "  , 'yellow') 
    print(" ")

    print("#"*100)

    os.system("stty echo")