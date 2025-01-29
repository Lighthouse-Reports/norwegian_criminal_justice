def section_number_and_letter(number, letter):
    return rf"\s?§\s?{number}\s?(bokstav)?\s?{letter}"

regex_mitigating = {
    "young age": [
        ["unge\salder", "formildende"]
    ],
    "victim partially to blame": [
        ["tiltalte\sble\sprovosert", "formildende"],
        section_number_and_letter("78", "c")
    ],
    "processing time": [
        ["formildende", "EMK"],
        ["saksbehandlingstid", "formildende"],
        ["saksbehandlingstiden", "formildende"],
        ["relativt\slang\stid", "formildende"],
        ["lang\stid", "formildende"],
        ["lang\sliggetid", "formildende"],
        ["lange\stidsforløpet", "formildende"],
        ["langt\stidsforløp", "formildende"],
        ["lange\stidsbruken", "reduksjon"],
        ["lang\stidsbruk", "reduksjon"],
        ["formildende", "tidsbruk"],
        ["saken\shar\sblitt\sgammel", "formildende"],
    ],
    "personal challenges": [
        ["personlige\sutfordringer", "formildende"],
        ["helsemessige\sutfordringer", "formildende"]
    ],
    "perpetrator vulnerability": [
        section_number_and_letter("78", "g")
    ],
    "perpetrator underage": [
        section_number_and_letter("78", "i"),
        section_number_and_letter("80", "h")
    ],
    "limited mental capacity": [
        section_number_and_letter("78", "d"),
        section_number_and_letter("80", "f")
    ],
    "limited damage": [
        section_number_and_letter("78", "b")
    ],
    "intoxication": [
        section_number_and_letter("80", "g")
    ],
    "confession": [
        ["formildende", "erkjent"],
        ["erkjennelse", "formildende"],
        "uforbeholden\stilståelse",
        ["formildende", "forklaring"],
        ["tilståelse", "formildende"]
    ]
}

regex_aggravating = {

}
