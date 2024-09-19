from flask import Flask, render_template, request, url_for
from bridging_teaching import bridging_teaching_mode  # 橋渡教示ありモードの関数をインポート
from no_bridging_teaching import no_bridging_teaching_mode  # 橋渡教示なしモードの関数をインポート
from co_working import co_working_mode  # 自由共同モードの関数をインポート
import os
from dotenv import load_dotenv
from openai import OpenAI
import boto3
import io

load_dotenv()
client = OpenAI(api_key=os.environ.get('OPENAI_API'))

app = Flask(__name__)

# S3クライアントの初期化
s3_client = boto3.client('s3', region_name='ap-southeast-2') 
S3_BUCKET_NAME = 'meta-suggestion'

# 課題ファイルをs3にアップロード
def save_image_to_s3(image_data):
    """
    画像データをS3にアップロードし、そのURLを返す関数
    
    :param image_data: バイナリ形式の画像データ
    :return: アップロードされた画像のS3 URL
    """
    output_filename = "question.png"  # S3に保存するファイル名（Key）
    
    # S3にファイルをアップロード
    s3_client.upload_fileobj(io.BytesIO(image_data), S3_BUCKET_NAME, output_filename)
    
    # アップロードされた画像のS3 URLを作成
    s3_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{output_filename}"
    print(f"画像がS3にアップロードされました: {s3_file_url}")
    return s3_file_url

# 課題ファイルとメタサジェスチョンファイルを読み取る共通関数
def load_task_and_questions():
    image_file = 'question.png'
    meta_suggestion = []

    # meta_suggestion.txtから質問一覧を読み込む
    with open('meta_suggestion.txt', 'r', encoding='utf-8') as f:
        meta_suggestion = f.readlines()

    # 画像をバイナリとして読み込む
    with open(image_file, 'rb') as f:
        image_data = f.read()

    print(f"meta_suggestion: {meta_suggestion}, Image Data Length: {len(image_data)}")
    return meta_suggestion, image_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    mode = request.form['mode']
    user_input = request.form.get('user_input', '')  # ユーザー発言を取得

    # モードに応じて処理を分岐
    if mode == 'bridging_teaching':
        # 橋渡教示ありモードの処理
        meta_suggestion, image_data = load_task_and_questions()  # 画像データを読み取る
        image_url = save_image_to_s3(image_data)  # 画像をS3にアップロード
        prompt = bridging_teaching_mode(meta_suggestion, user_input)
        
        # GPTにプロンプトと画像URLを送信
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
        )
        # GPTからの応答を取得
        result = response.choices[0].message.content
        
    elif mode == 'co_working':
        # 自由共同モードの処理（画像も送信）
        meta_suggestion, image_data = load_task_and_questions()  # 画像データを読み取る
        image_url = save_image_to_s3(image_data)  # 画像をS3にアップロード
        prompt = co_working_mode(user_input)

        # GPTにプロンプトと画像URLを送信
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
        )
        # GPTからの応答を取得
        result = response.choices[0].message.content

    elif mode == 'no_bridging_teaching':
        # 橋渡教示なしモードの処理（画像を送信しない）
        meta_suggestion, _ = load_task_and_questions()  # 画像データは無視
        result = no_bridging_teaching_mode(meta_suggestion)

    else:
        return "Invalid mode selected.", 400


    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
