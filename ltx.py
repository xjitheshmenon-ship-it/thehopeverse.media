"""LTX-2.5 test (owner, 2 Nov 2026): make a few of a Short's AI shots with the open-source LTX-2.5 model on a
rented Modal GPU, to compare with the HeyGen shots. Free on Modal's $30 monthly credit; nothing is uploaded.

    modal run ltx.py --package outbox/yt-instinct-37.json --scenes 0,3,10

Needs MODAL_TOKEN_ID / MODAL_TOKEN_SECRET (Modal) and HF_TOKEN (Hugging Face, LTX-2.5 licence accepted).
Each shot starts on the character's reference photo (hosts/<name>-real.png), like our HeyGen image-to-video.
"""
import json
import time
from pathlib import Path

import modal

MODEL = "Lightricks/LTX-2.5-Diffusers"
HEIGHT, WIDTH, FRAMES, FPS = 1280, 704, 121, 24  # 9:16, about 5 s (frames % 8 == 1, sides divisible by 32)

image = (modal.Image.debian_slim(python_version="3.12").apt_install("git", "ffmpeg")
         .pip_install("torch", "torchvision", "transformers", "accelerate", "sentencepiece", "imageio", "imageio-ffmpeg", "av",
                      "huggingface_hub[hf_transfer]", "git+https://github.com/huggingface/diffusers")
         .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": "/cache"}))
cache = modal.Volume.from_name("ltx-cache", create_if_missing=True)  # ~70 GB of weights, downloaded once
app = modal.App("hopeverse-ltx", image=image)


@app.function(gpu="H100", volumes={"/cache": cache}, timeout=3600, secrets=[modal.Secret.from_local_environ(["HF_TOKEN"])])
def make(shots: list) -> list:
    """shots: [{"prompt", "photo" (png bytes)}] -> [(mp4 bytes, seconds of GPU time for that shot)]."""
    import io

    import torch
    from diffusers import LTX2ImageToVideoPipeline
    from diffusers.pipelines.ltx2.utils import DEFAULT_NEGATIVE_PROMPT, DISTILLED_SIGMA_VALUES
    from diffusers.utils import encode_video
    from PIL import Image

    start = time.time()
    pipe = LTX2ImageToVideoPipeline.from_pretrained(MODEL, dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    cache.commit()
    print(f"model ready in {time.time() - start:.0f} s")
    out = []
    for i, shot in enumerate(shots):
        t = time.time()
        video, _audio = pipe(image=Image.open(io.BytesIO(shot["photo"])).convert("RGB"), prompt=shot["prompt"],
                             negative_prompt=DEFAULT_NEGATIVE_PROMPT, height=HEIGHT, width=WIDTH, num_frames=FRAMES,
                             frame_rate=float(FPS), sigmas=DISTILLED_SIGMA_VALUES, guidance_scale=1.0,
                             audio_guidance_scale=1.0, stg_scale=0.0, audio_stg_scale=0.0, modality_scale=1.0,
                             audio_modality_scale=1.0, generator=torch.Generator("cuda").manual_seed(42),
                             output_type="np", return_dict=False)
        path = f"/tmp/shot-{i}.mp4"
        encode_video(video[0], fps=FPS, output_path=path)  # picture only: our Shorts carry their own voice and music
        out.append((Path(path).read_bytes(), round(time.time() - t)))
        print(f"shot {i}: {out[-1][1]} s")
    return out


@app.function(gpu="H100", volumes={"/cache": cache}, timeout=1800)
def pose(shots: list) -> list:
    """Scene still first (owner, 2 Nov): put the character from its reference photo into the shot's scene with the
    open-source Qwen-Image-Edit (Apache 2.0), so LTX animates the right place, not the reference photo's background."""
    import io

    import torch
    from diffusers import QwenImageEditPipeline
    from PIL import Image

    pipe = QwenImageEditPipeline.from_pretrained("Qwen/Qwen-Image-Edit", torch_dtype=torch.bfloat16).to("cuda")
    cache.commit()
    out = []
    for shot in shots:
        img = pipe(image=Image.open(io.BytesIO(shot["photo"])).convert("RGB"), height=HEIGHT, width=WIDTH,
                   prompt="Keep this exact animal (same face, fur, markings, age and size) and place it in this scene: "
                          f"{shot['scene']} Photorealistic vertical phone photo, no text.",
                   negative_prompt=" ", true_cfg_scale=4.0, num_inference_steps=30,
                   generator=torch.Generator("cuda").manual_seed(42)).images[0]
        buf = io.BytesIO()
        img.save(buf, "PNG")
        out.append(buf.getvalue())
    return out


@app.local_entrypoint()
def main(package: str, scenes: str = "0,3,10", out: str = "ltx-test", scene_first: bool = False):
    pkg = json.loads(Path(package).read_text())
    picked = [pkg["scenes"][int(i)] for i in scenes.split(",")]
    shots = [{"prompt": f"{s['image_prompt']} Natural, subtle real movement, cinematic. No text.",
              "photo": Path(f"hosts/{s['on_screen'].lower()}-real.png").read_bytes()} for s in picked]
    start = time.time()
    Path(out).mkdir(parents=True, exist_ok=True)
    if scene_first:
        for idx, shot, s, png in zip(scenes.split(","), shots, picked, pose.remote(
                [{"photo": sh["photo"], "scene": s["image_prompt"]} for sh, s in zip(shots, picked)])):
            shot["photo"] = png
            (Path(out) / f"scene-{int(idx):02}-still.png").write_bytes(png)
    results = make.remote(shots)
    report = []
    for idx, (mp4, secs), s in zip(scenes.split(","), results, picked):
        (Path(out) / f"scene-{int(idx):02}-ltx.mp4").write_bytes(mp4)
        report.append({"scene": int(idx), "character": s["on_screen"], "gpu_seconds": secs,
                       "usd_at_h100_rate": round(secs * 0.001097, 3)})
    total = time.time() - start  # includes start-up and the first download of the weights
    Path(out, "report.json").write_text(json.dumps({"shots": report, "run_seconds": round(total),
                                                     "usd_whole_run_at_h100_rate": round(total * 0.001097, 2)}, indent=2))
    print(Path(out, "report.json").read_text())
