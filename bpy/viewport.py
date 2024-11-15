import bpy

def get_viewport_size():
    for a in bpy.context.screen.areas:
        if a.type == 'VIEW_3D':
            for r in a.regions:
                if r.type == 'WINDOW':
                    return r.width, r.height
                    #print(f"Viewport dimensions: {r.width}x{r.height}, approximate aspect rato: {round(r.width/r.height, 2)}")
                    

def ceil_divisible(n, m) :
    q = int(n / m)  #lower ceil
    n1 = m * q
    return n1
    
    
def crop_image(img):
    width, height = img.size
    
    #Find lowest divisible factor by 8
    width_crop = ceil_divisible(width)
    height_crop = ceil_divisible(height)
    
    dw = width - width_crop
    dh = height - height_crop
    
    
    #If odd, +1 pixel to make it even, if even => unchanged
    dw += dw % 2
    dh += dh % 2
        
    cropped = im.crop((dw/2, dh/2, dw/2, dh/2))   #(left, top, right, bottom)
    return cropped