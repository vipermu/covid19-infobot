from typing import *


class TextManager:
    def __init__(
        self,
    ) -> None:
        self.button_text = {
            'es': "Español seleccionado! 🇪🇸",
            'en': "English chosen! 🇺🇸 🇬🇧",
        }

        self.missing_country = {
            'es': "Asegurate de que has introducido correctamente el nombre!"
            "Te puedo dar información de:",
            'en': "Was that name correct?"
            "Here's a list with the information I have:",
        }

        self.welcome = {
            'es': "Hola! 👋 \n\nMándame un mensaje con el nombre del país o continente del que quieras información! \n\n"
            "Escribe 'Mundo' para ver la situación mundial. Usa el comando /lang para cambiar el idioma del bot 😃",
            'en': "Hi! 👋 \n\nSend me the name of the country or continent that you want to receive information from! \n\n"
            "Use the command /lang to switch the language of the bot 😃",
        }

    @staticmethod
    def country_dict_to_text(
        country_dict: Dict[str, str],
        input_country: str,
        lang: str,
    ) -> str:
        if lang == 'es':
            text = f"<b><i>{input_country}</i></b> cuenta con un total de " \
                f"<b><i>{country_dict['total_cases']} casos confirmados</i></b>.\n\n" \
                f"Por el momento han habido " \
                f"<b><i>{country_dict['total_deaths']} muertes</i></b> y " \
                f"<b><i>{country_dict['total_recoveries']} recuperaciones</i></b>.\n\n"

            if country_dict['new_cases'] > 0 or country_dict['new_deaths'] > 0:
                text += f"En las últimas horas se han confirmado " \
                    f"<b><i>{country_dict['new_cases']} nuevos casos</i></b> y " \
                    f"<b><i>{country_dict['new_deaths']} nuevos fallecimientos</i></b>.\n\n"

            text += f"Hay un total de <b><i>{country_dict['active_cases']} casos activos</i></b> "\
                f" de los cuales <b><i>{country_dict['critical']}</i></b> se encuentran " \
                f"en <b><i>estado crítico</i></b>. \n\n"

            if country_dict['total_tests'] > 0:
                text += f"Se han realizado <b><i>tests</i></b> a <b><i>{country_dict['total_tests']}</i></b> personas. \n\n"

            if country_dict['cases_per_million'] > 0 or country_dict['deaths_per_million'] > 0 or country_dict['tests_per_million']:
                text += f"Por cada <b><i>millón de personas</i></b> existen <b><i>{country_dict['cases_per_million']} casos " \
                    f"</i></b>, se han realizado <b><i>{country_dict['tests_per_million']} tests</i></b> "\
                    f"y <b><i>{country_dict['deaths_per_million']} muertes</i></b>.\n\n"
            return text

        elif lang == 'en':
            text = f"<b><i>{input_country}</i></b> has confirmed " \
                f"<b><i>{country_dict['total_cases']} cases</i></b>.\n\n" \
                f"There have been " \
                f"<b><i>{country_dict['total_deaths']} deaths</i></b> and " \
                f"<b><i>{country_dict['total_recoveries']} recoveries</i></b>.\n\n"

            if country_dict['new_cases'] > 0 or country_dict['new_deaths'] > 0:
                text += f"During the last few hours " \
                    f"<b><i>{country_dict['new_cases']} new cases </i></b> and " \
                    f"<b><i>{country_dict['new_deaths']} new deaths </i></b> have been confirmed.\n\n"

            text += f"There exist <b><i>{country_dict['active_cases']} active cases</i></b>, "\
                f"<b><i>{country_dict['critical']}</i></b> of them are <b><i>critical</i></b>. \n\n"
            
            if country_dict['total_tests'] > 0:
                text += f"In total, <b><i>{country_dict['total_tests']}</i></b> people have been <b><i>tested</i></b>. \n\n"

            if country_dict['cases_per_million'] > 0 or country_dict['deaths_per_million'] > 0 or country_dict['tests_per_million']:
                text += f"For every million people there are <b><i>{country_dict['cases_per_million']} cases " \
                    f"</i></b>, <b><i>{country_dict['tests_per_million']} tests</i></b> "\
                    f"and <b><i>{country_dict['deaths_per_million']} deaths</i></b>.\n\n"

            return text
