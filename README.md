# AI・チャットボット自動連携システム（POC）

このリポジトリには、LINE Webhook / Webフォームから受けた問い合わせを受信し、Gemini 3.6-flash を想定したナレッジ参照結果に応じて **自動返信** または **有人エスカレーション** を返す最小構成の Django POC を実装しています。

## エンドポイント

- `GET /`  
  POC の概要と利用可能なエンドポイントを返します。
- `POST /api/inquiries/line/`  
  LINE Messaging API 互換の簡易 Webhook です。
- `POST /api/inquiries/webform/`  
  Web フォームからの問い合わせ受付用エンドポイントです。

## ローカル実行

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## テスト

```bash
python manage.py test
```
