"""Invoice App."""
from flask import Flask

from invoiceapp import invoice


def create_app(config_object="invoiceapp.settings"):
    """Create application factory."""
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    app.register_blueprint(invoice.blueprint)
    return app
