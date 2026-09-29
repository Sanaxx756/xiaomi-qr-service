import base64
import os
from flask import Flask, jsonify

# A hivatalos micloud csomag a MiCloud osztályt használja
try:
    from micloud import MiCloud as MiAccount
except ImportError:
    try:
        from micloud.micloud import MiCloud as MiAccount
    except ImportError:
        from micloud.miaccount import MiAccount

app = Flask(__name__)


@app.route('/get_qr', methods=['GET'])
def get_qr():
    try:
        account = MiAccount()
        qr_data = account.get_qr_code()

        qr_path = qr_data.get('qr_image_path')
        if qr_path and os.path.exists(qr_path):
            with open(qr_path, 'rb') as f:
                b64_img = base64.b64encode(f.read()).decode('utf-8')

            return jsonify({
                'success': True,
                'qr_b64': f'data:image/png;base64,{b64_img}',
                'lp_url': qr_data.get('login_url'),
            })
        return jsonify({
            'success': False,
            'error': 'Nem jött létre a QR kép fájl.',
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'Xiaomi QR Generator API'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
