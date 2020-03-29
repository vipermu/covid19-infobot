import gspread
from oauth2client.service_account import ServiceAccountCredentials


class SpreadSheet:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'covid_credentials.json', scope)
        client = gspread.authorize(creds)
        self.sheet = client.open('lang_data').sheet1

    def get_user_lang_dict_list(self):
        return self.sheet.get_all_records()

    def append_row(
        self,
        chat_id: int,
        lang: str,
    ):
        self.sheet.append_row(
            values=[chat_id, lang],
        )

    def update_lang(
        self,
        index: int,
        lang: str,
    ):
        self.sheet.update_cell(
            row=index + 2,
            col=2,
            value=lang,
        )

    def update_history(
        self,
        index: int,
        new_hist: str,
    ):
        self.sheet.update_cell(
            row=index + 2,
            col=3,
            value=new_hist,
        )