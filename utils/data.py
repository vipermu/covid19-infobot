import os
import pickle
import logging
import time
from typing import *

import telegram as tel
from googletrans import Translator

import .scraper as scraper


class DataManager:
    def __init__(self):
        self.rescrape_time = 3600
        self.update_data_dict()

    def update_data_dict(self):
        print("Extracting data...")
        self.data_dict = {}
        self.data_dict['en'] = scraper.scrape_worldometers_data()

        en_to_es_country_dict = self.get_en_to_es_dict(self.data_dict['en'])
        self.data_dict['es'] = {en_to_es_country_dict[en_country_name]: country_dict
                                for en_country_name, country_dict
                                in self.data_dict['en'].items()}

        self.last_scrape_time = time.time()

    @staticmethod
    def get_en_to_es_dict(
        data_dict: Dict[str, Dict[str, str]],
    ) -> Tuple[Dict[str, str]]:
        translator = Translator()
        extended_data_dict = data_dict.copy()

        en_to_es_country_dict_path = './en_to_es_country_dict.pkl'

        if os.path.exists(en_to_es_country_dict_path):
            with open(en_to_es_country_dict_path, 'rb') as pickle_file:
                en_to_es_country_dict = pickle.load(pickle_file)

            en_to_es_keys_set = set(en_to_es_country_dict.keys())
            data_dict_keys_set = set(data_dict.keys())
            if not len(en_to_es_keys_set.symmetric_difference(data_dict_keys_set)):
                return en_to_es_country_dict

        en_to_es_country_dict = {}
        for country_key, country_dict in data_dict.items():
            country_name = country_dict['country']
            if country_name not in country_dict.keys():
                if country_name == 'Diamond Princess':
                    trans_country_name = 'Diamond Princess (crucero)'
                elif country_name == 'Bahrain':
                    trans_country_name = 'Baréin'
                elif country_name == 'CAR':
                    trans_country_name = 'CAR'
                elif country_name == 'North Macedonia':
                    trans_country_name = 'Macedonia del Norte'
                elif country_name == 'Qatar':
                    trans_country_name = 'Qatar'
                elif country_name == 'Jordan':
                    trans_country_name = 'Jordania'
                elif country_name == 'Togo':
                    trans_country_name = 'Togo'
                elif country_name == 'Iran':
                    trans_country_name = 'Irán'
                elif country_name == 'Turkey':
                    trans_country_name = 'Turquía'
                elif country_name == 'Sint Maarten':
                    trans_country_name = 'San Martín'
                else:
                    trans_country_name = translator.translate(
                        country_name, src='en', dest='es').text

                print(f"Transled English to Spanish: "
                      f"{country_name} --> {trans_country_name}")

                en_to_es_country_dict[country_key] = trans_country_name.lower()

        with open(en_to_es_country_dict_path, 'wb') as pickle_file:
            pickle.dump(en_to_es_country_dict, pickle_file,
                        protocol=pickle.HIGHEST_PROTOCOL)

        return en_to_es_country_dict
