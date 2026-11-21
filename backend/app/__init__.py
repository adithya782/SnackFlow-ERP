from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate # type: ignore
from flask_cors import CORS
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config.from_object("app.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    from app import models

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "success",
            "message": "SnackFlow ERP backend is running!"
        }), 200

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.items import items_bp
    app.register_blueprint(items_bp)

    from app.routes.customers import customers_bp
    app.register_blueprint(customers_bp)

    from app.routes.suppliers import suppliers_bp
    app.register_blueprint(suppliers_bp)

    from app.routes.inventory import inventory_bp
    app.register_blueprint(inventory_bp)

    from app.routes.purchases import purchases_bp
    app.register_blueprint(purchases_bp)

    from app.routes.boms import boms_bp
    app.register_blueprint(boms_bp)

    from app.routes.production import production_bp
    app.register_blueprint(production_bp)

    from app.routes.sales_orders import sales_orders_bp
    app.register_blueprint(sales_orders_bp)

    from app.routes.company import company_bp
    app.register_blueprint(company_bp)

    from app.routes.invoices import invoices_bp
    app.register_blueprint(invoices_bp)

    from app.routes.dispatches import dispatches_bp
    app.register_blueprint(dispatches_bp)

    from app.routes.payments import payments_bp
    app.register_blueprint(payments_bp)

    from app.routes.audit_logs import audit_logs_bp
    app.register_blueprint(audit_logs_bp)

    from app.routes.reports import reports_bp
    app.register_blueprint(reports_bp)
    
    return app
