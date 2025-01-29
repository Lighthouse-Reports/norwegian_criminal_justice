from . import avsagt_dato, dommere_og_parter, type_avgjorelse, domsslutning, constants, log


class Dom:
    def __init__(self, filename, doc, page1, page1_sorted, full_text, lagmannsrett=False):
        log.feilmeldinger = []
        log.tekst_dissens_vs_enstemmig = ""
        self.filnavn = filename
        self.dom_tekst = full_text
        self.avsagt_dato = avsagt_dato.avsagt_dato(page1)
        self.fagdommere = dommere_og_parter.finn_fagdommer(page1)
        self.meddommere = dommere_og_parter.finn_meddommer(page1, lagmannsrett)

        if self.meddommere is None:
            try:
                self.meddommere = dommere_og_parter.finn_meddommer_i_bunn_av_dom(full_text)[1:]
            except TypeError:
                pass

        self.part1 = dommere_og_parter.finn_part1(page1)
        self.motpart = dommere_og_parter.finn_motpart(page1_sorted, lagmannsrett)
        self.adresse = dommere_og_parter.finn_adresse_motpart(doc, self.motpart)
        self.domsslutning = domsslutning.finn_domsslutning(constants.DOMSSLUTNING_FORMULERINGER, full_text, self.fagdommere, lagmannsrett)
        self.dom_og_lov = domsslutning.finn_dom_og_lov_fra_domsslutning(self.domsslutning, self.motpart)
        self.tiltale = domsslutning.finn_lov_fra_tiltale(doc)

        self.type_avgjorelse, avsnitt = type_avgjorelse.enstemmig_eller_dissens(full_text)

        if self.type_avgjorelse == "dissens":
            mindretall_og_flertall = type_avgjorelse.dommere_for_og_imot(full_text, self.fagdommere, self.meddommere)
            if mindretall_og_flertall:
                self.fagdommere, self.meddommere = mindretall_og_flertall

        if self.domsslutning:
            domsslutning.finn_fodselsdato(self.domsslutning, self.motpart)

        self.tekst_dissens_vs_enstemmig = log.tekst_dissens_vs_enstemmig
        self.feilmeldinger = log.feilmeldinger

