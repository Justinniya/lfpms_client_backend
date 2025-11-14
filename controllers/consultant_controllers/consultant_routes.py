from flask import Blueprint

consultant = Blueprint('consultant',__name__)

@consultant.route('/')
def consultant_index():
    return "welcome to consultant Route"