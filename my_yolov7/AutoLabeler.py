#######################################
src_pt = 'chair2_ind1.pt'
target = 'voyagerBasic-dobo7_fin'
cb = src_pt[:src_pt.find(".")]
cb_dir = '../../dataset/'+target+'-'+cb

is_hard_negative_collect = True
is_auto_reject = True       # high_iou를 전부 reject함
AR_limit = 8

iou = 0.3 #보다 높고 클래스가 같으면 무시
iou_warning = 0.5 #보다 높으면 사용자 직접확인
conf = {  # conf 설정  {클래스이름:[매뉴얼conf, 자동conf]}, 항상 보수적으로 잡기
    "default":1,
    "Zebra_Cross":0.52,
    "R_Signal":0.4,
    "G_Signal":0.4,
    "Braille_Block":0.48,
    "person":0.7,
    "dog":0.5,
    "tree":0.38,
    "car":0.65,
    "bus":0.6,
    "truck":0.55,
    "motorcycle":0.6,
    "bicycle":0.6,
    # "none":,
    "wheelchair":0.25,
    "stroller":0.25,
    "kickboard":0.25,
    "bollard":0.55,
    "manhole":0.45,
    "labacon":0.46,
    "bench":0.4,
    "barricade":0.55,
    "pot":0.5,
    "table":0.4,
    "chair":0.4,
    "fire_hydrant":0.55,
    "movable_signage":0.5,
    "bus_stop":0.5
}

img_size= [640, 360]
#######################################
import yaml, os, shutil, json, easydict
from PIL import Image, ImageDraw, ImageFont
import torch, random
from pathlib import Path

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, xyxy2xywh, strip_optimizer, increment_path
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel

global final, ignore, add_info
confirms={} # 통합클래스이름: [가장높은 불합격conf, 가장낮은 합격conf]
final=[]  # 통합클래스이름
class_book={}
ignore=[]  # src 중 무시할 클래스이름
img_box=[0,0,0,0] # Number of total [images, bboxes, tiny, large]
added={} # 클래스이름:추가된 박스 갯수
add_info=[]

# src_dir = '../../dataset/'+src
target_dir = '../../dataset/'+target
font = ImageFont.truetype("utils/arial_bold.ttf", 15)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"using devide {DEVICE}")

##### 모델 불러오기 #####
# 여기선 이미지, 텍스트 저장이 작동하지 않음
opt = easydict.EasyDict({'agnostic_nms':False, 'augment':True, 'classes':None, 'conf_thres':0.25, 'device':'', 
                            'exist_ok':False, 'img_size':640, 'iou_thres':0.45, 'name':'exp',
                            'no_trace':False, 'nosave':False, 'project':'runs/detect', 'save_conf':True, 'save_txt':True, 'source':'',
                            'update':False, 'view_img':False, 'weights':[src_pt]})

source, weights, view_img, save_txt, imgsz, trace = opt.source, opt.weights, opt.view_img, opt.save_txt, opt.img_size, not opt.no_trace
save_img = not opt.nosave and not source.endswith('.txt')  # save inference images

# Initialize
device = select_device(opt.device)
half = device.type != 'cpu'  # half precision only supported on CUDA

# Load model
model = attempt_load(weights, map_location=device)  # load FP32 model

# Directories
# save_dir = Path(increment_path(Path(opt.project) / opt.name, exist_ok=opt.exist_ok))  # increment run
# (save_dir).mkdir(parents=True, exist_ok=True)  # make dir
stride = int(model.stride.max())  # model stride
imgsz = check_img_size(imgsz, s=stride)  # check img_size

if trace:
    model = TracedModel(model, device, opt.img_size)

# Get names and colors
names = model.module.names if hasattr(model, 'module') else model.names
colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]
# BGR
colors[0] = [235,143,67] #Crosswalk
colors[1] = [0,0,255] #R_Signal
colors[2] = [0,255,0] #G_Signal
colors[3] = [0,212,255] #Braille

if device.type != 'cpu':
    model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))

##### 모델 불러오기 완료 #####

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

