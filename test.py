import yaml
# j = yaml.safe_load(open("../dataset/Wesee_sample_parsed/data.yaml", encoding='UTF-8'))
# con ={}
# con["classes"]=['Zebra_Cross', 'R_Signal', 'G_Signal', 'Braille_Block', 'person', 'dog', 'tree', 'car', 'bus', 'truck', 'motorcycle', 'bicycle', 'train', 'wheelchair', 'stroller', 'kickboard', 'bollard', 'manhole', 'labacon', 'bench', 'barricade', 'pot', 'table', 'chair', 'fire_hydrant', 'movable_signage', 'bus_stop']
# con["numbers"]=5
# dict={}
# dict["r_signal"]=5
# dict["g_signal"]=3
# con["dict"]=dict
# with open('test.yaml', 'w') as f:
#     yaml.dump(con,f, default_flow_style=None, width=70)


result = [{'name':'abc', 'x':3, 'y':5, 'depth':0.2},
 {'name':'xyz', 'x':6, 'y':1, 'depth':0.9},
{'name':'qqq', 'x':7, 'y':1, 'depth':0.9}]

for li in result:
    if li['x']>4:
        result.remove(li)

print(result)
# print(sorted(result, key=lambda x: x['y'], reverse=False))