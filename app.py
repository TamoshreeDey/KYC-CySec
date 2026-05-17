# app.py
import sys
import os
from flask import Flask, jsonify
from flask_cors import CORS

# Points to AdavncePython/backend/ — which directly contains 'routes/'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

def create_app():
    app = Flask(__name__)
    CORS(app)

    from routes.submitkyc import kyc_app          # ← removed 'backend.'
    from routes.retrivekyc import kyc_retrive
    app.register_blueprint(kyc_app, url_prefix='/api/kyc')
    app.register_blueprint(kyc_retrive, url_prefix='/api/kyc')

    @app.route('/health')
    def health():
        from config import client
        try:
            client.admin.command('ping')
            return jsonify({"status": "ok", "db": "connected"}), 200
        except Exception as e:
            return jsonify({"status": "error", "db": str(e)}), 503

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)