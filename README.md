# README.md
# Registry Information System API

不動産登記情報管理システムのバックエンドAPI

## 機能

- 登記簿情報のPDFアップロードと処理
- 登記情報からの所有者情報抽出
- 住所からの郵便番号取得
- 顧客管理
- タスク管理
- レポート生成

## 技術スタック

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- OpenAI API
- Google Cloud Vision API
- Playwright

## セットアップ

### 前提条件

- Python 3.9以上
- PostgreSQL
- Redis (バックグラウンドタスク用)

### インストール

1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/registry-system.git
cd registry-system