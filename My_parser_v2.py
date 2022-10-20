######################################################
# ------------------ Parameters -------------------- #
dataset_type = 0
'''
0 = Dobo 도보 aihub -> 현재 폴더 열람방식 문제있음, 폴더 한겹 추가해야됨
1 = Chair 휠체어 aihub
2 = COCO, 미리 class 줄여놔야됨
3 = Wesee 셀렉트스타
'''

image_process = True
imgsize = [640, 360]
if_compress = False
jpg_quality = 50  # value: 1~95  (default=75)

data_ratio = [8,1,1]  # train/val/test
src_dir = '../dataset/Dobo'
target_dir = '../dataset/Dobo_parsed'
# src_dir = 'C:/Users/dklee/Downloads/MVP/dataset/Wesee_sample'
# target_dir = 'C:/Users/dklee/Downloads/MVP/dataset/Wesee_parsed'

#######################################################

classes={}  # Key : class name, Value : int allocated to that class
cases={}  # Key : class name, Value : number of its bbox
train_val_test=[0,0,0]  # Number of each type of data [train, val, test]
img_box = [0, 0, 0]   # Number of total [images, bboxes, tiny_boxes]

from PIL import Image
import os
import shutil
import random
import json

def path_generator():
    dest=0
    total_score = sum(data_ratio)
    tmp = random.random()
    if(tmp < data_ratio[0]/total_score):
        path = target_dir+'/train'
        dest=0
    elif(tmp < (data_ratio[0]+data_ratio[1])/total_score):
        path = target_dir+'/val'
        dest=1
    else:
        path = target_dir+'/test'
        dest=2
    return [path, dest]  # dir_path & ENUM

def yaml_writer():
    class_ = list(classes.keys())
    with open(target_dir+"/data.yaml", 'w') as f:
        f.write("path: "+target_dir+"\ntrain: train/images\nval: val/images\n")
        f.write("test: test/images\n\nnc: %d\nnames: ["%nc)
        len_ = len(class_)
        for i in range(len_):
            f.write("'%s'"%class_[i])
            if(i<len_-1):
                f.write(', ')
            else:
                f.write(']')
        f.write("\n# Dataset statistics: \n#\tTotal imgs: %d\n#\t\tTrain-Val-Test: [%d,%d,%d]\n"%(img_box[0],
            train_val_test[0],train_val_test[1],train_val_test[2]))
        f.write("#\tTotal Bbox: %d\n#\tToo small boxes ignored: %d\n"%(img_box[1], img_box[2]))
        for i in range(len_):
            f.write("#\t\t%s: %d\n"%(class_[i],cases[class_[i]]))
        f.close()

def image_maker(img_dir, image_name, store_dir, store_name):
    img = Image.open(img_dir+'/'+image_name)
    img_resize = img.resize((imgsize[0],imgsize[1]))

    if(if_compress):
        img_resize.save(store_dir+'/'+store_name, quality=jpg_quality)
    else:
        img_resize.save(store_dir+'/'+store_name)

# def image_maker(img_dir, image_name, store_dir):
#     image_maker(img_dir, image_name, store_dir, image_name)
    
def parsing(class_name, xtl, ytl, xbr, ybr, width, height):
    if xtl<=0:
        xtl=1
    if xbr>=width:
        xbr=width-1
    if ytl<=0:
        ytl=1
    if ybr>=height:
        ybr = height-1
    if ((xbr-xtl)*(ybr-ytl)) < 2000:
        img_box[2] += 1
        return False
    else:
        return str(classes[class_name])+' '+str((xbr+xtl)/2/width)+' '+str((ybr+ytl)/2/height)+' '+str(abs(xbr-xtl)/width)+' '+str(abs(ybr-ytl)/height)+'\n'

