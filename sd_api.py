import json
import requests
import io
import os
import base64
from PIL import Image, PngImagePlugin
import time
from datetime import datetime

url = "http://127.0.0.1:7860"

datetimenow = datetime.now()
formatted_date = datetimenow.strftime("%Y%m%d")

output_dir = f'C:/Users/mokos/Stable_Diffusion/sd.webui/webui/outputs/{formatted_date}_api_output/'

# Read prompt from a file
#prompt_file_path = 'prompt.txt'  # Update this path if your file is located elsewhere
prompt_file_path = 'korean.txt'
with open(prompt_file_path, 'r', encoding='utf-8') as file:
    prompt = file.read().strip()

n_prompt_file_path = 'n.korean.txt'
with open(n_prompt_file_path, 'r', encoding='utf-8') as file:
    negative_prompt = file.read().strip()

override_settings = {}
override_settings["sd_model_checkpoint"] = "BRAV5finalfp16.safetensors"
#override_settings["sd_model_checkpoint"] = "chilloutmix_NiPrunedFp32Fix"
#override_settings["sd_model_checkpoint"] = "beautifulRealistic_brav5"
#override_settings["sd_model_checkpoint"] = "beautifulRealistic_v60"
#override_settings["sd_vae"] = "vae-ft-mse-840000-ema-pruned"
#override_settings["sd_vae"] = "v2-1_768-ema-pruned"

# loop and seed settings
loop = 1
seed = -1
#enable_hr = False
enable_hr = True

#prompt = f"{quality1}, {quality5}, {angle11}, {person1}, {style1}, {age1}, {face1}, {hairlength7}, {chest1}, {cloth6}, {cloth8}, ({pose4}:1.1), {place5}, {light1}"
#prompt = "A woman in an elegant pose on a beach bathed in sunlight. She is wearing a summer dress, looking at the camera with a natural smile. The image is bright and colorful, conveying a positive atmosphere. In the background, the blue sky and sea stretch out, with a sense of a gentle breeze"
#negative_prompt = "illustration,3d,sepia,painting,cartoons,sketch,(worst quality:2),((monochrome)),((grayscale:1.2)),(backlight:1.2),analog,analog photo,(bad hands, bad fingers, bad arms, bad legs, bad knees, bad navel:1.5),Shank Hair,(nipples:1.2), (muscle:1.1),(extra fingers, extra arms, extra legs, extra digit, fewer digits:1.5),(text:1.3), signature, missing limb, missing fingers, nipples, 2 persons"

def counter_file_check(counter=0):
    # スクリプトの実行回数の記録
    try:
        with open(f"{output_dir}script_counter.txt", "r") as file:
            counter = int(file.read().strip()) + 1
    except FileNotFoundError:
        counter = 0

    # スクリプトの実行回数を追記する
    with open(f"{output_dir}script_counter.txt", "w") as file:
        file.write(str(counter))

    return(counter)

def loop_crate_image(seed):
    for c in range(loop):

        payload = {
            # "sd_model_checkpoint": "BRAV5finalfp16.safetensors",
            # "sd_model_checkpoint": "chilloutmix_NiPrunedFp32Fix",
            # "enable_hr": True,
            "enable_hr": enable_hr,
            "denoising_strength": 0.3,
            "hr_scale": 2.05,
            "hr_upscaler": "LDSR",
            "prompt": prompt,
            "steps": 40,
            "seed": seed,
            "width": 540,
            "height": 960,
            "negative_prompt": negative_prompt,
            "sampler_index": "DPM++ SDE Karras",
            "override_settings": override_settings
        }

        response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

        r = response.json()

        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))
            
            #image.save(f'C:/Users/mokos/Stable_Diffusion/sd.webui/webui/outputs/api_output/{counter}-{c + 1}-seed[{seed}].png', pnginfo=pnginfo)
            image.save(f'{output_dir}{counter}-{c + 1}-seed[{seed}].png', pnginfo=pnginfo)

            # seed値に1を加えてループを終了(seed = -1 の場合はスルー)
            if seed == -1:
                seed = -1
            else:
                seed = seed + 1 

        if not os.path.exists(f'{output_dir}prompt'):
            os.makedirs(f'{output_dir}prompt')
        
        with open(f"{output_dir}prompt/prompt.txt", "a") as file:
            file.write(f'date : {formatted_date}\n')
            file.write(f'counter : {c}\n')
            file.write(f'seed : {seed}\n')
            file.write('prompt : \n')
            file.write(f'{prompt}\n')
            file.write('\n')
            file.write('negative_prompt : \n')
            file.write(f'{negative_prompt}\n')
            file.write('\n')


        print(f"image created : {c + 1}")
        print(f"Prompt : {prompt}")
        print(f"Negative : {negative_prompt}")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

start_time = time.time() # スクリプトの開始時間
nows = datetime.now()

print(f"Start time: {nows.strftime('%Y-%m-%d %H:%M:%S')}")
counter = counter_file_check()
loop_crate_image(seed)

nowe = datetime.now()
print(f"End time: {nowe.strftime('%Y-%m-%d %H:%M:%S')}")

end_time = time.time() # 終了時間の記録
execution_time = end_time - start_time # 実行時間計算

# print(f"start_time : {start_time} s")
# print(f"end_time : {end_time} s")
print(f"Execution time : {execution_time} s")

m, s = divmod(execution_time, 60)
h, m = divmod(m, 60)
d, h = divmod(h, 24)

print(f"Execution time: {d} days, {h} hours, {m} minutes, {s} seconds")