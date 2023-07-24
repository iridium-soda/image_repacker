import sys
import os
import hashlib
import json
usage="""
Usage: python packer.py <path_to_unpacked_image>
"""
import hashlib

import tarfile

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:") as tar:
        tar.add(source_dir, arcname="")



def calculate_sha256(filename)->str:
    # 创建一个SHA256哈希对象
    sha256 = hashlib.sha256()

    # 以二进制模式打开文件并逐块更新哈希对象
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(4096), b''):
            sha256.update(block)

    # 返回SHA256哈希值的十六进制字符串表示
    return sha256.hexdigest()

def get_subdirectories(parent_dir):
    # 获取parent_dir目录下的所有文件和目录
    files_and_dirs = os.listdir(parent_dir)
    
    # 遍历文件和目录，筛选出目录
    subdirectories = []
    for file_or_dir in files_and_dirs:
        file_or_dir_path = os.path.join(parent_dir, file_or_dir)
        if os.path.isdir(file_or_dir_path):
            subdirectories.append(file_or_dir_path)
    
    # 返回子目录列表
    return subdirectories



def modify_json_field(json_file_path, field_path, new_value):
    # 打开JSON文件并加载数据
    with open(json_file_path, "r") as f:
        data = json.load(f)
        
    # 获取要修改的字段
    field_list = field_path.split(".")
    field = data
    for i in range(len(field_list)-1):
        field = field.get(field_list[i], {})
    field[field_list[-1]] = new_value
    
    # 保存修改后的数据
    with open(json_file_path, "w") as f:
        json.dump(data, f)


def main(main_path:str):
    # get file structure
    # 没有做输入校验！务必保证输入的路径是真的从docker save解包的镜像!!!
    dirs=get_subdirectories(main_path)
    layers_path=[d+"/layer.tar" for d in dirs]

    # Generate digests of layer.tar
    digests={}
    for index,p in enumerate(layers_path):
        digests[dirs[index]]="sha256:"+calculate_sha256(p)
        print(f"{p} sha256:{calculate_sha256(p)}")
    
    # write config.json
    diff_ids=[digests[k] for k in digests]
    print("diff_ids:",diff_ids)
    #查找config.json
    for filename in os.listdir(main_path):
        # 检查文件名是否为十六进制字符串以及是否以'.json'结尾
        if filename.endswith('.json') and all(c in '0123456789abcdef' for c in filename[:-5]):
            filepath = os.path.join(main_path, filename)
            print("Config.json is ",filepath)
            with open(filepath) as f:
                data = json.load(f)
                data['rootfs']['diff_ids']=diff_ids
                print("Write diff_ids in ",filepath)
                break
    # calculate new config digest
    config_new=os.path.join(main_path,calculate_sha256(filepath).lower()+".json")
    
    os.rename(filepath, config_new)
    print("New path is ",config_new)
    
    # write manifest.json
    manifest_path=os.path.join(main_path,"manifest.json")
    print("manifest_path is ",manifest_path)
    with open(manifest_path) as f:
        data=json.load(f)
        data[0]['Config']=config_new
        print("manifest.json written")
    
    # maketar
    make_tarfile(calculate_sha256(filepath)+".tar", main_path) #Named as image's digest
    print("Done!")


if __name__=="__main__":
    if len(sys.argv)==2 and  os.path.isdir(sys.argv[1]):
        main(sys.argv[1])
    else:
        print(usage)