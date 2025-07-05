import json5
# import argparse
from typing import Dict, List, Any, Optional, Union, Generator

from itertools import product

def read_config(file_path: str) -> Dict[str, Any]:
    """读取配置文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json5.load(f)
    except FileNotFoundError:
        print(f"错误：找不到配置文件 '{file_path}'")
        exit(1)
    except json5.JSONDecodeError as e:
        print(f"错误：配置文件格式错误 - {e}")
        exit(1)

def generate_range_values(start: Union[int, float], end: Union[int, float], 
                         step: Union[int, float]) -> Generator[Union[int, float], None, None]:
    """生成范围内的所有值，支持整数和浮点数"""
    current = start
    while current <= end:
        yield current
        current += step

def process_variable_params(variable_params: Dict[str, Any]) -> Dict[str, List[Any]]:
    """处理可变参数，包括范围配置"""
    processed_params = {}
    for param, value in variable_params.items():
        if param == "kernel":
            # print(value)
            # value 可能为str或者 str的list 根据路径是 文件还是目录 ，获取文件列表 , 找出 所有 .elf 和 .riscv 文件
            import os
            if isinstance(value, str):
                value = [value]
            processed_params[param] = []
            for path in value:
                if os.path.isdir(path):
                    processed_params[param].extend([os.path.join(path, f) for f in os.listdir(path) if f.endswith('.elf') or f.endswith('.riscv')])
                elif os.path.isfile(path):
                    processed_params[param].append(path)
                else:
                    print(f"错误：参数 '{param}' 的路径不存在")
        elif isinstance(value, dict):
            # 处理范围配置
            if 'start' in value and 'end' in value and 'step' in value:
                start = value['start']
                end = value['end']
                step = value['step']
                # 确保类型一致
                if isinstance(start, float) or isinstance(end, float) or isinstance(step, float):
                    start = float(start)
                    end = float(end)
                    step = float(step)
                else:
                    start = int(start)
                    end = int(end)
                    step = int(step)
                processed_params[param] = list(generate_range_values(start, end, step))
            else:
                print(f"错误：参数 '{param}' 的范围配置不完整，需要包含 start、end 和 step")
                exit(1)
        else:
            # 处理普通值列表
            processed_params[param] = value
    # print(processed_params)
    return processed_params

def generate_group_commands(group: Dict[str, Any], group_number: int, global_config: Dict[str, Any]) -> List[str]:
    """为单个命令组生成所有命令"""
    # 获取全局配置
    common_command_template = global_config.get('common_command_template', '')
    if not common_command_template:
        print(f"错误：缺少 'common_command_template'")
        exit(1)
    if isinstance(common_command_template, list):
        common_command_template = " ".join(common_command_template)
    
    group_command_template = group.get('group_command_template', '')
    if not group_command_template:
        print(f"错误：缺少 'group_command_template' for group {group_number}")
        exit(1)
    if isinstance(group_command_template, list):
        group_command_template = " ".join(group_command_template)
        
    output_pattern = global_config.get('output_pattern', 'results_{group_name}_{scan_number}/output_{group_name}_{scan_number}.txt')
    
    # 获取组配置
    group_name = group.get('group_name', f'group_{group_number}')
    fixed_params = group.get('fixed_params', {})
    
    # 处理可变参数
    variable_params = group.get('variable_params', {})
    processed_variable_params = process_variable_params(variable_params)
    
    # 获取固定参数组
    fixed_param_groups = group.get('fixed_param_groups', [])
    
    # 生成所有可能的参数组合
    param_combinations = []
    
    if processed_variable_params:
        # 获取每个可变参数的所有可能值
        param_values = [processed_variable_params[key] for key in sorted(processed_variable_params.keys())]
        # 生成所有可能的组合
        base_combinations = list(product(*param_values))
    else:
        # 如果没有可变参数，至少有一个空组合
        base_combinations = [tuple()]
    
    if fixed_param_groups:
        # 为每个固定参数组生成组合
        for group_params in fixed_param_groups:
            for base_combination in base_combinations:
                combination = {}
                # 添加可变参数
                for i, key in enumerate(sorted(processed_variable_params.keys())):
                    combination[key] = base_combination[i]
                # 添加固定参数组
                combination.update(group_params)
                param_combinations.append(combination)
    else:
        # 如果没有固定参数组，直接使用可变参数组合
        for base_combination in base_combinations:
            combination = {}
            for i, key in enumerate(sorted(processed_variable_params.keys())):
                combination[key] = base_combination[i]
            param_combinations.append(combination)
    
    # 生成命令
    commands = []
    params_list = []
    for scan_number, params in enumerate(param_combinations):
        # 合并固定参数和当前组合的可变参数
        all_params = {**fixed_params, **params}
        # 添加组信息
        all_params['group_number'] = group_number
        all_params['group_name'] = group_name
        all_params['scan_number'] = scan_number
        # 生成输出路径
        try:
            all_params['output_path'] = output_pattern.format(**all_params)
        except KeyError as e:
            print(f"错误：输出模式中引用了未定义的参数 '{e}'")
            exit(1)
        # 生成公共命令部分
        try:
            common_command = common_command_template.format(**all_params)
        except KeyError as e:
            print(f"错误：公共命令模板中引用了未定义的参数 '{e}'")
            exit(1)
        # 生成组特定命令部分
        try:
            group_command = group_command_template.format(**all_params)
        except KeyError as e:
            print(f"错误：组命令模板中引用了未定义的参数 '{e}'")
            exit(1)
        # 合并公共命令和组特定命令
        command = f"{common_command} {group_command}"
        commands.append(command)
        # print(all_params)
        params_list.append(all_params)
    
    return commands , params_list

def gen_cmd(config_file):
    # parser = argparse.ArgumentParser(description='命令组合生成器')
    # parser.add_argument('--config_file', help='配置文件路径')
    # parser.add_argument('-o', '--output', help='输出文件路径，不指定则打印到控制台')
    # args = parser.parse_args()
    
    # 读取配置
    config = read_config(config_file)
    
    # 获取全局配置和命令组
    global_config = {k: v for k, v in config.items() if k != 'groups'}
    command_groups = config.get('groups', [])
    
    if not command_groups:
        # 兼容旧格式：如果没有groups，将整个配置视为一个组
        command_groups = [config]
    
    # 为每个组生成命令
    all_commands = []
    all_params= []
    for group_number, group in enumerate(command_groups):
        group_commands , params_list = generate_group_commands(group, group_number, global_config)
        all_commands.extend(group_commands)
        all_params.extend(params_list)
    
    return [all_commands, all_params]

    # 输出结果
    # if args.output:
    #     try:
    #         with open(args.output, 'w', encoding='utf-8') as f:
    #             for command in all_commands:
    #                 f.write(command + '\n')
    #         print(f"成功生成 {len(all_commands)} 条命令到文件 '{args.output}'")
    #     except Exception as e:
    #         print(f"错误：无法写入输出文件 - {e}")
    #         exit(1)
    # else:
    #     print(f"成功生成 {len(all_commands)} 条命令：")
    #     for command in all_commands:
    #         print(command)



# if __name__ == "__main__":
#     main()    

