from __future__ import annotations

from . import avsagt_dato, dommere_og_parter, log, dom_strenghetsgrad
# from . import dom_strenghetsgrad
import dateparser
import re


def flatten_top_level(lst):
    flattened = []
    for item in lst:
        if isinstance(item, list):
            flattened.extend(item)
        else:
            flattened.append(item)
    return flattened


def fjern_domsslutning_i_innholdsfortegnelse(full_text):
    if "DOMSSLUTNING ................" in full_text:
        full_text = full_text.replace("DOMSSLUTNING ................", "")
    elif "DOMSSLUTNING................" in full_text:
        full_text = full_text.replace("DOMSSLUTNING................")
    return full_text


def finn_domsslutning(domsslutning_formuleringer, full_text, fagdommere, lagmannsrett=False):
    full_text = fjern_domsslutning_i_innholdsfortegnelse(full_text)
    if lagmannsrett:
        for formulering in domsslutning_formuleringer:
            if formulering in full_text:
                if fagdommere:
                    for fagdommer in fagdommere:
                        if dommere_og_parter.tekst_mellom_ord(full_text, [{formulering: fagdommer["navn"]}]):
                            return dommere_og_parter.tekst_mellom_ord(full_text, [{formulering: fagdommer["navn"]}])
                else:
                    return dommere_og_parter.tekst_mellom_ord(full_text, [{formulering: "Retten hevet"}])
    else:
        for formulering in domsslutning_formuleringer:
            if formulering in full_text:
                if dommere_og_parter.tekst_mellom_ord(full_text, [{formulering: "\*\*\*"}]):
                    return dommere_og_parter.tekst_mellom_ord(full_text, [{formulering: "\*\*\*"}])
                elif dommere_og_parter.tekst_mellom_ord(full_text, [{formulering: "\* \* \*"}]):
                    return dommere_og_parter.tekst_mellom_ord(full_text, [{formulering: "\* \* \*"}])
                elif dommere_og_parter.tekst_mellom_ord(full_text, [{formulering: "Retten hevet"}]):
                    return dommere_og_parter.tekst_mellom_ord(full_text, [{formulering: "Retten hevet"}])
                else:
                    return dommere_og_parter.tekst_mellom_ord(full_text,
                                                              [{formulering: "Til deg som har fått en dom i"}])


# Finner ut om domsslutningen er nummerert
def domsslutning_er_nummerert(domsslutning: str) -> bool:
    if domsslutning:
        if domsslutning.strip().startswith("1"):
            return True
    return False


def domsslutning_er_nummerert_med_romertall(domsslutning: str) -> bool:
    if domsslutning:
        if "I" in domsslutning and "II" in domsslutning and "III" in domsslutning:
            return True
    return False


def domsslutning_er_gruppert_med_navn(domsslutning: str, motpart) -> bool | list:
    if domsslutning:
        domsslutning_linjer = domsslutning.split("\n")
        if motpart:
            navn_tiltalte = [p["navn"] for p in motpart if "tittel" not in p]
            if len(navn_tiltalte) > 1:
                navn_index = []
                for navn in navn_tiltalte:
                    navn_funnet = False
                    for linje in domsslutning_linjer:
                        if navn == linje.strip():
                            navn_index.append(domsslutning_linjer.index(linje))
                            navn_funnet = True
                    if navn_funnet:
                        continue
                    else:
                        return False
                return navn_index
                # Returner liste splittet på navn
        return False


def finn_avsnitt_gruppert_med_navn(domsslutning: str, navn_index: list) -> list:
    domsslutning_linjer = domsslutning.split("\n")
    navn_index_split_koordinater = []
    for i in range(0, len(navn_index)):
        try:
            # Legger til 1 i koordinater for å unngå at avsnittet starter med navnet. Dette gjør det mulig å detektere
            # nummererte lister under navnet
            koordinater = [sorted(navn_index)[i] + 1, sorted(navn_index)[i + 1]]
        except IndexError:
            koordinater = [sorted(navn_index)[i] + 1, -1]

        navn_index_split_koordinater.append(koordinater)
    avsnitt = []
    for i in navn_index_split_koordinater:
        # navn_avsnitt = "".join(domsslutning_linjer[i[0]:i[1]])
        avsnitt.append("\n".join(domsslutning_linjer[i[0]:i[1]]).strip())
    return avsnitt


