import os
import time
from typing import *

import telegram as tel
import telegram.ext as ext

from data_utils import DataManager
from text_utils import TextManager
from google_drive import SpreadSheet


class Bot:
    def __init__(
        self,
    ):
        self.data_manager = DataManager()
        self.text_manager = TextManager()
        self.spread_sheet = SpreadSheet()

        token_filename = 'dev_token.txt'
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

        start_handler = ext.CommandHandler('start', self.start)
        dispatcher.add_handler(start_handler)

        lang_handler = ext.CommandHandler('lang', self.lang_selector)
        dispatcher.add_handler(lang_handler)

        updater.dispatcher.add_handler(
            ext.CallbackQueryHandler(self.process_selected_lang))

        country_handler = ext.MessageHandler(
            ext.Filters.text, self.get_country_info)
        dispatcher.add_handler(country_handler)

        print("Ready!")

        mode = os.environ.get('MODE', 'dev')
        if mode == 'prod':
            port = int(os.environ.get("PORT", "8443"))
            HEROKU_APP_NAME = os.environ.get(
                "HEROKU_APP_NAME", "covid19-infobot")

            # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
            updater.start_webhook(listen="0.0.0.0",
                                  port=port,
                                  url_path=token)
            updater.bot.set_webhook(
                "https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, token))

        elif mode == 'dev':
            updater.start_polling()

        else:
            self.logger.error("No MODE specified!")
            sys.exit(1)

    def start(self, update, context):
        with open('chat_ids.txt', 'a') as chat_ids_file:
            chat_ids_file.write(str(update.effective_chat.id) + '\n')

        self.lang_selector(update, context)

        # if self.data_manager.language == 'en':
        #     text = 'Send me a text with the country that you want to get information from!'
        # elif self.data_manager.language == 'es':
        #     text = "Hola! Mandame un mensaje con el nombre del país del que quieras recibir información."

        # context.bot.send_message(
        #     chat_id=update.effective_chat.id,
        #     text=text,
        # )

    @staticmethod
    def lang_selector(update, context):
        keyboard = [[tel.InlineKeyboardButton("Español", callback_data='es'),
                     tel.InlineKeyboardButton("English", callback_data='en')]]

        reply_markup = tel.InlineKeyboardMarkup(keyboard)

        update.message.reply_text('<i>Escoge el idioma en que quieras que responda:\n\n'
                                  "Choose the language you want me to answer:</i>",
                                  reply_markup=reply_markup,
                                  parse_mode=tel.ParseMode.HTML)

    def process_selected_lang(self, update, context):
        query = update.callback_query
        language = query.data

        text = self.text_manager.button_text[language]
        query.edit_message_text(text=text)

        self.data_manager.language = language

    @staticmethod
    def get_country_info(update, context):
        chat_id = update.effective_chat.id
        with open('chat_ids.txt', 'a') as chat_ids_file:
            chat_ids_file.write(str(chat_id) + '\n')

        # print(f"COUNTRY INFO QUERIED --> {chat_id}")

        if time.time() - self.data_manager.last_scrape_time > self.data_manager.rescrape_time:
            self.data_manager.update_data_dict()

        req_country = update.message.text.lower()
        data_dict = self.data_manager.data_dict

        country_list = [country_key for country_key in data_dict.keys()
                        if country_key != 'total:']

        if self.data_manager.language == 'es':
            es_to_en_country_dict = self.data_manager.es_to_en_country_dict
            country_list = [country_key for country_key in es_to_en_country_dict.keys()
                            if country_key != 'total:']

        country_list.sort()

        if req_country not in country_list:
            text = "Asegurate de que has introducido correctamente el nombre del país. " \
                "Aquí tienes una lista de los países de los que puedes obtener información:\n" \
                + '\n'.join(country_list)
        else:
            if self.data_manager.language == 'es':
                req_country = es_to_en_country_dict[req_country]

            country_dict = data_dict[req_country.lower()]
            text = f"<b><i>{update.message.text}</i></b> cuenta con un total de " \
                f"<b><i>{country_dict['total_cases']} casos confirmados</i></b>.\n\n" \
                f"Por el momento han habido " \
                f"<b><i>{country_dict['total_deaths']} muertes</i></b> y " \
                f"<b><i>{country_dict['total_recoveries']} recuperaciones</i></b>.\n\n" \
                f"En las últimas horas se han confirmado " \
                f"<b><i>{country_dict['new_cases']} nuevos casos</i></b> y " \
                f"<b><i>{country_dict['new_deaths']} nuevos fallecimientos</i></b>.\n\n" \
                f"Hay un total de <b><i>{country_dict['active_cases']} casos activos</i></b> "\
                f" de los cuales <b><i>{country_dict['critical']}</i></b> se encuentran " \
                f"en <b><i>estado crítico</i></b>. \n\n" \
                f"Existen <b><i>{country_dict['cases_per_million']} casos " \
                f"por cada millón</i></b> de personas. \n\n" \

        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=tel.ParseMode.HTML,
        )
