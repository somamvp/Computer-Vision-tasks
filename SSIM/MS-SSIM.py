from pytorch_msssim import ssim, ms_ssim, SSIM, MS_SSIM
from PIL import Image
import natsort
import os, torch
import matplotlib.pyplot as plt
import numpy as np
from torchvision.transforms import ToTensor
tf_toTensor = ToTensor() 
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

src_dir = "../../dataset/Wesee_sample_parsed/train/images/"
# target_dir="./"
img_list = os.listdir(src_dir) #디렉토리 내 모든 파일 불러오기
img_list_jpg = [img for img in img_list if img.endswith(".jpg")] #지정된 확장자만 필터링
img_list_jpg = natsort.natsorted(img_list_jpg)
total_size = len(img_list_jpg)

def ms_ssim_in(base):
    base_list_tensor = []
    img_list_tensor = []

    img = Image.open(src_dir + base)
    img_tensor = tf_toTensor(img)
    for i in range(1,total_size+1):
        base_list_tensor.append(img_tensor)
    X = torch.stack(base_list_tensor)

    for i in img_list_jpg:
        img = Image.open(src_dir + i)
        img_tensor = tf_toTensor(img)  #0~1
        img_list_tensor.append(img_tensor)
        
    img_tensor = torch.stack(img_list_tensor)
    Y = img_tensor

    # calculate ssim & ms-ssim for each image
    # ssim_val = ssim( X, Y, data_range=1, size_average=False) # return (N,)
    return ms_ssim( X, Y, data_range=1, size_average=False ) #(N,)

def heat_map(val):
    arr = val.numpy()
    if arr.ndim == 1:
        arr = np.expand_dims(arr, axis=0)
    # print(arr.shape)
    plt.matshow(arr)
    # cmap = plt.get_cmap('Greys')
    plt.clim(-1.0, 1.0)
    plt.colorbar()  
    plt.show()

result_list = []
for k in img_list_jpg:
    tmp = ms_ssim_in(k)
    result_list.append(tmp)
print(img_list_jpg)
print(result_list)
result = torch.stack(result_list)
heat_map(result)



# arr = np.random.standard_normal((30, 40))