# Finner ut om minst ett av ordene i en liste er i en tekst
def er_i_avsnitt(ordliste: list, tekst: str) -> bool:
    for i in ordliste:
        if i in tekst:
            return True
    return False


def formater_lovnavn(lov):
    if lov is None:
        return None
    else:
        if any(word in lov.lower() for word in
               ["strpl", "straffeproessloven", "straffeprosesloven", "straffeprosesssloven"]):
            lov = "Straffeprosessloven"
        elif any(word in lov.lower() for word in ["strl", "sstraffeloven", "staffeloven"]):
            lov = "Straffeloven"
        elif "vareførselloven" in lov.lower():
            lov = "Vareførselsloven"
        elif "veitrafikkloven" in lov.lower():
            lov = "Vegtrafikkloven"
        if "lova" in lov:
            lov.replace("lova", "loven")
        if lov.endswith("s"):
            lov = lov[:-1]
        return lov


# Returnerer liste med navn på lover og paragrafer i en tekst
def finn_lov_og_paragraf(tekst) -> list:
    # regex_iter = re.finditer(r'((?P<hovedlov>[A-ZÆØÅa-zæøå]\w+lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?)(?: av)?\s?\(?\d?\d?\d?\d?\)? ? ? ? ?[ ?|\n](?P<hovedparagraf>§\s?\s?\d+)(,?\s\w+\s\w+\s?\w+\s?\w+)?(,?\s?(?:jf[r]?.|jamfør))\s?\s?((?P<jfr1lov>(?:[A-ZÆØÅa-zæøå]\w+lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?|[A-ZÆØÅa-zæøå]\w+forskrift(?:a|en))))? ?(?P<jfr1paragraf>§\s?\s?\d+)(\s\w+\s\w+\s?\w+\s?\w+)?(,? ?(?:jf[r]?.|jamfør))\s?\s?((?P<jfr2lov>(?:[A-ZÆØÅa-zæøå]\w+lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?|[A-ZÆØÅa-zæøå]\w+forskrift(?:a|en))))? ?(?P<jfr2paragraf>§\s?\s?\d+)?)|((?P<hovedlov_g2>[A-ZÆØÅa-zæøå]\w+lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?)(?: av)?\s?\(?\d?\d?\d?\d?\)? ? ? ? ?[ ?|\n](?P<hovedparagraf_g2>§\s?\s?\d+)(,?\s\w+\s\w+\s?\w+\s?\w+)?(,? ?(?:jf[r]?.|jamfør))\s?\s?((?P<jfr1lov_g2>(?:[A-ZÆØÅa-zæøå]\w+lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?|[A-ZÆØÅa-zæøå]\w+forskrift(?:a|en))))?\s?(?P<jfr1paragraf_g2>§\s?\s?\d+)?)|((?P<hovedlov_g3>[A-ZÆØÅa-zæøå]\w+lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?)(?: av)? ?\(?\d?\d?\d?\d?\)? ? ? ? ?[ ?|\n](?P<hovedparagraf_g3>§\s?\s?\d+))',
    #                         tekst)
    # regex_iter = re.finditer(
    #    r'((?P<hovedlov>[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)s?|[Ss]trl\.?|[Ss]trpl\.?)(?: av)?\s?\(?\d?\d?\d?\d?\)? ? ? ? ?[ ?|\n](?P<hovedparagraf>§\s?\s?\d+)(,?\s\w+\s\w+\s?\w+\s?\w+)?(,?\s?(?:jf[r]?.|jamfør))\s?\s?((?P<jfr1lov>(?:[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?|[A-ZÆØÅa-zæøå]\w+forskrift(?:a|en))))? ?(?P<jfr1paragraf>§\s?\s?\d+)(\s\w+\s\w+\s?\w+\s?\w+)?(,? ?(?:jf[r]?.|jamfør))\s?\s?((?P<jfr2lov>(?:[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?|[A-ZÆØÅa-zæøå]\w+forskrift(?:a|en))))? ?(?P<jfr2paragraf>§\s?\s?\d+)?)|((?P<hovedlov_g2>[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?)(?: av)?\s?\(?\d?\d?\d?\d?\)? ? ? ? ?[ ?|\n](?P<hovedparagraf_g2>§\s?\s?\d+)(,?\s\w+\s\w+\s?\w+\s?\w+)?(,? ?(?:jf[r]?.|jamfør))\s?\s?((?P<jfr1lov_g2>(?:[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?|[A-ZÆØÅa-zæøå]\w+forskrift(?:a|en))))?\s?(?P<jfr1paragraf_g2>§\s?\s?\d+)?)|((?P<hovedlov_g3>[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?)(?: av)? ?\(?\d?\d?\d?\d?\)? ? ? ? ?[ ?|\n](?P<hovedparagraf_g3>§\s?\s?\d+))',
    #    tekst)
    regex_iter = re.finditer(
        r'(?P<jfstart>jf[r]?\.\s\s?|jamfør\s\s?)?((?P<hovedlov>[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)s?|[Ss]trl\.?|[Ss]trpl\.?)(?: av)?\s?\(?\d?\d?\d?\d?\)? ? ? ? ?[ ?|\n](?P<hovedparagraf>§\s?\s?\d+)(,?\s\w+\s\w+\s?\w+\s?\w+)?(,?\s?(?:jf[r]?.|jamfør))\s?\s?((?P<jfr1lov>(?:[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?|[A-ZÆØÅa-zæøå]\w+forskrift(?:a|en))))? ?(?P<jfr1paragraf>§\s?\s?\d+)(\s\w+\s\w+\s?\w+\s?\w+)?(,? ?(?:jf[r]?.|jamfør))\s?\s?((?P<jfr2lov>(?:[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?|[A-ZÆØÅa-zæøå]\w+forskrift(?:a|en))))? ?(?P<jfr2paragraf>§\s?\s?\d+)?)|(?P<jfstart_g2>jf[r]?\.\s\s?|jamfør\s\s?)?((?P<hovedlov_g2>[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?)(?: av)?\s?\(?\d?\d?\d?\d?\)? ? ? ? ?[ ?|\n](?P<hovedparagraf_g2>§\s?\s?\d+)(,?\s\w+\s\w+\s?\w+\s?\w+)?(,? ?(?:jf[r]?.|jamfør))\s?\s?((?P<jfr1lov_g2>(?:[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?|[A-ZÆØÅa-zæøå]\w+forskrift(?:a|en))))?\s?(?P<jfr1paragraf_g2>§\s?\s?\d+)?)|(?P<jfstart_g3>jf[r]?\.\s\s?|jamfør\s\s?)?((?P<hovedlov_g3>[A-ZÆØÅa-zæøå]\w+(-\sog\s\w+?)?lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?)(?: av)? ?\(?\d?\d?\d?\d?\)? ? ? ? ?[ ?|\n](?P<hovedparagraf_g3>§\s?\s?\d+)|(?P<jfstart_dp>jf[r]?\.\s\s?|jamfør\s\s?)?(?P<hovedlov_dp>[A-ZÆØÅa-zæøå]\w+lov(?:a|en)|[Ss]trl\.?|[Ss]trpl\.?)(?: av)?\s?\(?\d?\d?\d?\d?\)? ? ? ? ?[ ?|\n](§§?\s?\s?(?P<paragraf1_dp>\d+))\s?og\s?(?P<paragraf2_dp>\d+))',
        tekst)

    lov_og_paragraf_formatert = []
    lov_og_paragraf_uten_duplikat = []
    for i in regex_iter:
        if i.group("hovedlov") and not i.group("jfstart"):
            hovedlov = formater_lovnavn(i.group("hovedlov").capitalize())
            hovedparagraf = "".join(i.group("hovedparagraf").split())
            jfr1lov = formater_lovnavn(i.group("jfr1lov").capitalize() if i.group("jfr1lov") else None)
            jfr1paragraf = "".join(i.group("jfr1paragraf").split()) if i.group("jfr1paragraf") else None
            jfr2lov = formater_lovnavn(i.group("jfr2lov").capitalize() if i.group("jfr2lov") else None)
            jfr2paragraf = "".join(i.group("jfr2paragraf").split()) if i.group("jfr2paragraf") else None
            if not jfr1lov:
                jfr1lov = hovedlov
            if not jfr2lov and not jfr1lov:
                jfr2lov = hovedlov
            if not jfr2lov and jfr1lov:
                jfr2lov = jfr1lov
            if not jfr2paragraf:
                lov_og_paragraf_formatert.append(
                    [str(hovedlov + " " + hovedparagraf), [str(jfr1lov + " " + jfr1paragraf)]])
            if jfr2paragraf:
                lov_og_paragraf_formatert.append([str(hovedlov + " " + hovedparagraf),
                                                  [str(jfr1lov + " " + jfr1paragraf),
                                                   str(jfr2lov + " " + jfr2paragraf)]])

        elif i.group("hovedlov_g2") and not i.group("jfstart_g2"):
            hovedlov = formater_lovnavn(i.group("hovedlov_g2").capitalize())
            hovedparagraf = "".join(i.group("hovedparagraf_g2").split())
            jfr1lov = formater_lovnavn(i.group("jfr1lov_g2").capitalize() if i.group("jfr1lov_g2") else None)
            jfr1paragraf = "".join(i.group("jfr1paragraf_g2").split()) if i.group("jfr1paragraf_g2") else None
            if not jfr1lov:
                jfr1lov = hovedlov
            if not jfr1paragraf:
                lov_og_paragraf_formatert.append([str(hovedlov + " " + hovedparagraf)])
            else:
                lov_og_paragraf_formatert.append(
                    [str(hovedlov + " " + hovedparagraf), [str(jfr1lov + " " + jfr1paragraf)]])

        elif i.group("hovedlov_g3") and not i.group("jfstart_g3"):
            hovedlov = formater_lovnavn(i.group("hovedlov_g3").capitalize())
            hovedparagraf = "".join(i.group("hovedparagraf_g3").split())
            if hovedparagraf:
                lov_og_paragraf_formatert.append([str(hovedlov + " " + hovedparagraf)])

        elif i.group("hovedlov_dp") and not i.group("jfstart_dp"):
            hovedlov = formater_lovnavn(i.group("hovedlov_dp").capitalize())
            paragraf1 = f"§{i.group('paragraf1_dp')}"
            paragraf2 = f"§{i.group('paragraf2_dp')}"
            if paragraf2:
                lov_og_paragraf_formatert.append([str(hovedlov + " " + paragraf1)])
                lov_og_paragraf_formatert.append([str(hovedlov + " " + paragraf2)])

        for lov in lov_og_paragraf_formatert:
            if lov not in lov_og_paragraf_uten_duplikat:
                lov_og_paragraf_uten_duplikat.append(lov)
    return lov_og_paragraf_uten_duplikat


