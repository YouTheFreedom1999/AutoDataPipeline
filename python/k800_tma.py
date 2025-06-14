import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
import subprocess
import re
import json5
import time

TMA_rename_width = 0
def time_statistics(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"函数 {func.__name__} 执行耗时: {elapsed_time} 秒")
        return result
    return wrapper

# add will use perf counter 
def TMA_additional_find(config_file_path):
    global TMA_rename_width
    with open(os.path.join(config_file_path, "config.json"), 'r') as gem5_config_file:
        gem_config_json = json5.load(gem5_config_file)
        TMA_rename_width = gem_config_json["system"]["cpu"][0]["roqBankNum"]

    TMA_find_list = []
    TMA_find_list.append("system.cpu.ipc")
    TMA_find_list.append("system.cpu.numCycles")
 
    TMA_find_list.append("system.cpu.commit.instsCommitted")
    TMA_find_list.append("system.cpu.commit.opsCommitted")
    TMA_find_list.append("system.cpu.commit.memRefs")
    TMA_find_list.append("system.cpu.commit.loads")
    TMA_find_list.append("system.cpu.commit.amos")
    TMA_find_list.append("system.cpu.commit.membars")
    TMA_find_list.append("system.cpu.commit.branches")
    TMA_find_list.append("system.cpu.commit.vectorInstructions")
    TMA_find_list.append("system.cpu.commit.floating")
    TMA_find_list.append("system.cpu.commit.integer")
    TMA_find_list.append("system.cpu.commit.functionCalls")

    TMA_find_list.append("system.cpu.roq.squashInsts")
    TMA_find_list.append("system.cpu.me1.recoverySlot")
    TMA_find_list.append("system.cpu.me1.stallCauseFrontendSlot")
    TMA_find_list.append("system.cpu.me1.stallCauseRoqFullSlot")
    TMA_find_list.append("system.cpu.me1.stallCauseWaitFlushSlot")
    TMA_find_list.append("system.cpu.me1.stallCauseCopyBackSlot")
    TMA_find_list.append("system.cpu.me1.stallCauseUnKnowSlot")


    return TMA_find_list

# add will show TMA result
# @time_statistics
def TMA_statas(stats_list):
    TMA_statas_list = []
    TMA_statas_list.append("TMA.cycle")
    TMA_statas_list.append("TMA.IPC")
    TMA_statas_list.append("TMA.renameWidth")
    if "coremarkScore" in stats_list:
        TMA_statas_list.append("TMA.Coremark")

    TMA_statas_list.append("TMA.frontendBound")
    TMA_statas_list.append("TMA.badSpeculation")
    TMA_statas_list.append("TMA.retire")
    TMA_statas_list.append("TMA.backendBound")

    # TMA_statas_list.append("TMA.frontendBound.latency")
    # TMA_statas_list.append("TMA.frontendBound.bandwidth")
    TMA_statas_list.append("TMA.badSpeculation.misprediction")
    TMA_statas_list.append("TMA.badSpeculation.recoveryBubble")
    # TMA_statas_list.append("TMA.backendBound.coreBound")
    # TMA_statas_list.append("TMA.backendBound.memoryBound")

    # TMA_statas_list.append("TMA.frontendBound.latency.ITLBMiss")
    # TMA_statas_list.append("TMA.frontendBound.latency.IcacheMiss")
    # TMA_statas_list.append("TMA.frontendBound.latency.misprediction")
    # TMA_statas_list.append("TMA.frontendBound.latency.pipelineRestart")
    # TMA_statas_list.append("TMA.frontendBound.latency.unknown")
    # TMA_statas_list.append("TMA.frontendBound.bandwidth.branch")
    # TMA_statas_list.append("TMA.frontendBound.bandwidth.cacheline")
    # TMA_statas_list.append("TMA.frontendBound.bandwidth.unknown")

    # TMA_statas_list.append("TMA.badSpeculation.misprediction.branch")
    # TMA_statas_list.append("TMA.badSpeculation.misprediction.memoryViolation")
    # TMA_statas_list.append("TMA.badSpeculation.recoveryFetch.branch")
    # TMA_statas_list.append("TMA.badSpeculation.recoveryFetch.memoryViolation")
    # TMA_statas_list.append("TMA.badSpeculation.recoveryROB.branch")
    # TMA_statas_list.append("TMA.badSpeculation.recoveryROB.memoryViolation")

    TMA_statas_list.append("TMA.retire.integer")
    TMA_statas_list.append("TMA.retire.float")
    TMA_statas_list.append("TMA.retire.branch")
    TMA_statas_list.append("TMA.retire.load")
    TMA_statas_list.append("TMA.retire.store")

    # TMA_statas_list.append("TMA.backendBound.coreBound.serial")
    # TMA_statas_list.append("TMA.backendBound.coreBound.execute")
    # TMA_statas_list.append("TMA.backendBound.memoryBound.load")
    # TMA_statas_list.append("TMA.backendBound.memoryBound.store")
    return TMA_statas_list

