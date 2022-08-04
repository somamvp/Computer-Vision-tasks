target_path = 'my_yolov5/data/'
target_file = 'wesee.yaml'
# remain = ['person', 'bicycle', 'car','motorcycle', 'bus', 'train', 'truck', 'fire hydrant','bench']
remain = ['Zebra_Cross']

import yaml, os
mapping={}

def match_class():
    global dict
    dict = yaml.safe_load(open(target_path + target_file, encoding='UTF-8'))
    # print(dict)
    print(dict['names'])

    for name in remain:
        if name not in dict['names']:
            print("Not existing class chosen: %s"%name)
            exit()
    print("Target classes are : %s"%remain)

def make_mapping():
    global mapping, mapping_key
    for cnt in range(0,len(remain)-1):
        mapping[dict['names'].index(remain[cnt])] = cnt
    mapping_key = mapping.keys()
    # print(mapping_key)

def reannotation():
    path = dict['path']
    with open(path[path.find('../')+3:]+"/val/labels") as folder:
        print(len(os.listdir(folder)))

def write_yaml():
    pass


def main():
    match_class()
    make_mapping()
    reannotation()
    write_yaml()

if __name__ == "__main__":
    main()