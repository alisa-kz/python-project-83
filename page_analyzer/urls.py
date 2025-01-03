from urllib.parse import urlparse

import validators


def validate(url):
    errors = {}
    if len(url) > 255:
        errors["big_len"] = "Адрес сайта не должен превышать 255 символов"
    if not validators.url(url):
        errors["not_valid"] = "Неправильный адрес"
    return errors


def normalize(url_full):
    url_norm = urlparse(url_full)
    url = url_norm.scheme + "://" + url_norm.hostname
    return url
