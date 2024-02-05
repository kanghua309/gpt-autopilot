#!/usr/bin/env python3

import os
import sys
from modules.config import get_config, save_config
# from modules.helpers import yesno
import openai
# -*- coding: utf-8 -*-

# import io
# import traceback
# import openai
# import shutil
# import random
# import json
# import copy
# import time
# import sys
# import os
# import re

# from modules.helpers import yesno, safepath, codedir, numberfile, reset_code_folder, relpath, ask_input
# from modules.config import get_config, save_config
# from modules import prompt_selector
# from modules import gpt_functions
# from modules import betterprompter
# from modules import filesystem
# from modules import checklist
# #from modules import cmd_args
# from modules import chatgpt
# from modules import tokens
# from modules import paths
# from modules import git



CONFIG = get_config()


def get_code_files(project_dir):
    code_files = []
    # 定义要搜索的文件后缀
    extensions = ('.py', '.js', '.c', '.c++', '.cpp', '.css', '.html')
    # 遍历项目目录
    print("project_dir:",project_dir)
    for root, dirs, files in os.walk(project_dir):
        print("root:",root,dirs,files)
        for file in files:
            #print("file:",file)
            if file.endswith(extensions):
                #print(os.path.join(root, file))
                code_files.append(os.path.join(root, file))
    
    print("code_files:",code_files)
    return code_files





# MAIN FUNCTION
def run_conversation(project_dir, model = "gpt-3.5-turbo-16k-0613", messages = [], conv_id = None, temp = 1.0):
    # if conv_id is None:
    #     conv_id = numberfile(paths.relative("history"))

    # 从./promote/default/course/system_message中读取数据
    with open('./prompts/default/course/system_message', 'r') as file:
       system_message = {
           "role" : "system",
           "content": file.read()
       }
    #print("system_message:",system_message)
    messages.append(system_message)
    try:
        response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temp,
                request_timeout=120,
            )
    except Exception as e:
        raise

    # get chatgpt response
    #print("response:",response)
    print(u"response:",response["choices"][0]["message"]["content"])

    messages.append(response["choices"][0]["message"]) # type: ignore
    #print("messages:",messages)
    
    code_files = get_code_files(project_dir)
    prompt = ""
    for cf in code_files:
        with open(cf, 'r') as file:     
            prompt += cf + ":" + file.read() + "\n"

    
    print("prompt:",prompt)
    user_message = {
        "role": "user",
        "content": prompt
    }
    messages.append(user_message)

    try:
        response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temp,
                request_timeout=120,
            )
    except Exception as e:
        raise
    print(u"response:",response["choices"][0]["message"]["content"])
    messages.append(response["choices"][0]["message"]) # type: ignore
    # loop until project is finished
    return response["choices"][0]["message"]["content"]

    
def ask_input(message):
    global autonomous_message_count
    autonomous_message_count = 0
    try:
        return input(message)
    except KeyboardInterrupt:
        print("\n\nExiting")
        sys.exit(0)

def yesno(prompt, answers = ["y", "n"]):
    answer = ""
    while answer not in answers:
        slash_list = '/'.join(answers)
        answer = ask_input(f"{prompt} ({slash_list}): ")
        if answer not in answers:
            or_list = "' or '".join(answers)
            print(f"\nERROR:    Please type '{or_list}'\n")
    return answer

def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key in [None, ""]:
        if "api_key" in CONFIG:
            api_key = CONFIG["api_key"]
        else:
            print("Put your OpenAI API key into the config.json file or OPENAI_API_KEY environment variable to skip this prompt.\n")
            api_key = ask_input("Input OpenAI API key: ").strip()

            if api_key == "":
                sys.exit(1)

            save = yesno("Do you want to save this key to config.json?", ["y", "n"])
            if save == "y":
                CONFIG["api_key"] = api_key
                save_config(CONFIG)
            print()
    return api_key




if __name__ == "__main__":
    print("脚本名：", sys.argv[0])
    # for i, arg in enumerate(sys.argv[1:], start=1):
    #     print(f"参数 {i}: {arg}")
    if len(sys.argv) != 3:
        print("Usage: python gpt-autocourse.py <project_dir> <course_path>")
        sys.exit(1)

    project_dir  = sys.argv[1]
    course_path  = sys.argv[2]
    if not os.path.exists(project_dir) or  not os.path.isdir(project_dir):
        print(f"The directory '{project_dir}' does not exist.")
        sys.exit(1)

    directory = os.path.dirname(course_path)
    # 检查目录是否存在，如果不存在，则创建它
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # GET API KEY
    openai.api_key = get_api_key()
    message = run_conversation(project_dir,model = "gpt-3.5-turbo-16k-0613", messages = [], conv_id = None, temp = 1.0)
    print("message:",message)
    with open(course_path,"w",encoding='utf-8') as file:
        file.write(message)

