import os, json
from PIL import Image, ImageDraw, ImageFont

src_dir = '../dataset/weseel_RAplus1-Dobo_sample_parsed/train/'
show_others = True
# wanted={'9':'scooter'}  #Dobo
# wanted = {'14':'unusual bench','16':"Chair"}   #Chair set
# wanted = {'8':'bus','10':'motorcycle'}
wanted = {'0':"Zebra_Cross",
'1':"R_Signal",
'2':"G_Signal",
# '3':"Braille_Block",
# '4':"person",
# '5':"dog",
# '6':"tree",
# '7':"car",
# '8':"bus",
# '9':"truck",
# '10':"motorcycle",
# '11':"bicycle",
# '12':"train",
# '13':"wheelchair",
# '14':"stroller",
# '15':"kickboard",
# '16':"bollard",
# '17':"manhole",
# '18':"labacon",
# '19':"bench",
# '20':"barricade",
# '21':"pot",
# '22':"table",
# '23':"chair",
# '24':"fire_hydrant",
# '25':"movable_signage",
# '26':"bus_stop",
# ' ':"wrong approach"
}  #all

def main():
    final = json.load(open('class.json',))['Final']['Original']
        
    label_path = src_dir+'labels'
    image_path = src_dir+'images'
    label_list = os.listdir(label_path)
    # print(len(label_list))
    font_size = 15
    font = ImageFont.truetype("my_yolov5/utils/arial_bold.ttf", font_size)

    for label in label_list:
        image_name = label[:label.find(".txt")]+".jpg"
        if(not os.path.exists(image_path+'/'+image_name)):
            image_name = label[:label.find(".txt")]+".png"
        with open(label_path+'/'+label) as l:
            detected=False
            lines = l.readlines()
            image = Image.open(image_path+'/'+image_name)
            # print(text)
            for line in lines:
                tok = line.split()
                draw = ImageDraw.Draw(image)
                x=float(tok[1])*image.size[0]
                y=float(tok[2])*image.size[1]
                w=float(tok[3])*image.size[0]
                h=float(tok[4])*image.size[1]
                xtl=int(x-w/2)
                ytl=int(y-h/2)
                xbr=int(x+w/2)
                ybr=int(y+h/2)

                if tok[0] in list(wanted.keys()):
                    detected=True
                    print(f"{image_name} contains --{wanted[tok[0]]}--\t--Size: {xbr-xtl}*{ybr-ytl} = {(xbr-xtl)*(ybr-ytl)}")
                
                if show_others or tok[0] in list(wanted.keys()):
                    draw.line((xtl, ytl, xtl, ybr), fill="red", width=2)
                    draw.line((xtl, ybr, xbr, ybr), fill="red", width=2)
                    draw.line((xbr, ybr, xbr, ytl), fill="red", width=2)
                    draw.line((xbr, ytl, xtl, ytl), fill="red", width=2)
                    text = final[int(tok[0])]
                    bbox = font.getbbox(text)
                    text_shift = 12
                    draw.rectangle((xtl, ytl-text_shift, xtl + bbox[2], ytl), fill='red')
                    draw.text((xtl,ytl-text_shift), text, (255,255,255), font=font)

            if detected==False:
                continue
            image.show()
            wait = input("")
            image.close()

if __name__ == "__main__":
    main()