def draw_box(feature, coor, text, color):
    feature.line((coor[0], coor[1], coor[0], coor[3]), fill=color, width=2)
    feature.line((coor[0], coor[3], coor[2], coor[3]), fill=color, width=2)
    feature.line((coor[2], coor[3], coor[2], coor[1]), fill=color, width=2)
    feature.line((coor[2], coor[1], coor[0], coor[1]), fill=color, width=2)
    bbox = font.getbbox(text)
    text_shift = 12
    feature.rectangle((coor[0], coor[1]-text_shift, coor[0] + bbox[2], coor[1]), fill=color)
    feature.text((coor[0],coor[1]-text_shift), text, (255,255,255), font=font)

# 수동으로 판단한 내용을 confirm 객체에 저장
def add_confirm(name, ans, conf):
    if(name not in confirms.keys()):
        confirms[name] = ['NA','NA']
    if(ans=='y' or ans=='replace'):
        if(confirms[name][1]=='NA'):
            confirms[name][1]=conf
        elif(confirms[name][1]>conf):
            confirms[name][1]=conf
    elif(ans=='n'):
        if(confirms[name][0]=='NA'):
            confirms[name][0]=conf
        elif(confirms[name][0]<conf):
            confirms[name][0]=conf

def inference(image_path):
    dataset = LoadImages(image_path, img_size=imgsz, stride=stride)
                
    # YOLOv7 model
    for path, img, im0s, vid_cap in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.float()  # uint8 to fp32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        boxes=[]
        # Inference
        pred = model(img, augment=opt.augment)[0]
        pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)

        for i, det in enumerate(pred):  # detections per image
            s, im0, frame = '', im0s, getattr(dataset, 'frame', 0)
            # s += '%gx%g ' % img.shape[2:]  # print string
            # gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
            
                # Print results
                # for c in det[:, -1].unique():
                #     n = (det[:, -1] == c).sum()  # detections per class
                #     s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
                
                # Write results
                for *xyxy, conf, cls in reversed(det):
                    # print(f"{int(cls)} {names[int(cls)]} {torch.tensor(xyxy).view(1, 4)[0].tolist()} {conf}")
                    coor = torch.tensor(xyxy).view(1, 4)[0].tolist()
                    box={}
                    box["xmin"]= coor[0]
                    box["ymin"]= coor[1]
                    box["xmax"]= coor[2]
                    box["ymax"]= coor[3]
                    box["confidence"]= round(float(conf),5)
                    box["class"]= int(cls)
                    box["name"]= names[int(cls)]

                    boxes.append(box)
    return boxes

def image_collector(img_path, img_name):
    global data_name
    if not os.path.exists(f'../../dataset/hard_negative/{data_name}/'):
        os.mkdir(f'../../dataset/hard_negative/{data_name}/')
    shutil.copy(img_path+img_name, f'../../dataset/hard_negative/{data_name}/'+img_name)

