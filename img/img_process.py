from PIL import Image

def ceil_divisible(n, m):
    # Find closest lower divisible number
    q = int(n / m)  #lower ceil
    n1 = m * q
    return n1

def div_image_size(img):
    #Returns the expected image resolution size
    width, height = img.size
    
    #Find lowest divisible factor by 8
    width_crop = ceil_divisible(width,8)
    height_crop = ceil_divisible(height,8)
    return width_crop, height_crop
    
def crop_image(img):
    #Returns the cropped image for stable diffusion
    width, height = img.size
    width_crop, height_crop = div_image_size(img)
    dw = width - width_crop
    dh = height - height_crop

    left = dw // 2
    top = dh // 2
    right = width - (dw - left)
    bottom = height - (dh - top)

    cropped_img = img.crop((left, top, right, bottom))
    return cropped_img

