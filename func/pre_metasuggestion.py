import boto3
import io
import os
import uuid
import base64

#画像をエンコード
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# 使わない-S3クライアントの初期化
s3_client = boto3.client('s3', region_name='ap-southeast-2') 
S3_BUCKET_NAME = 'meta-suggestion'

# 使わない-課題ファイルをs3にアップロード
def save_image_to_s3(image_data):
    """
    画像データをS3にアップロードし、そのURLを返す関数
    
    :param image_data: バイナリ形式の画像データ
    :return: アップロードされた画像のS3 URL
    """
    output_filename = f"{uuid.uuid4()}.png"  # S3に保存するファイル名（Key）
    
    # S3にファイルをアップロード
    s3_client.upload_fileobj(io.BytesIO(image_data), S3_BUCKET_NAME, output_filename)
    
    # アップロードされた画像のS3 URLを作成
    s3_file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{output_filename}"
    print(f"画像がS3にアップロードされました: {s3_file_url}")
    return s3_file_url

# 課題ファイルとメタサジェスチョンファイルを読み取る共通関数
def load_task_and_questions():
    meta_suggestion = []

    # meta_suggestion.txtから質問一覧を読み込む
    with open('meta_suggestion.txt', 'r', encoding='utf-8') as f:
        meta_suggestion = f.readlines()
    return meta_suggestion

# 課題ファイルとメタサジェスチョンファイルを読み取る共通関数
def load_task_and_questions_2():
    meta_suggestion = []

    # meta_suggestion.txtから質問一覧を読み込む
    with open('meta_suggestion_2.txt', 'r', encoding='utf-8') as f:
        meta_suggestion = f.readlines()
    return meta_suggestion


# 課題ファイルとメタサジェスチョンファイルを読み取る共通関数
def load_task_and_questions_c1():
    meta_suggestion = []

    # meta_suggestion.txtから質問一覧を読み込む
    with open('meta_suggestion_c1.txt', 'r', encoding='utf-8') as f:
        meta_suggestion = f.readlines()
    return meta_suggestion
# 課題ファイルとメタサジェスチョンファイルを読み取る共通関数
def load_task_and_questions_c2():
    meta_suggestion = []

    # meta_suggestion.txtから質問一覧を読み込む
    with open('meta_suggestion_c2.txt', 'r', encoding='utf-8') as f:
        meta_suggestion = f.readlines()
    return meta_suggestion
# 課題ファイルとメタサジェスチョンファイルを読み取る共通関数
def load_task_and_questions_c3():
    meta_suggestion = []

    # meta_suggestion.txtから質問一覧を読み込む
    with open('meta_suggestion_c3.txt', 'r', encoding='utf-8') as f:
        meta_suggestion = f.readlines()
    return meta_suggestion
# 課題ファイルとメタサジェスチョンファイルを読み取る共通関数
def load_task_and_questions_c4():
    meta_suggestion = []

    # meta_suggestion.txtから質問一覧を読み込む
    with open('meta_suggestion_c4.txt', 'r', encoding='utf-8') as f:
        meta_suggestion = f.readlines()
    return meta_suggestion