# SSIM, MS-SSIM 은 흑백이미지를 대상으로 디자인 된 것
# FSIM_c 가 컬러 이미지를 위해 디자인 된 것

from IQA_pytorch import SSIM, utils
from PIL import Image
import torch
 
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device = torch.device('cpu')

ref_path  = '7.jpg'
dist_path = 'other.jpg' 
 
ref = utils.prepare_image(Image.open(ref_path).convert("RGB")).to(device)
dist = utils.prepare_image(Image.open(dist_path).convert("RGB")).to(device)
 
model = SSIM(channels=3)
 
score = model(dist, ref, as_loss=False)
print('score: %.4f' % score.item())
