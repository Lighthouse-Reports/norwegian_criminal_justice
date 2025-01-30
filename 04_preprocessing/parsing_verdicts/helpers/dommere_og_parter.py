from __future__ import annotations

from . import log, constants as c
import re


# Finn tittel og navn på dommere
def tittel_og_navn(result: str, titler: list, funksjon: str) -> dict:
    for tittel in titler:
        # Sjekker om tekst starter med tittel
        result_clean_list = result.strip().replace(":", "").split()
        try:
            if result_clean_list[0].lower().startswith(tittel):
                # regex = re.compile(r'(^[A-ZÆØÅ]{1}[ a-zæøå\n\-]{0,200})([A-ZÆØÅa-zæøå\-äöëï \n]+)')
                # regex = re.compile(r'(^[A-ZÆØÅ]{1}[ a-zæøå\n\-.\d/]{0,200})([A-ZÆØÅa-zæøå\-äöëï \n]+)')
                regex = re.compile(
                    r'(^[A-ZÆØÅa-zæøå()]{0,5}[ a-zæøå\n\-.\d/()]{0,200})([A-ZÆØÅa-zæøå.\-äöëïü\'éèáàóò \n]+)')
                tittel = regex.search(result.strip()).group(1).strip().replace("\n", " ")
                dommer = regex.search(result.strip()).group(2).strip().replace("\n", " ").replace("  ", " ")
                # Unngår at navnet ender med "m"
                if dommer.endswith(" m"):
                    dommer = dommer[:-2]
                return {"tittel": tittel, "navn": dommer, "funksjon": funksjon}
        except IndexError:
            continue

    # Hvis ikke tittel er funnet
    regex = re.compile(r'(^[A-ZÆØÅ][ a-zæøå\n\-]{0,200}[A-ZÆØÅa-zæøå.\-äöëïü\'éèáàóò \n]+)')
    dommer = regex.search(result.strip()).group(1).strip().replace("\n", " ").replace("  ", " ")
    if dommer.endswith(" m"):
        dommer = dommer[:-2]
    return {"navn": dommer, "funksjon": funksjon}


def tekst_mellom_ord(tekst: str, ordliste: list, streng_startverdi: bool = False,
                     streng_sluttverdi: bool = False) -> str | None:
    kandidater = []
    for ord in ordliste:
        for k, v in ord.items():
            try:
                if streng_startverdi:
                    kandidat = re.search(f'\s{k}\s(.*){v}', tekst, flags=re.S).group(1)
                elif streng_sluttverdi:
                    kandidat = re.search(f'({k}.*)\s{v}\s', tekst, flags=re.S).group(1)
                else:
                    # kandidat = re.search(f'{k}(.*){v}', tekst, flags=re.S).group(1)
                    kandidat = re.search(r'(?<=' + k + r')([\s\S]*?)(?=' + v + r')', tekst, flags=re.S).group(1)

                kandidater.append(kandidat)

            except AttributeError as e:
                continue
    # Sammenligne lengden på treffene, velge riktig lengde
    kandidater_sortert = sorted(kandidater, key=len)
    try:
        if len(kandidater_sortert[0]) > 12:
            return kandidater_sortert[0]
        elif len(kandidater_sortert[1]) > 12:
            return kandidater_sortert[1]
        else:
            return kandidater_sortert[2]
    except IndexError:
        return None


