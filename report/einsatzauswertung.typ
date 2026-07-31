#import "lib.typ": report, status_image, data_table


#let data = json("../output/daten_auswertung.json")

#let contact = [*Leitung der Feuerwehr*\
    #link("mailto:wehrleitung@feuerwehr-hamminkeln.de")[
      wehrleitung$at$feuerwehr-hamminkeln.de
    ]\
    Brüner Straße 9, 46499 Hamminkeln
  ]

#report(
  doc-title: "Einsatzauswertung Gesamt",
  author: "Feuerwehr Hamminkeln",
  logo: image("../input/0_logo-FW-HMM.png", width: 85%),
  contact: contact,
  period: [#data.datum_auswertung_start bis #data.datum_auswertung_ende]
)[

= Statuszeiten LE Hamminkeln
#status_image("../output/grafik/Statuszeiten_HMM.1.png")
#status_image("../output/grafik/Statuszeiten_DLK_Hamminkeln.png")
#status_image("../output/grafik/Statuszeiten_RW_Hamminkeln.png")
#status_image("../output/grafik/Statuszeiten_GW-L2_Hamminkeln.png")

= Statuszeiten LE Dingden
#status_image("../output/grafik/Statuszeiten_HMM.2.png")

= Statuszeiten LE Brünen
#status_image("../output/grafik/Statuszeiten_HMM.3.png")
#status_image("../output/grafik/Statuszeiten_ELW_Brünen.png")

= Statuszeiten LE Loikum
#status_image("../output/grafik/Statuszeiten_HMM.4.png")

= Statuszeiten LE Wertherbruch
#status_image("../output/grafik/Statuszeiten_HMM.5.png")

= Statuszeiten LE Mehrhoog
#status_image("../output/grafik/Statuszeiten_HMM.6.png")

#set page(flipped: true)
= Einsatzübersicht
#data_table("../output/statuszeiten_gesamt.csv")
]
