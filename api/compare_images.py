from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from torchvision.models import ResNet18_Weights
from PIL import Image
import sys
import pyheif
import pillow_heif


router = APIRouter()


@router.post("/compare/images")
async def compare_images(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...)
):
    
    try:
        img1 = load_image(image1).convert("RGB")
        img2 = load_image(image2).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="画像ファイルを開けませんでした")

    score = calculate_similarity(img1, img2)
    return JSONResponse(content={"similarity_score": round(score, 4)})

# 特徴量抽出モデル
model = models.resnet18(weights=ResNet18_Weights.DEFAULT)
model.eval()

# 前処理
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def load_image(upload: UploadFile) -> Image.Image:
        if upload.filename.lower().endswith('.heic'):
            heif_file = pyheif.read(upload.file.read())
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
        else:
            image = Image.open(upload.file)
        return image

# 画像から特徴ベクトルを取得
def get_features(image: Image.Image):

    # 前処理と特徴抽出
    tensor = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        features = model(tensor)
    return features.squeeze()

# 類似度を計算
def calculate_similarity(img1: Image.Image, img2: Image.Image):
    f1 = get_features(img1)
    f2 = get_features(img2)
    similarity = F.cosine_similarity(f1, f2, dim=0)
    return float(similarity)
