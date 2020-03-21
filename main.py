import os
import pickle
import logging
import time
from typing import *

import telegram
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
        self.rescrape_time = 10000  # 2h 45mins
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

        if self.language == 'es':
            self.es_to_en_country_dict = self.get_es_to_en_dict(self.data_dict)

    @staticmethod
    def get_es_to_en_dict(
        data_dict: Dict[str, Dict[str, str]]
    ) -> Tuple[Dict[str, str]]:
        translator = Translator()
        extended_data_dict = data_dict.copy()

        en_to_es_country_dict_path = './es_to_en_country_dict.pkl'
        if os.path.exists(en_to_es_country_dict_path):
            with open(en_to_es_country_dict_path, 'rb') as pickle_file:
                es_to_en_country_dict = pickle.load(pickle_file)
            return es_to_en_country_dict
        else:
            es_to_en_country_dict = {}

        for country_key, country_dict in data_dict.items():
            country_name = country_dict['country']
            if country_name not in country_dict.keys():
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
                elif country_name == 'Sint Maarten':
                    trans_country_name = 'San Martín'
                else:
                    trans_country_name = translator.translate(
                        country_name, src='en', dest='es').text

                logger.info(f"Transled English to Spanish: "
                            f"{country_name} --> {trans_country_name}")

                es_to_en_country_dict[trans_country_name.lower()] = country_key

            with open(en_to_es_country_dict_path, 'wb') as pickle_file:
            pickle.dump(es_to_en_country_dict, pickle_file,
                            protocol=pickle.HIGHEST_PROTOCOL)

        return es_to_en_country_dict


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

    logger.info(f"COUNTRY INFO QUERIED --> {chat_id}")

    if time.time() - data_manager.last_scrape_time > data_manager.rescrape_time:
        data_manager.update_data_dict()
    data_dict = data_manager.data_dict
    country_list = list(data_dict.keys())
    if country not in country_list:
        text = "Asegurate de que has introducido correctamente el nombre del país. " \
            "Aquí tienes una lista de los países de los que puedes obtener información:\n" \
            + '\n'.join(country_list)
    else:
        text = f"<b><i>{update.message.text}</i></b> cuenta con un total de " \
            f"<b><i>{country_dict['total_cases']} casos confirmados</i></b>.\n\n" \
            f"Por el momento han habido " \
            f"<b><i>{country_dict['total_deaths']} muertes</i></b> y " \
            f"<b><i>{country_dict['total_recoveries']} recuperaciones</i></b>.\n\n" \
            f"En las últimas hora se han confirmado " \
            f"<b><i>{country_dict['new_cases']} nuevos casos</i></b> y " \
            f"<b><i>{country_dict['new_deaths']} nuevos fallecimientos</i></b>.\n\n" \
            f"Hay un total de <b><i>{country_dict['active_cases']} casos activos</i></b> "\
            f" de los cuales <b><i>{country_dict['critical']}</i></b> se encuentran " \
            f"en <b><i>estado crítico</i></b>. \n\n" \
            f"Existen <b><i>{country_dict['cases_per_million']}</i></b> casos " \
            f"<b><i>por cada millón</i></b> de personas. \n\n" \

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=telegram.ParseMode.HTML,
    )


if __name__ == '__main__':
    main()
