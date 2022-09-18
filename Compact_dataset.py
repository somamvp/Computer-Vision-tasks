# Reannotate에서 무시된 이미지를 삭제하고 기타 필요없는 파일들은 삭제해 필요한 파일만 남기는 작업 #

global src_dir
src_dir = '../dataset/Barrier_np_old'

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