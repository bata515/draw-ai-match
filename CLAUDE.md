# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

このプロジェクトは画像の類似度比較を行うFastAPIアプリケーションです。深層学習を使用して2つの画像を受け取り、類似度スコアを返します。ResNet18による特徴抽出とコサイン類似度を使用しています。

## 開発環境

このプロジェクトはDockerとPoetryによる依存関係管理を使用しています。すべての開発作業はDockerコンテナ内で行ってください。

### 必須コマンド

**開発環境の起動:**
```bash
docker-compose up
```

**実行中のコンテナにアクセス:**
```bash
docker-compose exec demo-app bash
```

**新しい依存関係を追加:**
```bash
docker-compose exec demo-app poetry add パッケージ名
```

**依存関係を削除:**
```bash
docker-compose exec demo-app poetry remove パッケージ名
```

**ゼロからリビルド:**
```bash
docker-compose build --no-cache
```

### アプリケーションURL

- API ベース: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- メインエンドポイント: POST http://localhost:8000/api/compare/images

## アーキテクチャ

アプリケーションはモジュラーなFastAPI構造に従っています：

- `api/main.py`: メインのFastAPIアプリエントリーポイント、すべてのルーターを統合
- `api/compare_images.py`: ResNet18特徴抽出による画像比較機能
- PyTorch ResNet18（事前訓練済み）を特徴抽出に使用
- pyheif/pillow-heifライブラリを通じてHEIC形式をサポート
- 画像特徴間のコサイン類似度スコアを返す

## 主要な依存関係

- FastAPI: APIフレームワーク
- PyTorch + torchvision: 深層学習モデル
- PIL/Pillow: 画像処理
- pyheif/pillow-heif: HEIC画像サポート
- uvicorn: ASGIサーバー

## 開発時の注意事項

- ResNet18モデルはモジュールインポート時に一度ロードされ、メモリに保持されます
- 画像は一貫した特徴抽出のため自動的に224x224にリサイズされます
- 通常の画像形式とHEICの両方をサポートしています
- コンテナには開発用のホットリロードが有効になっています