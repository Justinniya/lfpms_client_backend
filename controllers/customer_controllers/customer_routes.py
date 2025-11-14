from flask import Blueprint,request,jsonify,current_app

customer = Blueprint('customer',__name__)

@customer.route('/')
def customer_index():
    return "welcome to customer Route <a href='http://localhost/client_project/index.php'>start</a>"


@customer.route('/scanResult')
def scanResult():
    transaction_id = request.args.get('Id')
    print(transaction_id)
    
    if not transaction_id:
        return jsonify({'error': 'Transaction ID not specified'}), 400

    try:
        mysql = current_app.extensions['mysql']
        conn = mysql.connection
        cursor = conn.cursor()

        # Fetch transaction
        cursor.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
        transaction = cursor.fetchone()

        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404

        # Insert scan record
        cursor.execute("INSERT INTO qr_scans (transaction_id, ReviewStat) VALUES (%s, '0')", (transaction_id,))
        conn.commit()

        # Fetch purchases with product details
        cursor.execute("""
            SELECT p.product_id, p.productName, pr.quantity, pr.total_price
            FROM purchases pr
            JOIN products p ON p.product_id = pr.product_id
            WHERE pr.transaction_id = %s
        """, (transaction_id,))
        purchases = cursor.fetchall()

        total_quantity = sum(row['quantity'] for row in purchases)
        total_amount = sum(row['total_price'] for row in purchases)

        return jsonify({
            'transaction': transaction,
            'purchases': purchases,
            'total_quantity': total_quantity,
            'total_amount': total_amount
        })

    except Exception as e:
        current_app.logger.error(f"Error fetching transaction: {e}")
        return jsonify({'error': str(e)}), 500