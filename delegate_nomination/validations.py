from django.core.exceptions import ValidationError

def validate_even(value):
    if value == 100:
        raise ValidationError('The value must be an even number.')


def validate_fee(value):
    if value == 100:
        raise ValidationError('The value must be an even number.')