def auto_labeling():
    global final, ignore, img_box, cases
    total_num=0
    num=0
    for type_ in ['/train','/val','/test']:
        image_folder = target_dir+type_+'/images/'
        if os.path.exists(image_folder):
            total_num += len(os.listdir(image_folder))


    for type_ in ['/train','/val','/test']:
        image_folder = target_dir+type_+'/images/'
        label_folder = target_dir+type_+'/labels/'
        if os.path.exists(image_folder):
            image_list = os.listdir(image_folder)
            for image_file in image_list:
                num+=1
                # image = Image.open(image_folder+image_file)
                image_path = image_folder+image_file
                image = Image.open(image_path)
                
                result = inference(image_path)
                # print(result)
                # Format is as follows:
                # [{"xmin":57.0689697266,"ymin":391.7705993652,"xmax":241.3835449219,"ymax":905.7978515625,"confidence":0.8689641356,"class":0.0,"name":"person"},
                # {"xmin":667.6612548828,"ymin":399.3035888672,"xmax":810.0,"ymax":881.3966674805,"confidence":0.8518877029,"class":0.0,"name":"person"},
                # {"xmin":222.8783874512,"ymin":414.774230957,"xmax":343.804473877,"ymax":857.8250732422,"confidence":0.8383761048,"class":0.0,"name":"person"},
                # {"xmin":4.2053861618,"ymin":234.4476776123,"xmax":803.7391357422,"ymax":750.0233764648,"confidence":0.6580058336,"class":5.0,"name":"bus"},
                # {"xmin":0.0,"ymin":550.5960083008,"xmax":76.6811904907,"ymax":878.669921875,"confidence":0.4505961835,"class":0.0,"name":"person"}]

                gts = []  # 각 원소는 [(int)라벨, xc, yc, w, h] 임
                gt_txt = label_folder+image_file[:image_file.find(".")]+".txt"
                if os.path.exists(gt_txt):
                    original_txt = open(gt_txt, 'r')
                    originals = original_txt.readlines()
                    for line in originals:
                        tok = list(map(float,line.split()))
                        if len(tok)!=5:
                            continue
                        tok[0] = int(tok[0])
                        gts.append(tok)
                    # Format is as follows:
                    # [[23, 0.19799479166666664, 0.4273148148148148, 0.20296875, 0.11388888888888889],
                    # [23, 0.038734375, 0.4248796296296296, 0.07642708333333334, 0.11018518518518519],
                    # [23, 0.39765364583333335, 0.43243518518518514, 0.07333854166666663, 0.07290740740740737]]
                for bbox in result:
                    # Too small box
                    if (bbox["xmax"]-bbox["xmin"])*(bbox["ymax"]-bbox["ymin"]) <150:
                        continue
                    aspect_ratio = (bbox["ymax"]-bbox["ymin"])/(bbox["xmax"]-bbox["xmin"])
                    if (aspect_ratio > AR_limit and bbox["name"] != "Braille"):
                        continue

                    is_addbox=-1  # 이 값이 0으로 바뀌면 해당 박스는 추가하지 않는것이고, 1로 바뀌면 추가하는 것
                    name = bbox['name']
                    class_num = int(bbox['class'])
                    confidence = round(bbox['confidence'], 5)
                    auto_level = conf['default']
                    if(name in ignore) or (name not in conf.keys() and confidence < conf['default']):
                       continue 
                    if(name in conf.keys()):
                        if(type(conf[name]) != type([])):
                            auto_level = conf[name]
                            if(confidence < conf[name]):
                                continue
                        elif(len(conf[name])==2):
                            auto_level = conf[name][1]
                            if(confidence < conf[name][0]):
                                continue
                        else:
                            print("Argument 'conf' Incorrect error. Exiting...")
                            exit()

                    for gt in gts:
                        predict_box = [bbox["xmin"], bbox["ymin"], bbox["xmax"], bbox["ymax"]]
                        xc = gt[1]*img_size[0]
                        yc = gt[2]*img_size[1]
                        w = gt[3]*img_size[0]
                        h = gt[4]*img_size[1]
                        gt_box = [xc-w/2, yc-h/2, xc+w/2, yc+h/2]
                        this_iou = IoU(predict_box, gt_box)
                        # print(this_iou)

                        # High IoU Manual Labeling
                        if(this_iou > iou_warning):
                            if(class_num==gt[0]):
                                is_addbox = 0
                                print(f"({num}/{total_num}) %-32s High IoU Bbox overlap ignored: {name}\tconf={confidence}"%image_file)
                                break
                            
                            rule_reject = this_iou>iou_warning and name=='labacon' and (final[gt[0]]=='fire_hydrant' or final[gt[0]]=='barricade')\
                                    or (this_iou>iou_warning and (name=='movable_signage' or name=="bollard") and (final[gt[0]]=='labacon'))
                            rule_replace = (this_iou>0.8 and confidence>0.8) or (this_iou>iou_warning and name=='labacon' and (final[gt[0]]=='movable_signage' or final[gt[0]]=='bollard'))\
                                    or (this_iou>iou_warning and (name=='fire_hydrant') and (final[gt[0]]=='bollard'))
                            
                            if not (rule_replace or rule_reject or is_auto_reject):
                                draw = ImageDraw.Draw(image)
                                draw_box(draw, gt_box, final[int(gt[0])],'red')
                                draw_box(draw, predict_box, name,'blue')
                                image.show()
                                
                            while(True):
                                if rule_reject:
                                    print(f"{image_file}: High-conf Rule base rejected box {name} on GT {final[gt[0]]}")
                                    ans='n'
                                elif rule_replace:
                                    print(f"{image_file}: High-conf Rule base replace box {name} over GT {final[gt[0]]}")
                                    ans='replace'
                                elif is_auto_reject:
                                    print(f"{image_file}: Auto rejecting & Hard Negative collecting.. {name} over GT {final[gt[0]]}, conf = {confidence}")
                                    if is_hard_negative_collect:
                                        image_collector(image_folder, image_file)
                                    ans='n'
                                else:
                                    ans = input(f"{image_file}: Confirm overlap box(blue) {name} over GT {final[gt[0]]}?: [y,n,replace,purge] > ")
                                    print(f"{ans} \n\t\t\t\t\t",end='')
                                if ans=='y':
                                    is_addbox = 1
                                    break
                                elif ans=='n':    
                                    is_addbox = 0
                                    print(f"Bbox overlap Manually ignored: GT: {final[gt[0]]}\treject {name} \tconf={confidence}")
                                    break
                                elif ans=='replace':
                                    is_addbox = 0
                                    print(f"Bbox overlap Manual/Auto replaced from: {final[gt[0]]}\tto: {name} \tconf={confidence}")
                                    gt[0]=class_num
                                    break
                                elif ans=='purge':
                                    gts.remove(gt)
                                    is_addbox = 0
                                    print(f"Bbox overlap Manually purged both GT: {final[gt[0]]}\tand {name} \tconf={confidence}")
                                    break
                                else:
                                    print("Wrong input, select again")

                            add_confirm(name, ans, confidence)
                            break

                        # Midium IoU
                        elif(this_iou > iou):
                            if(class_num==gt[0]):
                                is_addbox = 0
                                print(f"({num}/{total_num}) %-32s Medium IoU Bbox overlap ignored: {name}\tconf={confidence}"%image_file)
                                break

                    # Low-conf Quick Manual Labeling
                    if(confidence < auto_level and is_addbox==-1):
                        draw = ImageDraw.Draw(image)
                        draw_box(draw, predict_box, name,'green')
                        image.show()
                        while(True):
                            ans = input(f"{image_file}: Confirm low-conf: {confidence} box(green) {name}?: [y,n] > ")
                            print(f"{ans} \n\t\t\t\t\t",end='')
                            
                            if ans=='n':
                                is_addbox=0
                                print(f"Low-conf Manually ignored: {name}\tconf={confidence}")
                                break
                            elif ans=='y':
                                is_addbox=1
                                break
                            else:
                                print("Wrong answer, do it again")
                        add_confirm(name, ans, confidence)
                        break 
                            

                    if is_addbox:
                        print(f"({num}/{total_num}) {type_}/%-32s AutoLabeling new:\t{name}\tconf={confidence}"%image_file)
                    
                        # print(f"Normally adding new box: {name}")
                        xc = (bbox["xmax"]+bbox["xmin"])/2/img_size[0]
                        yc = (bbox["ymax"]+bbox["ymin"])/2/img_size[1]
                        w = (bbox["xmax"]-bbox["xmin"])/img_size[0]
                        h = (bbox["ymax"]-bbox["ymin"])/img_size[1]
                        new_box=[class_num, xc, yc, w, h]
                        gts.append(new_box)
                        if cases[name]=='Invalid':
                            cases[name]=1
                        else:
                            cases[name]+=1
                        if not name in added.keys():
                            added[name]=1
                        else:
                            added[name]+=1
                        img_box[1]+=1
                                
                with open(cb_dir+type_+'/labels/'+image_file[:image_file.find(".")]+'.txt','w') as t:
                    for nodes in gts:
                        for node in nodes:
                            t.write(str(node)+' ')
                        t.write('\n')


