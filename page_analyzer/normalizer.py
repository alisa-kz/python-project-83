from urllib.parse import urlparse


def normalize(url_full):
    url_norm = urlparse(url_full)
    url = url_norm.scheme + "://" + url_norm.hostname
    return url
