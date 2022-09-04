######################################################
# ------------------ Parameters -------------------- #
image_process = True
imgsize = [640, 360]
if_compress = False
jpg_quality = 50  # value: 1~95  (default=75)
force_classing = True

src_dir = '../dataset/Barrier'
target_dir = src_dir+'_np'

# Ver4 변경사항 :
# - Test/val/test 간 이미지 도메인을 나눠놓음 (데이터셋마다 다르게 적용됨)
# - 바로 Final class로 라벨링 됨
#######################################################
dataset_type = 6
'''
0 = Dobo 도보 aihub
1 = Chair 휠체어 aihub
2 = Wesee 신호등 셀렉트스타
3 = Barrier
'''
#######################################################

classes={}  # Key : class name, Value : int allocated to that class
cases={}  # Key : class name, Value : number of its bbox
train_val_test=[0,0,0]  # Number of each type of data [train, val, test]
img_box=[0,0,0,0]   # Number of total [images, bboxes, tiny, large]
global nc
nc=0

from PIL import Image
import os
import shutil
import random
import json

def path_generator(indicator):
    global data_name
    dest=-1
    if data_name=='Wesee' or data_name=='Dobo':
        if('KSC' in indicator):
            path = target_dir+'/val'
            dest=1
        elif('MIN' in indicator):
            path = target_dir+'/test'
            dest=2
        else:
            path = target_dir+'/train'
            dest=0

    elif data_name=='Chair':
        if('가천대' in indicator):
            path = target_dir+'/val'
            dest=1
        elif('폴리텍' in indicator):
            path = target_dir+'/test'
            dest=2
        else:
            path = target_dir+'/train'
            dest=0
    elif data_name=='Barrier':
        if('DC0203' in indicator):
            path = target_dir+'/test'
            dest=2
        elif('DC020' in indicator):
            path = target_dir+'/val'
            dest=1
        else:
            path = target_dir+'/train'
            dest=0
    else:
        print("path generate error")
        exit()
    return [path, dest]  # dir_path & ENUM

def yaml_writer():
    class_ = list(classes.keys())
    with open(target_dir+"/data.yaml", 'w') as f:
        f.write(f"train: ../{target_dir}/train/images\nval: ../{target_dir}/val/images\n")
        f.write(f"test: ../{target_dir}/test/images\n\nnc: {nc}\nnames: [")
        len_ = len(class_)
        for i in range(len_):
            f.write("'%s'"%class_[i])
            if(i<len_-1):
                f.write(', ')
            else:
                f.write(']')
        f.write("\n# Dataset statistics: \nTotal imgs: %d\nTrain-Val-Test: [%d,%d,%d]\n\n"%(img_box[0],
            train_val_test[0],train_val_test[1],train_val_test[2]))
        # f.write("Too small boxes ignored: %d\nToo large boxes ignored: %d\n\n"%(img_box[2],img_box[3]))
        f.write("Total Bbox: %d\nBbox distribution:\n"%(img_box[1]))
        for i in range(len_):
            if(cases[class_[i]]!=0):
                f.write("    %s: %d\n"%(class_[i],cases[class_[i]]))
            else:
                f.write("    %s: Invalid\n"%(class_[i]))
        f.close()

def image_maker(img_dir, image_name, store_dir, store_name):
    img = Image.open(img_dir+'/'+image_name)
    img_resize = img.resize((imgsize[0],imgsize[1]))

    if(if_compress):
        img_resize.save(store_dir+'/'+store_name, quality=jpg_quality)
    else:
        img_resize.save(store_dir+'/'+store_name)
    
def parsing(class_name, xtl, ytl, xbr, ybr, width, height):
    if xtl<=0:
        xtl=1
    if xbr>=width:
        xbr=width-1
    if ytl<=0:
        ytl=1
    if ybr>=height:
        ybr = height-1
    # area = ((xbr-xtl)*(ybr-ytl))*imgsize[0]/width*imgsize[1]/height
    # if area < tiny_cutoff:
    #     img_box[2] += 1
    #     return False
    # elif area > large_cutoff:
    #     img_box[3] += 1
    #     return False
    return str(classes[class_name])+' '+str((xbr+xtl)/2/width)+' '+str((ybr+ytl)/2/height)+' '+str(abs(xbr-xtl)/width)+' '+str(abs(ybr-ytl)/height)+'\n'