# def yaml_dumper():
#     content={}
#     with open(cb_dir+'/'+'data.yaml','w') as y:
#          yaml.dump(content, y)

def autolabel_yaml_writer():
    global origin_data_stat, img_box, add_info
    o = origin_data_stat
    train_val_test = o['Train-Val-Test']
    new_add_info={}
    new_add_info['weight']=src_pt
    new_add_info['Bbox_added']=added
    new_add_info['conf_threshold']=conf
    new_add_info['manual_confirms']=confirms
    add_info.append(new_add_info)

    nc = len(final)
    with open(cb_dir+"/data.yaml", 'w') as f:
        f.write(f"train: {cb_dir}/train/images\nval: ../{cb_dir}/val/images\n")
        f.write(f"test: {cb_dir}/test/images\n\nnc: {nc}\nnames: [")
        
        for i in range(nc):
            f.write(f"{final[i]}")
            if(i<nc-1):
                f.write(', ')
            else:
                f.write(']')
        f.write("\n# Dataset statistics: \nTotal imgs: %d\nTrain-Val-Test: [%d,%d,%d]\n\n"%(img_box[0],
            train_val_test[0],train_val_test[1],train_val_test[2]))
        f.write("Too small boxes ignored: %d\nToo large/odd boxes ignored: %d\n\n"%(img_box[2],img_box[3]))
        f.write("Total Bbox: %d\nBbox distribution:\n"%(img_box[1]))
        for i in range(nc):
            f.write("    %s: %s\n"%(final[i],cases[final[i]]))
        f.write("\nAuto labels:  # 라벨링 된 순서로 정렬됨  # Higest Reject, Lowest Confirm\n")
        for autolabel in add_info:
            f.write(f"  - weight : {autolabel['weight']}\n    Bbox_added: {autolabel['Bbox_added']}\n")
            f.write(f"    conf_threshold: {autolabel['conf_threshold']}\n    manual_confirms: {autolabel['manual_confirms']}\n")
        f.close()

