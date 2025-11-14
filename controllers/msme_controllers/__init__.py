from .msme_routes import msme


def msme_register_controller(app):
    app.register_blueprint(msme,url_prefix='/msme')