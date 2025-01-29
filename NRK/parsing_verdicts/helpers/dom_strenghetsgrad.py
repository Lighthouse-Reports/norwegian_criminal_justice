import re


# FINN TYPE STRAFF
# Forvaring, fengsel, samfunnstraff eller bøter

def gjør_om_til_int(verdi) -> int:
    nums = {"en": 1, "ett": 1, "to": 2, "tre": 3, "fire": 4, "fem": 5, "seks": 6, "sju": 7, "åtte": 8, "ni": 9}
    for k, v in nums.items():
        if k == verdi:
            return v


# Funksjon som sjekker om straffen er betinget eller ubetinget. Returnerer tuple med (betinget, ubetinget, lengde_på_ubetinget)
def betinget_eller_ubetinget(avsnitt: int) -> (bool, bool, int):
    regex_iter = re.finditer(
        r'(?P<betinget>[Ff]ullbyrding(en|a)?|[Ff]ullbyrdelse)(\s+av\s+(fengsels)?straff(en|a))?\s+(utsettes|(blir|vert)(\s+i\s+medh[o|a]ld\s+av\s+straffelov[en|a]\s+§\s?34)?\s+utsett)|(([Ff]ullbyrding(en|a)?|[Ff]ullbyrdelse)\s+av\s+)(?P<db_lengde_1>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?((?P<db_aar_1>år)|(?P<db_maaneder_1>måneder|månader)|(?P<db_dager_1>dager|dagar)|(?P<db_uker_1>uker|ukar))(\s+av\s+(fengsels)?straff(en|a))?\s+(utsettes|(blir|vert)\s+utsett)|((?P<db_f_lengde_2>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)\s+?(\s?[-|–]\s?(\w+|\d+)\s?[-|–]\s?)?((?P<db_f_aar_2>år)|(?P<db_f_maaneder_2>måneder|månader)|(?P<db_f_dager_2>dager|dagar))\s+og\s+)?(?P<db_lengde_2>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)\s+?(\s?[-|–]\s?(\w+|\d+)\s?[-|–]\s?)?(\s+)?((?P<db_aar_2>år)|(?P<db_maaneder_2>måneder|månader)|(?P<db_dager_2>dager|dagar)|(?P<db_uker_2>uker|ukar))\s+(av\s+straffen\s+)?((gjøres\s+)?betinget|utsettes)|[Ff]engsel\s+i\s+(?P<betinget_3>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)\s+?(\s?[-|–]\s?\w+\s?[-|–]\s?)?((år)|(måneder|månader)|(dager|dagar)|(uker|ukar)),?\s+som\s+gjøres\s+betinget|(?P<db_f_lengde_4>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)\s+?(\s?[-|–]\s?\w+\s?[-|–]\s?)?((?P<db_f_aar_4>år)|(?P<db_f_maaneder_4>måneder|månader)|(?P<db_f_dager_4>dager|dagar)|(?P<db_f_uker_4>uker|ukar))\s+og\s+(?P<db_lengde_4>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)\s+?(\s?[-|–]\s?\w+\s?[-|–]\s+?)?((?P<db_aar_4>år)|(?P<db_maaneder_4>måneder|månader)|(?P<db_dager_4>dager|dagar)|(?P<db_uker_4>uker|ukar))\s+(gjøres)?\s+betinget|(?P<db_lengde_5>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)\s+?(\s?[-|–]\s?\w+\s?[-|–]\s?)?((?P<db_aar_5>år)|(?P<db_maaneder_5>måneder|månader)|(?P<db_dager_5>dager|dagar)|(?P<db_uker_5>uker|ukar))\s+betinget|(?P<db_lengde_6>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?((?P<db_aar_6>år)|(?P<db_maaneder_6>måneder|månader)|(?P<db_dager_6>dager|dagar)|(?P<db_uker_6>uker|ukar))\s+(blir|vert)\s+gjort\s+på\s+vilkår',
        avsnitt
    )
    betinget = delvis_betinget = False
    for i in regex_iter:
        if i.group("betinget"):
            betinget = True
            return True, False, 0
        else:
            lengde_1 = lengde_1_type = lengde = lengde_type = None
            for k, v in i.groupdict().items():
                if v:
                    if k.startswith("db_f_lengde"):
                        lengde_1 = v
                        if not lengde_1.isnumeric():
                            lengde_1 = gjør_om_til_int(lengde_1)
                    if k.startswith("db_lengde"):
                        lengde = v
                        if not lengde.isnumeric():
                            lengde = gjør_om_til_int(lengde)
                    if k.startswith("db_f_aar"):
                        lengde_1_type = "aar"
                    if k.startswith("db_f_maaneder"):
                        lengde_1_type = "maaneder"
                    if k.startswith("db_f_uker"):
                        lengde_1_type = "uker"
                    if k.startswith("db_f_dager"):
                        lengde_1_type = "dager"
                    if k.startswith("db_aar"):
                        lengde_type = "aar"
                    if k.startswith("db_maaneder"):
                        lengde_type = "maaneder"
                    if k.startswith("db_uker"):
                        lengde_type = "uker"
                    if k.startswith("db_dager"):
                        lengde_type = "dager"
            if lengde_1:
                if lengde_1_type == "aar":
                    lengde_1 = int(lengde_1) * 360
                elif lengde_1_type == "maaneder":
                    lengde_1 = int(lengde_1) * 30
                elif lengde_1_type == "uker":
                    lengde_1 = int(lengde_1) * 7
            if lengde:
                if lengde_type == "aar":
                    lengde = int(lengde) * 360
                elif lengde_type == "maaneder":
                    lengde = int(lengde) * 30
                elif lengde_type == "uker":
                    lengde = int(lengde) * 7
            if lengde_1:
                lengde += lengde_1
            return False, True, lengde
    return False, False, 0