def finn_dommer(dom: str, fra_til: list, titler: list, funksjon: str, skille="\n \n") -> list:
    result = tekst_mellom_ord(dom, fra_til).strip()

    dommere = []
    # Sjekk om det er flere dommere
    # Oftest vil flere dommere være adskilt med to linjeskift
    if skille in result:
        dommere_liste = [i.strip() for i in result.split(skille)]
        # Unngå tittel som fornavn
        for tittel in titler:
            for tekst in dommere_liste:
                # Fjerner listeelement dersom det kun er tittel i elementet
                if tekst.lower().startswith(tittel):
                    if len(tekst.split("\n")) == 1:
                        dommere_liste.remove(tekst)
                    else:
                        # Endrer listeelement til navn dersom det er noe etter tittel og linjeskift
                        tekst = tekst.split("\n")[1]

        enkeltdommer_liste = [i.split("\n") for i in dommere_liste]
        # Fjerner eventuelle tomme lister i listen
        while [":"] in enkeltdommer_liste:
            enkeltdommer_liste.remove([":"])
        while [""] in enkeltdommer_liste:
            enkeltdommer_liste.remove([""])
        for dommer in enkeltdommer_liste:
            if sum(s.isdigit() for s in dommer[0]) > 1:
                continue
            dommer_joined = ' '.join(dommer)
            dommere.append(tittel_og_navn(dommer_joined, titler, funksjon))

    elif "   " in result:
        dommere_liste = [i.strip() for i in result.split("   ")]
        enkeltdommer_liste = [i.split("\n") for i in dommere_liste]
        # Fjerner eventuelle tomme lister i listen
        while [":"] in enkeltdommer_liste:
            enkeltdommer_liste.remove([":"])
        while [""] in enkeltdommer_liste:
            enkeltdommer_liste.remove([""])
        for dommer in enkeltdommer_liste:
            if sum(s.isdigit() for s in dommer[0]) > 1:
                continue
            dommer_joined = ' '.join(dommer)
            dommere.append(tittel_og_navn(dommer_joined, titler, funksjon))
    else:
        dommere.append(tittel_og_navn(result, titler, funksjon))
    return dommere


def finn_fagdommer(dom: str) -> list | False:
    try:
        fra_til = c.FAGDOMMER_FRA_TIL
        dommertitler = c.FAGDOMMER_TITLER
        return finn_dommer(dom, fra_til, dommertitler, "fagdommer")
    except AttributeError as e:
        log.feilmeldinger.append(f"Finner ikke fagdommer: {e} ")
        return None


def finn_meddommer(dom: str, lagmannsrett=False) -> list | None:
    try:
        if lagmannsrett:
            fra_til = c.MEDDOMMER_LAGMANNSRETT_FRA_TIL
        else:
            fra_til = c.MEDDOMMER_TINGRETT_FRA_TIL

        titler = c.MEDDOMMER_TITLER
        return finn_dommer(dom, fra_til, titler, "meddommer")
    except AttributeError as e:
        log.feilmeldinger.append(f"Finner ikke meddommer: {e}")
        return None


def finn_meddommer_i_bunn_av_dom(dom: str) -> list | None:
    try:
        fra_til = [{"Retten hevet": "Dokument i samsvar"}, {"Retten hevet": "Til deg som"}]
        titler = c.MEDDOMMER_TITLER
        return finn_dommer(dom, fra_til, titler, "meddommer", "\n")
    except AttributeError as e:
        log.feilmeldinger.append(f"Finner ikke meddommer i bunn av dokument: {e}")


def finn_part1(dom: str):
    try:
        fra_til = [{"Påtale": "mot"}, {"Staten": "mot"}, {"Oslo": "mot"}, {"Agder": "mot"}, {"Finnmark": "mot"},
                   {"Innlandet": "mot"}, {"Møre": "mot"}, {"Nordland": "mot"}, {"Sør": "mot"}, {"Troms": "mot"},
                   {"Trøndelag": "mot"}, {"Vest": "mot"}, {"Øst": "mot"}, {"Saksøker": "Saksøkt"},
                   {"Den offentlige påtalemyndighet": "mot"}]
        result = tekst_mellom_ord(dom, fra_til, False, True).strip()

        if result.startswith("Den offentlige påtalemyndighet"):
            result_split = [" ".join(result.strip().split()[0:3])] + result.strip().split()[3:]
        else:
            result_split = result.strip().split()

        if len(result_split) > 2:
            titler = ["politiadvokat", "politifullmektig", "statsadvokat"]
            part1_repr = tittel_og_navn(" ".join(result_split[1:]), titler, "Part 1")
            return {
                "part1": result_split[0],
                "repr": part1_repr
            }
        return {
            "part1": result
        }
    except AttributeError as e:
        log.feilmeldinger.append(f"Finner ikke part 1: {e}")
        return None


