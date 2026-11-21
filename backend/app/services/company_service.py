from app import db
from app.models.company_settings import CompanySettings


def get_company_settings():
    return CompanySettings.query.first()


def create_company_settings(data):
    # Only one manufacturer per ERP installation
    existing = get_company_settings()

    if existing:
        raise ValueError(
            "Company settings already exist. Update them instead."
        )

    business_name = data.get("business_name")
    state = data.get("state")

    if not business_name or not business_name.strip():
        raise ValueError("Business name is required.")

    if not state or not state.strip():
        raise ValueError("Registered state is required.")

    company = CompanySettings(
        business_name=business_name.strip(),
        gstin=data.get("gstin") or None,
        address=data.get("address"),
        city=data.get("city"),
        state=state.strip(),
        pincode=data.get("pincode"),
        phone=data.get("phone"),
        email=data.get("email")
    )

    db.session.add(company)
    db.session.flush()

    return company


def update_company_settings(company, data):
    allowed_fields = [
        "business_name",
        "gstin",
        "address",
        "city",
        "state",
        "pincode",
        "phone",
        "email"
    ]

    for field in allowed_fields:
        if field in data:
            value = data[field]

            if field in ["business_name", "state"]:
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"{field} cannot be empty.")
                value = value.strip()

            if field == "gstin" and value == "":
                value = None

            setattr(company, field, value)

    db.session.flush()

    return company
