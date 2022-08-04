######################################################################
# Only works for YOLO Format. Convert the format first! 
######################################################################

yaml_path = 'my_yolov5/data/'
yaml_name = 'wesee.yaml'
target_dir = '../dataset/Wesee_Re'
remain = ['person', 'bicycle', 'car','motorcycle', 'bus', 'train', 'truck', 'fire hydrant','bench']
# remain = ['Zebra_Cross']
ratio_blankimage = 0.3  # Sustain image without any bounding box randomly (0~1)

#######################################################################

import yaml, os, random, shutil
mapping={}
cases={}

def match_class():
    global dict
    dict = yaml.safe_load(open(yaml_path + yaml_name, encoding='UTF-8'))
    # print(dict)
    print(dict['names'])

    for name in remain:
        if name not in dict['names']:
            print("Not existing class chosen: %s"%name)
            exit()
    print("Target classes are : %s  PASSED"%remain)

    for name in remain:
        cases[name] = 0
    
def make_mapping():
    global mapping, mapping_key
    for cnt in range(0,len(remain)):
        mapping[dict['names'].index(remain[cnt])] = cnt   # Key matches to original label, Value matches to new label
    mapping_key = mapping.keys()
    print("Remaining labels are : %s\n"%mapping_key)

def reannotation():
    global main_path, image_num, bbox_num
    image_num=0
    bbox_num=0
    main_path = dict['path']
    for type in ['train','test','val']:
    # for type in ['val']:
        sub_path = main_path[main_path.find('../')+3:]+'/'+type
        if (not os.path.exists(sub_path)):
            print("No %s folder exists"%type)
            continue
        file_list = os.listdir(sub_path+'/labels')
        # print(len(file_list))
        for txt in file_list:
            with open(sub_path+'/labels/'+txt) as f:
                bboxes=[]
                lines = f.readlines()
                for line in lines:
                    t = line.split()
                    label = t[0]
                    if(len(t)!=5):
                        print("Wrong Yolo format detected at %s"%txt)
                        exit()
                    if(int(label) not in mapping_key):
                        # print("Ignore original label %s"%t[0])
                        continue
                    t[0] = str(mapping[int(label)])
                    bboxes.append(t)
                # print(bbox)

                if(len(bboxes)==0):
                    if(random.random()>=ratio_blankimage):
                        continue

                bbox_num+=len(bboxes)
                with open(target_dir+'/'+type+'/labels/'+txt,'w') as n:
                    for bbox in bboxes:
                        cases[remain[int(bbox[0])]]+=1
                        result = ' '.join(s for s in bbox)
                        n.write(result+'\n')
                image = txt[:txt.find(".txt")]+'.jpg'
                image_num+=1
                shutil.copy(sub_path+'/images/'+image, target_dir+'/'+type+'/images/'+image)


def write_yaml():
    with open(target_dir+'/'+yaml_name[:yaml_name.find(".yaml")]+'_re.yaml', 'w') as f:
        len_ = len(remain)
        f.write("path: "+main_path+"\ntrain: train/images\nval: val/images\n")
        f.write("test: test/images\n\nnc: %d\nnames: ["%len_)

        for i in range(len_):
            f.write("'%s'"%remain[i])
            if(i<len_-1):
                f.write(', ')
            else:
                f.write(']')
        f.write("\n# Dataset statistics: \n#\tTotal imgs: %d\n#\tTotal Bbox: %d\n"%(image_num,bbox_num))
        for i in range(len_):
            f.write("#\t\t%s: %d\n"%(remain[i],cases[remain[i]]))


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

    dir_list = ['train','train/images','train/labels','val','val/images','val/labels',
        'test','test/images','test/labels']
    for tmp in dir_list:
        os.mkdir(target_dir+'/'+tmp)
    match_class()
    make_mapping()
    reannotation()
    write_yaml()

if __name__ == "__main__":
    main()