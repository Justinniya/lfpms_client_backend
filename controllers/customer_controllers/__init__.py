from .customer_routes import customer


def customer_register_controller(app):
    app.register_blueprint(customer)