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

## Einsatzauswertung
*TODO*

## Personalauswertung
### Auswertung konfigurieren
Die Datei _config.ini_ enthält Daten die in FEUERnetz definiert sind und bei der Auswertung berücksichtig werden
#### FEUERnetz
- id_prefix: Prefix der FEUERnetz-ID
- id_ignore: FEUERnetz-IDs die zu ignorieren sind, z.B. vom FEUERnetz-Admin
#### Qualifikation
- benennung_gruppenfuehrer: Benennung der Qualifikation die ein Mitglied erhält, dass die Gruppenführer-Qualifikation nach FwDV2 erlangt hat
#### Rollen
- mitglieder: Benennungen der Rollen die für die Personalauswertung berücksichtig werden sollen
#### Ehrungen
- verband: Jahreszahlen die für eine Ehrung vom Feuerwehrverband berücksichtigt werden sollen (z.B. 10, 40, 50, 60, 70, 75, 80)
- land: Jahreszahlen die für eine Ehrung vom Land berücksichtigt werden sollen (z.B. 25, 35, 50)

### Auswertung initiieren
1. Repository in einen beliebigen Ordner clonen
1. Python Umgebung erstellen: ```python3 -m venv venv```
1. Python Umgebung starten ```source venv/bin/activate```
1. Pakete installieren: ```pip install -r requirements.txt```

#### Personalauswertung
```marimo run personalauswertung.py```

#### Einsatzauswertung
```marimo run einsatzauswertung.py```

