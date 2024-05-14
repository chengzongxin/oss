import os
import openpyxl
import sys

from login_model import LoginModel
from signature_model import SignatureModel
from upload_oss import getUserLoginData, uploadAudioToOSS, uploadOss

import os
import datetime

current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

def collect_file_paths_exclude_hidden():
    # 获取当前工作目录
    current_dir = os.getcwd()
    # 指定要遍历的文件夹路径
    folder_path = os.path.join(current_dir, 'files')
    file_paths = []  # 创建一个空列表来存储文件路径
    
    # 确保files文件夹存在
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print("The 'files' directory does not exist.")
        return []
    
    # 使用os.walk遍历files文件夹
    for root, dirs, files in os.walk(folder_path):
        # 过滤掉以"."开头的隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            # 过滤掉以"."开头的隐藏文件
            if not file.startswith('.'):
                # 将非隐藏文件的完整路径添加到列表中
                file_paths.append(os.path.join(root, file))
    
    return file_paths

def write_txt(path: str, url: str):
    # 在当前目录下创建一个新文件
    output_filename = formatted_time + '.txt'
    with open(output_filename, 'a') as output_file:
        output_file.write(path + '\n')
        output_file.write(url + '\n')
    

if __name__ == '__main__':
    loginModel: LoginModel = getUserLoginData()
    # 调用函数收集文件路径
    file_paths = collect_file_paths_exclude_hidden()
    # 遍历列表并打印每个文件路径
    for path in file_paths:
        model = uploadOss(filePath=path, isTestEnv=False, loginModel=loginModel)
        if (isinstance(model, SignatureModel)):
            newUrl = 'https://pic.to8to.com/' + model.newPath
            write_txt(path=path, url=newUrl)
            print(path)
            print(newUrl)

    