def parser_0():
    global nc
    nc=0
    fn=0
    upper_list = os.listdir(src_dir)
    for upper_folder in upper_list:
        lower_list = os.listdir(src_dir+'/'+upper_folder)
        fn+=1
        print("Processing %s ...  (%d/%d)"%(upper_folder, fn, len(upper_list)))
    
        for lower_folder in lower_list:
            folder = upper_folder+'/'+lower_folder
            file_list = os.listdir(src_dir+'/'+folder)
            for file in file_list:
                if file.endswith(".xml"):
                    xml = file
                    break
            images = [file for file in file_list if file.endswith(".jpg")]

            # xml parsing
            with open(src_dir+'/'+folder+'/'+xml,'rt',encoding='UTF8') as f:
                lines = f.readlines()
                
                for i in range(len(lines)):
                    line = lines[i]
                    if "name" not in line or "username" in line or i<10:
                        continue
                    # Classes
                    if "id" not in line:
                        class_name = line[line.find('<name>')+6 : line.find("</name>")]
                        if(class_name not in list(classes.keys())):
                            classes[class_name] = nc
                            cases[class_name]=0
                            nc+=1
                    # Annotation
                    else:                            
                        image_name = line[line.find('name=')+6 : line.find('.jpg')]
                        if(not os.path.exists(src_dir+'/'+folder+'/'+image_name+'.jpg')):
                            print(image_name+'.jpg  [Missing]')
                            continue
                        img_box[0]+=1
                        path = path_generator()
                        train_val_test[path[1]] += 1
                        width = float(line[line.find('width')+7 : line.find('height')-2])
                        height = float(line[line.find('height')+8 : line.find('>')-1])
                        with open(path[0]+'/labels/'+image_name+'.txt', 'w') as t:
                            while (1):
                                i=i+1
                                if("</image>" in lines[i]):
                                    break
                                src = lines[i]
                                img_box[1]+=1
                            
                                # print(src)
                                class_name = src[src.find('label')+7 : src.find('occ')-2]
                                cases[class_name]+=1
                                xtl = float(src[src.find('xtl')+5 : src.find('ytl')-2])
                                ytl = float(src[src.find('ytl')+5 : src.find('xbr')-2])
                                xbr = float(src[src.find('xbr')+5 : src.find('ybr')-2])
                                ybr = float(src[src.find('ybr')+5 : src.find('z_order')-2])
                                i=i+1
                                parse = parsing(class_name, xtl, ytl, xbr, ybr, width, height)
                                if not parse:
                                    cases[class_name] -= 1
                                    img_box[1] -= 1
                                    continue
                                else:
                                    t.write(parse)
                                
                            t.close()
                        if(image_process):
                            image_maker(src_dir+'/'+folder, image_name+'.jpg', path[0]+'/images', image_name+'.jpg')
    return

# 4장 중 한장씩만 입력됨
def parser_1():
    global nc
    nc=0
    for type in ['/train','/val']:
    # for type in ['/val']:
        fn=0
        label_folders = os.listdir(src_dir+type+'/labels')
        if len(label_folders)==0:
            continue
        
        for label_folder in label_folders:
            fn+=1
            print("%s folder (%d/%d)..."%(type, fn, len(label_folders)))
            if(os.path.exists(src_dir+type+'/labels/'+label_folder+'/Out/Day')):
                period = "Day"
            elif(os.path.exists(src_dir+type+'/labels/'+label_folder+'/Out/Night')):
                period = "Night"
            else:
                print("Inappropriate folder structure : %s"%(type+'/labels/'+label_folder))
                return
            location = os.listdir(src_dir+type+'/labels/'+label_folder+'/Out/'+period)[0]
            label_path = src_dir+type+'/labels/'+label_folder+'/Out/'+period+'/'+location+'/Left'
            image_path = src_dir+type+'/images/'+label_folder[0]+'S'+label_folder[2:]+'/Out/'+period+'/'+location+'/Left'
            label_list = os.listdir(label_path)
            # print(len(label_list))

            if type=='/train':
                train_val_test[0] += int(len(label_list)/4)
            else:
                train_val_test[1] += int(len(label_list)/4)
            img_box[0] += len(label_list)

            mod=0
            for label in label_list:
                mod = (mod+1)%4
                if mod!=3:
                    continue
                with open(label_path+'/'+label, 'r') as l:
                    j = json.load(l)
                    file_name = location+'_'+period+label[label.find("Left_")+5:label.find(".json")]
                    with open(target_dir+type+'/labels/'+file_name+'.txt','w') as t:
                        img_box[1] += len(j["shapes"])
                        for feature in j["shapes"]:
                            class_name = feature["label"]
                            if class_name not in classes.keys():
                                classes[class_name] = nc
                                cases[class_name] = 1
                                nc+=1
                            else:
                                cases[class_name] += 1
                            points = feature["points"]

                            # Image size is 1920*1080
                            height = 1080
                            width = 1920
                            x=[]
                            y=[]
                            for point in points:
                                x.append(point[0])
                                y.append(point[1])
                            xtl = min(x)
                            xbr = max(x)
                            ytl = min(y)
                            ybr = max(y)

                            parse = parsing(class_name, xtl, ytl, xbr, ybr, width, height)
                            if not parse:
                                cases[class_name] -= 1
                                img_box[1] -= 1
                                continue
                            else:
                                t.write(parse)
                
                if image_process:
                    image_name = label[:label.find('.json')]+'.jpg'
                    if os.path.exists(image_path+'/'+image_name):
                        image_maker(image_path, image_name, target_dir+type+'/images', file_name+'.jpg')
                    else:
                        print("Cannot find image %s"%(image_path+'/'+image_name))

    return

