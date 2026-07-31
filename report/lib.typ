// ----- Main Template Function: `report` ----------------------

#let report(
  doc-title: none,
  subtitle: none,
  author: none,
  period: none,
  logo: none,
  contact: none,
  language: "de",
  show-outline: true,
  heading-color: green,
  heading-font: "Latin Modern Roman", // recommended alternatives: "Fira Sans", "Lato", "Source Sans Pro"
  body-font: "Ubuntu",
  datetime-fmt: "[day].[month].[year]",
  body,
) = {

  // ----- Global Parameters ------------------------

  set document(title: doc-title, author: author)
  set text(lang: language)

  let body-size = 11pt

  // heading font is used in this size for kind of "information blocks"
  let info-size = 10pt              
  
  // heading font is used in this size for different sorts of labels            
  let label-size = 9pt  

  // ----- Basic Text-Setup ------------------------
  set text(
    font: body-font,
    size: body-size
  )

  // ----- Basic Page-Setup ------------------------
  set page(
    paper: "a4",
    margin: (top: 3cm, left: 3cm, right: 2.5cm, bottom: 3cm),
    header-ascent: 1.5em
  )

  // ----- Title Page ------------------------
  align(center,[

    #v(1fr)
    #text(font: heading-font, 3em, "  Stadt Hamminkeln  ")\
    #line(length: 80%)
    #v(0.3fr)
    #text(font: heading-font, 4em, "Feuerwehr")    
    
    #v(2fr)
    #align(center, logo)
    #v(2fr)
    #text(font: heading-font, 3em, doc-title)
    #v(0.4fr)
    #text(font: heading-font, 2.7em, subtitle)
    #if period != none {
      v(1fr)
      text(font: heading-font, 1.8em, [
        #period
      ])
    }
    
    #v(1fr)
  ])

  // ----- Contact ------------------------
  if contact != none {
    pagebreak()
    v(1fr)
    contact
    v(15mm)
  }

  // ----- Footer ------------------------
  set page(
    footer: context [
      #doc-title #subtitle
      #h(1fr)
      #counter(page).display("1 / 1", both: true,)
    ]
  )
  
  // ----- Headings & Numbering Schemes ------------------------

  set heading(numbering: "1.1.1")
  show heading: set text(font: heading-font, fill: heading-color, weight: "regular")


  show heading.where(level: 1): it => {
    pagebreak() + v(3.8 * body-size, weak: true) + text(it) + v(0.2 * body-size)
  }
  show heading.where(level: 2): it => {
    v(0.8 * body-size) + text(it) + v(0.2 * body-size)
  }
  show heading.where(level: 3): it => {
    v(0.8 * body-size) + text(it) + v(0.2 * body-size)
  }

  set figure(numbering: "1")
  show figure.caption: it => {
    set text(font: heading-font, size: label-size)
    block(it)
  }

  // ----- Table of Contents ------------------------
  outline(
    depth: 2,
    title: if language == "de" { 
        "Inhalt"
      } else if language == "fr" {
        "Table des matières"
      } else if language == "es" {
        "Contenido"
      } else if language == "it" {
        "Indice"
      } else if language == "nl" {
        "Inhoud"
      } else if language == "pt" {
        "Índice"
      } else if language == "zh" {
        "目录"
      } else if language == "ja" {
        "目次"
      } else if language == "ru" {
        "Содержание"
      } else if language == "ar" {
        "المحتويات"
      } else {
        auto
      },
  )

  // ----- Body Text ------------------------

  body

}

// ----- status image
#let status_image(path, width: 95%) = {
  align(center)[
    #image(path, width: width )
  ]
}

// ----- data table
#let data_table(path)={
  let data = csv(path, delimiter: ",")
  let header = data.first()
  let num_header = header.len()
  let content = data.slice(1)

  table(
    columns: (26mm, 25mm, 40mm, 24mm, 20mm, 24mm, 20mm, 24mm, 24mm, 16mm),
    table.header([*ID*], [*Fahrzeug*], [*Stichwort*], [*Alarm*], [*Alarm bis Status 3 [Min]*], [*Status 3*], [*Status 3 bis Status 4 [Min]*], [*Status 4*], [*Status 2*], [*Dauer Ges. [h]*]),
    ..content.flatten()
  )
}

// ----- filter personal
#let filter_einheit(data, einheit) = {
  data.filter(row => {row.first() == einheit}).map(row => row.slice(1))
}

// ----- unit table
#let tabelle_einheit(data) = {
  table(
  columns: 2,
  align: (start, end),
  stroke: 1pt + gray,
  [*Abteilung*], [*Mitglieder*],
  ..data.flatten(),
)
}

// ----- image personal
#let staff_image(path, width: 85%) = {
  align(center)[
    #image(path, width: width )
  ]
}