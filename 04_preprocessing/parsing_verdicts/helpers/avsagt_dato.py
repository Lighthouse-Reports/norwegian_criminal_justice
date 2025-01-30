from . import dommere_og_parter, log
import dateparser
import re


def finn_regex_dato(tekst):
    try:
        regex = re.compile(r'((\d+)[/.]\s?(\d+)[/. ]\s?(\d+))')
        dato = regex.search(tekst.strip()).group(1)
        return dato
    except AttributeError:
        regex = re.compile(r'((\d+)[.]\s?(\w+)\s?(\d+))')
        dato = regex.search(tekst.strip()).group(1)
        return dato


# Finne avsagt dato i form dd.mm.yyyy eller dd. måned yyyy
def avsagt_dato(dom: str) -> str | None:
    try:
        fra_til = [{"Avsagt:": "Sak"}, {"RETTSBOK": "Sak"}, {"RETT": "Sak"}]
        result = dommere_og_parter.tekst_mellom_ord(dom, fra_til).strip()
        dato = finn_regex_dato(result)

        return dateparser.parse(dato, settings={'DATE_ORDER': 'DMY'}).strftime("%Y-%m-%d")
    except AttributeError as e:
        log.feilmeldinger.append(f"Finner ikke avsagt dato: {e}")
        return None
