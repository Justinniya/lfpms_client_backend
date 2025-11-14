from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from controllers.admin_controllers import admin_register_controller
from controllers.consultant_controllers import consultant_register_controller
from controllers.customer_controllers import customer_register_controller
from controllers.msme_controllers import msme_register_controller



app = Flask(__name__)
CORS(app,origins='*')
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'lfpms'
app.config['MYSQL_UNIX_SOCKET'] = '/opt/lampp/var/mysql/mysql.sock'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


def create_app(app):
    admin_register_controller(app)
    consultant_register_controller(app)
    customer_register_controller(app)
    msme_register_controller(app)

    mysql = MySQL(app)
    app.extensions['mysql'] = mysql

if __name__ == "__main__":
    create_app(app)
    app.run(debug=True)