import fitz
import os
from pymongo import errors
from .helpers.dom_class import Dom
from .helpers.db import collection

def send_dommer_til_db(input_files, collection=collection):
    num = 0

    for filename in os.listdir(input_files):
        if ".pdf" in filename:
            if "MED-" in filename and not filename.startswith("."):
                if collection.count_documents({"filnavn": filename}, limit=1) == 1:
                    continue
                else:
                    num += 1
                    print(num)
                    print(filename)

                    # Åpne dokument og hente ut tekst
                    doc = fitz.open(f"{input_files}/{filename}")
                    full_text = "\n\n".join([page.get_text("text", sort=True) for page in doc])
                    page1 = doc[0].get_text("text")
                    page1_sorted = doc[0].get_text("text", sort=True)

                    if "Dokumentet er signert digitalt av følgende undertegnere" in page1:
                        page1 = doc[1].get_text("text")
                        page1_sorted = doc[1].get_text("text", sort=True)

                    dom = Dom(filename, doc, page1, page1_sorted, full_text)

                    # Filtrerer ut advokater fra dom.motpart for å legge dem som eget element i json
                    advokater = [m for m in dom.motpart if "tittel" in m]
                    tiltalte = [m for m in dom.motpart if "tittel" not in m]

                    json = {
                        "filnavn": dom.filnavn,
                        "avsagt_dato": dom.avsagt_dato,
                        "fagdommere": dom.fagdommere,
                        "meddommere": dom.meddommere,
                        "part1": dom.part1,
                        "type_avgjørelse": dom.type_avgjorelse,
                        "tiltale": dom.tiltale,
                        "dom": dom.dom_og_lov,
                        "dom_tekst": dom.dom_tekst,
                        "type_avgjørelse_tekst": dom.tekst_dissens_vs_enstemmig,
                        "domsslutning": dom.domsslutning,
                        "advokater": advokater,
                        "tiltalte": tiltalte
                    }

                    if dom.feilmeldinger:
                        json["feilmeldinger"] = dom.feilmeldinger

                    try:
                        collection.insert_one(json)
                    except (errors.DuplicateKeyError, UnicodeEncodeError) as e:
                        continue
    print(f"Ferdig med å sjekke {num} dommer.")
    return collection.name

if __name__ == "__main__":
    input_files = "/Volumes/Dommedag/arkiv/"
    send_dommer_til_db(input_files)
