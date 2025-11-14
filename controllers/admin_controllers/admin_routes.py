from flask import Blueprint,request

admin = Blueprint('admin',__name__)

@admin.route('/')
def admin_index():
    data = request.args.get('user')
    print(data)
    return f"welcome to admin {data}"