# Kobler dom og paragraf med om personen er domfelt eller frifunnet
def koble_dom_og_lov(domfelt: bool, paragrafer: list) -> dict:
    if domfelt:
        return {
            "dømt": paragrafer
        }
    return {
        "frifunnet": paragrafer
    }


# Returnerer dictionary med hvert avsnitt i en nummerert domsslutning
def finn_avsnitt_i_nummerert_domsslutning(tekst: str) -> dict:
    linjer = tekst.split("\n")
    punktnummer = 1

    domsslutning_dict = {}

    # Looper gjennom linjer for å finne punktene og legge hvert punkt som egen key/value i en dictionary
    for linje in linjer:
        if linje.startswith(f"{punktnummer}."):
            domsslutning_dict[punktnummer] = linje
            punktnummer += 1
        elif linje.startswith(f"{punktnummer}"):
            domsslutning_dict[punktnummer] = linje
            punktnummer += 1
        elif punktnummer - 1 in domsslutning_dict:
            domsslutning_dict[punktnummer - 1] = domsslutning_dict[punktnummer - 1] + linje

    return domsslutning_dict


def finn_avsnitt_i_nummerert_domsslutning_romertall(tekst: str) -> dict:
    linjer = tekst.split("\n")
    punktnummer = 1

    domsslutning_dict = {}
    romertall = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI",
                 "XVII", "XVIII", "XIV", "XV"]

    # Looper gjennom linjer for å finne punktene og legge hvert punkt som egen key/value i en dictionary
    for linje in linjer:
        if linje.startswith(f"{romertall[punktnummer - 1]}."):
            domsslutning_dict[punktnummer] = linje
            punktnummer += 1
        elif linje.startswith(f"{romertall[punktnummer - 1]}"):
            domsslutning_dict[punktnummer] = linje
            punktnummer += 1
        elif punktnummer - 1 in domsslutning_dict:
            domsslutning_dict[punktnummer - 1] = domsslutning_dict[punktnummer - 1] + linje
    return domsslutning_dict


