import os
from PIL import Image, ImageDraw

src_dir = '../dataset/Wesee_sample_parsed/train/'
# wanted={'9':'scooter'}  #Dobo
# wanted = {'14':'unusual bench','16':"Chair"}   #Chair set
wanted = {'0':'Cross','1':'R_Signal','2':'G_Signal'}

label_path = src_dir+'labels'
image_path = src_dir+'images'
label_list = os.listdir(label_path)
# print(len(label_list))

for label in label_list:
    image_name = label[:label.find(".txt")]+".jpg"
    with open(label_path+'/'+label) as l:
        detected=False
        lines = l.readlines()
        image = Image.open(image_path+'/'+image_name)
        # print(text)
        for line in lines:
            tok = line.split()
            if tok[0] in list(wanted.keys()):
                detected=True
                draw = ImageDraw.Draw(image)
                x=int(float(tok[1])*image.size[0])
                y=int(float(tok[2])*image.size[1])
                w=int(float(tok[3])*image.size[0])
                h=int(float(tok[4])*image.size[1])
                xtl=int(x-w/2)
                ytl=int(y-h/2)
                xbr=int(x+w/2)
                ybr=int(y+h/2)
                print(f"{image_name} contains --{wanted[tok[0]]}--\t--Size:\
 {xbr-xtl}*{ybr-ytl} = {(xbr-xtl)*(ybr-ytl)}")
                # print(xtl, ytl, xbr, ybr)
                draw.line((xtl, ytl, xtl, ybr), fill="red", width=2)
                draw.line((xtl, ybr, xbr, ybr), fill="red", width=2)
                draw.line((xbr, ybr, xbr, ytl), fill="red", width=2)
                draw.line((xbr, ytl, xtl, ytl), fill="red", width=2)
                draw.text((xtl,ytl-15), f"{wanted[tok[0]]}", (255,0,0))
        if detected==False:
            continue
        image.show()
        wait = input("")