# @time_statistics
def compute_TMA(stats_dict, TMA_stats_dict):

    global TMA_rename_width
    # print(TMA_rename_width)
    total_cycle = TMA_stats_dict["system.cpu.numCycles"]
    IPC = TMA_stats_dict["system.cpu.ipc"]
    stats_dict["TMA.renameWidth"] = TMA_rename_width
    total_slot = total_cycle * TMA_rename_width

    retire_slot = TMA_stats_dict["system.cpu.commit.instsCommitted"]
    retire__integer__slot = TMA_stats_dict["system.cpu.commit.integer"] 
    retire__float__slot = TMA_stats_dict["system.cpu.commit.floating"] 
    retire__branch__slot = TMA_stats_dict["system.cpu.commit.branches"]
    retire__load__slot = TMA_stats_dict["system.cpu.commit.loads"]
    retire__store__slot = TMA_stats_dict["system.cpu.commit.memRefs"] - retire__load__slot

    # Level 3
   
    retire__integer = retire__integer__slot / total_slot
    retire__float = retire__float__slot / total_slot
    retire__branch = retire__branch__slot / total_slot
    retire__load = retire__load__slot / total_slot
    retire__store = retire__store__slot / total_slot

    # Level 2
    # frontend_bound__latency = 0
    # frontend_bound__bandwidth = 0

    bad_speculation__misprediction = TMA_stats_dict["system.cpu.roq.squashInsts"] / total_slot
    bad_speculation__recovery = TMA_stats_dict["system.cpu.me1.recoverySlot"] / total_slot

    # backend_bound__core = 0
    # backend_bound__memory = 0

    # Level 1
    frontend_bound = TMA_stats_dict["system.cpu.me1.stallCauseFrontendSlot"] / total_slot

    bad_speculation = \
        bad_speculation__misprediction + \
        bad_speculation__recovery
    
    retire = \
        retire__integer + \
        retire__float + \
        retire__branch + \
        retire__load + \
        retire__store
    
    backend_bound =( TMA_stats_dict["system.cpu.me1.stallCauseCopyBackSlot"] + \
                    TMA_stats_dict["system.cpu.me1.stallCauseRoqFullSlot"] + \
                    TMA_stats_dict["system.cpu.me1.stallCauseWaitFlushSlot"] + \
                    TMA_stats_dict["system.cpu.me1.stallCauseUnKnowSlot"])/total_slot
                    

    stats_dict["TMA.cycle"] = total_cycle
    stats_dict["TMA.IPC"] = IPC
    stats_dict["TMA.renameWidth"] = TMA_rename_width

    stats_dict["TMA.frontendBound"] = frontend_bound
    stats_dict["TMA.badSpeculation"] = bad_speculation
    stats_dict["TMA.retire"] = retire
    stats_dict["TMA.backendBound"] = backend_bound

    # stats_dict["TMA.frontendBound.latency"] = frontend_bound__latency
    # stats_dict["TMA.frontendBound.bandwidth"] = frontend_bound__bandwidth
    stats_dict["TMA.badSpeculation.misprediction"] = bad_speculation__misprediction
    stats_dict["TMA.badSpeculation.recoveryBubble"] = bad_speculation__recovery

    stats_dict["TMA.retire.integer"] = retire__integer
    stats_dict["TMA.retire.float"] = retire__float
    stats_dict["TMA.retire.branch"] = retire__branch
    stats_dict["TMA.retire.load"] = retire__load
    stats_dict["TMA.retire.store"] = retire__store

    # stats_dict["TMA.backendBound.coreBound.serial"] = backend_bound__core__serial
    # stats_dict["TMA.backendBound.coreBound.execute"] = backend_bound__core__execute
    # stats_dict["TMA.backendBound.memoryBound.load"] = backend_bound__memory__load
    # stats_dict["TMA.backendBound.memoryBound.store"] = backend_bound__memory__store