# Finner ut om avsnittet gjelder dom eller frifinnelse. Kobler dom med lover og paragrefer. Returnerer kun lover og
# paragrafer dersom funksjonen ikke finner ut om det er domfellelse eller frifinnelse
def finn_dom_og_lov(tekst: str) -> dict:
    frifunnet = ["frifunnet", "frifinnes", "frifunnen"]
    domt = ["dømmes", "dømt", "idømmes", "idømt", "dømd", "dømmast"]

    if er_i_avsnitt(frifunnet, tekst) and er_i_avsnitt(domt, tekst):
        print("Klarer ikke å tolke om det er frifinnelse eller domfellelse")
        log.feilmeldinger.append(
            "Både dømt og frifunnet i samme avsnitt. Klarer ikke å tolke frifinnelse eller domfellelse")
    elif er_i_avsnitt(domt, tekst):
        dom_og_lov = koble_dom_og_lov(True, finn_lov_og_paragraf(tekst))
        if dom_og_lov.get("dømt"):
            return dom_og_lov
        else:
            return {"dømt": ""}
    elif er_i_avsnitt(frifunnet, tekst):
        dom_og_lov = koble_dom_og_lov(False, finn_lov_og_paragraf(tekst))
        if dom_og_lov.get("frifunnet"):
            return dom_og_lov
        else:
            return {"frifunnet": ""}
    elif tekst:
        return {"uvisst": finn_lov_og_paragraf(tekst)}


