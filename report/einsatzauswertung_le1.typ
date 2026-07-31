#import "lib.typ": report, status_image, data_table

#let contact = [*Leitung der Feuerwehr*\
    #link("mailto:wehrleitung@feuerwehr-hamminkeln.de")[
      wehrleitung$at$feuerwehr-hamminkeln.de
    ]\
    Brüner Straße 9, 46499 Hamminkeln
  ]

#report(
  doc-title: "Einsatzauswertung",
  subtitle: "LE Hamminkeln",
  author: "Feuerwehr Hamminkeln",
  logo: image("../input/0_logo-FW-HMM.png", width: 85%),
  contact: contact
)[

= Statuszeiten LE Hamminkeln
#status_image("../output/grafik/Statuszeiten_HMM.1.png")
#status_image("../output/grafik/Statuszeiten_DLK_Hamminkeln.png")
#status_image("../output/grafik/Statuszeiten_RW_Hamminkeln.png")
#status_image("../output/grafik/Statuszeiten_GW-L2_Hamminkeln.png")

#set page(flipped: true)
= Einsatzübersicht
#data_table("../output/statuszeiten_HMM_1.csv")
]