from datetime import datetime

from bs4 import BeautifulSoup


def data_build(response, id):
    check_data = {}
    check_data['url_id'] = id
    code = response.status_code
    check_data['code'] = code
    bs = BeautifulSoup(response.text, 'html.parser')
    h1 = bs.h1.string
    check_data['h1'] = h1
    title = bs.title.string
    check_data['title'] = title
    metas = bs.find_all('meta')
    for meta in metas:
        if meta.get('name') == 'description':
            content = meta['content']
            check_data['content'] = content
            break
        else:
            check_data['content'] = None
    ch_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    check_data['ch_date'] = ch_date
    return check_data
