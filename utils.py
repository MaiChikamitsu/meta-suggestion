import base64
from PIL import Image
import io

def resize_image(image_path):
    """
    画像を指定したサイズにリサイズする関数。
    """
    img = Image.open(image_path)
    img = img.resize((300, int(img.height * (300 / img.width))))  # 幅300pxにリサイズ
    return img

def encode_image(image):
    """
    画像をBase64形式にエンコードする関数。
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return base64_image
