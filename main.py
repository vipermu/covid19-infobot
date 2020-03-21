import csv
import os
import pickle
import logging
import time
from typing import *

import telegram.ext as ext
from googletrans import Translator

import scraper as scraper

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger()


class DataManager:
    def __init__(self):
        self.language_dict = {
            'spanish': 'es',
            'english': 'en',
        }
        self.language = self.language_dict['spanish']
        self.update_data_dict()

    def update_data_dict(self):
        logger.info("Extracting data...")
        self.data_dict = scraper.scrape_worldometers_data()
        self.last_scrape_time = time.time()

        if self.language != 'en':
            self.data_dict = eval(
                f'self.translate_dict_to_{self.language}(self.data_dict)')

    def translate_dict_to_es(
        self,
        data_dict: Dict[str, Dict[str, str]]
    ) -> Tuple[Dict[str, str], Dict[str, Dict[str, Any]]]:
        translator = Translator()

        en_to_es_country_dict_path = './en_to_es_country_dict.pkl'
        if os.path.exists(en_to_es_country_dict_path):
            with open(en_to_es_country_dict_path, 'r') as pickle_file:
                en_to_es_country_dict = pickle.load(pickle_file)
                else:
            en_to_es_country_dict = {}

        for country_key, country_dict in data_dict.items():
            country_name = country_dict['country']
            if country_name not in en_to_es_country_dict:
                if country_name == 'Diamond Princess':
                    trans_country_name = 'Diamond Princess (crucero)'
                elif country_name == 'Bahrain':
                    trans_country_name = 'Baréin'
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
                    else:
                    trans_country_name = translator.translate(
                        country_name, src='en', dest='es').text

                en_to_es_country_dict[country_name] = trans_country_name

                logger.info(f"Transled English to Spanish: "
                            f"{country_name} --> {trans_country_name}")
            else:
                trans_country_name = en_to_es_country_dict[country_name]

            data_dict[country_key][country_name] = trans_country_name

        with open(en_to_es_country_dict_path, 'w') as pickle_file:
            pickle.dump(en_to_es_country_dict, pickle_file,
                        protocol=pickle.HIGHEST_PROTOCOL)

        return data_dict


data_manager = DataManager()


def main():
    token_filename = 'token.txt'
    if os.path.exists(token_filename):
        with open(token_filename, 'r') as token_file:
            token = token_file.read().strip()
    else:
        token = os.environ['TOKEN']

    updater = ext.Updater(
        token=token,
        use_context=True,
    )
    dispatcher = updater.dispatcher

    start_handler = ext.CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    country_handler = ext.MessageHandler(ext.Filters.text, get_country_info)
    dispatcher.add_handler(country_handler)

    print("Ready!")
    logger.info("Ready!")

    mode = os.environ.get('MODE', 'dev')
    if mode == 'prod':
        port = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", "covid19-infobot")

        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=port,
                              url_path=token)
        updater.bot.set_webhook(
            "https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, token))

    elif mode == 'dev':
        updater.start_polling()

    else:
        logger.error("No MODE specified!")
        sys.exit(1)


def start(update, context):
    with open('chat_ids.txt', 'a') as chat_ids_file:
        chat_ids_file.write(str(update.effective_chat.id) + '\n')

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hola! Con este bot puedes obtener la última información sobre la"
        "situacion del COVID-19 alrededor del mundo."
    )


def get_country_info(update, context):
    chat_id = update.effective_chat.id
    with open('chat_ids.txt', 'a') as chat_ids_file:
        chat_ids_file.write(str(chat_id) + '\n')

    print(f"COUNTRY INFO QUERIED --> {chat_id}")
    logger.info(f"COUNTRY INFO QUERIED --> {chat_id}")

    country = update.message.text
    data_dict = data_manager.data_dict
    country_list = list(data_dict.keys())
    if country not in country_list:
        text = "Asegurate de que has introducido correctamente el nombre del país. " \
            "Aquí tienes una lista de los países de los que puedes obtener información:\n" \
            + '\n'.join(country_list)
    else:
        country_dict = data_dict[country]
        text = f"País: {country_dict['country']}\n"
        f"Número total de casos: {country_dict['total_cases']}\n"
        f"Número de nevos casos: {country_dict['new_cases']}\n"
        f"Número total de muertes: {country_dict['total_deaths']} \n"
        f"Número de nuevas muertes: {country_dict['new_deaths']} \n"
        f"Número total de recuperaciones: {country_dict['total_recoveries']} \n"
        f"Número de contagios activos: {country_dict['active_cases']} \n"
        f"Número de personas en estado crítico: {country_dict['critical']} \n"
        f"Número de casos por millón: {country_dict['cases_per_milion']} "

    context.bot.send_message(
        chat_id=chat_id,
        text=text
    )


if __name__ == '__main__':
    main()