def koble_motpart_til_lov_og_paragraf(motpart, dom_og_lov_liste_med_motpart):
    for p in motpart:
        d = {}
        for i in dom_og_lov_liste_med_motpart:
            if i[1] == p:
                (dom, lov), = i[0].items()
                d.setdefault(f"{dom}", []).append(lov)
        if "dømt" in d and d["dømt"] != [""]:
            while "" in d["dømt"]:
                d["dømt"].remove("")
            domt_liste_formatert = flatten_top_level(d["dømt"])
            p["dømt"] = domt_liste_formatert
        if "frifunnet" in d:
            if d["frifunnet"] == [""]:
                p["frifunnet"] = ["true"]
            else:
                while "" in d["frifunnet"]:
                    d["frifunnet"].remove("")
                frifunnet_liste_formatert = flatten_top_level(d["frifunnet"])
                p["frifunnet"] = frifunnet_liste_formatert


def finn_dom_og_lov_fra_nummerert_domsslutning(domsslutning: str, motpart: list, romertall=False) -> tuple:
    dom_og_lov_liste = []
    dom_og_lov_liste_med_motpart = []
    # Dictionary for å samle navn på tiltalte og avsnitt i domsslutning. Brukes til å tolke eventuell straff
    navn_og_avsnitt = {}

    if romertall:
        domsslutning_dict = finn_avsnitt_i_nummerert_domsslutning_romertall(domsslutning)
    else:
        domsslutning_dict = finn_avsnitt_i_nummerert_domsslutning(domsslutning)

    for avsnitt in domsslutning_dict.values():
        dom_og_lov = finn_dom_og_lov(avsnitt)
        if dom_og_lov:
            dom_og_lov_liste.append(dom_og_lov)
            # Koble dom og lov til person
            if motpart:
                for p in motpart:
                    if p["navn"] in avsnitt:
                        dom_og_lov_liste_med_motpart.append([dom_og_lov, p])
                        # Legger til navn og avsnitt i dictionary
                        if not p["navn"] in navn_og_avsnitt:
                            navn_og_avsnitt[p["navn"]] = [avsnitt]
                        else:
                            navn_og_avsnitt[p["navn"]].append(avsnitt)

    # Looper gjennom motparter og legger til straff
    for p in motpart:
        avsnitt = [a for a in domsslutning_dict.values()]
        for a in avsnitt:
            straff = dom_strenghetsgrad.finn_type_straff([a])
            if straff:
                if p["navn"] in a:
                    if "straff" in p:
                        p["straff"].update(straff)
                    else:
                        p["straff"] = straff

    return dom_og_lov_liste, dom_og_lov_liste_med_motpart


