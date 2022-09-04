######################################################################
# Only works for YOLO Format, Labeled by 'class.json'
######################################################################
global src_dir
src_dir = '../dataset/Dobo_np'
# 초기 labels가 'labels_old' 폴더로 이동됨
# 'labels_old'가 이미 있는 경우 'labels'폴더는 바로 삭제됨

ratio_blankimage = 1  # Sustain image without any bounding box randomly (0~1)
size_threshold = True
tiny_cutoff = 150
large_cutoff = 300000
img_size = [640, 360]

#######################################################################
# 데이터셋이 이제 자동으로 감지되므로 필요없음
dataset_type = 5
'''
0 = Dobo 도보 aihub
1 = Chair 휠체어 aihub
2 = Wesee 신호등 셀렉트스타
3 = COCO [Not Working now]
'''
#######################################################################

import yaml, os, random, shutil, json
target_class={}  # 통합클래스이름:통합라벨
to_unified_class={}  # 기존클래스이름:통합클래스이름
src_class={}  # 기존클래스이름:기존라벨
mapping={}  # 기존라벨:통합라벨
cases={}  # 통합클래스이름:Bbox갯수
final=[]
train_val_test=[0,0,0]  # Number of each type of data [train, val, test]
img_box=[0,0,0,0,0]   # Number of total [images, bboxes, tiny, large, blank_ripped]

    
def make_mapping():
    cnt=0
    for probe in list(src_class.keys()):
        convert = to_unified_class[probe]
        if convert in target_class.keys():
            mapping[src_class[probe]] = target_class[convert]
            cases[convert] = 0
        else:
            if(convert=="NA"):
                continue
            print(f"== WARNING == Ignored class: {probe}")

def reannotation():
    global src_dir, final
    
    for type in ['train','test','val']:
        old_path = src_dir+'/'+type+'/labels_old/'
        new_path = src_dir+'/'+type+'/labels/'
        if not os.path.exists(old_path):
            continue
        file_list = os.listdir(old_path)
        # print(len(file_list))
        img_box[0]+=len(file_list)
        
        for txt in file_list:
            with open(old_path+txt, 'r') as old:
                new = open(new_path+txt, 'w')
                bboxes=[]
                lines = old.readlines()
                for line in lines:
                    bbox = line.split()
                    label = bbox[0]

                    if(len(bbox)!=5):
                        print("Wrong Yolo format detected at %s"%txt)
                        exit()
                    if(int(label) not in mapping.keys()):  # 라벨 탈락
                        continue
                    if(size_threshold):
                        area = float(bbox[3])*float(bbox[4])*img_size[0]*img_size[1]
                        if(area<tiny_cutoff):  # 사이즈 limit
                            img_box[2]+=1
                            continue
                        elif(area>large_cutoff):  # 사이즈 limit
                            img_box[3]+=1
                            continue

                    bbox[0] = str(mapping[int(label)])
                    if bbox not in bboxes:
                        bboxes.append(bbox)
                # print(len(bboxes))

                if(len(bboxes)==0):  # 라벨이 하나도 없는 경우
                    if(random.random()>=ratio_blankimage):
                        img_box[4]+=1
                        continue

                img_box[1]+=len(bboxes)
                for bbox in bboxes:
                    # print(final[int(bbox[0])])
                    cases[final[int(bbox[0])]]+=1
                    result = ' '.join(s for s in bbox)
                    new.write(result+'\n')
                # image = txt[:txt.find(".txt")]+'.jpg'
                # image_num+=1
                new.close()
            if(type=="train"):
                train_val_test[0]+=1
            elif(type=="val"):
                train_val_test[1]+=1
            if(type=="test"):
                train_val_test[2]+=1

def yaml_writer_ReAnnotation():
    global final
    
    with open(src_dir+"/data.yaml", 'w') as f:
        # f.write("path: "+src_dir+"\ntrain: train/images\nval: val/images\n")
        # f.write("test: test/images\n\nnc: %d\nnames: ["%len(final))
        f.write(f"train: ../{src_dir}/train/images\nval: ../{src_dir}/val/images\n")
        f.write(f"test: ../{src_dir}/test/images\n\nnc: {len(final)}\nnames: [")
        len_ = len(final)
        for i in range(len_):
            f.write("'%s'"%final[i])
            if(i<len_-1):
                f.write(', ')
            else:
                f.write(']')
        f.write("\n# Dataset statistics: \nTotal imgs: %d\nTrain-Val-Test: [%d,%d,%d]\n"%(img_box[0],
            train_val_test[0],train_val_test[1],train_val_test[2]))
        f.write("Blank images ignored: %d\n\n"%img_box[4])
        f.write("Too small boxes ignored: %d\nToo large boxes ignored: %d\n\n"%(img_box[2],img_box[3]))
        f.write("Total Bbox: %d\nBbox distribution:\n"%(img_box[1]))
        for i in range(len_):
            f.write("    %s: %s\n"%(final[i],cases[final[i]]))
        f.close()

def data_init(data_name):
    global src_class, target_class, src_dir, to_unified_class
    global final
    
    if os.path.exists(src_dir+"/data_old.yaml"):
        if os.path.exists(src_dir+"/data.yaml"):
            ans = input("기존 어노테이션을 지우고 계속합니다. [y,n] : ")
            if(ans!='y'):
                exit()    
            os.remove(src_dir+"/data.yaml")
    else:
        os.rename(src_dir+"/data.yaml", src_dir+"/data_old.yaml")
    src_yaml = yaml.safe_load(open(src_dir +'/data_old.yaml', encoding='UTF-8'))
    cnt=0
    for name in src_yaml["names"]:
        src_class[name] = cnt
        cnt+=1
    # src_dir = src_yaml["path"]

    class_json = json.load(open('class.json','r', encoding='UTF-8'))
    target_class = class_json["Final"]["Label"]
    to_unified_class = class_json[data_name]["Mapping"]  
    final = class_json["Final"]["Original"]
    for name in final:
        cases[name] = 'Invalid'

def main():
    if("wesee" in src_dir.lower()):
        data_name = 'Wesee'
    elif("dobo" in src_dir.lower()):
        data_name = 'Dobo'
    elif("chair" in src_dir.lower()):
        data_name = 'Chair'
    elif("coco" in src_dir.lower()):
        data_name = 'Coco'
    else:
        print("Dataset type auto detect failed. Switching to manual")
        if dataset_type==0:
            data_name = "Dobo"
        elif dataset_type==1:
            data_name = "Chair"
        elif dataset_type==2:
            data_name = "Wesee"
        elif dataset_type==3:
            data_name = "Coco"
        else:
            print("Wrong dataset type number")
            return
    print(f"Selected dataset_type: {data_name}")
    data_init(data_name)
    assigned = False

    if not os.path.exists(src_dir):
        print("데이터셋 경로가 존재하지 않습니다")
        return
    traversal = ['/train','/val','/test']
    for folder in traversal:
        if(not os.path.exists(src_dir+folder)):
            continue
        folder_path = src_dir+folder+'/labels'
        if os.path.exists(folder_path):
            if not os.path.exists(src_dir+folder+'/labels_old'):
                os.rename(folder_path, src_dir+folder+'/labels_old')
            else:
                shutil.rmtree(folder_path)
        os.mkdir(folder_path)

    make_mapping()
    reannotation()
    yaml_writer_ReAnnotation()
    print("Processed numbers of dataset = Train: %d, Val: %d, Test: %d"%(train_val_test[0],
        train_val_test[1], train_val_test[2]))

if __name__ == "__main__":
    main()