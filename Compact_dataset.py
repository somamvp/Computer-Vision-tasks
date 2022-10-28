# Reannotate에서 무시된 이미지를 삭제하고 기타 필요없는 파일들은 삭제해 필요한 파일만 남기는 작업 #
# 에서 원하는 라벨이 있는 데이터만 남기는 작업으로 변형함 #

global src_dir
src_dir = '../dataset/Wesee_np'
# wanted = ['13','14','15','17','18','19','21','22','23','24','26']  # 소수 오브젝트
wanted = ['1','2']  #신호등

##########################################################

import os, shutil
if not os.path.exists(src_dir):
    print("데이터셋 경로가 존재하지 않습니다")
    exit()

target_dir = src_dir+'_clear'
types = ['test','train','val']
    
if os.path.exists(target_dir):
    ans = input("기존 데이터셋을 지우고 계속합니다. [y,n] : ")
    if(ans!='y'):
        exit()    
    shutil.rmtree(target_dir)

os.mkdir(target_dir)
for type in types:
    os.mkdir(target_dir+'/'+type)
    os.mkdir(target_dir+'/'+type+'/labels')
    os.mkdir(target_dir+'/'+type+'/images')

for type in types:
    src_label_path = src_dir+'/'+type+'/labels/'
    src_image_path = src_dir+'/'+type+'/images/'
    target_label_path = target_dir+'/'+type+'/labels/'
    target_image_path = target_dir+'/'+type+'/images/'   

    labels = os.listdir(src_label_path)

    for label in labels:
        if 'custom' in label:
            continue
        save = False
        l = open(f'{src_label_path}{label}', 'r')
        lines = l.readlines()
        for line in lines:
            class_num = line.split()[0]
            if class_num in wanted:
                save = True
                break
        l.close()

        if not save:
            continue

        image = label[:-4]
        # print(image)
        if os.path.exists(src_image_path+image+'.jpg'):
            image = image+'.jpg'
        elif os.path.exists(src_image_path+image+'.png'):
            image = image+'.png'
        else:
            print('Image detect Failed')
            exit()
        shutil.copy2(src_label_path+label, target_label_path+label)
        shutil.copy2(src_image_path+image, target_image_path+image)

shutil.copy2(src_dir+'/data.yaml', target_dir+'/data.yaml')