#import "data.typ": feuerwehr

#set page(footer: [
  #datetime.today().display("[day].[month].[year]")
  #h(1fr)
  #feuerwehr
  #h(1fr)
  Einsatzauswertung
])

#show heading.where(level: 1): it => { pagebreak(weak: true); it }

#let status_image(path, width: 95%) = {
  align(center)[
    #image(path, width: width )
  ]
}

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
