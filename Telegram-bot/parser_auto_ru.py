import requests
from bs4 import BeautifulSoup
from random import random
import csv
from time import sleep



URL_CRYSLER = "https://auto.ru/moskva/cars/chrysler/all/"
PARSE_METHOD_CRYSLER = {'title.a': 'ListingItemTitle-module__link',
                        'title.get_text': '',
                        'price.div': 'ListingItemPrice-module__content',
                        'price.get_text': '',
                        'city.span': 'MetroListPlace__regionName',
                        'city.get_text': '',
                        }

URL_SUBARU = "https://auto.ru/moskva/cars/subaru/all/"
PARSE_METHOD_SUBARU = {'title.a': 'ListingItemTitle-module__link',
                        'title.get_text': '',
                        'price.div': 'ListingItemPrice-module__content',
                        'price.get_text': '',
                        'city.span': 'MetroListPlace__regionName',
                        'city.get_text': '',
                        }

URL_MINI = "https://auto.ru/moskva/cars/mini/all/"
PARSE_METHOD_MINI = {'title.a': 'ListingItemTitle-module__link',
                        'title.get_text': '',
                        'price.div': 'ListingItemPrice-module__content',
                        'price.get_text': '',
                        'city.span': 'MetroListPlace__regionName',
                        'city.get_text': '',
                        }

URL_HAVAL = "https://auto.ru/moskva/cars/haval/all/"
PARSE_METHOD_HAVAL = {'title.a': 'ListingItemTitle-module__link',
                      'title.get_text': '',
                      'price.div': 'ListingItemPrice-module__content',
                      'price.get_text': 'span',
                      'city.span': 'MetroListPlace__regionName',
                      'city.get_text': '',
                      }



HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/89.0.4389.90 Safari/537.36',
    'accept': '*/*'}
FILE = 'cars.csv'

quantity_auto = 0

def quantity_auto_return():
    return quantity_auto

def get_html(url, params=None):
    """Получаем страницу с помощью requests"""
    r = requests.get(url, headers=HEADERS, params=params)
    r.encoding = 'utf-8'
    return r


def get_pages_count(html):
    """Переключает страницы. Будем ходить по всем страничкам"""
    soup = BeautifulSoup(html, 'html.parser')  # Создаем экземпляр
    pagination = soup.find_all('a', class_='ListingPagination-module__page')  # Ищем все страницы

    if pagination:
        return int(pagination[-1].get_text())  # Приводим номер страницы к int
    else:
        return 1  # Если страниц нет, возвращаем просто номер 1


def save_to_file(items, path):
    """Записываем данные в файл"""
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Марка', 'Цена', 'Город', 'Ссылка'])
        for item in items:
            writer.writerow([item['title'], item['price'], item['city'], item['link']])
    return open(path, 'rb')


def parsing_pages(pages_count, url, cars, ext):
    """Сделан для отлавнивания ошибок и перезапуска парсинга"""
    for page in range(1, pages_count + 1):  # Проходим по всем страницам
    # for page in range(1, 2):  # Проходим по 1-й странице
        print(f'\rПарсинг страницы {page} из {pages_count}...', end='')
        html = get_html(url, params={'page': page})
        cars.extend(get_content(html=html.text, ext=ext))
        sleep(random())  # Чтоб не заблочили, на всякий случай засыпаем на полсекунды на каждой итерации
    return cars


def get_content(html, ext):
    """Распарсиваем с помощью супа"""
    soup = BeautifulSoup(html, 'html.parser')  # Создаем экземпляр
    items = soup.find_all('div', class_='ListingItem-module__container')  # Получаем все карточки с авто

    cars = []
    for item in items:
        try:
            cars.append({'title': item.find('a', class_=ext['title.a']).get_text(ext['title.get_text']),
                         'price': item.find('div', class_=ext['price.div']).get_text(ext['price.get_text']),
                         'city': item.find('span', class_=ext['city.span']).get_text(ext['city.get_text']),
                         'link': item.find('a', class_='Link').get('href')

                         })
        except AttributeError as err:
            print(f'Некритичная ошибка, продолжаем сбор автомобилей {err}')
            pass


    return cars


def sort(cars):
    """Ищем самую дешевую машину"""
    for i in range(len(cars)):
        if cars[i]['price'].startswith('от '):
            cars[i]['price'] = cars[i]['price'][3:]

    cars = sorted(cars, key=lambda x: x['price'])
    return cars


def parse(variant):
    """Скелет программы"""
    global quantity_auto
    if variant.lower() == 'haval':
        url = URL_HAVAL
        ext = PARSE_METHOD_HAVAL
    elif variant.lower() == 'crysler':
        url = URL_CRYSLER
        ext = PARSE_METHOD_CRYSLER
    elif variant.lower() == 'mini':
        url = URL_MINI
        ext = PARSE_METHOD_MINI
    elif variant.lower() == 'subaru':
        url = URL_SUBARU
        ext = PARSE_METHOD_SUBARU
    print(f'Начата задача парсинга {variant.upper()}')

    html = get_html(url=url)
    if html.status_code == 200:
        cars = []
        pages_count = get_pages_count(html.text)  # Получает кол-во страниц
        try:
            cars = parsing_pages(pages_count=pages_count, url=url, cars=cars, ext=ext)
        except Exception as err:
            print(f'\r{err} Перезапуск парсинга...')
            sleep(random())
            parsing_pages(pages_count=pages_count, url=url, cars=cars, ext=ext)
        quantity_auto = len(cars)
        print(f'\nПолучено {quantity_auto} шт автомобилей')

        cars = sort(cars)

        return save_to_file(cars, FILE)
    else:
        print(f'Error, {html.status_code}')


if __name__ == '__main__':
    parse('subaru')
    print(quantity_auto_return())