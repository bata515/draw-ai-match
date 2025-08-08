import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, UploadFile
from fastapi.testclient import TestClient
from PIL import Image
import torch
import io

from api.compare_images import (
    compare_images, 
    load_image, 
    get_features, 
    calculate_similarity,
    router
)
from api.main import app

client = TestClient(app)


class TestLoadImage:
    def test_load_image_jpg(self):
        # JPG画像のテスト用ファイルを作成
        test_image = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        # UploadFileのモック作成
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "test.jpg"
        upload_file.file = img_bytes
        
        # 関数をテスト
        result = load_image(upload_file)
        
        assert isinstance(result, Image.Image)
        assert result.size == (100, 100)

    def test_load_image_png(self):
        # PNG画像のテスト用ファイルを作成
        test_image = Image.new('RGBA', (50, 50), color='blue')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "test.png"
        upload_file.file = img_bytes
        
        result = load_image(upload_file)
        
        assert isinstance(result, Image.Image)
        assert result.size == (50, 50)

    @patch('api.compare_images.pyheif')
    def test_load_image_heic(self, mock_pyheif):
        # HEICファイルのモック設定
        mock_heif_file = Mock()
        mock_heif_file.mode = 'RGB'
        mock_heif_file.size = (200, 200)
        mock_heif_file.data = b'fake_image_data' * 40000  # 200*200*3相当のデータ
        mock_heif_file.stride = 600  # 200 * 3 (RGB)
        mock_pyheif.read.return_value = mock_heif_file
        
        # UploadFileモックの修正
        mock_file = Mock()
        mock_file.read.return_value = b'fake_heic_data'
        
        upload_file = Mock(spec=UploadFile)
        upload_file.filename = "test.heic"
        upload_file.file = mock_file
        
        with patch('api.compare_images.Image.frombytes') as mock_frombytes:
            mock_image = Mock(spec=Image.Image)
            mock_frombytes.return_value = mock_image
            
            result = load_image(upload_file)
            
            assert result == mock_image
            mock_pyheif.read.assert_called_once()


class TestGetFeatures:
    @patch('api.compare_images.model')
    @patch('api.compare_images.preprocess')
    def test_get_features(self, mock_preprocess, mock_model):
        # モック設定
        test_image = Image.new('RGB', (224, 224), color='green')
        mock_tensor = torch.randn(3, 224, 224)
        mock_features = torch.randn(1, 1000)
        
        mock_preprocess.return_value = mock_tensor
        mock_model.return_value = mock_features
        
        # 関数をテスト
        result = get_features(test_image)
        
        # モックが正しく呼ばれたかチェック
        mock_preprocess.assert_called_once_with(test_image)
        mock_model.assert_called_once()
        
        # 結果のチェック
        assert isinstance(result, torch.Tensor)
        assert result.shape == (1000,)  # squeeze()後のshape


class TestCalculateSimilarity:
    @patch('api.compare_images.get_features')
    def test_calculate_similarity_identical(self, mock_get_features):
        # テスト用の画像
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')
        
        # 同一の特徴ベクトル（類似度1.0になる）
        feature_vector = torch.tensor([1.0, 0.0, 0.0])
        mock_get_features.side_effect = [feature_vector, feature_vector]
        
        result = calculate_similarity(img1, img2)
        
        # 結果の検証
        assert isinstance(result, float)
        assert result == 1.0  # 同じ特徴ベクトル同士なので類似度は1.0
        assert mock_get_features.call_count == 2

    @patch('api.compare_images.get_features')
    def test_calculate_similarity_orthogonal(self, mock_get_features):
        # テスト用の画像
        img1 = Image.new('RGB', (100, 100), color='red')
        img2 = Image.new('RGB', (100, 100), color='blue')
        
        # 直交する特徴ベクトル（類似度0.0になる）
        feature1 = torch.tensor([1.0, 0.0, 0.0])
        feature2 = torch.tensor([0.0, 1.0, 0.0])
        mock_get_features.side_effect = [feature1, feature2]
        
        result = calculate_similarity(img1, img2)
        
        # 結果の検証
        assert isinstance(result, float)
        assert result == 0.0  # 直交ベクトル同士なので類似度は0.0


class TestCompareImagesAPI:
    @pytest.mark.asyncio
    async def test_compare_images_success(self):
        # テスト用画像データの作成
        test_image1 = Image.new('RGB', (100, 100), color='red')
        test_image2 = Image.new('RGB', (100, 100), color='blue')
        
        img1_bytes = io.BytesIO()
        img2_bytes = io.BytesIO()
        test_image1.save(img1_bytes, format='JPEG')
        test_image2.save(img2_bytes, format='JPEG')
        img1_bytes.seek(0)
        img2_bytes.seek(0)
        
        # UploadFileモックの作成
        upload1 = Mock(spec=UploadFile)
        upload1.filename = "test1.jpg"
        upload1.file = img1_bytes
        
        upload2 = Mock(spec=UploadFile)
        upload2.filename = "test2.jpg"
        upload2.file = img2_bytes
        
        with patch('api.compare_images.calculate_similarity') as mock_calc_sim:
            mock_calc_sim.return_value = 0.8542
            
            response = await compare_images(upload1, upload2)
            
            # レスポンスの検証
            assert response.status_code == 200
            content = response.body.decode()
            assert '0.8542' in content
            assert 'similarity_score' in content

    @pytest.mark.asyncio
    async def test_compare_images_invalid_file(self):
        # 無効なファイルのモック
        upload1 = Mock(spec=UploadFile)
        upload1.filename = "invalid.txt"
        upload1.file = io.BytesIO(b"not an image")
        
        upload2 = Mock(spec=UploadFile)
        upload2.filename = "test.jpg"
        upload2.file = io.BytesIO(b"also not an image")
        
        # 例外が発生することをテスト
        with pytest.raises(HTTPException) as exc_info:
            await compare_images(upload1, upload2)
        
        assert exc_info.value.status_code == 400
        assert "画像ファイルを開けませんでした" in str(exc_info.value.detail)


class TestAPIIntegration:
    def test_compare_images_endpoint_with_valid_images(self):
        # 実際のテスト画像を作成
        test_image1 = Image.new('RGB', (100, 100), color='red')
        test_image2 = Image.new('RGB', (100, 100), color='blue')
        
        img1_bytes = io.BytesIO()
        img2_bytes = io.BytesIO()
        test_image1.save(img1_bytes, format='JPEG')
        test_image2.save(img2_bytes, format='JPEG')
        img1_bytes.seek(0)
        img2_bytes.seek(0)
        
        with patch('api.compare_images.calculate_similarity') as mock_calc_sim:
            mock_calc_sim.return_value = 0.75
            
            response = client.post(
                "/api/compare/images",
                files={
                    "image1": ("test1.jpg", img1_bytes, "image/jpeg"),
                    "image2": ("test2.jpg", img2_bytes, "image/jpeg")
                }
            )
            
            assert response.status_code == 200
            json_response = response.json()
            assert "similarity_score" in json_response
            assert json_response["similarity_score"] == 0.75

    def test_compare_images_endpoint_with_invalid_file(self):
        # 無効なファイルでテスト
        invalid_file = io.BytesIO(b"not an image")
        
        response = client.post(
            "/api/compare/images",
            files={
                "image1": ("test1.txt", invalid_file, "text/plain"),
                "image2": ("test2.txt", io.BytesIO(b"also not an image"), "text/plain")
            }
        )
        
        assert response.status_code == 400
        json_response = response.json()
        assert "画像ファイルを開けませんでした" in json_response["detail"]