def finn_motpart(dom: str, lagmannsrett=False) -> list | None:
    try:
        if lagmannsrett:
            fra_til = [{"Tiltalt": "Påtalemyndighet"}, {"Tiltalt": "Ingen begrensninger"}]
        else:
            fra_til = [{"mot": "Fornærmede"}, {"mot": "Ingen begrensninger"}, {"mot": "Ingen avgrensing"},
                       {"mot": "Kan bare"}, {"mot": "Retten har forbudt"}, {"mot": ""}]
        titler = ["advokat", "advokatfullmektig", "statsadvokat"]
        return finn_motparter(dom, fra_til, titler, "motpart")
    except AttributeError as e:
        log.feilmeldinger.append(f"Finner ikke motpart: {e}")
        return None


def finn_motparter(dom: str, fra_til: list, titler: list, funksjon: str) -> list:
    result = tekst_mellom_ord(dom, fra_til, True).strip()
    motparter = []
    # Sjekk om det er flere motparter
    # Oftest vil flere motparter være adskilt med to linjeskift
    if "\n" in result:
        try:
            motparter_liste = [i.strip() for i in result.split("\n")]
            # Unngå tittel som fornavn
            enkeltmotpart_liste = [i.split("\n") for i in motparter_liste]
            while [""] in enkeltmotpart_liste:
                enkeltmotpart_liste.remove([""])

            for motpart in enkeltmotpart_liste:
                # Sjekker om elementet inneholder tall
                motpart_joined = ' '.join(motpart)
                if any(char.isdigit() for char in motpart_joined):
                    continue
                elif motpart_joined == "født":
                    continue
                motparter.append(tittel_og_navn(motpart_joined, titler, funksjon))
        except AttributeError as e:
            print(e)
            pass

    elif "   " in result:
        motparter_liste = [i.strip() for i in result.split("   ")]
        enkeltmotpart_liste = [i.split("\n") for i in motparter_liste]
        # Fjerner eventuelle tomme lister i listen
        while [""] in enkeltmotpart_liste:
            enkeltmotpart_liste.remove([""])
        for motpart in enkeltmotpart_liste:
            motpart_joined = ' '.join(motpart)
            motparter.append(tittel_og_navn(motpart_joined, titler, funksjon))
    else:
        motparter.append(tittel_og_navn(result, titler, funksjon))
    return motparter


def finn_adresse_motpart(doc, motpart):
    if len(doc) > 1:
        page2 = doc[1].get_text("text")
        split_per_linje = page2.split("\n")
        if motpart:
            for p in motpart:
                for linje in split_per_linje:
                    if p["navn"] in linje:
                        index = split_per_linje.index(linje)
                        try:
                            linje2 = split_per_linje[index + 1]
                        except IndexError:
                            linje2 = ""
                        try:
                            linje3 = split_per_linje[index + 2]
                        except IndexError:
                            linje3 = ""
                        tre_linjer = linje + linje2 + linje3
                        try:
                            if "bor i" in tre_linjer:
                                adresse = \
                                    re.search(f'bor i(.*)\\.', tre_linjer, flags=re.S).group(1).strip().split(".")[0]
                                p["adresse"] = adresse
                            elif "bur i" in tre_linjer:
                                adresse = \
                                    re.search(f'bur i(.*)\\.', tre_linjer, flags=re.S).group(1).strip().split(".")[0]
                                p["adresse"] = adresse
                            elif "adresse" in tre_linjer:
                                adresse = \
                                    re.search(f'adresse(.*)\\.', tre_linjer, flags=re.S).group(1).strip().split(".")[0]
                                p["adresse"] = adresse
                            elif "soner" in tre_linjer or "sonar" in tre_linjer:
                                adresse = \
                                    re.search(f'soner(.*)\\.', tre_linjer, flags=re.S).group(1).strip().split(".")[0]
                                p["adresse"] = "Soner fengselsstraff"
                        except AttributeError:
                            continue
                        break
