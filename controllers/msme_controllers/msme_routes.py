from flask import Blueprint,current_app,request,jsonify,session
from datetime import datetime
import os
from werkzeug.utils import secure_filename

msme = Blueprint('msme',__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploaded_file')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'txt'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@msme.route('/')
def msme_index():
    return "welcome to msme Route"

@msme.route('/add_transaction',methods=['POST'])
def add_transaction():
    data = request.get_json()
    print("HAHAHA")
    user_id = data.get('user_id')
    products = data.get('product_id', [])
    quantities = data.get('quantity', [])
    total_prices = data.get('total_price', [])

    date = datetime.now().strftime('%Y-%m-%d')
    prefix = 'A'

    mysql = current_app.extensions['mysql']
    cur = mysql.connection.cursor()

    try:
        # Count today's transactions
        cur.execute("SELECT COUNT(*) FROM transactions WHERE DATE(transaction_date) = %s", (date,))
        transaction_count = cur.fetchone()[0] + 1

        transaction_id = f"{prefix}-{date}-{transaction_count}"

        total_quantity = sum(quantities)
        total_transaction_price = sum(total_prices)

        # Start transaction
        mysql.connection.begin()

        # Insert into transactions
        cur.execute("""
            INSERT INTO transactions (transaction_id, msme_id, user_id, quantity, total_price, transaction_date)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (transaction_id, session.get('id'), user_id, total_quantity, total_transaction_price))

        # Insert into purchases
        for i, product_id in enumerate(products):
            cur.execute("""
                INSERT INTO purchases (transaction_id, product_id, quantity, total_price)
                VALUES (%s, %s, %s, %s)
            """, (transaction_id, product_id, quantities[i], total_prices[i]))

        mysql.connection.commit()

        return jsonify({
            'status': 'success',
            'message': f'Transaction added successfully! Transaction ID: {transaction_id}'
        })

    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        cur.close()


@msme.route('/add_message',methods=['POST'])
def add_message():
    """
    Accepts multipart/form-data:
    - room_id
    - message
    - user_id
    - optional file
    Returns JSON:
    { username, message, file_url (or null), created_at }
    """
    mysql = current_app.extensions.get('mysql')
    if mysql is None:
        return jsonify({'error': 'MySQL not configured'}), 500

    room_id = request.form.get('room_id')
    message = request.form.get('message', '')
    user_id = request.form.get('user_id')

    if not room_id or not user_id:
        return jsonify({'error': 'Missing room_id or user_id'}), 400

    file_url = None
    file_path = None

    # handle file upload
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            if not allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
            # ensure upload directory exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(file.filename)
            # avoid overwrite: prefix timestamp
            timestamp_prefix = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
            filename_with_prefix = f"{timestamp_prefix}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename_with_prefix)
            file.save(file_path)
            # create web-accessible URL (Flask serves /static/)
            # if UPLOAD_FOLDER is inside 'static', prefix with '/'
            file_url = '/' + file_path.replace('\\', '/')

    cur = mysql.connection.cursor()
    try:
        # insert chat with timestamp
        cur.execute("""
            INSERT INTO chat (room_id, user_id, message, file_path, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (room_id, user_id, message, file_path))

        mysql.connection.commit()

        # fetch username (robust to tuple or dict)
        cur.execute("SELECT username FROM users WHERE userid = %s", (user_id,))
        row = cur.fetchone()
        username = None
        if row:
            # row may be tuple like (username,) or dict-like
            if isinstance(row, dict):
                username = row.get('username')
            else:
                username = row[0]

        if not username:
            username = 'Unknown'

        created_at = datetime.now().strftime("%b %d, %Y %I:%M %p")

        return jsonify({
            'username': username,
            'message': message,
            'file': file_url,         
            'created_at': created_at
        }), 201

    except Exception as exc:
        mysql.connection.rollback()
        current_app.logger.exception("Failed to add message")
        return jsonify({'error': str(exc)}), 500

    finally:
        try:
            cur.close()
        except Exception:
            pass