import os
import polars as pl

import database.fn_config as fn_config

ORDNER_EINGABE = 'input'
ORDNER_AUSGABE = 'output'
ORDNER_JAHRESBERICHT = 'jahresbericht'
ORDNER_AUSGABE_GRAFIK = 'grafik'

pfad_jahresbericht = os.path.join(ORDNER_AUSGABE, ORDNER_AUSGABE_GRAFIK)
pfad_grafik = os.path.join(ORDNER_AUSGABE, ORDNER_AUSGABE_GRAFIK)

DATUM_FORMAT1 = "%Y-%m-%d"
DATUM_FORMAT2 = "%d.%m.%Y"
DATUM_FORMAT3 = "%d.%m.%Y %H:%M"
DATUM_FORMAT4 = "%Y-%m-%d %H:%M:%S"
DATUM_FORMAT5 = "%d.%m.%Y %H:%M:%S"

DATUM_AUSGABE = DATUM_FORMAT2

config_data = fn_config.config_object["FEUERnetz"]
config_allgemein = fn_config.config_object["allgemein"]


if not os.path.exists(ORDNER_EINGABE):
    os.makedirs(ORDNER_EINGABE)

if not os.path.exists(ORDNER_AUSGABE):
    os.makedirs(ORDNER_AUSGABE)

if not os.path.exists(pfad_grafik):
    os.makedirs(pfad_grafik)

if not os.path.exists(pfad_jahresbericht):
    os.makedirs(pfad_jahresbericht)


def postleitzahl_list() -> list[int]:
    plz = config_allgemein['postleitzahlen']
    return [int(p.strip()) for p in plz.split(',')]


def entferne_ignorierte_ids(df: pl.DataFrame) -> pl.DataFrame:
    id_prefix = config_data['id_prefix']
    ids_to_ignore = [id_prefix+id.strip() for id in config_data['id_ignore'].split(',')]
    return df.filter(pl.col("FEUERnetz-ID").is_in(ids_to_ignore).not_())


def lese_stammdaten() -> pl.DataFrame:
  df = pl.read_csv(
    os.path.join(ORDNER_EINGABE, 'Personalliste.csv'),
    separator=';',
    encoding="iso-8859-1",
  )
  df = entferne_ignorierte_ids(df)
  df = df.with_columns(pl.col('Geburtsdatum').str.to_datetime(DATUM_FORMAT1))
  df = df.with_columns(pl.col('Angelegt am').str.to_datetime(DATUM_FORMAT1))
  return df


def lese_rollen() -> pl.DataFrame:    
    df = pl.read_excel(
        os.path.join(ORDNER_EINGABE, "Personal - Rollenauswertung.xlsx"),
    )
    df = entferne_ignorierte_ids(df)
    df = df.with_columns(pl.col('Start').str.to_datetime(DATUM_FORMAT2))
    df = df.with_columns(pl.col('Ende').str.to_datetime(DATUM_FORMAT2))
    return df
  

def lese_qualifikationen() -> pl.DataFrame:    
    df = pl.read_excel(
        os.path.join(ORDNER_EINGABE, 'Personal - Qualifikationsexport.xlsx'),
    )
    df = entferne_ignorierte_ids(df)
    df = df.with_columns(pl.col('Start').cast(str))
    df = df.with_columns(pl.col('Start').str.to_datetime(DATUM_FORMAT1))
    df = df.with_columns(pl.col('Ende').cast(str))
    df = df.with_columns(pl.col('Ende').str.to_datetime(DATUM_FORMAT1))
    return df


def lese_dienstgrade() -> pl.DataFrame:    
    df = pl.read_excel(
        os.path.join(ORDNER_EINGABE, "Personal - Beförderungshistorie.xlsx"),
    )
    df = entferne_ignorierte_ids(df)
    df = df.with_columns([
        pl.col('Ernannt ab').str.to_datetime(DATUM_FORMAT2),
        pl.col('Urkundendatierung').str.to_datetime(DATUM_FORMAT2)
    ])
    return df
    

def lese_einsatzdaten() -> pl.DataFrame:    
    #df = pl.read_excel(os.path.join(ORDNER_EINGABE, "Einsatzverwaltung.xlsx"))
    #df = df.with_columns(pl.col('Beginn').str.to_datetime(DATUM_FORMAT3))
    df = pl.read_csv(
        os.path.join(ORDNER_EINGABE, "Einsatzexport.csv"),
        separator=';',
        encoding="iso-8859-1",
    )
    df = df.with_columns(pl.col('Beginn').str.to_datetime(DATUM_FORMAT5))
    df = df.with_columns(pl.col('Ende').str.to_datetime(DATUM_FORMAT5))
        
    return df

def lese_einsatz_einheiten_details() -> pl.DataFrame:
    df = pl.read_excel(os.path.join(ORDNER_EINGABE, "Einsatz - Ausrückezeiten.xlsx"))
    df = df.with_columns([
        pl.col('Beginn').str.to_datetime(DATUM_FORMAT4),
        pl.col('Alarm').str.to_datetime(DATUM_FORMAT4),
        pl.col('Ausruecken S3').str.to_datetime(DATUM_FORMAT4),
        pl.col('Eintreffen S4').str.to_datetime(DATUM_FORMAT4),
        pl.col('Ende S2').str.to_datetime(DATUM_FORMAT4),
    ])
    
    df = df.with_columns([
        pl.when(pl.col('VF').is_nan()).then(0.0).cast(int).alias('VF'),
        pl.when(pl.col('ZF').is_nan()).then(0.0).cast(int).alias('ZF'),
        pl.when(pl.col('GF').is_nan()).then(0.0).cast(int).alias('GF'),
        pl.when(pl.col('FM (SB)').is_nan()).then(0.0).cast(int).alias('FM (SM)'),
        pl.when(pl.col('davon AGT').is_nan()).then(0.0).cast(int).alias('davon AGT'),
    ])
    
    return df


if __name__ == "__main__":
    pass