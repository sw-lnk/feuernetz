import os
import datetime as dt
import polars as pl

import database.fn_config as fn_config
import database.database as db

config_ehrung = fn_config.config_object["ehrungen"]

ehrung_verband = [int(verband.strip()) for verband in config_ehrung['verband'].split(',')]
ehrung_land = [int(land.strip()) for land in config_ehrung['land'].split(',')]

def export_daten_jahresbericht(df: pl.DataFrame, datum_auswertung: dt.date, datum_befoerderung: dt.date) -> None:
    befoerderungen = {
        'FFrA / FMA': 'FMA',
        'FFr / FM': 'FM',
        'OFFr / OFM': 'OFM',
        'HFFr / HFM': 'HFM',
        'UBM': 'UBM',
        'BM': 'BM',
        'OBM': 'OBM',
        'HBM': 'HBM',
        'BI': 'BI',
        'BOI': 'BOI',
        'StBI': 'StBI',
    }

    df.filter(
        pl.col('Rolle').is_not_null(),
        pl.col('Beförderung').is_not_null(),
    ).select(
        pl.col('FEUERnetz-ID'),
        pl.col('Nachname'),
        pl.col('Vorname'),
        pl.col('Ortsteil'),
        pl.col('Abteilung'),
        pl.col('Dienstgrad Letzte'),
        pl.col('Beförderung'),
        pl.col('Beförderungs Datum'),
    ).write_csv(
        os.path.join(db.ORDNER_AUSGABE, f'befoerderungen_{datum_befoerderung.year}.csv')
    )

    df.filter(
        pl.col('Rolle').is_not_null(),
        pl.col('Ehrung').is_not_null(),
    ).select(
        pl.col('FEUERnetz-ID'),
        pl.col('Anrede'),
        pl.col('Nachname'),
        pl.col('Vorname'),
        pl.col('Ortsteil'),
        pl.col('Abteilung'),
        pl.col('Dienstgrad FF'),
        pl.col('Beförderung'),
        pl.col('Geburtsdatum'),
        pl.col('Eintritt Feuerwehr'),
        pl.col('Ehrung'),
    ).write_csv(
        os.path.join(db.ORDNER_AUSGABE, f'ehrungen_{datum_befoerderung.year}.csv')
    )

    df.filter(
        pl.col('Personalbewegung').str.contains('-> Ehren'),
    ).select(
        pl.col('Nachname'),
        pl.col('Vorname'),
        pl.col('Ortsteil'),
        pl.col('Dienstgrad FF'),
        pl.col('Personalbewegung'),
    ).write_csv(
        os.path.join(db.ORDNER_AUSGABE, f'ehrenabteilung_{datum_auswertung.year}.csv')
    )

    (df.filter(pl.col('Personalbewegung').is_not_null())
    .group_by(['Ortsteil', 'Abteilung', 'Personalbewegung'])
    .agg(pl.col("Nachname").count())
    .rename({"Nachname": "Anzahl"})
    .write_csv(
        os.path.join(db.ORDNER_AUSGABE, f'personalbewegung_{datum_auswertung.year}.csv')
    ))

    for key_b, value_b in befoerderungen.items():
        df.filter(
            pl.col('Rolle').is_not_null(),
            pl.col('Beförderung').is_not_null(),
            pl.col('Beförderung').eq(key_b)
        ).select(
            pl.col('Nachname'),
            pl.col('Vorname'),
            pl.col('Ortsteil'),
        ).write_csv(
            os.path.join(db.ORDNER_AUSGABE, db.ORDNER_JAHRESBERICHT, f'{value_b}.csv')
        )

    ehrungen = {
        'Verband': ehrung_verband,
        'Land': ehrung_land,
    }

    for key_e, value_e in ehrungen.items():
        for jahr in value_e:
            df.filter(
                pl.col('Rolle').is_not_null(),
                pl.col('Ehrung').eq(f'{key_e} - {jahr} Jahre')
            ).select(
                pl.col('Nachname'),
                pl.col('Vorname'),
                pl.col('Ortsteil')
            ).write_csv(
                os.path.join(db.ORDNER_AUSGABE, db.ORDNER_JAHRESBERICHT, f'{key_e}-{jahr}Jahre.csv')
            )