# meta-suggestion

AI を活用したメタ学習支援ツール「meta-suggestion」は、研究者や学生が効率的に学習や研究を進めるためのプロンプト生成や情報整理を支援します。

## 📁 ディレクトリ構成

```
meta-suggestion/
├── app.py                     # アプリケーションのメインスクリプト
├── func/                      # 各種機能を実装したモジュール群
├── prompt/                    # プロンプトテンプレートや関連ファイル
├── sota-json-converter/      # SOTA（State of the Art）情報の JSON 変換ツール
├── templates/                 # HTML テンプレートなどのフロントエンド関連ファイル
├── meta_suggestion_*.txt      # メタサジェストのサンプルデータ
├── question_*.png             # クイズ・質問関連の画像
└── requirements.txt          # 必要なPythonライブラリ一覧
```

## ⚙️ セットアップ手順

1. このリポジトリをクローンします：

```bash
git clone https://github.com/MaiChikamitsu/meta-suggestion.git
cd meta-suggestion
```

2. Python の依存パッケージをインストールします：

```bash
pip install -r requirements.txt
```

3. `.env` ファイルを作成し、OpenAI API キーなどの必要な環境変数を記述します。

4. アプリケーションを起動します：

## 🧪 機能概要

- メタ学習用プロンプトの自動生成  
- 学習に役立つ State-of-the-Art 情報の取得と整形  
- クイズ形式での知識習得支援  
- 自動回答補助や要約生成（OpenAI API 活用）

## 💻 技術スタック

- 言語: Python 3.8+
- フレームワーク: Flask
- API: OpenAI API
- 構成管理: `.env`, `requirements.txt`

## 📄 ライセンス

このプロジェクトは MIT License のもとで公開されています。

## 🙌 貢献

順次リファクタリングしています
