# Forex Local Visual

為替・金・Bitcoin の収集と可視化を行う Django アプリです。v0.2.0 では合成データによるオフラインデモ、バッチ検証、トランザクションによる置換、クロスプラットフォーム CI を提供します。

Python 3.12 とリポジトリ内の .venv を使用してください。[README](../README.md) に macOS/Linux と Windows PowerShell の手順があります。外付け SSD で開発する場合は、インストール前に[ストレージ設定](macos-development.md)を行ってください。

専用の空の SQLite データベースを指定し、migrate、seed_demo、runserver の順に実行します。既存の市場データがある場合、seed_demo は書き込みを拒否します。デモ価格はすべて合成データです。

python scripts/verify.py はローカルの .env を読み込まず、一時データベースとネットワークを遮断したテストを使用します。

[データ契約](architecture.md)・[貢献ガイド](../CONTRIBUTING.md)・[リリース手順](releasing.md)・[今後の計画](roadmap.zh-CN.md)を参照してください。本アプリはローカル研究・学習向けです。コードは MIT ライセンスですが、実際の市場データは提供元の利用条件に従います。
