
import os
import sys

from app import create_app
from app.services.auth_service import create_user

app = create_app()

with app.app_context():
    name = os.getenv("ADMIN_NAME", "").strip()
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")

    if not name or not email or not password:
        print("ERROR: Admin environment variables are missing.")
        sys.exit(1)

    if len(password) < 8:
        print("ERROR: Admin password must be at least 8 characters.")
        sys.exit(1)

    try:
        admin = create_user(
            name=name,
            email=email,
            password=password,
            role="ADMIN"
        )

        print(f"SUCCESS: Admin account created: {admin.email}")

    except ValueError as error:
        print(f"ERROR: {error}")
        sys.exit(1)
