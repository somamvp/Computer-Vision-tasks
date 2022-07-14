######################################################
# ------------------ Parameters -------------------- #
dataset_type = 0
'''
0 = aihub 도보영상
1 = aihub 표지판 신호등
2 = 셀렉트스타
3 = ETRI 신호등
'''
# blank_image_remain_ratio = 0.6  # image not contains any class
if_resize = True
imgsize = [640, 480]
ratio = [8,1,1]  # train/val/test
src_dir = 'C:/Users/dklee/Downloads/Aihub_pedestrian_sample/bbox'
target_dir = 'C:/Users/dklee/Downloads/Aihub_pedestrian_sample/parsed'

########################################################

from PIL import Image
import pickle
import os
import shutil
import random

def path_generator():
    total_score = sum(ratio)
    tmp = random.random()
    if(tmp < ratio[0]/total_score):
        path = target_dir+'/train'
    elif(tmp < (ratio[0]+ratio[1])/total_score):
        path = target_dir+'/val'
    else:
        path = target_dir+'/test'

    return path

def yaml_writer(nc, classes):
    with open(target_dir+"/data.yaml", 'w') as f:
        f.write("path: "+target_dir+"\ntrain: train/images\nval: val/images\n")
        f.write("test: test/images\n\nnc: %d\nnames: "%nc)
        # pickle.dump(classes, f)
        f.close()

def parser_0():
    file_list = os.listdir(src_dir)
    for file in file_list:
        if file.endswith(".xml"):
            xml = file
            break
    for file in file_list:
        if file.endswith(".txt"):
            dumy = file
            break
    images = [file for file in file_list if file.endswith(".jpg")]

    # print(xml)
    # print(len(images))
    # print(type(dumy))    

    # xml parsing
    nc=0
    classes=[]
    with open(src_dir+'/'+xml,'r') as f:
        lines = f.readlines()
        
        for i in range(len(lines)):
            line = lines[i]
            if "name" not in line or "username" in line or i<10:
                continue

            # Classes
            if "id" not in line:
                nc+=1
                classes.append(line[line.find('<name>')+6 : line.find("</name>")])
                
            # Annotation
            else:
                path = path_generator()
                

                # Resize image
    
    # Write data.yaml
    yaml_writer(nc, classes)
    return

def parser_1():
    return

def parser_2():
    return

def parser_3():
    return


def main():
    if os.path.exists(target_dir):
        if(len(os.listdir(target_dir))>0):
            ans = input("타겟 폴더 내부에 파일이 있습니다. 전부 지우고 계속 하시겠습니까? [y,n] : ")
            if(ans!='y'):
                return
            shutil.rmtree(target_dir)
            os.mkdir(target_dir)
    else:
        os.mkdir(target_dir)

    os.mkdir('./'+target_dir+'/train')
    os.mkdir('./'+target_dir+'/val')
    os.mkdir('./'+target_dir+'/test')

    if(dataset_type==0):
        parser_0()
    elif(dataset_type==1):
        parser_1()
    elif(dataset_type==2):
        parser_2()
    elif(dataset_type==3):
        parser_3()
    else:
        print("Wrong dataset_type value")

if __name__ == "__main__":
    main()