def parser_0():
    global nc
    fn=0
    upper_list = os.listdir(src_dir)
    for upper_folder in upper_list:
        lower_list = os.listdir(src_dir+'/'+upper_folder)
        fn+=1
        print("Processing %s ...  (%d/%d)"%(upper_folder,fn,len(upper_list)))
    
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
                        if(class_name not in list(classes.keys()) and not force_classing):
                            classes[class_name] = nc
                            cases[class_name]=0
                            nc+=1
                    # Annotation
                    else:
                        image_name = line[line.find('name=')+6 : line.find('.jpg')]
                        if(not os.path.exists(src_dir+'/'+folder+'/'+image_name+'.jpg')):
                            print(image_name+'.jpg  [Missing]')
                            continue
                        
                        path = path_generator(image_name)
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
                                t.write(parse)
                                
                        img_box[0]+=1
                        if(image_process):
                            image_maker(src_dir+'/'+folder, image_name+'.jpg', path[0]+'/images', image_name+'.jpg')
    return

def parser_1():
    mod=3  # 3장 중 한장씩만 입력됨
    global nc
    for type in ['/train','/val']:
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

            iter=0
            for label in label_list:
                iter = (iter+1)%mod
                if iter!=mod-1:
                    continue
                img_box[0] += 1
                with open(label_path+'/'+label, 'r') as l:
                    j = json.load(l)
                    file_name = location+'_'+period+label[label.find("Left_")+5:label.find(".json")]
                    path = path_generator(location)
                    train_val_test[path[1]] += 1

                    with open(path[0]+'/labels/'+file_name+'.txt','w') as t:
                        img_box[1] += len(j["shapes"])
                        for feature in j["shapes"]:
                            class_name = feature["label"]
                            if class_name not in list(classes.keys()) and not force_classing:
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
                        image_maker(image_path, image_name,  path[0]+'/images', file_name+'.jpg')
                    else:
                        print("Cannot find image %s"%(image_path+'/'+image_name))

    return

def parser_2():
    global nc
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

                    #사진이 jpg도 있고 png도 있음
                    image_name = image_file[:image_file.find(".")]
                    if(not os.path.exists(folder_dir+image_file)):
                        print(image_file+'  [Missing]: json=%s%s'%(folder_dir,file))
                        break
                    
                    img_box[0]+=1
                    img_box[1]+=len(j["shapes"])
                    path = path_generator(image_name)
                    train_val_test[path[1]] += 1

                    with open(path[0]+'/labels/'+image_name+'.txt', 'w') as t:
                        for i in range(len(j["shapes"])):
                            class_name = j["shapes"][i]["label"]

                            # 일부 클래스명이 숫자 1로 되어있는 오류가 있음    
                            if(class_name=='1'): 
                                continue
                            if(class_name not in list(classes.keys()) and not force_classing):
                                classes[class_name] = nc
                                cases[class_name]=0
                                nc+=1
                            cases[class_name] += 1

                            width = float(j["imageWidth"])
                            height = float(j["imageHeight"])

                            # Min, Max가 섞여있는 경우 상정
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

