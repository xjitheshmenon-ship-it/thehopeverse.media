"""LTX-2.5 on RunPod Serverless: the backup when Modal fails or its credit runs out (owner, 3 Nov 2026).

Same model and settings as ltx.py on Modal, so the shots look the same. The RunPod worker starts from a stock
PyTorch image, installs diffusers and runs this file (no image to build); weights live on a network volume at
/runpod-volume, downloaded once. Set up with: push run/runpod (runpod.yml), which saves the endpoint id to runpod.json.

Worker input: {"mode": "make" | "make_text" | "pose", "prompt", "photo" (base64 png), "scene"}
Worker output: {"mp4": base64, "secs": GPU seconds} or {"png": base64}
"""
import base64
import io
import json
import os
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
API = "https://api.runpod.ai/v2"
H100_USD_S = 0.00076  # ponytail: RunPod serverless H100 flex price per second, Nov 2026; re-check if billing differs


def runpod_clip(prompt: str, path: Path, photo: Path = None, scene: str = "") -> float:
    """ltx_clip on RunPod: same arguments, same 5 s silent mp4, returns the cost in dollars."""
    still, cost = (base64.b64encode(photo.read_bytes()).decode() if photo else None), 0.0
    if photo and scene:
        out = _run({"mode": "pose", "photo": still, "scene": scene})
        still, cost = out["png"], 30 * H100_USD_S
    out = _run({"mode": "make" if still else "make_text", "prompt": prompt, "photo": still})
    path.write_bytes(base64.b64decode(out["mp4"]))
    return round(cost + out["secs"] * H100_USD_S, 3)


def _run(job: dict) -> dict:
    endpoint = json.loads((HERE / "runpod.json").read_text())["endpoint"]
    head = {"Authorization": f"Bearer {os.environ['RUNPOD_API_KEY']}", "Content-Type": "application/json"}
    req = urllib.request.Request(f"{API}/{endpoint}/run", json.dumps({"input": job}).encode(), head)
    jid = json.load(urllib.request.urlopen(req, timeout=60))["id"]
    for _ in range(240):  # up to 40 min: the very first job downloads the weights to the volume
        time.sleep(10)
        st = json.load(urllib.request.urlopen(urllib.request.Request(f"{API}/{endpoint}/status/{jid}", headers=head), timeout=60))
        if st["status"] == "COMPLETED":
            return st["output"]
        if st["status"] in ("FAILED", "CANCELLED", "TIMED_OUT"):
            raise RuntimeError(f"RunPod LTX {st['status']}: {str(st.get('error'))[:300]}")
    raise TimeoutError("RunPod LTX took over 40 minutes")


# ---- worker side (runs on the RunPod GPU) ----
_pipes = {}


def _pipe(mode: str):
    import torch
    if mode not in _pipes:
        _pipes.clear()  # one pipeline at a time fits the GPU
        if mode == "pose":
            from diffusers import QwenImageEditPipeline
            _pipes[mode] = QwenImageEditPipeline.from_pretrained("Qwen/Qwen-Image-Edit", torch_dtype=torch.bfloat16).to("cuda")
        else:
            from diffusers import LTX2ImageToVideoPipeline, LTX2Pipeline
            p = (LTX2Pipeline if mode == "make_text" else LTX2ImageToVideoPipeline).from_pretrained(
                "Lightricks/LTX-2.5-Diffusers", dtype=torch.bfloat16)
            p.enable_model_cpu_offload()
            _pipes[mode] = p
        torch.cuda.empty_cache()
    return _pipes[mode]


def handler(event):
    import torch
    from PIL import Image
    job, t = event["input"], time.time()
    photo = Image.open(io.BytesIO(base64.b64decode(job["photo"]))).convert("RGB") if job.get("photo") else None
    if job["mode"] == "pose":
        img = _pipe("pose")(image=photo, height=1280, width=704,
                            prompt="Keep this exact person or animal (same face, hair, clothes, fur, markings, age and size) and place them in this scene: "
                                   f"{job['scene']} Photorealistic vertical phone photo, no text.",
                            negative_prompt=" ", true_cfg_scale=4.0, num_inference_steps=30,
                            generator=torch.Generator("cuda").manual_seed(42)).images[0]
        buf = io.BytesIO()
        img.save(buf, "PNG")
        return {"png": base64.b64encode(buf.getvalue()).decode()}
    from diffusers.pipelines.ltx2.utils import DEFAULT_NEGATIVE_PROMPT, DISTILLED_SIGMA_VALUES
    from diffusers.utils import encode_video
    video, _audio = _pipe(job["mode"])(**({"image": photo} if photo else {}), prompt=job["prompt"],
                                       negative_prompt=DEFAULT_NEGATIVE_PROMPT, height=1280, width=704, num_frames=121,
                                       frame_rate=24.0, sigmas=DISTILLED_SIGMA_VALUES, guidance_scale=1.0,
                                       audio_guidance_scale=1.0, stg_scale=0.0, audio_stg_scale=0.0, modality_scale=1.0,
                                       audio_modality_scale=1.0, generator=torch.Generator("cuda").manual_seed(42),
                                       output_type="np", return_dict=False)
    encode_video(video[0], fps=24, output_path="/tmp/shot.mp4")
    return {"mp4": base64.b64encode(Path("/tmp/shot.mp4").read_bytes()).decode(), "secs": round(time.time() - t)}


if __name__ == "__main__":
    import runpod
    runpod.serverless.start({"handler": handler})
