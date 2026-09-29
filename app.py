import base64
import json
import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)


@app.route('/get_qr', methods=['GET'])
def get_qr():
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                ' (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'application/json, text/plain, */*',
        })

        # 1. Munkamenet kezdeti indítása a Xiaomi felé
        init_url = 'https://account.xiaomi.com/longPolling/loginUrl?_qrsize=240&qs=%3Fcallback%3Dhttps%253A%252F%252Fsts.api.io.mi.com%252Fsts%253Fsign%253DZ332228394%2526sid%3Dxiaomiio%26sid%3Dxiaomiio&_json=true'

        res = session.get(init_url, timeout=15)

        # Ellenőrizzük a válasz státuszkódját
        if res.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'Xiaomi szerver válaszkód: {res.status_code}',
            })

        # Válasz tisztítása
        text_resp = res.text.replace('&&START&&', '').strip()

        if not text_resp:
            return jsonify(
                {'success': False, 'error': 'Üres válasz érkezett a Xiaomitól.'}
            )

        data = json.loads(text_resp)

        qr_img_url = data.get('qr')
        login_url = data.get('lp')

        if not qr_img_url or not login_url:
            return jsonify({
                'success': False,
                'error': 'A QR kód adatai hiányoznak a válaszból.',
            })

        # 2. QR-kód kép letöltése
        img_res = session.get(qr_img_url, timeout=10)
        if img_res.status_code == 200:
            b64_img = base64.b64encode(img_res.content).decode('utf-8')
            return jsonify({
                'success': True,
                'qr_b64': f'data:image/png;base64,{b64_img}',
                'lp_url': login_url,
            })

        return jsonify(
            {'success': False, 'error': 'A QR kép letöltése sikertelen.'}
        )

    except json.JSONDecodeError:
        return jsonify({
            'success': False,
            'error': (
                'A Xiaomi szervere nem valid JSON formátumot küldött vissza.'
            ),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'Xiaomi QR Generator API'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
