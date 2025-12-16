from flask import Flask, request, send_file
import requests
from io import BytesIO
from PIL import Image

app = Flask(__name__)

fadai = "https://freefire.samsedrain.com.np/api/v1/profileboard/"
API_KEY = "CTX-TEAM"
DEFAULT_AVATAR = 102000000
DEFAULT_BANNER = 901000000

@app.route('/')
def home():
    return "API is running! Use /xProFiLe endpoint"

@app.route('/xProFiLe', methods=['GET'])
def get_profile_image_tiny():
    try:
        uid = request.args.get('uid')
        key = request.args.get('KEY')

        if not uid or not key:
            return 'Error => Missing UID or KEY!', 400

        if key != API_KEY:
            return 'Error => Invalid KEY!', 403

        info_url = f"https://info-ob49.vercel.app/api/account/?uid={uid}&region=sg"
        response = requests.get(info_url)
        if response.status_code != 200:
            return 'Error => Cannot fetch player info!', 400

        data = response.json()
        basic = data.get("basicInfo", {})

        nickname = basic.get("nickname", f"Player_{uid}")
        level = basic.get("level", 1)
        avatarId = basic.get("profileInfo", {}).get("avatarId") or basic.get("headPic", DEFAULT_AVATAR)
        bannerId = basic.get("bannerId", DEFAULT_BANNER)

        profileboard_params = {
            'password': 'K180726733',
            'name': nickname,
            'level': int(level),
            'banner': bannerId,
            'avatar': avatarId
        }

        img_response = requests.get(fadai, params=profileboard_params)
        if img_response.status_code != 200:
            return 'Error => Cannot create image!', 400
        original_img = Image.open(BytesIO(img_response.content))
        
        TINY_WIDTH = 730
        TINY_HEIGHT = 155 

        original_width, original_height = original_img.size
        original_ratio = original_width / original_height
        
        if original_ratio > (TINY_WIDTH / TINY_HEIGHT):
            new_width = TINY_WIDTH
            new_height = int(TINY_WIDTH / original_ratio)
        else:
            new_height = TINY_HEIGHT
            new_width = int(TINY_HEIGHT * original_ratio)

        resized_img = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        final_img = Image.new('RGB', (TINY_WIDTH, TINY_HEIGHT), (0, 0, 0))

        x_offset = (TINY_WIDTH - new_width) // 2
        y_offset = (TINY_HEIGHT - new_height) // 2
        
        final_img.paste(resized_img, (x_offset, y_offset))

        output = BytesIO()
        final_img.save(output, format='PNG', quality=95)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='image/png',
            as_attachment=False,
            download_name=f'{nickname}_profile_tiny_{TINY_WIDTH}x{TINY_HEIGHT}.png'
        )

    except Exception as e:
        return f'Error => System! ({str(e)})', 500

if __name__ == '__main__':
    app.run(debug=False)
