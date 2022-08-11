#######################################
src = 'Wesee_sample_parsed'
src_pt = 'Wesee_RA3.pt'
target = 'Dobo_sample_parsed'


#######################################
import yaml, os, shutil
import torch as torch
from PIL import Image
from models.common import DetectMultiBackend, AutoShape

src_dir = '../dataset/'+src
# model = yolov5.load()
target_dir = '../dataset/'+target
cb = src_pt[:src_pt.find("_")]
cb_dir = '../dataset/'+cb+'_CBon_'+target

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"using devide {DEVICE}")

model = AutoShape(
    DetectMultiBackend(weights=src_pt, device=DEVICE)
    (weights='my_yolov5/'+src_pt, device=torch.device(DEVICE))
)

def cross_boxing():
    for type in ['/train','/val','/test']:
        image_folder = cb_dir+type
        if os.path.exists(image_folder):
            image_list = os.listdir(image_folder)
            for image_file in image_list:
                image = Image.open(image_folder+'/'+image_file)
                result_dict = model(image, size=640).pandas().xyxy[0].to_dict(orient="records")
                print(result_dict)


def main():
    if not os.path.exists(cb_dir):
        for dir in ['','/train','/val','/test']:
            os.mkdir(cb_dir+dir)
        for dir in ['/train/images','/val/images','/test/images']:
            if os.path.exists(target_dir+dir):
                shutil.copytree(target_dir+dir, cb_dir+dir)
    
    for dir in ['/train/labels','/val/labels','/test/labels']:
        if os.path.exists(cb_dir+dir):
            shutil.rmtree(cb_dir+dir)
        if os.path.exists(target_dir+dir):
            os.mkdir(cb_dir+dir)
    
    cross_boxing()

if __name__ == "__main__":
    main()