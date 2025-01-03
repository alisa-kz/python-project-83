from datetime import datetime

from bs4 import BeautifulSoup


def data_build(response, id):
    bs = BeautifulSoup(response.text, 'html.parser')

    check_data = {
        'url_id': id,
        'code': response.status_code,
        'h1': bs.h1.string if bs.h1 else None,
        'title': bs.title.string if bs.title else None,
        'content': None,
        'ch_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    description_meta = bs.find('meta', {"name": 'description'}).get('content')
    if description_meta:
        check_data['content'] = description_meta
    return check_data
