from src.services.exceptions import ValidationException


def validate_user_input(username: str, password: str) -> None:
    errors = []

    if not username:
        errors.append("Username cannot be empty")
    elif not username.strip():
        errors.append("Username cannot be empty or contain only spaces")

    if not password:
        errors.append("Password cannot be empty")
    elif not password.strip():
        errors.append("Password cannot be empty or contain only spaces")

    if errors:
        error_message = "; ".join(errors)
        raise ValidationException(error_message)
