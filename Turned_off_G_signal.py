from PIL import Image
import os, shutil, colorsys

src_dir = '../dataset/Wesee_sample_parsed'
target_dir = src_dir + '_truned-off'
deletion = [0,0]

def rgb_to_rxv(r,g,b):
    (h, s, v) = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    h *= 360
    s *= 100
    v *= 100
    return h,s,v

def delete():
    types = ['/test/','/train/','/val/']
    for type_ in types:
        label_list = os.listdir(src_dir+type_+'labels')

        for label_file in label_list:
            with open(src_dir+type_+'labels/'+label_file) as label:
                lines = label.readlines()
                for line in lines:
                    gt = line.split()
                    if gt[0]=='1' or gt[0]=='2':  #R_Signal or G_Signal
                        if os.path.exists(src_dir+type_+'images/'+label_file[:-4]+'.jpg'):
                            img = Image.open(src_dir+type_+'images/'+label_file[:-4]+'.jpg')
                        else:
                            img = Image.open(src_dir+type_+'images/'+label_file[:-4]+'.png')
                        width = img.size[0]
                        height = img.size[1]
                        for i in range(0,5):
                            gt[i] = float(gt[i])
                        x1 = int(width*(gt[1]-gt[3]/2))+2
                        x2 = int(width*(gt[1]+gt[3]/2))+3
                        y1 = int(height*(gt[2]-gt[4]/2))-2
                        y2 = int(height*(gt[2]+gt[4]/2))-3

                        

                        cropped = img.crop((x1+2,y1+3,x2-2,y2-3))
                        cropped.show()
                        ans=input()

                        for x in range(x1, x2):
                            for y in range(y1, y2):


def main():
    if not os.path.exists(target_dir):
        print("Copying images from src folder...")
        for dir in ['','/train','/val','/test']:
            os.mkdir(target_dir+dir)
        for dir in ['/train/images','/val/images','/test/images']:
            if os.path.exists(target_dir+dir):
                shutil.copytree(target_dir+dir, target_dir+dir)

    assigned=False
    for dir in ['/train/labels','/val/labels','/test/labels']:
        if os.path.exists(target_dir+dir):
            if not assigned:
                ans = input("기존 라벨을 지우고 계속합니다. [y,n] : ")
                print(ans)
                if(ans!='y'):
                    exit() 
                else:
                    assigned=True
            shutil.rmtree(target_dir+dir)
        if os.path.exists(target_dir+dir):
            os.mkdir(target_dir+dir)

    print("Turned-off traffic light will be deleted")
    delete()
    # yaml_writer()
    print(f"\n\nG_Signal deleted: {deletion[0]}, R_Signal deleted: {deletion[1]}")


if __name__ == "__main__":
    main()