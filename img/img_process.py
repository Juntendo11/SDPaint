from PIL import Image


def ceil_divisible(n, m) :
    q = int(n / m)  #lower ceil
    n1 = m * q
    return n1
    
    
def crop_image(img):
    width, height = img.size
    
    #Find lowest divisible factor by 8
    width_crop = ceil_divisible(width,8)
    height_crop = ceil_divisible(height,8)
    
    dw = width - width_crop
    dh = height - height_crop

    left = dw // 2
    top = dh // 2
    right = width - (dw - left)
    bottom = height - (dh - top)

    cropped_img = img.crop((left, top, right, bottom))
    return cropped_img

ren_img = Image.open("mahousyojyo_chara_01.png")
print(ren_img.size)
cropped = crop_image(ren_img)
print(cropped.size)