# @time_statistics
def TMA_plot(config, stats_dict, picture_file):
    # print(stats_dict)
    kernel = config["kernel"]
    kernel = kernel.split("/")[-1]
    output_path = config["outputDir"]

    # git_ver = '0a63eee\n'
    git_ver = os.popen("git rev-parse --short HEAD")
    git_ver = git_ver.read()
    git_ver = git_ver[0:-1]

    now = datetime.now()  # current date and time
    now_str = now.strftime("%Y-%m-%d, %H:%M:%S")

    TMA_1 = {
        "Frontend Bound": stats_dict["TMA.frontendBound"],
        "Bad Speculation": stats_dict["TMA.badSpeculation"],
        "Retire": stats_dict["TMA.retire"],
        "Backend Bound": stats_dict["TMA.backendBound"],
    }

    TMA_2 = {
        # "Latency": stats_dict["TMA.frontendBound.latency"],
        # "Bandwidth": stats_dict["TMA.frontendBound.bandwidth"],
        "Misprediction": stats_dict["TMA.badSpeculation.misprediction"],
        "Recovery Bubble": stats_dict["TMA.badSpeculation.recoveryBubble"],
        # "Retire": stats_dict["TMA.retire"],
        # "Core Bound": stats_dict["TMA.backendBound.coreBound"],
        # "Memory Bound": stats_dict["TMA.backendBound.memoryBound"],
    }

    # TMA_3_frontend_bound = {
    #     "LT-ITLB Miss": stats_dict["TMA.frontendBound.latency.ITLBMiss"],
    #     "LT-I$ Miss": stats_dict["TMA.frontendBound.latency.IcacheMiss"],
    #     "LT-Mispred": stats_dict["TMA.frontendBound.latency.misprediction"],
    #     "LT-Pipe Restart": stats_dict["TMA.frontendBound.latency.pipelineRestart"],
    #     "LT-Unknown": stats_dict["TMA.frontendBound.latency.unknown"],
    #     "BW-Br": stats_dict["TMA.frontendBound.bandwidth.branch"],
    #     "BW-$line": stats_dict["TMA.frontendBound.bandwidth.cacheline"],
    #     "BW-Unknown": stats_dict["TMA.frontendBound.bandwidth.unknown"],
    # }

    # TMA_3_bad_speculation = {
    #     "Br Mispred": stats_dict["TMA.badSpeculation.misprediction.branch"],
    #     "Br Recovery\nFetch": stats_dict["TMA.badSpeculation.recoveryFetch.branch"],
    #     "Br Recovery\nROB": stats_dict["TMA.badSpeculation.recoveryROB.branch"],
    #     "Mem Vio Mispred": stats_dict["TMA.badSpeculation.misprediction.memoryViolation"],
    #     "Mem Vio Recovery\nFetch": stats_dict["TMA.badSpeculation.recoveryFetch.memoryViolation"],
    #     "Mem Vio Recovery\nROB": stats_dict["TMA.badSpeculation.recoveryROB.memoryViolation"],
    # }

    TMA_3_retire = {
        "Integer": stats_dict["TMA.retire.integer"],
        "Float": stats_dict["TMA.retire.float"],
        "Branch": stats_dict["TMA.retire.branch"],
        "Load": stats_dict["TMA.retire.load"],
        "Store": stats_dict["TMA.retire.store"],
    }

    # TMA_3_backend_bound = {
    #     "Core Bound Serial": stats_dict["TMA.backendBound.coreBound.serial"],
    #     "Core Bound Execute": stats_dict["TMA.backendBound.coreBound.execute"],
    #     "Memory Bound Load": stats_dict["TMA.backendBound.memoryBound.load"],
    #     "Memory Bound Store": stats_dict["TMA.backendBound.memoryBound.store"],
    # }

    labels = list(TMA_1.keys())
    data = np.array(list(TMA_1.values()))
    data_cum = data.cumsum(axis=0)
    category_names = labels
    category_colors = plt.get_cmap('RdYlGn')(np.linspace(0.15, 0.85, data.shape[0]))

    plt.subplots(6, 1, figsize=(12, 6))

    suptitle = "TMA for Kernel: " + kernel + ",  Result: " + output_path
    suptitle = suptitle + "\nCycles: " + "{:.0f}".format(stats_dict["TMA.cycle"])
    suptitle = suptitle + ", IPC: " + "{:.2f}".format(stats_dict["TMA.IPC"])
    if "coremarkScore" in stats_dict:
        suptitle = suptitle + ", Coremark: " + "{:.2f}".format(stats_dict["coremarkScore"]) + "/MHz"
    plt.suptitle(suptitle, x=0.5, y=0.95, fontsize=15)

    plt.subplots_adjust(
        left=0.09,
        bottom=0.07,
        right=0.97,
        top=0.8,
        wspace=0,
        hspace=1
    )

    version_info = "Git Version: " + git_ver + ", Time: " + now_str
    ax = plt.subplot(6, 1, 6)
    ax.text(
        0.85,
        -0.6,
        version_info,
        ha='center',
        va='center',
        transform=ax.transAxes,
    )

    ax = plt.subplot(6, 1, 1)
    plot_barh(ax, TMA_1,
              title="1st Layer", start=0, scale=1)
    ax = plt.subplot(6, 1, 2)
    plot_barh(ax, TMA_2,
              title="2nd Layer", start=0, scale=1)
    # ax = plt.subplot(6, 1, 3)
    # plot_barh(ax, TMA_3_frontend_bound,
    #           title="3rd Layer\nFrontend\nBound", start=0, scale=1)
    # ax = plt.subplot(6, 1, 4)
    # plot_barh(ax, TMA_3_bad_speculation,
    #           title="3rd Layer\nBad\nSpeculation", start=0, scale=1)
    ax = plt.subplot(6, 1, 5)
    plot_barh(ax, TMA_3_retire,
              title="3rd Layer\nRetire", start=0, scale=1)
    # ax = plt.subplot(6, 1, 6)
    # plot_barh(ax, TMA_3_backend_bound,
    #           title="3rd Layer\nBackend\nBound", start=0, scale=1)

    plt.savefig(picture_file, dpi=350)
    plt.close()


def plot_barh(ax, source_dict, title="", start=0, scale=1):
    labels = list(source_dict.keys())
    data = np.array(list(source_dict.values()))
    data_cum = data.cumsum(axis=0)
    data_sum = data_cum[-1]

    category_names = labels
    category_colors = plt.get_cmap('RdYlGn')(np.linspace(0.15, 0.85, data.shape[0]))

    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=0).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[i]
        starts = data_cum[i] - widths

        if colname.find('\n') == -1:
            colname = colname + '\n'
        else:
            colname = colname + ' '
        colname = colname + "{:.2f}%".format(widths*100)

        ax.barh(title, widths, left=starts, height=0.5,
                label=colname, color=color)
        xcenters = starts + widths / 2

        text = "{:.1f}%".format(widths*100)
        text = "" if widths/data_sum < 0.04 else text
        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.3 else 'black'
        ax.text(xcenters, 0, text, ha='center', va='center',
                color=text_color)
    ax.text(
        0.975,
        1.38,
        "sum:    \n{:0>5.2f}%".format(data_sum*100),
        ha='center',
        va='center',
        color='black',
        transform=ax.transAxes
    )
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0.5, 0.9),
              loc='lower center', fontsize='small')