def finn_dom_og_lov_fra_unummerert_domsslutning(domsslutning: str, motpart: list) -> tuple:
    dom_og_lov_liste = []
    dom_og_lov_liste_med_motpart = []
    # Dictionary for å samle navn på tiltalte og avsnitt i domsslutning. Brukes til å tolke eventuell straff
    try:
        dom_og_lov = finn_dom_og_lov(domsslutning)
        if dom_og_lov:
            dom_og_lov_liste.append(dom_og_lov)
            if motpart:
                # Sjekk om flere motpartsnavn nevnes, for å unngå å koble lov på feil navn
                motparter = [p["navn"] for p in motpart if p["navn"] in domsslutning]
                if len(motparter) == 1:
                    for p in motpart:
                        if p["navn"] in domsslutning:
                            dom_og_lov_liste_med_motpart.append([dom_og_lov, p])

        # Looper gjennom motparter og legger til straff
        for p in motpart:
            if p["navn"] in domsslutning:
                if "tittel" not in p:
                    straff = dom_strenghetsgrad.finn_type_straff([domsslutning])
                    if straff:
                        if "straff" in p:
                            p["straff"].update(straff)
                        else:
                            p["straff"] = straff

        return dom_og_lov_liste, dom_og_lov_liste_med_motpart
    except TypeError as e:
        print(f"Fant ikke dom og lov: {e}")
        log.feilmeldinger.append(f"Fant ikke dom og lov: {e}")
        pass


def finn_alle_paragrafer_fra_domsslutning(dom_og_lov_liste):
    domt_list = []
    domt_list_formatert = []
    frifunnet_list = []
    frifunnet_list_formatert = []
    uvisst_list = []
    uvisst_list_formatert = []
    dom_og_lov_dict = {}
    for i in dom_og_lov_liste:
        if "dømt" in i:
            for element in i["dømt"]:
                domt_list.append(element)
        if "frifunnet" in i:
            for element in i["frifunnet"]:
                frifunnet_list.append(element)
        if "uvisst" in i:
            for element in i["uvisst"]:
                uvisst_list.append(element)

    if domt_list:
        for i in domt_list:
            if i not in domt_list_formatert:
                domt_list_formatert.append(i)
        dom_og_lov_dict["dømt"] = domt_list_formatert
    if frifunnet_list:
        for i in frifunnet_list:
            if i not in frifunnet_list_formatert:
                frifunnet_list_formatert.append(i)
        dom_og_lov_dict["frifunnet"] = frifunnet_list_formatert
    if uvisst_list:
        for i in uvisst_list:
            if i not in uvisst_list_formatert:
                uvisst_list_formatert.append(i)
        dom_og_lov_dict["uvisst"] = uvisst_list_formatert

    # Legger til "true" hvis frifunnet uten dom og paragraf
    for i in dom_og_lov_liste:
        if "frifunnet" in i and not frifunnet_list:
            dom_og_lov_dict["frifunnet"] = ["true"]

    return dom_og_lov_dict


def finn_dom_og_lov_fra_domsslutning(domsslutning: str, motpart: list):
    gruppert_med_navn = domsslutning_er_gruppert_med_navn(domsslutning, motpart)
    if gruppert_med_navn:
        try:
            domsslutning_gruppert = finn_avsnitt_gruppert_med_navn(domsslutning, gruppert_med_navn)
            fullstendig_dom_og_lov_liste = []
            for domsslutning_del in domsslutning_gruppert:
                if domsslutning_er_nummerert(domsslutning_del):
                    dom_og_lov_liste, dom_og_lov_liste_med_motpart = finn_dom_og_lov_fra_nummerert_domsslutning(
                        domsslutning_del, motpart)
                    if motpart:
                        koble_motpart_til_lov_og_paragraf(motpart, dom_og_lov_liste_med_motpart)
                else:
                    dom_og_lov_liste, dom_og_lov_liste_med_motpart = finn_dom_og_lov_fra_unummerert_domsslutning(
                        domsslutning_del, motpart)
                    if motpart:
                        koble_motpart_til_lov_og_paragraf(motpart, dom_og_lov_liste_med_motpart)
                fullstendig_dom_og_lov_liste.append(dom_og_lov_liste)
            # Sortere dommer og lover
            lov_og_paragrafer = {}
            try:
                for i in fullstendig_dom_og_lov_liste:
                    for k, v in i[0].items():
                        if k == "dømt" or k == "frifunnet" or k == "uvisst":
                            lov_og_paragrafer[k] = [e for e in v]
            except IndexError:
                pass
            return finn_alle_paragrafer_fra_domsslutning([lov_og_paragrafer])
        except TypeError as e:
            log.feilmeldinger.append(f"Finner ikke dom og lov: {e}")
            print(e)

    elif domsslutning_er_nummerert(domsslutning):
        try:
            dom_og_lov_liste, dom_og_lov_liste_med_motpart = finn_dom_og_lov_fra_nummerert_domsslutning(domsslutning,
                                                                                                        motpart)
            if motpart:
                koble_motpart_til_lov_og_paragraf(motpart, dom_og_lov_liste_med_motpart)
            return finn_alle_paragrafer_fra_domsslutning(dom_og_lov_liste)
        except TypeError as e:
            log.feilmeldinger.append(f"Finner ikke dom og lov: {e}")
            print(e)
    elif domsslutning_er_nummerert_med_romertall(domsslutning):
        try:
            dom_og_lov_liste, dom_og_lov_liste_med_motpart = finn_dom_og_lov_fra_nummerert_domsslutning(domsslutning,
                                                                                                        motpart, True)
            if motpart:
                koble_motpart_til_lov_og_paragraf(motpart, dom_og_lov_liste_med_motpart)
            return finn_alle_paragrafer_fra_domsslutning(dom_og_lov_liste)
        except TypeError as e:
            log.feilmeldinger.append(f"Finner ikke dom og lov: {e}")
            print(e)
    else:
        try:
            dom_og_lov_liste, dom_og_lov_liste_med_motpart = finn_dom_og_lov_fra_unummerert_domsslutning(domsslutning,
                                                                                                         motpart)
            if motpart:
                koble_motpart_til_lov_og_paragraf(motpart, dom_og_lov_liste_med_motpart)
            return finn_alle_paragrafer_fra_domsslutning(dom_og_lov_liste)
        except TypeError as e:
            log.feilmeldinger.append(f"Finner ikke dom og lov: {e}")
            print(e)


