from .consultant_routes import consultant


def consultant_register_controller(app):
    app.register_blueprint(consultant,url_prefix='/consultant')