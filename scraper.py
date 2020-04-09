import requests

from bs4 import BeautifulSoup


def get_soup_from_url(
    url: str
) -> BeautifulSoup:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    return soup


def process_data_item(data):
    data = data.text.strip()
    data = data.replace(',', '')
    data = data.replace('+', '')
    if data == '':
        data = '0'
    if data.isdecimal():
        data = int(data)
    return data


def get_table_data_from_soup(
    soup: BeautifulSoup,
) -> None:
    data_dict = {}
    key_list = [
        'country', 'total_cases', 'new_cases', 'total_deaths',
        'new_deaths', 'total_recoveries', 'active_cases', 'critical',
        'cases_per_million',
    ]
    table = soup.find('table', {'id': 'main_table_countries_today'})
    row_list = table.find_all('tr')

    for row in row_list:
        data_soup = row.find_all('td')

        if (len(data_soup) > 0):
            if len(data_soup) == len(key_list):
                continue

            data_text_list = list(map(process_data_item, data_soup))
            country_dict = dict(zip(key_list, data_text_list))

            if type(country_dict['country']) != str:
                continue

            data_dict[country_dict['country'].lower()] = country_dict

            print(f"{country_dict['country']} scraped!")

    return data_dict


def scrape_worldometers_data():
    url = 'https://www.worldometers.info/coronavirus/#countries'
    soup = get_soup_from_url(url=url)
    data_dict = get_table_data_from_soup(soup=soup)

    return data_dict
