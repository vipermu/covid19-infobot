import csv
import os
import pickle
import logging
from collections import defaultdict
from typing import *

import telegram.ext as ext
from googletrans import Translator


class CountryInfo:
    def __init__(self):
        print("Processing data...")

        data_file_path = './data/covid_19_clean_complete.csv'
        country_trans_dict_pkl_file = 'country_trans_dict.pkl'
        data_dict_pkl_file = 'data_dict.pkl'

        if os.path.exists(country_trans_dict_pkl_file):
            with open(country_trans_dict_pkl_file, 'rb') as pkl_file:
                self.country_trans_dict = pickle.load(pkl_file)
            with open(data_dict_pkl_file, 'rb') as pkl_file:
                self.data_dict = pickle.load(pkl_file)
        else:

            self.country_trans_dict, self.data_dict = self.get_dictionaries(
                data_file_path=data_file_path,
            )

            with open(country_trans_dict_pkl_file, 'wb') as pkl_file:
                pickle.dump(self.country_trans_dict, pkl_file,
                            protocol=pickle.HIGHEST_PROTOCOL)
            with open(data_dict_pkl_file, 'wb') as pkl_file:
                pickle.dump(self.data_dict, pkl_file,
                            protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def get_dictionaries(
        data_file_path: str,
    ) -> Tuple[Dict[str, str], Dict[str, Dict[str, Any]]]:

        translator = Translator()
        country_trans_dict = {}
        data_dict = defaultdict(lambda: {
            'date': None,
            'confirmed': 0,
            'deaths': 0,
            'recovered': 0,
        })

        with open(data_file_path, newline='') as csv_file:
            data_reader = csv.reader(csv_file, delimiter=',', quotechar='|')
            header_list = next(data_reader)
            for data in data_reader:
                # TODO: solve problem of comma for Korea
                if len(data) != len(header_list):
                    _province, country1, country2, _lat, _long, date, \
                        confirmed, deaths, recovered = data
                    country = country1[1:] + country2[:-1]
                else:
                    _province, country, _lat, _long, date, confirmed, \
                        deaths, recovered = data

                if country not in country_trans_dict.keys():
                    if country == 'US':
                        trans_country = 'Estados Unidos'
                    elif country == 'Bahrain':
                        trans_country = 'Baréin'
                    elif country == 'North Macedonia':
                        trans_country = 'Macedonia del Norte'
                    elif country == 'Qatar':
                        trans_country = 'Qatar'
                    elif country == 'Jordan':
                        trans_country = 'Jordania'
                    elif country == 'Togo':
                        trans_country = 'Togo'
                    elif country == 'Holly See':
                        trans_country = 'Vaticano'
                    elif country == 'Iran':
                        trans_country = 'Irán'
                    elif country == 'Turkey':
                        trans_country = 'Turquía'
                    elif country == 'Taiwan*':
                        trans_country = 'Taiwan'
                    elif country == 'Cruise Ship':
                        continue
                    else:
                        trans_country = translator.translate(
                            country, src='en', dest='es').text

                    country_trans_dict[country] = trans_country

                country = country_trans_dict[country]

                # TODO: this could be faster
                if data_dict[country]['date'] == date:
                    data_dict[country]['confirmed'] += int(confirmed)
                    data_dict[country]['deaths'] += int(deaths)
                    data_dict[country]['recovered'] += int(recovered)
                else:
                    data_dict[country] = {
                        'date': date,
                        'confirmed': int(confirmed),
                        'deaths': int(deaths),
                        'recovered': int(recovered),
                    }

        return country_trans_dict, dict(data_dict)


country_info = CountryInfo()


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

    send_updates = False
    if send_updates:
        with open('chat_ids.txt', 'r') as chat_ids_file:
            chat_ids_list = list(set(chat_ids_file.readlines()))
            for chat_id in chat_ids_list:
                dispatcher.bot.send_message(
                    chat_id=int(chat_id),
                    text="Hola! Los datos han sido actualizados :)",
                )

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )

    start_handler = ext.CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    echo_handler = ext.MessageHandler(ext.Filters.text, get_country_info)
    dispatcher.add_handler(echo_handler)

    print("Ready!")
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

    country = update.message.text
    data_dict = country_info.data_dict
    country_list = list(data_dict.keys())
    if country not in list(country_list):
        text = f"Asegurate de que has introducido correctamente el nombre del país. " \
            f"Aquí tienes una lista de los países de los que puedes obtener información:\n{country_list}"
    else:
        country_dict = data_dict[country]
        text = f"País: {country}\n" \
            f"Casos confirmados: {country_dict['confirmed']}\n" \
            f"Numero de muertes: {country_dict['deaths']}\n" \
            f"Numero de recuperaciones: {country_dict['recovered']} "

    context.bot.send_message(
        chat_id=chat_id,
        text=text
    )


if __name__ == '__main__':
    main()
