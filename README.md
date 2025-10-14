# Feuernetz
Erweiterte Auswertung der Daten aus [FEUERnetz](feuernetz.de).

## Daten aus FEUERnetz speichern
Die nachfolgenden Daten werden aus FEUERnetz als Eingabe für die weiteren Auswertungen benötigt.

### Einsatzdaten
#### Einsatzgrunddaten
1. Verwaltungsmodul
1. Einsätze
1. Filter nach Bedarf setzen
1. Exportieren
1. Erzeugte Datei als _Einsatzexport.csv_ im input-Ordner speichern

#### Ausrückezeiten
1. Verwaltungsmodul
1. Statistiken / Berichte
1. Einsatz - Ausrückezeiten
1. Bericht ausführen
1. als Excel exportieren
1. Erzeugte Datei als _Einsatz - Ausrückezeiten.xlsx_ im input-Ordner speichern

### Personaldaten
#### Stammdaten
1. Personalverwaltung
2. Personal suchen
3. Suchen
4. Mehrfachaktion
5. Stammdaten exportiern
6. Ausführen
7. Erzeugte Datei als _Personalliste.csv_ im input-Ordner speichern

#### Rollen
1. Verwaltungsmodul
2. Statistiken / Berichte
3. Personal - Rollenauswertung
4. Zeitraum auf den gewünschten Bereich einschränken. Alternativ: Startdatum auf 01.01.2000 setzen.
5. Bericht ausführen
6. als Excel exportieren
7. Erzeugte Datei als _Personal - Rollenauswertung.xlsx_ im input-Ordner speichern

#### Qualifikationen
1. Verwaltungsmodul
2. Statistiken / Berichte
3. Personal - Qualifikationsexport
4. Bericht ausführen
6. als Excel exportieren
7. Erzeugte Datei als _Personal - Qualifiaktionsexport.xlsx_ im input-Ordner speichern

#### Beförderungshistorie
1. Verwaltungsmodul
2. Statistiken / Berichte
3. Personal - Beförderungshistorie
4. Zeitraum auf den gewünschten Bereich einschränken. Alternativ: Startdatum auf 01.01.2000 setzen.
5. Bericht ausführen
6. als Excel exportieren
7. Erzeugte Datei als _Personal - Beförderungshistorie.xlsx_ im input-Ordner speichern

### Wasserentnahmestellen

1. Verwaltungsmodul
2. Material
3. Materialkategorie: Wasserentnahmestellen
4. Suche ausführen
5. Exportieren
6. Erzeugte Datei als _Wasserentnahmestellen.csv_ im input-Ordner speichern


## Auswertung konfigurieren
Die Datei _config.ini_ enthält Daten die in FEUERnetz definiert sind und bei der Auswertung berücksichtig werden
### FEUERnetz
- id_prefix: Prefix der FEUERnetz-ID
- id_ignore: FEUERnetz-IDs die zu ignorieren sind, z.B. vom FEUERnetz-Admin
### Qualifikation
- benennung_gruppenfuehrer: Benennung der Qualifikation die ein Mitglied erhält, dass die Gruppenführer-Qualifikation nach FwDV2 erlangt hat
### Rollen
- mitglieder: Benennungen der Rollen die für die Personalauswertung berücksichtig werden sollen
### Ehrungen
- verband: Jahreszahlen die für eine Ehrung vom Feuerwehrverband berücksichtigt werden sollen (z.B. 10, 40, 50, 60, 70, 75, 80)
- land: Jahreszahlen die für eine Ehrung vom Land berücksichtigt werden sollen (z.B. 25, 35, 50)
### Wasserentnahmestellen
- kommune_name: Name der zu berücksichtigenden Kommune
- kommune_id = Amtlicher Gemeindeschlüssel (AGS) der zu berücksichtigenden Kommune

#### OpenDataLab
Export-Tool für Verwaltungsgrenzen von Bundesländern, Landkreisen und Gemeinden

Quelle der Daten zur Anzeige der Verwaltungsgrenzen: [OpenDataLab](https://opendatalab.de/projects/geojson-utilities/)

Datensatz entsrepchend auswählen und inder Genauigkeit **20 - mittlere Vereinfachung und Genauigkeit** im _input-Ordner_ speichern: gemeinden_simplify20.geojson

#### Point of Interests
Im _input-Ordner_ eine Datei _poi.csv_ mit der Kodierung _iso-8859-1_ im folgenden Aufbau erstellen:
```
Typ;Benennung;Längengrad;Breitengrad;Icon;Farbe
Feuerwehrhaus;Feuerwehrhaus Hamminkeln;51.73816204724966;6.5921835128642225;warehouse;red
```
- Icons: [fontawesome.com](https://fontawesome.com/search?f=classic&s=solid&ic=free&o=r)
- Farben:
    red,
    blue,
    gray,
    darkred,
    lightred,
    orange,
    beige,
    green,
    darkgreen,
    lightgreen,
    darkblue,
    lightblue,
    purple,
    darkpurple,
    pink,
    cadetblue,
    lightgray,
    black

## Auswertung initiieren
1. Repository in einen beliebigen Ordner clonen
1. Python Umgebung erstellen: ```python3 -m venv venv```
1. Python Umgebung starten ```source venv/bin/activate```
1. Pakete installieren: ```pip install -r requirements.txt```

### Personalauswertung
```marimo run personalauswertung.py```

### Einsatzauswertung
```marimo run einsatzauswertung.py```

### Wasserentnahmestellen
```marimo run wasserentnahme.py```
