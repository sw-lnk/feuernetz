#import "data.typ": feuerwehr

#set page(footer: [
  #datetime.today().display("[day].[month].[year]")
  #h(1fr)
  #feuerwehr
  #h(1fr)
  Personalauswertung
])

#show heading.where(level: 1): it => { pagebreak(weak: true); it }

#let filter_einheit(data, einheit) = {
  data.filter(row => {row.first() == einheit}).map(row => row.slice(1))
}

#let tabelle_einheit(data) = {
  table(
  columns: 2,
  align: (start, end),
  stroke: 1pt + gray,
  [*Abteilung*], [*Mitglieder*],
  ..data.flatten(),
)
}

#let personal_gesamt = csv("../output/personal_ges_pivot.csv").sorted()
#let personal_hamminkeln = filter_einheit(personal_gesamt, "Hamminkeln")
#let personal_dingden = filter_einheit(personal_gesamt, "Dingden")
#let personal_bruenen = filter_einheit(personal_gesamt, "Brünen")
#let personal_loikum = filter_einheit(personal_gesamt, "Loikum")
#let personal_wertherbruch = filter_einheit(personal_gesamt, "Wertherbruch")
#let personal_mehrhoog = filter_einheit(personal_gesamt, "Mehrhoog")

#let staff_image(path, width: 85%) = {
  align(center)[
    #image(path, width: width )
  ]
}

#title("Personalauswertung")

#staff_image("../output/grafik/Mitglieder_alter_box.png")
#staff_image("../output/grafik/Mitglieder_alter_box_orga.png")
#staff_image("../output/grafik/Mitglieder_alter.png", width: 100%)
#staff_image("../output/grafik/Mitglieder_neu.png", width: 75%)
#staff_image("../output/grafik/Mitglieder_verlust.png")

#staff_image("../output/grafik/Mitglieder_einheit.png")
#staff_image("../output/grafik/Mitglieder_einheit_FK.png")



#pagebreak()
#staff_image("../output/grafik/AGT_alter.png")
#staff_image("../output/grafik/AGT_einheiten.png")

#pagebreak()
#staff_image("../output/grafik/CSA_alter.png")
#staff_image("../output/grafik/CSA_einheiten.png")

#pagebreak()
#staff_image("../output/grafik/LKW_alter.png")
#staff_image("../output/grafik/LKW_einheit.png")


= LE Hamminkeln
#tabelle_einheit(personal_hamminkeln)
#staff_image("../output/grafik/Mitglieder_alter_Hamminkeln.png", width: 100%)
#staff_image("../output/grafik/Mitglieder_wechsel_Hamminkeln.png", width: 70%)

= LE Dingden
#tabelle_einheit(personal_dingden)
#staff_image("../output/grafik/Mitglieder_alter_Dingden.png", width: 100%)
#staff_image("../output/grafik/Mitglieder_wechsel_Dingden.png", width: 70%)

= LE Brünen
#tabelle_einheit(personal_bruenen)
#staff_image("../output/grafik/Mitglieder_alter_Brünen.png", width: 100%)
#staff_image("../output/grafik/Mitglieder_wechsel_Brünen.png", width: 70%)

= LE Loikum
#tabelle_einheit(personal_loikum)
#staff_image("../output/grafik/Mitglieder_alter_Loikum.png", width: 100%)
#staff_image("../output/grafik/Mitglieder_wechsel_Loikum.png", width: 70%)

= LE Wertherbruch
#tabelle_einheit(personal_wertherbruch)
#staff_image("../output/grafik/Mitglieder_alter_Wertherbruch.png", width: 100%)
#staff_image("../output/grafik/Mitglieder_wechsel_Wertherbruch.png", width: 70%)

= LE Mehrhoog
#tabelle_einheit(personal_mehrhoog)
#staff_image("../output/grafik/Mitglieder_alter_Mehrhoog.png", width: 100%)
#staff_image("../output/grafik/Mitglieder_wechsel_Mehrhoog.png", width: 70%)

= Kinder- und Jugendfeuerwehr
#staff_image("../output/grafik/Mitglieder_KiFw_JFw_alter.png", width: 100%)

== Jugendfeuerwehr
#table(
  columns: 2,
  align: (start, end),
  stroke: 1pt + gray,
  [*Ortsteil*], [*Anzahl*],
  ..personal_gesamt.filter(row => "Jugend" in row.at(1)).map(row => (row.first(), row.last())).flatten(),
)

== Kinderfeuerwehr
#table(
  columns: 2,
  align: (start, end),
  stroke: 1pt + gray,
  [*Ortsteil*], [*Anzahl*],
  ..personal_gesamt.filter(row => "Kinder" in row.at(1)).map(row => (row.first(), row.last())).flatten(),
)
