# Forex Local Visual（日本語）

言語: [English](README.en.md) | [中文](README.zh-CN.md) | 日本語

## 概要

Forex Local Visual は、為替・コモディティ・暗号資産データを収集して可視化する Django ベースのオープンソースプロジェクトです。

## 主な機能

- APScheduler による定期データ収集
- Django ORM と SQLite によるデータ保存
- pyecharts を使ったインタラクティブなチャート表示
- 拡張しやすいアプリ構成

## クイックスタート

1. 仮想環境を作成して有効化します。

```powershell
cd forex\forex
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. 依存関係をインストールします。

```powershell
pip install -r requirements.txt
```

3. 環境変数を設定します。

```powershell
Copy-Item .env.example .env
```

DJANGO_SECRET_KEY、DJANGO_DEBUG、DJANGO_ALLOWED_HOSTS を設定してください。

4. DB 初期化とサーバー起動を行います。

```powershell
python manage.py migrate
python manage.py runserver
```

アクセス先: http://127.0.0.1:8000/visual/

## コントリビュート

1. リポジトリを Fork します。
2. 機能ブランチを作成します。
3. プッシュ前にチェックを実行します。
4. 変更内容を明確にした Pull Request を作成します。

## セキュリティ

.env、ローカル DB、ログファイル、生成された CSV データはコミットしないでください。

## ライセンス

MIT ライセンスです。詳細は ../LICENSE を参照してください。