def data_init():
    global final, ignore, origin_data_stat, cases, img_box, add_info, data_name
    data_name = src_pt[:src_pt.find('7')]

    class_json = json.load(open('../class.json'))
    final = class_json['Final']['Original']
    class_book = class_json['Final']['Label']
    origin_data_stat = yaml.safe_load(open(target_dir+'/data.yaml', encoding='UTF-8'))
    img_box[0] = origin_data_stat['Total imgs']
    img_box[1] = origin_data_stat['Total Bbox']
    img_box[2] = origin_data_stat['Too small boxes ignored']
    img_box[3] = origin_data_stat['Too large/odd boxes ignored']
    
    cases = origin_data_stat['Bbox distribution']
    for name in final:
        if name not in cases.keys():
            cases[name] = 0
    if 'Auto labels' in origin_data_stat.keys():
        add_info = origin_data_stat['Auto labels']

def main():
    if not os.path.exists(cb_dir):
        print("Copying images from src folder...")
        for dir in ['','/train','/val','/test']:
            os.mkdir(cb_dir+dir)
        for dir in ['/train/images','/val/images','/test/images']:
            if os.path.exists(target_dir+dir):
                shutil.copytree(target_dir+dir, cb_dir+dir)
    
    assigned=False
    for dir in ['/train/labels','/val/labels','/test/labels']:
        if os.path.exists(cb_dir+dir):
            if not assigned:
                ans = input("기존 오토라벨을 지우고 계속합니다. [y,n] : ")
                print(ans)
                if(ans!='y'):
                    exit() 
                else:
                    assigned=True
            shutil.rmtree(cb_dir+dir)
        if os.path.exists(target_dir+dir):
            os.mkdir(cb_dir+dir)

    print(f"Your confidence settings: {conf}")
    print(f"Source dataset : {target}, Using model: {src_pt}\n")
    data_init()
    auto_labeling()
    # yaml_dumper()
    autolabel_yaml_writer()
    if(not os.path.exists(cb_dir+'/test/images')):
        shutil.rmtree(cb_dir+'/test')

    print(f"\n\nFollowing bboxes are added: {added}")
    print(f"Manual confirm INFO:  # Higest Reject, Lowest Confirm\n\t{confirms}")
    


if __name__ == "__main__":
    main()