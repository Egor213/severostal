from src.services.exceptions import ValidationException


def validate_task_create(title: str, descr: str) -> None:
    errors = []

    if not title:
        errors.append("title cannot be empty")
    elif not title.strip():
        errors.append("title cannot be empty or contain only spaces")

    if errors:
        error_message = "; ".join(errors)
        raise ValidationException(error_message)
