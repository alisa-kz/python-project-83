import validators


def validate(url):
    errors = {}
    if len(url) > 255:
        errors["big_len"] = "Адрес сайта не должен превышать 255 символов"
    if not validators.url(url):
        errors["not_valid"] = "Неправильный адрес"
    return errors
