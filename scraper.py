import requests

from bs4 import BeautifulSoup


def get_soup_from_url(
    url: str
) -> BeautifulSoup:
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'lxml')
    return soup


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
            assert len(data_soup) == len(key_list), \
                'Key list and numbers of data elements should be equal.'

            data_text_list = [data.text for data in data_soup]
            country_dict = dict(zip(key_list, data_text_list))
            data_dict[country_dict['country'].lower()] = country_dict

            print(f"{country_dict['country']} scraped!")

    return data_dict


def scrape_worldometers_data():
    url = 'https://www.worldometers.info/coronavirus/#countries'
    soup = get_soup_from_url(url=url)
    data_dict = get_table_data_from_soup(soup=soup)

    return data_dict