# Funksjon som finner forvaring, fengselsstraff, samfunnsstraff og/eller bøter. Returnerer dict
def finn_type_straff(domsslutning: list) -> dict:
    forvaring = fengsel = samfunnsstraff = bot = False
    straff_dict = {}
    for avsnitt in domsslutning:
        if "forvaring" in avsnitt:
            forvaring = True
            straff_dict["forvaring"] = "true"
        if "fengsel i" in avsnitt or "dager fengsel" or "måneder fengsel" or "år fengsel" in avsnitt:
            fengsel = True
            betinget, delvis_betinget, betinget_dager = betinget_eller_ubetinget(avsnitt)
            regex_iter = re.finditer(
                r'(?P<sub>[Ss]ubsidiært|subsidiære?\s?fengselsstraff(en|a)?\s?settes\s?til)?\s?fengsel\si\s\s?\s?\s?\s?(?P<lengde_1>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s?\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?\s?((?P<aar>år)|(?P<maaneder_1>måneder|månader)|(?P<dager_1>dager|dagar)|(?P<timer_1>timer|timar))((?P<og>\sog\s)?\s?(?P<lengde_2>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s)?\s?\s?((?P<maaneder_2>måneder|månader)|(?P<dager_2>dager|dagar)|(?P<timer_2>timer|timar))(?P<samfunnsstraff_2>\s?samfunnsstraff)?)?|(?P<sub_2>[Ss]ubsidiært)?\s?\s?(?P<lengde_3>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s?\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?\s?\s?((?P<aar_2>år)|(?P<maaneder_3>måneder|månader)|(?P<dager_3>dager|dagar)s?)\s?\s?fengsel((?P<og_2>\sog\s)?\s?(?P<lengde_4>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s)?\s?\s?((?P<maaneder_4>måneder|månader)|(?P<dager_4>dager|dagar)|(?P<timer_3>timer|timar))(?P<samfunnsstraff_3>\s?samfunnsstraff)?)?',
                avsnitt
            )
            for i in regex_iter:
                # Hvis to ledd i teksten og ikke andre ledd ender med samfunnsstraff
                if i.group("lengde_1"):
                    if i.group("lengde_1").isnumeric():
                        num1 = int(i.group("lengde_1"))
                    else:
                        num1 = gjør_om_til_int(i.group("lengde_1"))
                elif i.group("lengde_3"):
                    if i.group("lengde_3").isnumeric():
                        num1 = int(i.group("lengde_3"))
                    else:
                        num1 = gjør_om_til_int(i.group("lengde_3"))

                if i.group("dager_1") or i.group("dager_3"):
                    dager = num1
                elif i.group("aar") or i.group("aar_2"):
                    dager = num1 * 360
                elif i.group("maaneder_1") or i.group("maaneder_3"):
                    dager = num1 * 30
                # Skiller fengselsstraff fra subsidiær straff
                if i.group("sub") or i.group("sub_2"):
                    type_fengselsstraff = "fengsel_subsidiært_dager"
                else:
                    type_fengselsstraff = "fengsel_dager"

                # Hvis kun ett ledd, send antall dager til dictionary
                if not (i.group("og") or i.group("og_2")) or i.group("samfunnsstraff_2") or i.group("samfunnsstraff_3"):
                    # Unngår at subsidiær fengselsstraff for bot overskriver subsidiær straff for samfunnsstraff
                    if type_fengselsstraff not in straff_dict:
                        straff_dict[type_fengselsstraff] = dager

                # Hvis to ledd, hent ut data fra det andre leddet
                else:
                    if i.group("lengde_2"):
                        if i.group("lengde_2").isnumeric():
                            num2 = int(i.group("lengde_2"))
                        else:
                            num2 = gjør_om_til_int(i.group("lengde_2"))
                    elif i.group("lengde_4"):
                        if i.group("lengde_4").isnumeric():
                            num2 = int(i.group("lengde_4"))
                        else:
                            num2 = gjør_om_til_int(i.group("lengde_4"))
                    if i.group("dager_2") or i.group("dager_4"):
                        dager2 = num2
                    elif i.group("maaneder_2") or i.group("maaneder_4"):
                        dager2 = num2 * 30
                    if type_fengselsstraff not in straff_dict:
                        straff_dict[type_fengselsstraff] = dager + dager2
            if betinget:
                straff_dict["betinget"] = "true"
            elif delvis_betinget:
                straff_dict["betinget"] = "delvis"
                if betinget_dager:
                    straff_dict["fengsel_dager_betinget"] = betinget_dager
        if "samfunnsstraff" in avsnitt:
            samfunnsstraff = True
            regex_iter = re.finditer(
                r'samfunnsstraff\s(i|med)\s\s?\s?\s?\s?(?P<lengde_1>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s?\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?\s?((?P<timer_1>timer|timar))\,?\s+?(og\s)?(med\s?)?(en|ei)?\s?\s?(gjennomføringstid\s?)(og\s\s?subsidiær\s\s?fengselsstraff\s)?(på\s?)?(?P<g_lengde_1>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s?\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?\s?((?P<g_aar_1>år)|(?P<g_maaneder_1>måneder|månader)|(?P<g_dager_1>dager|dagar))|(?P<lengde_2>\d+)\s+(\s?\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?((?P<timer_2>timer|timar))s?\ssamfunnsstraff\s?(med\s?)?(en|ei)?\s?\s?(gjennomføringstid\s?)(og\s\s?subsidiær\s\s?fengselsstraff\s)?(på\s?)?(?P<g_lengde_2>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s?\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?\s?((?P<g_aar_2>år)|(?P<g_maaneder_2>måneder|månader)|(?P<g_dager_2>dager|dagar))|samfunnsstraff\s(i|med)\s\s?\s?\s?\s?((?P<lengde_3>\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s?\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?\s?((?P<timer_3>timer|timar))\.?\s+(Gjennomføringstiden)\s?(skal\svære|settes\stil|blir)\s+?(?P<g_lengde_3>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s?\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?\s?((?P<g_aar_3>år)|(?P<g_maaneder_3><måneder|månader)|(?P<g_dager_3>dager|dagar))|samfunnsstraff\s(i|med)\s\s?\s?\s?\s?(?P<lengde_4>(\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s?\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?\s?((?P<timer_4>timer|timar))\.?\s+(Gjennomføringstiden)\s?(skal\svære|settes\stil|blir)\s+?((?P<g_lengde_4>\d+)|en|ett|to|tre|fire|fem|seks|sju|syv|åtte|ni)(\s?\s?[-|–]\s?\s?\w+\s?\s?[-|–]\s?\s?)?\s?((?P<g_aar_4>år)|(?P<g_maaneder_4>måneder|månader)|(?P<g_dager_4>dager|dagar))',
                avsnitt
            )

            for i in regex_iter:
                lengde = timer = g_lengde = g_aar = g_maaneder = g_dager = None
                for k, v in i.groupdict().items():
                    if v:
                        if k.startswith("lengde"):
                            lengde = v
                            if not lengde.isnumeric():
                                lengde = gjør_om_til_int(lengde)
                        if k.startswith("timer"):
                            timer = v
                        if k.startswith("g_lengde"):
                            g_lengde = v
                            if not g_lengde.isnumeric():
                                g_lengde = gjør_om_til_int(g_lengde)
                        if k.startswith("g_aar"):
                            g_lengde = int(g_lengde) * 360
                        elif k.startswith("g_maaneder"):
                            g_lengde = int(g_lengde) * 30

                if timer:
                    straff_dict["samfunnsstraff_timer"] = int(lengde)
                if g_lengde:
                    straff_dict["samfunnsstraff_gjennomføringstid_dager"] = int(g_lengde)

        if any(word in avsnitt for word in ["bot", "bøtelagt", "bøter"]):
            bot = True
            regex_iter = re.finditer(
                r'en\s+bot(\s+til\s+det\s+offentlige)?\s+(på|stor)\s+((kroner|kr[\.]?)\s+(?P<bot_storrelse_1>\d+[\s\.]?\d+)|(?P<bot_storrelse_2>\d+[\s\.]?\d+)(\s?[-|–]\s+?(\w+|\d+)\s?[-|–]?\s?)?\s+?(kroner|kr[\.]?))|idømmes\s+en\s+bot\s+på(\s+(kroner|kr[\.]?))?\s+(?P<bot_storrelse_3>\d+[\s\.]?\d+)|til\s+en\s+bot\s+på\s+(kroner|kr[\.]?)\s+(?P<bot_storrelse_4>\d+[\s\.]?\d+)',
                avsnitt
            )
            for i in regex_iter:
                for k, v in i.groupdict().items():
                    if v:
                        bot_storrelse = v.replace(".", "")
                        straff_dict["bot"] = int(bot_storrelse.replace(" ", ""))
        return straff_dict

# LAVERE PRIORITET:
# HVIS TAP AV FØRERKORT:
# FINN UT HVOR LENGE
# Se etter vegtrafikkloven § 33

# OPPREISNING
# Se etter skadeerstatningsloven $ 3.
