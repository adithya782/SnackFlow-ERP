from getpass import getpass

from app import create_app
from app.services.auth_service import create_user

app = create_app()

with app.app_context():
    print("=== SnackFlow ERP | Initial Admin Setup ===")

    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password: ")
    confirm_password = getpass("Confirm password: ")

    if not name or not email or not password:
        print("All fields are required.")
    elif password != confirm_password:
        print("Passwords do not match.")
    elif len(password) < 8:
        print("Password must be at least 8 characters.")
    else:
        try:
            admin = create_user(
                name=name,
                email=email,
                password=password,
                role="ADMIN"
            )
            print(f"Admin account created successfully: {admin.email}")

        except ValueError as error:
            print(error)