def parser_2():
    return

def parser_3():
    global nc
    nc=0
    folder_list = os.listdir(src_dir)
    fn=0
    
    for folder in folder_list:
        fn+=1
        print("Processing %s ...  (%d/%d)"%(folder,fn,len(folder_list)))
        file_list = os.listdir(src_dir+'/'+folder)
        
        for file in file_list:
            if file.endswith(".json"):
                folder_dir = src_dir+'/'+folder+'/'
                with open(folder_dir+file, 'r') as f:
                    j = json.load(f)                    
                    image_file = j["imagePath"]
                    if(not os.path.exists(folder_dir+image_file)):
                        print(image_file+'  [Missing]: json=%s%s'%(folder_dir,file))
                        break
                    
                    img_box[0]+=1
                    img_box[1]+=len(j["shapes"])
                    path = path_generator()
                    train_val_test[path[1]] += 1

                    #사진이 jpg도 있고 png도 있음
                    with open(path[0]+'/labels/'+image_file[:image_file.find(".")]+'.txt', 'w') as t:
                        for i in range(len(j["shapes"])):
                            class_name = j["shapes"][i]["label"]

                            # 일부 클래스명이 숫자 1로 되어있는 오류가 있음    
                            if(class_name=='1'):
                                continue
                            if(class_name not in list(classes.keys())):
                                classes[class_name] = nc
                                cases[class_name]=0
                                nc+=1
                            cases[class_name] += 1

                            width = float(j["imageWidth"])
                            height = float(j["imageHeight"])
                            point = j["shapes"][i]["points"]
                            if float(point[0][0])>float(point[1][0]):
                                xtl = float(point[1][0])
                                xbr = float(point[0][0])
                            else:
                                xtl = float(point[0][0])
                                xbr = float(point[1][0])

                            if float(point[0][1])>float(point[1][1]):
                                ytl = float(point[1][1])
                                ybr = float(point[0][1])
                            else:
                                ytl = float(point[0][1])
                                ybr = float(point[1][1])
                            
                            parse = parsing(class_name, xtl, ytl, xbr, ybr, width, height)
                            if not parse:
                                cases[class_name] -= 1
                                img_box[1] -= 1
                                continue
                            else:
                                t.write(parse)
                        t.close 
                    if(image_process):
                        image_maker(folder_dir, image_file, path[0]+'/images', image_file)
    return


def main():
    if src_dir==target_dir:
        print("ERROR : 소스 폴더와 타켓 폴더가 같습니다")
        return
    if os.path.exists(target_dir):
        if(len(os.listdir(target_dir))>0):
            ans = input("타겟 폴더 내부에 파일이 있습니다. 전부 지우고 계속 하시겠습니까? [y,n] : ")
            if(ans!='y'):
                return
            shutil.rmtree(target_dir)
            os.mkdir(target_dir)
    else:
        os.mkdir(target_dir)

    dir_list = ['train','train/images','train/labels','val','val/images','val/labels',
        'test','test/images','test/labels']
    for tmp in dir_list:
        os.mkdir(target_dir+'/'+tmp)

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
        return
    # Write data.yaml
    yaml_writer()
    if train_val_test[2]==0:
        shutil.rmtree(target_dir+'/test')
    print("Processed numbers of dataset = Train: %d, Val: %d, Test: %d"%(train_val_test[0],
        train_val_test[1], train_val_test[2]))

if __name__ == "__main__":
    main()
