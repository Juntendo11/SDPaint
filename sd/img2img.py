import webuiapi

api = webuiapi.WebUIApi(host='127.0.0.1',
                        port=7860,
                        sampler='DPM++ 2M',
                        steps=22)

ads = webuiapi.ADetailer(ad_model="face_yolov8n.pt")

def image_gen(img, pos, neg):
    result = api.img2img(images=[img], 
                          prompt=pos,
                          negative_prompt=neg,
                          seed=-1, 
                          cfg_scale=7.0, 
                          denoising_strength=0.6
                          )

    #result.image.save("C:\\Users\\PC-kun\\AppData\\Roaming\\Blender Foundation\\Blender\\3.3\\scripts\\addons\\sdpaint\\gen.png")
    return result.image