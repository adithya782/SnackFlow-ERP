
from app import create_app, db

app = create_app()

with app.app_context():
    try:
        db.session.execute(db.text("SELECT 1"))
        print("PostgreSQL connection successful!")
    except Exception as e:
        print("Database connection failed:", e)
