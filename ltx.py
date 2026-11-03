"""LTX-2.5 test (owner, 2 Nov 2026): make a few of a Short's AI shots with the open-source LTX-2.5 model on a
rented Modal GPU, to compare with the HeyGen shots. Free on Modal's $30 monthly credit; nothing is uploaded.

    modal run ltx.py --package outbox/yt-instinct-37.json --scenes 0,3,10

video.py uses the deployed app (modal deploy ltx.py, done by hope.yml) for acting shots: ltx_clip() below.
One warm container per function (max_containers=1), so the parallel scenes queue instead of each loading the model.

Needs MODAL_TOKEN_ID / MODAL_TOKEN_SECRET (Modal) and HF_TOKEN (Hugging Face, LTX-2.5 licence accepted).
Each shot starts on the character's reference photo (hosts/<name>-real.png), like our HeyGen image-to-video.
"""
import json
import os
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


def _render(text_only: bool, shots: list) -> list:
    """shots: [{"prompt", "photo" (png bytes)}] -> [(mp4 bytes, GPU seconds for that shot)]."""
    import io

    import torch
    from diffusers import LTX2ImageToVideoPipeline, LTX2Pipeline
    from diffusers.pipelines.ltx2.utils import DEFAULT_NEGATIVE_PROMPT, DISTILLED_SIGMA_VALUES
    from diffusers.utils import encode_video
    from PIL import Image

    start = time.time()
    pipe = (LTX2Pipeline if text_only else LTX2ImageToVideoPipeline).from_pretrained(MODEL, dtype=torch.bfloat16)
    pipe.enable_model_cpu_offload()
    cache.commit()
    print(f"model ready in {time.time() - start:.0f} s")
    out = []
    for i, shot in enumerate(shots):
        t = time.time()
        start_on = {} if text_only else {"image": Image.open(io.BytesIO(shot["photo"])).convert("RGB")}
        video, _audio = pipe(**start_on, prompt=shot["prompt"],
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


GPU = dict(gpu="H100", volumes={"/cache": cache}, timeout=3600, max_containers=1, scaledown_window=300,
           secrets=[modal.Secret.from_local_environ(["HF_TOKEN"])] if os.environ.get("HF_TOKEN") else [])  # set at deploy; video.py imports ltx_clip without it


@app.function(**GPU)
def make(shots: list) -> list:
    """Image-to-video: each shot starts on its photo."""
    return _render(False, shots)


@app.function(**GPU)
def make_text(shots: list) -> list:
    """Text-to-video for shots with no starting picture (own container: two LTX pipelines don't fit one H100)."""
    return _render(True, shots)


@app.function(gpu="H100", volumes={"/cache": cache}, timeout=1800, max_containers=1, scaledown_window=300)
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
                   prompt="Keep this exact person or animal (same face, hair, clothes, fur, markings, age and size) and place them in this scene: "
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


def ltx_clip(prompt: str, path: Path, photo: Path = None, scene: str = "") -> float:
    """For video.py and film.py (owner, 2 Nov 2026: LTX makes every AI shot, HeyGen only talking hosts).
    photo + scene: the character placed into the scene (Qwen-Image-Edit), then animated; photo alone: animated as it is;
    neither: text-to-video. Saves a 5 s silent mp4 to path and returns the cost in dollars (H100 rate)."""
    try:
        return _modal_clip(prompt, path, photo, scene)
    except Exception as e:  # Modal down or out of credit: the same model on RunPod (owner, 3 Nov 2026)
        if not (os.environ.get("RUNPOD_API_KEY") and (Path(__file__).parent / "runpod.json").exists()):
            raise
        print(f"    Modal LTX failed ({str(e)[:120]}); using RunPod")
        from runpod_ltx import runpod_clip
        return runpod_clip(prompt, path, photo, scene)


def _modal_clip(prompt: str, path: Path, photo: Path = None, scene: str = "") -> float:
    still, gpu = photo.read_bytes() if photo else None, 0
    if photo and scene:
        still = modal.Function.from_name("hopeverse-ltx", "pose").remote([{"photo": still, "scene": scene}])[0]
        gpu += 30  # ponytail: typical Qwen still time on a warm H100; pose() could return its own seconds
    mp4, secs = modal.Function.from_name("hopeverse-ltx", "make" if still else "make_text").remote(
        [{"prompt": prompt, "photo": still}])[0]
    path.write_bytes(mp4)
    # GPU time only: wall time counts the queue (scenes run 6 at a time on one GPU) and ate the $3 video cap on 3 Nov
    return round((gpu + secs) * 0.001097, 3)
