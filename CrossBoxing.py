#######################################
src = 'Wesee_sample_parsed'
src_pt = 'Wesee_RA3.pt'
target = 'Dobo_sample_parsed'
conf = 0.5
iou = 0.3

img_size= [640, 360]
#######################################
import yaml, os, shutil, json
from PIL import Image
import torch
class_book={}  # 통합클래스이름 : 통합클래스라벨
final=[]  # 통합클래스이름
ignore=[]  # src 중 무시할 클래스이름

src_dir = '../dataset/'+src
# model = yolov5.load()
target_dir = '../dataset/'+target
cb = src_pt[:src_pt.find("_")]
cb_dir = '../dataset/'+cb+'_CBon_'+target

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"using devide {DEVICE}")


model = AutoShape( 
    DetectMultiBackend(weights='my_yolov5/'+src_pt, device=torch.device(DEVICE))
)

def IoU(box1, box2):
    # box = (x1, y1, x2, y2)
    box1_area = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
    box2_area = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)

    # obtain x1, y1, x2, y2 of the intersection
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    # compute the width and height of the intersection
    w = max(0, x2 - x1 + 1)
    h = max(0, y2 - y1 + 1)

    inter = w * h
    iou = inter / (box1_area + box2_area - inter)
    return iou

def cross_boxing():
    for type in ['/train','/val','/test']:
        image_folder = cb_dir+type
        if os.path.exists(image_folder):
            image_list = os.listdir(image_folder)
            for image_file in image_list:
                image = Image.open(image_folder+'/'+image_file)
                result = model(image, size=640).pandas().xyxy[0].to_dict(orient="records")
                print(result)
                # Format is as follows:
                # [{"xmin":57.0689697266,"ymin":391.7705993652,"xmax":241.3835449219,"ymax":905.7978515625,"confidence":0.8689641356,"class":0.0,"name":"person"},
                # {"xmin":667.6612548828,"ymin":399.3035888672,"xmax":810.0,"ymax":881.3966674805,"confidence":0.8518877029,"class":0.0,"name":"person"},
                # {"xmin":222.8783874512,"ymin":414.774230957,"xmax":343.804473877,"ymax":857.8250732422,"confidence":0.8383761048,"class":0.0,"name":"person"},
                # {"xmin":4.2053861618,"ymin":234.4476776123,"xmax":803.7391357422,"ymax":750.0233764648,"confidence":0.6580058336,"class":5.0,"name":"bus"},
                # {"xmin":0.0,"ymin":550.5960083008,"xmax":76.6811904907,"ymax":878.669921875,"confidence":0.4505961835,"class":0.0,"name":"person"}]

                provided = []
                original_txt = open(image_folder+image_file[:image_file.find("jpg")]+"txt", 'r')
                originals = original_txt.readlines()
                for line in originals:
                    provided.append(line.split())
                # Format is as follows:
                # [[23, 0.19799479166666664, 0.4273148148148148, 0.20296875, 0.11388888888888889],
                # [23, 0.038734375, 0.4248796296296296, 0.07642708333333334, 0.11018518518518519],
                # [23, 0.39765364583333335, 0.43243518518518514, 0.07333854166666663, 0.07290740740740737]]
                
                for bbox in result:
                    if(bbox['name'] in ignore):
                       continue 
                    if(bbox['confidence'] > conf):
                        is_addbox = True
                        for gt in provided:
                            predict_box = [bbox["xmin"], bbox["ymin"], bbox["xmax"], bbox["ymax"]]
                            xc = gt[1]*img_size[0]
                            yc = gt[2]*img_size[1]
                            w = gt[3]*img_size[0]
                            h = gt[4]*img_size[1]
                            gt_box = [xc-w/2, yc-h/2, xc+w/2, yc+h/2]
                            if(IoU(predict_box, gt_box) > iou):
                                print(f"Bbox overlapped new: {bbox['name']} on GT: {final[gt[0]]}")
                                if(bbox['class']==gt[0]):
                                    if(bbox['name']!="tree"):
                                        is_addbox = False
                                        break
                        if is_addbox:
                            if(bbox['name']=="tree"):  # Special case

                            else:  # Normal case



def data_init():
    if("wesee" in src.lower()):
        data_name = 'Wesee'
    elif("dobo" in src.lower()):
        data_name = 'Dobo'
    elif("chair" in src.lower()):
        data_name = 'Chair'
    elif("coco" in src.lower()):
        data_name = 'Coco'
    else:
        print("Dataset type auto detect failed. Exiting...")
        exit()
    # src_yaml = yaml.safe_load(open(src_dir +'/data_old.yaml', encoding='UTF-8'))
    class_json = json.laod(open('class.json'))
    final = class_json['Final']['Original']
    class_book = class_json['Final']['Label']
    ignore = class_json[data_name]['Ignore']

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
    data_init()
    cross_boxing()

if __name__ == "__main__":
    main()