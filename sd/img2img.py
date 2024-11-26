import os
import random
from PIL import Image

ads = webuiapi.ADetailer(ad_model="face_yolov8n.pt")

def image_gen(out_path, img, pos, neg, seed, steps, cfg, denoising_strength, scale = 1.0):
    w, h = img.size
    result = api.img2img(images=[img], 
                          prompt=pos,
                          negative_prompt=neg,
                          seed=seed,
                          steps=steps,
                          cfg_scale=cfg,
                          denoising_strength=denoising_strength,
                          resize_mode=2,
                          width=w*scale,
                          height=h*scale,
                          )
    output_directory = os.path.join(out_path, "gen.png")

    result.image.save(output_directory)
    print(result)
    return result.image
    
def generate_seed():
    # Generates int64 seed value
    seed_val = random.randint(0, 2**31 - 1)
    return seed_val