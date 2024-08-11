import webuiapi
import os
from PIL import Image

api = webuiapi.WebUIApi(host='127.0.0.1',
                        port=7860,
                        sampler='DPM++ 2M',
                        steps=22)

ads = webuiapi.ADetailer(ad_model="face_yolov8n.pt")

def image_gen(out_path, img, pos, neg, seed, steps, cfg, denoising_strength):
    w, h = img.size
    result = api.img2img(images=[img], 
                          prompt=pos,
                          negative_prompt=neg,
                          seed=seed,
                          steps=steps,
                          cfg_scale=cfg,
                          denoising_strength=denoising_strength,
                          resize_mode=2,
                          width=w,
                          height=h,
                          )
    output_directory = os.path.join(out_path, "gen.png")

    result.image.save(output_directory)
    return result.image