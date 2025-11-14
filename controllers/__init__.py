from .admin_controllers import admin
from .customer_controllers import customer
from .consultant_controllers import consultant
from .msme_controllers import msme


def register_controller(app):
    app.register_blueprint(admin)
    app.register_blueprint(consultant)
    app.register_blueprint(customer)
    app.register_blueprint(msme)
