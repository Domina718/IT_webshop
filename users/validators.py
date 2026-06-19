from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex = r'^\+?[0-9\s\-]+$',
    message = 'Enter a valid phone number.'
)

postal_code_validator = RegexValidator(
    regex = r'^[0-9]{4,5}$',
    message = 'Enter a valid postal code.'
)

text_validator = RegexValidator(
    regex = r'^[a-zA-Z\s\-]+$',
    message = 'Only letters are allowed.'
)