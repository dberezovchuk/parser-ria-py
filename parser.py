import requests
from bs4 import BeautifulSoup
import csv


URL = 'https://auto.ria.com/moto/tricikl/?page=1'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0', 'accept': '*/*'}
FILE = 'cars.csv'

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='page-item mhide')
    if pagination:
        return int(pagination[-1].get_text(strip=True).replace(' ', ''))
    else:
        return 1



def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='content')

    cars = []
    for item in items:
        uah_price = item.find('span', class_='i-block')
        if uah_price:
            uah_price = uah_price.get_text().replace('\xa0', ' ')
        else:
            uah_price = 'Нет цены'
        cars.append({
            'title': item.find('span', class_='blue bold').get_text(),
            'link': item.find('a', class_='address').get('href'),
            'usd_price': item.find('span', class_='bold green size22').get_text(strip=True),
            'uah_price': uah_price,
            'city': item.find('li', class_='item-char view-location').get_text(strip=True),
        })
    return cars


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Марка', 'Ссылка', 'Цена в $', 'Цена в UAH', 'Город'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['usd_price'], item['uah_price'], item['city']])


def parse():
    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            cars.extend(get_content(html.text))
        save_file(cars, FILE)
        print(f'Получено {len(cars)} автомобилей')
    else:
        print('Error')

parse()