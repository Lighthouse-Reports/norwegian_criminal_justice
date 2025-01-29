from __future__ import annotations

from . import constants as c, log, domsslutning

import re


def test_formulering(formuleringer, full_tekst):
    for formulering in formuleringer:
        if formulering in full_tekst:
            return formulering
        for i in range(len(formulering)):
            if formulering[i] == ' ':
                modifisert_formulering = formulering[:i] + '\n' + formulering[i+1:]
                if modifisert_formulering in full_tekst:
                    return modifisert_formulering
    return False


def enstemmig_eller_dissens(full_text: str) -> tuple | None:
    full_text = domsslutning.fjern_domsslutning_i_innholdsfortegnelse(full_text)
    enstemmig = False
    dissens = False
    for formulering in c.DOMSSLUTNING_FORMULERINGER:
        if formulering in full_text:
            #regex = re.compile(r'\n(.*)\s+?(.*)\s+?(.*)\s+?\n' + formulering)
            regex = re.compile(r'([\s\S]*?)(?=' + formulering + r')')
            avsnitt = regex.search(full_text).group()
            avsnitt_liste = avsnitt.split('\n')
            avsnitt_liste = [x for x in avsnitt_liste if x not in ["", ", ", " "]][::-1]
            avsnitt_til_db = "\n".join(avsnitt_liste[0:20][::-1])
            log.tekst_dissens_vs_enstemmig = avsnitt_til_db
            try:
                for i in avsnitt_liste[0:20]:
                    if "enstemmig" in i:
                        enstemmig = True
                    elif "samrøystes" in i:
                        enstemmig = True
                    elif "einstemmig" in i:
                        enstemmig = True
                    elif "dissens" in i:
                        dissens = True
                    elif "flertall" in i.lower():
                        dissens = True
                    elif "mindretall" in i.lower():
                        dissens = True
                if dissens:
                    return "dissens", avsnitt
                elif enstemmig:
                    return "enstemmig", avsnitt
                else:
                    return "uvisst", avsnitt

            except AttributeError as e:
                log.feilmeldinger.append(f"Finner ikke om dom er enstemmig eller dissens: {e}")
                print(e)
                return None, avsnitt

    return None, None


def finn_dommeres_standpunkt(flertall_bool, flertall_eller_mindretall_split, fagdommere=None, meddommere=None):
    if flertall_bool:
        string1 = "flertall"
        string2 = "mindretall"
    else:
        string1 = "mindretall"
        string2 = "flertall"

    if fagdommere:
        for fagdommer in fagdommere:
            fagdommer_etternavn = fagdommer["navn"].split()[-1]
            if len(fagdommer_etternavn) > 1:
                for avsnitt in flertall_eller_mindretall_split:
                    if fagdommer_etternavn in avsnitt and string2 in avsnitt.lower():
                        log.feilmeldinger.append(f"Finner ikke dommers standpunkt: {string2} i samme avsnitt som fagdommer under tolkning av {string1}.")
                        raise ValueError(f"{string2} i samme avsnitt som fagdommer under tolkning av {string1}.")
                    if fagdommer_etternavn in avsnitt and string1 in avsnitt.lower():
                        fagdommer["flertall_eller_mindretall"] = string1
                        break
                    if len(fagdommere) == 1:
                        if "fagdommer" in avsnitt.lower() and string1 in avsnitt.lower():
                            fagdommer["flertall_eller_mindretall"] = string1
                            break
                        if "rettens leder" in avsnitt.lower() and string1 in avsnitt.lower():
                            fagdommer["flertall_eller_mindretall"] = string1
                            break
                        if "administrator" in avsnitt.lower() and string1 in avsnitt.lower():
                            fagdommer["flertall_eller_mindretall"] = string1
                            break
    if meddommere:
        for meddommer in meddommere:
            meddommer_etternavn = meddommer["navn"].split()[-1]
            if len(meddommer_etternavn) > 1:
                for avsnitt in flertall_eller_mindretall_split:
                    if meddommer_etternavn in avsnitt and string1 in avsnitt.lower():
                        meddommer["flertall_eller_mindretall"] = string1
                        break
                    if meddommer_etternavn in avsnitt and string2 in avsnitt.lower():
                        log.feilmeldinger.append(f"Finner ikke dommers standpunkt: {string2} i samme avsnitt som fagdommer under tolkning av {string1}.")
                        raise ValueError(f"{string2} i samme avsnitt som meddommer under tolkning av {string1}.")


def dommere_for_og_imot(full_text, fagdommere, meddommere) -> tuple:
    try:
        flertall_formuleringer = ["Rettens flertall, bestående av", "Et flertall av rettens medlemmer",
                                  "flertall bestående av", "flertall \nbestående av", "Flertallet består av", "Flertallet \nbestår av", "Flertallet, bestående av", "flertall, bestående av",
                                  "Flertallet,", "Rettens flertall på", "Rettens flertall,", "flertall \(",
                                  "Flertallet \(", "Flertallet \–",
                                  "Rettens flertall", "Flertallet", "flertall"]

        mindretall_formuleringer = ["Rettens mindretall, bestående av", "Et mindretall av rettens medlemmer",
                                    "mindretall bestående av", "Mindretallet består av", "Mindretallet, bestående av", "mindretall, bestående av",
                                    "Mindretallet,", "Rettens mindretall på", "Rettens mindretall,", "mindretall \(",
                                    "Mindretallet \(", "Mindretallet \–",
                                    "Rettens mindretall", "Mindretallet", "mindretall"]

        beste_flertall_formulering = test_formulering(flertall_formuleringer, full_text)
        if beste_flertall_formulering:
            formulering = beste_flertall_formulering
            regex = re.compile(r'(' + formulering + r'(.|\n)*)\n\n')
            flertall = regex.search(full_text).group(1)
            if "mindretall" in flertall:
                flertall = flertall.split("mindretall")[0]
            if "Mindretall" in flertall:
                flertall = flertall.split("Mindretall")[0]
            flertall_split = flertall.split("\n \n")
            finn_dommeres_standpunkt(True, flertall_split, fagdommere, meddommere)

        beste_mindretall_formulering = test_formulering(mindretall_formuleringer, full_text)
        if beste_mindretall_formulering:
            formulering = beste_mindretall_formulering
            regex = re.compile(r'(' + formulering + r'(.|\n)*)\n\n')
            mindretall = regex.search(full_text).group(1)
            if "flertall" in mindretall:
                mindretall = mindretall.split("flertall")[0]
            if "Flertall" in mindretall:
                mindretall = mindretall.split("Flertall")[0]
            mindretall_split = mindretall.split("\n \n")
            finn_dommeres_standpunkt(False, mindretall_split, fagdommere, meddommere)

        return fagdommere, meddommere

    except (AttributeError, ValueError) as e:
        log.feilmeldinger.append(f"Feil under tolkning av dommere for og imot: {e}")
        print(f"Feil under dommere for og imot: {e}")

