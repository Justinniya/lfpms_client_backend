from .admin_routes import admin


def admin_register_controller(app):
    app.register_blueprint(admin,url_prefix="/admin")