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

3. **新しい依存関係の追加**
   ```bash
   # コンテナ内でPoetryを使用してパッケージを追加
   docker-compose exec demo-app poetry add パッケージ名 bash
   
   # 例：requestsライブラリを追加
   docker-compose exec demo-app poetry add requests bash
   
   # 開発用パッケージを追加
   docker-compose exec demo-app poetry add --group dev pytest
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

### プロジェクト構成

```
draw-ai-match/
├── api/                  # FastAPIアプリケーション
│   ├── __init__.py
│   └── main.py           # API実装ファイル
├── docker-compose.yaml   # Docker Compose設定
├── Dockerfile            # Dockerイメージ定義
├── pyproject.toml        # Poetry設定・依存関係
├── poetry.lock           # 依存関係のロックファイル
└── README.md            
