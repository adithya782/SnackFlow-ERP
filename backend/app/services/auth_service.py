from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models.user import User


def create_user(name, email, password, role):
    """Create a user with a securely hashed password."""

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        raise ValueError("A user with this email already exists.")

    user = User(
        name=name,
        email=email.lower().strip(),
        password_hash=generate_password_hash(password),
        role=role.upper(),
        is_active=True
    )

    db.session.add(user)
    db.session.commit()

    return user


def authenticate_user(email, password):
    """Verify credentials and return the user."""

    user = User.query.filter_by(email=email.lower().strip()).first()

    if not user:
        return None

    if not user.is_active:
        return None

    if not check_password_hash(user.password_hash, password):
        return None

    return user
