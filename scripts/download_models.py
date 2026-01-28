import sys
import shutil
import argparse
from pathlib import Path

from huggingface_hub import hf_hub_download, snapshot_download


YOLO = "Daniil-Domino/yolo11x-dialectic"
TROCR_TORCH = "Daniil-Domino/trocr-base-ru-dialectic-stackmix"
TROCR_ONNX  = "CherryJam/trocr-base-ru-dialectic-stackmix-onnx"

MODEL_DIR = Path("/models")


def download_trocr_torch(using_docker: bool):
    downloaded_model_path = snapshot_download(
        repo_id=TROCR_TORCH,
    )

    if using_docker:
        model_dir = MODEL_DIR / "trocr_pytorch"
        model_dir.mkdir(parents=True, exist_ok=True)
        
        if model_dir.exists():
            if model_dir.is_symlink():
                model_dir.unlink()
            else:
                shutil.rmtree(model_dir)

        shutil.copytree(
            src=downloaded_model_path,
            dst=model_dir
        )


def download_trocr_onnx(using_docker: bool):
    downloaded_model_path = snapshot_download(
        repo_id=TROCR_ONNX,
    )

    if using_docker:
        model_dir = MODEL_DIR / "trocr_onnx"
        model_dir.mkdir(parents=True, exist_ok=True)
        
        if model_dir.exists():
            if model_dir.is_symlink():
                model_dir.unlink()
            else:
                shutil.rmtree(model_dir)

        shutil.copytree(
            src=downloaded_model_path,
            dst=model_dir
        )


def download_yolo(using_docker: bool):
    downloaded_model_path = Path(
        hf_hub_download(
            repo_id=YOLO,
            filename="model.pt",
        )
    )

    if using_docker:
        model_dir = MODEL_DIR / "yolo"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = model_dir / downloaded_model_path.name

        shutil.copy(
            src=downloaded_model_path,
            dst=model_path
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "download_models",
        description="Script to download YOLO and TrOCR models"
    )

    parser.add_argument(
        "--yolo", action="store_true",
        help="Download YOLO model"
    )
    parser.add_argument(
        "--pytorch", action="store_true",
        help="Download TrOCR PyTorch model"
    )
    parser.add_argument(
        "--onnx", action="store_true",
        help="Download TrOCR ONNX model"
    )
    parser.add_argument(
        "--docker", action="store_true", 
        help="Run in \"Docker mode\", used in Dockerfile to copy models to /models"
    )

    args = parser.parse_args()

    if args.yolo:
        download_yolo(using_docker=args.docker)
    if args.pytorch:
        download_trocr_torch(using_docker=args.docker)
    if args.onnx:
        download_trocr_onnx(using_docker=args.docker)
