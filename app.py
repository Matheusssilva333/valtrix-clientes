import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Sale, Affiliate
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///valtrix.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'valtrix-secret-key-123')

db.init_app(app)

# Initialize Database
with app.app_context():
    db.create_all()

# Helper: Robust Roblox Proxy
def roblox_proxy_request(target_url, method, headers, data=None):
    try:
        parsed_url = urlparse(target_url)
        if not parsed_url.hostname or not parsed_url.hostname.endswith('roblox.com'):
            return {"error": "Forbidden: Only Roblox domains are allowed"}, 403

        # Filter and clean headers
        safe_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = requests.request(
            method=method,
            url=target_url,
            headers=safe_headers,
            json=data if method in ['POST', 'PUT', 'PATCH'] else None,
            allow_redirects=True,
            timeout=10
        )

        return response.content, response.status_code, {"Content-Type": response.headers.get('Content-Type', 'application/json')}
    except Exception as e:
        return {"error": "Proxy Failure", "details": str(e)}, 500

@app.route('/api/proxy', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({"error": "Missing url parameter"}), 400

    content, status, headers = roblox_proxy_request(
        target_url, 
        request.method, 
        request.headers, 
        request.get_json(silent=True)
    )
    
    return content, status, headers

@app.route('/api/db', methods=['GET'])
def get_db_status():
    # Simulate the legacy structure for compatibility if needed, 
    # or return real stats.
    users = User.query.all()
    sales = Sale.query.all()
    affiliates = Affiliate.query.all()
    
    return jsonify({
        "users": [u.id for u in users],
        "sales_count": len(sales),
        "affiliates": [a.code for a in affiliates],
        "status": "online",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/save', methods=['POST'])
def save_data():
    try:
        payload = request.get_json()
        collection = payload.get('collection')
        data = payload.get('data')

        if collection == 'users':
            user = User.query.filter_by(roblox_id=str(data.get('uid'))).first()
            if not user:
                user = User(
                    roblox_id=str(data.get('uid')),
                    username=data.get('username'),
                    display_name=data.get('displayName'),
                    avatar_url=data.get('avatarUrl')
                )
                db.session.add(user)
                db.session.commit()
            return jsonify({"success": True, "user_id": user.id})

        return jsonify({"error": "Collection not supported"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/affiliate', methods=['POST'])
def handle_affiliate():
    try:
        data = request.get_json()
        action = data.get('action')

        if action == 'create_session':
            token = f"session_{int(datetime.utcnow().timestamp())}"
            new_sale = Sale(
                token=token,
                code=data.get('code'),
                item_id=data.get('item_id'),
                item_name=data.get('item_name'),
                item_price=float(data.get('item_price', 0))
            )
            db.session.add(new_sale)
            db.session.commit()
            return jsonify({"token": token})

        if action == 'confirm_purchase':
            token = data.get('token')
            buyer_uid = str(data.get('buyer_uid'))
            sale = Sale.query.filter_by(token=token).first()
            
            if not sale:
                return jsonify({"ok": False, "reason": "Session not found"}), 404

            # --- Senior Implementation: Real Inventory Verification ---
            # We check if the user actually owns the item on Roblox
            # Asset types: 1=Image, 2=T-Shirt, 8=Hat, 11=Shirt, 12=Pants, etc.
            # Usually these are Shirt (11) or Pants (12) or T-Shirt (2)
            
            asset_id = sale.item_id
            verified = False
            
            # Check different asset types if unknown
            for asset_type in ['Shirt', 'Pants', 'TShirt', 'Asset']:
                try:
                    inv_url = f"https://inventory.roblox.com/v1/users/{buyer_uid}/items/{asset_type}/{asset_id}"
                    # Use the proxy logic to fetch
                    resp = requests.get(inv_url, timeout=5)
                    if resp.status_code == 200:
                        inv_data = resp.json()
                        if inv_data.get('data') and len(inv_data['data']) > 0:
                            verified = True
                            break
                except:
                    continue

            if not verified:
                # Fallback: Maybe the inventory is private?
                # In a real "senior" app, we might check if inventory is public first
                return jsonify({"ok": False, "reason": "item_not_found_or_private"}), 200

            sale.status = 'confirmed'
            sale.buyer_uid = buyer_uid
            sale.confirmed_at = datetime.utcnow()
            
            # Update affiliate stats
            aff = Affiliate.query.filter_by(code=sale.code).first()
            if not aff:
                # Auto-create affiliate if it doesn't exist for this code
                aff = Affiliate(code=sale.code)
                db.session.add(aff)
            
            aff.total_sales += 1
            aff.total_commission += (sale.item_price * 0.1) # 10% commission
            
            db.session.commit()
            return jsonify({"ok": True, "commission": f"{(sale.item_price * 0.1):.2f}"})

        return jsonify({"error": "Invalid action"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve Frontend
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