def parser_3():
    global nc
    for type in ['/Training','/Validation']:
        fn=0
        label_folders = os.listdir(src_dir+type)
        label_folders = [folder for folder in label_folders if ("[라벨]" in folder)]
        if len(label_folders)==0:
            continue
        
        # 폴더 하나마다 실행
        for label_folder in label_folders:
            fn+=1
            print("Processing %s/ %s ...  (%d/%d)"%(type, label_folder,fn,len(label_folders)))

            label_folder = '/'+label_folder+'/'
            image_folder = '/[원천]'+label_folder[5:]
            labels = os.listdir(src_dir+type+label_folder)

            # 하나의 라벨마다 실행
            for label in labels:
                l=open(src_dir+type+label_folder+label, 'r', encoding="UTF-8")
                j = json.load(l)

                path = path_generator(label)
                train_val_test[path[1]] += 1

                file_name = label.replace(' ','_')[:-5]
                with open(path[0]+'/labels/'+file_name+'.txt','w') as t:
                    image_name = j["images"]["file_name"]
                    image_file = (src_dir+type+image_folder+image_name)

                    # 이미지가 존재하지 않는 경우
                    if not os.path.exists(image_file):
                        print(f"Image file {image_name} does not exist!!")
                        continue

                    # 이미지 사이즈가 1080p가 아닌 경우
                    if j["images"]["height"]!=1080 or j["images"]["width"]!=1920:
                        print(f"Images size not match : {image_name}")
                        continue
                    
                    # 이미지 카운트
                    img_box[0]+=1
                    
                    # 하나의 바운딩박스마다 실행
                    for bbox in j["annotations"]:
                        class_name = bbox["category_id"]
                        
                        # 기존에 없는 클래스명인 경우
                        if class_name not in list(classes.keys()):
                            classes[class_name] = nc
                            nc+=1
                            cases[class_name]=0
                        
                        points = bbox["segmentation"]

                        # 바운딩 박스를 나타내기 위한 점 갯수가 부족
                        if(len(points) <= 2):
                            # print(f"Contains less than three points for segmentation : {image_name}, {class_name}")
                            continue

                        x=[]
                        y=[]
                        for point in points:
                            x.append(point[0])
                            y.append(point[1])
                        xtl = min(x)
                        xbr = max(x)
                        ytl = min(y)
                        ybr = max(y)

                        parse = parsing(class_name, xtl, ytl, xbr, ybr, 1920, 1080)
                        if not parse:
                            continue
                        else:
                            # 바운딩박스 카운트 및 어노테이션 작성
                            cases[class_name] += 1
                            img_box[1] += 1
                            t.write(parse)
            if(image_process):
                    image_maker(image_folder, image_name, path[0]+'/images', image_name.replace(' ','_'))

    # print(classes.keys())
    # print(nc)
    return

def class_init(data_name):
    global nc
    with open('class.json','r',encoding="UTF-8") as class_json:
        forced_class = json.load(class_json)

    for c in forced_class[data_name]["Original"]:
        classes[c] = nc
        cases[c]=0
        nc+=1


def main():
    global data_name

    if src_dir==target_dir or not os.path.exists(src_dir):
        print("ERROR : 소스 폴더 및 타켓 폴더 지정에러")
        return
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    if image_process:
        if len(os.listdir(target_dir)) > 0:
            ans = input("타겟 폴더 내부 이미지가 전부 지워집니다. 계속 하시겠습니까? [y,n] : ")
            if(ans!='y'):
                return
        shutil.rmtree(target_dir)
        for dir in ['','/train','/val','/test','/train/labels','/val/labels','/test/labels'
                ,'/train/images','/val/images','/test/images']:
            os.mkdir(target_dir+dir)
    else:
        delete_list = ['/train/labels','/val/labels','/test/labels','/train/labels_old','/val/labels_old','/test/labels_old']
        for dir in delete_list:
            if os.path.exists(target_dir+dir):
                shutil.rmtree(target_dir+dir)
        for dir in ['','/train','/val','/test','/train/labels','/val/labels','/test/labels'
                ,'/train/images','/val/images','/test/images']:
            if not os.path.exists(target_dir+dir):
                os.mkdir(target_dir+dir)
    if os.path.exists(target_dir+'/data.yaml'):
        os.remove(target_dir+'/data.yaml')
    if os.path.exists(target_dir+'/data_old.yaml'):
        os.remove(target_dir+'/data_old.yaml')

    if("wesee" in src_dir.lower()):
        data_name = 'Wesee'
    elif("dobo" in src_dir.lower()):
        data_name = 'Dobo'
    elif("chair" in src_dir.lower()):
        data_name = 'Chair'
    elif("barrier" in src_dir.lower()):
        data_name = 'Barrier'
    else:
        print("Dataset type auto detect failed. Switching to manual")
        if dataset_type==0:
            data_name = "Dobo"
        elif dataset_type==1:
            data_name = "Chair"
        elif dataset_type==2:
            data_name = "Wesee"
        elif dataset_type==3:
            data_name = "Barrier"
        else:
            print("Wrong dataset type number")
            return
    print(f"Selected dataset_type: {data_name}")

    if force_classing:
        class_init(data_name)

    if(data_name=='Dobo'):
        parser_0()
    elif(data_name=='Chair'):
        parser_1()
    elif(data_name=='Wesee'):
        parser_2()
    elif(data_name=='Barrier'):
        parser_3()

    # Write data.yaml
    yaml_writer()
    print("Processed numbers of dataset = Train: %d, Val: %d, Test: %d"%(train_val_test[0],
        train_val_test[1], train_val_test[2]))

if __name__ == "__main__":
    main()
