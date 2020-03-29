import os
import time
from typing import *

import telegram as tel
import telegram.ext as ext

from utils.data import DataManager
from utils.text import TextManager
from utils.google_drive import SpreadSheet


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
            print("No MODE specified!")
            sys.exit(1)

    def start(self, update, context):
        self.lang_selector(update, context)

    @staticmethod
    def lang_selector(update, context):
        keyboard = [[tel.InlineKeyboardButton("Español", callback_data='es'),
                     tel.InlineKeyboardButton("English", callback_data='en')]]

        reply_markup = tel.InlineKeyboardMarkup(keyboard)

        update.message.reply_text('<i>🇪🇸 Escoge el idioma en que quieras que responda:\n\n'
                                  "🇺🇸 🇬🇧 Choose the language you want me to answer:</i>",
                                  reply_markup=reply_markup,
                                  parse_mode=tel.ParseMode.HTML)

    def process_selected_lang(self, update, context):
        query = update.callback_query
        language = query.data

        text = self.text_manager.button_text[language]
        query.edit_message_text(text=text)

        user_lang_list = self.spread_sheet.get_user_lang_dict_list()
        chat_id_list = [user_dict['chat_id'] for user_dict
                        in user_lang_list]

        chat_id = update.effective_chat.id
        if chat_id in chat_id_list:
            chat_id_pos = chat_id_list.index(chat_id)
            self.spread_sheet.update_lang(
                index=chat_id_pos,
                lang=language,
            )
        else:
            text = self.text_manager.welcome[language]
            context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=tel.ParseMode.HTML,
            )

            self.spread_sheet.append_row(
                chat_id=chat_id,
                lang=language,
            )

    def get_country_info(self, update, context):
        chat_id = update.effective_chat.id
        user_lang_list = self.spread_sheet.get_user_lang_dict_list()
        chat_id_list = [user_dict['chat_id'] for user_dict
                        in user_lang_list]

        if chat_id not in chat_id_list:
            self.lang_selector(update, context)
            return

        chat_id_pos = chat_id_list.index(chat_id)
        language = user_lang_list[chat_id_pos]['language']

        if time.time() - self.data_manager.last_scrape_time > self.data_manager.rescrape_time:
            self.data_manager.update_data_dict()

        req_country = update.message.text.lower()

        chat_pos = chat_id_list.index(chat_id)
        self.spread_sheet.update_history(
            index=chat_pos,
            new_hist=user_lang_list[chat_pos]['history'] + ' ' + req_country,
        )

        data_dict = self.data_manager.data_dict[language]

        country_list = [country_key for country_key in data_dict.keys()
                        if country_key != 'total:']
        country_list.sort()

        if req_country not in country_list:
            text = self.text_manager.missing_country[language] \
                + '\n\n' + '\n'.join(country_list)
        else:
            country_dict = data_dict[req_country.lower()]
            input_country = update.message.text
            text = self.text_manager.country_dict_to_text(
                country_dict=country_dict,
                input_country=input_country,
                lang=language,
            )

        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=tel.ParseMode.HTML,
        )
