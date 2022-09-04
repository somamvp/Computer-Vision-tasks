import pytorch_msssim
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# device = torch.device('cpu')
m = pytorch_msssim.MS_SSIM()

img1 = torch.rand(1, 1, 256, 256)
img2 = torch.rand(1, 1, 256, 256)

print(pytorch_msssim.ms_ssim(img1, img2))
# print(m(img1, img2))