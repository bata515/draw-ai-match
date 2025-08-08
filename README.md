# draw-ai-match

## Docker開発環境構築手順

### 環境構築

1. **リポジトリのクローン**
   ```bash
   git clone git@github.com:bata515/draw-ai-match.git
   cd draw-ai-match
   ```

2. **Docker環境の初回構築**
   ```bash
   # Dockerイメージをビルドしてコンテナを起動
   docker-compose up 
   ```

### 基本的なDocker操作

- **起動**
  ```bash
  docker-compose up 
  ```

- **停止**
  ```bash
  command + C # もしくはCtrl+Cで停止
  ```

- **コンテナへ接続**
  ```bash
  # コンテナ内のbashシェルに接続
  docker-compose exec demo-app bash
  ```

### 開発作業

1. **アプリケーションへのアクセス**
   - API: http://localhost:8000/hello
   - Swagger UI: http://localhost:8000/docs

2. **コードの変更とホットリロード**
   - `api/`ディレクトリ内のPythonファイルを編集すると、自動的にサーバーが再起動されます
   - ブラウザで変更を確認できます

3. **新しい依存関係の追加方法**
   ```bash
   # コンテナの起動
   docker-compose up
   
   # コンテナのbashシェルに接続
   docker exec -it コンテナ名 bash
   
   # パッケージを追加
   poetry add パッケージ名
   ```

4. **依存関係の削除**
   ```bash
   docker-compose exec demo-app poetry remove パッケージ名
   ```

### よく使うDockerコマンド

- **イメージビルドし直し**（キャッシュを使わずに再構築）
  ```bash
  docker-compose build --no-cache
  ```

- **コンテナの状態確認**
  ```bash
  docker ps -a
  ```

## テスト

### テストの実行

**全てのテストを実行:**
```bash
docker-compose exec demo-app poetry run pytest
```

**詳細な出力でテストを実行:**
```bash
docker-compose exec demo-app poetry run pytest -v
```

**特定のテストファイルを実行:**
```bash
docker-compose exec demo-app poetry run pytest tests/test_compare_images.py -v
```

### カバレッジの確認

**カバレッジ付きでテスト実行:**
```bash
docker-compose exec demo-app poetry run pytest --cov=api
```

**詳細なカバレッジレポートをHTML形式で生成:**
```bash
docker-compose exec demo-app poetry run pytest --cov=api --cov-report=html
```

**カバレッジレポート（ターミナル表示）:**
```bash
docker-compose exec demo-app poetry run pytest --cov=api --cov-report=term-missing
```

### プロジェクト構成

```
draw-ai-match/
├── api/                  # FastAPIアプリケーション
│   ├── __init__.py
│   ├── main.py           # メインのFastAPIアプリ
│   └── compare_images.py # 画像比較API実装
├── tests/                # テストファイル
│   ├── __init__.py
│   └── test_compare_images.py  # 画像比較APIのユニットテスト
├── docker-compose.yaml   # Docker Compose設定
├── Dockerfile            # Dockerイメージ定義
├── pyproject.toml        # Poetry設定・依存関係
├── poetry.lock           # 依存関係のロックファイル
└── README.md            