def tolk_dato(avsnitt: str, motpart: list):
    for p in motpart:
        if p["navn"] in avsnitt:
            avsnitt_split_via_navn = avsnitt.split(p["navn"])[1]
            try:
                if "født" in avsnitt:
                    try:
                        fodselsdato = avsagt_dato.finn_regex_dato(avsnitt_split_via_navn.split("født")[1])
                        p["fodselsdato"] = dateparser.parse(fodselsdato, settings={"DATE_ORDER": "DMY"}).strftime(
                            "%Y-%m-%d")
                    except AttributeError:
                        continue
                elif "fødd" in avsnitt:
                    try:
                        fodselsdato = avsagt_dato.finn_regex_dato(avsnitt_split_via_navn.split("fødd")[1])
                        p["fodselsdato"] = dateparser.parse(fodselsdato, settings={'DATE_ORDER': 'DMY'}).strftime(
                            "%Y-%m-%d")
                    except AttributeError:
                        continue
                elif "f." in avsnitt:
                    try:
                        fodselsdato = avsagt_dato.finn_regex_dato(avsnitt_split_via_navn.split("f.")[1])
                        p["fodselsdato"] = dateparser.parse(fodselsdato, settings={'DATE_ORDER': 'DMY'}).strftime(
                            "%Y-%m-%d")
                    except AttributeError:
                        continue
            except IndexError:
                continue


def finn_fodselsdato(domsslutning: str, motpart: list):
    if domsslutning_er_nummerert(domsslutning):
        domsslutning_dict = finn_avsnitt_i_nummerert_domsslutning(domsslutning)
        for avsnitt in domsslutning_dict.values():
            try:
                tolk_dato(avsnitt, motpart)
            except TypeError:
                continue
    else:
        try:
            tolk_dato(domsslutning, motpart)
        except TypeError as e:
            log.feilmeldinger.append(f"Fant ikke fødselsdato: {e}")
            print(e)
            pass


def finn_lov_fra_tiltale(doc):
    page2_to_end = "".join([page.get_text("text") for page in doc if not str(page).startswith("page 0")])
    ordliste = ["Rettens vurdering", "RETTENS VURDERING", "Vurderinga til retten", "R e t t e n s  v u r d e r i n g",
                "rettens vurdering", "nedla slik påstand", "la ned påstand", "la ned slik påstand"]
    søkeord = ""
    for k in ordliste:
        if k in page2_to_end:
            søkeord = [{"": k}]
            break
    if not søkeord:
        return "Fant ikke ord"

    tekst = dommere_og_parter.tekst_mellom_ord(page2_to_end, søkeord)
    try:
        lov_og_paragraf = finn_lov_og_paragraf(tekst)
        return lov_og_paragraf
    except TypeError as e:
        return e
