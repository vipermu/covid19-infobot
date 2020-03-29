from typing import *


class TextManager:
    def __init__(
        self,
    ) -> None:
        self.button_text = {
            'es': "Ahora tu bot está en español! 🇪🇸",
            'en': "Your bot is in English now! 🇺🇸 🇬🇧",
        }

        self.missing_country = {
            'es': "Asegurate de que has introducido correctamente el nombre del"
            " país! Aqui tienes una lista de los países de los que tengo datos:",
            'en': "Make sure that the name of the country is correct!"
            "Here you have a list with the different countries that you can "
            "choose:",
        }

        self.welcome = {
            'es': "Hola! 👋 \n\nMándame un mensaje con el nombre del país del que quieras información! \n\n"
            "Usa el comando /lang para cambiar el idioma del bot 😃",
            'en': "Hi! 👋 \n\nSend me the name of the country that you want to get information from! \n\n"
            "Use the command /lang to switch the language of the bot 😃",
        }

    @staticmethod
    def country_dict_to_text(
        country_dict: Dict[str, str],
        input_country: str,
        lang: str,
    ) -> str:
        if lang == 'es':
            return f"<b><i>{input_country}</i></b> cuenta con un total de " \
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
                f"por cada millón</i></b> de personas. \n\n"

        elif lang == 'en':
            return f"<b><i>{input_country}</i></b> has confirmed " \
                f"<b><i>{country_dict['total_cases']} cases</i></b>.\n\n" \
                f"There has been a total of " \
                f"<b><i>{country_dict['total_deaths']} deaths</i></b> and " \
                f"<b><i>{country_dict['total_recoveries']} recoveries</i></b>.\n\n" \
                f"During the last few hours " \
                f"<b><i>{country_dict['new_cases']} new cases </i></b> and " \
                f"<b><i>{country_dict['new_deaths']} new deaths </i></b> have been confirmed.\n\n" \
                f"There exist <b><i>{country_dict['active_cases']} active cases</i></b>, "\
                f"<b><i>{country_dict['critical']}</i></b> are <b><i>critical</i></b>. \n\n" \
                f"They account with <b><i>{country_dict['cases_per_million']} cases " \
                f"per million</i></b>. \n\n"
