#import "lib.typ": report, status_image, data_table

#let contact = [*Leitung der Feuerwehr*\
    #link("mailto:wehrleitung@feuerwehr-hamminkeln.de")[
      wehrleitung$at$feuerwehr-hamminkeln.de
    ]\
    Brüner Straße 9, 46499 Hamminkeln
  ]

#report(
  doc-title: "Einsatzauswertung",
  subtitle: "LE Wertherbruch",
  author: "Feuerwehr Hamminkeln",
  logo: image("../input/0_logo-FW-HMM.png", width: 85%),
  contact: contact
)[

= Statuszeiten LE Wertherbruch
#status_image("../output/grafik/Statuszeiten_HMM.5.png")

#set page(flipped: true)
= Einsatzübersicht
#data_table("../output/statuszeiten_HMM_5.csv")
]