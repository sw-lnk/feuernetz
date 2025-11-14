import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium", app_title="Personalauswertung")

with app.setup:
    # Initialization code that runs before all other cells
    import os
    import marimo as mo
    import polars as pl
    import datetime as dt

    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    import seaborn as sns

    from fn_data import datum_jahreshauptversammlung

    from database import database as db
    from database.database import ORDNER_AUSGABE, ORDNER_AUSGABE_GRAFIK

    import database.fn_config as fn_config


@app.cell
def _():
    start = dt.datetime.now()
    return (start,)


@app.cell
def _():
    config_allgemein = fn_config.config_object["allgemein"]

    ortsteile = [ortsteil.strip() for ortsteil in config_allgemein['ortsteile'].split(',')]
    abteilungen = [abteilung.strip() for abteilung in config_allgemein['abteilungen'].split(',')]
    return abteilungen, ortsteile


@app.cell
def _():
    config_ehrung = fn_config.config_object["ehrungen"]

    ehrung_verband = [int(verband.strip()) for verband in config_ehrung['verband'].split(',')]
    ehrung_land = [int(land.strip()) for land in config_ehrung['land'].split(',')]
    return ehrung_land, ehrung_verband


@app.cell
def _():
    mo.md(
        r"""
    # Personalauswertung

    - Beförderungen
    - Ehrungen Land NRW
    - Ehrungen VdF NRW
    - Alterverteilungen
        * Gesamtübersicht
        * Je Einheit
        * Je Abteilung
    - LKW-Führerscheine
    - Atemschutzgeräteträger
    - ABC I Absolventen
    """
    )
    return


@app.cell
def _():
    jahr_heute = dt.datetime.now().year
    datum_auswertung = mo.ui.date(
        value=dt.date(jahr_heute, 12, 31)
    )
    return (datum_auswertung,)


@app.cell
def _(datum_auswertung):
    datum_befoerderung = mo.ui.date(
        start=datum_auswertung.value,
        value=datum_auswertung.value+dt.timedelta(days=1)
    )
    return (datum_befoerderung,)


@app.cell
def _(datum_auswertung, datum_befoerderung):
    mo.md(
        f"""
    Tag der Auswertung: {datum_auswertung}

    Datum Beförderungen: {datum_befoerderung}
    """
    )
    return


@app.cell
def _(datum_auswertung, datum_befoerderung):
    date = datum_auswertung.value
    zeitpunkt_auswertung = dt.datetime(date.year, date.month, date.day)
    erster_tag_jahr = dt.datetime(year=zeitpunkt_auswertung.year, month=1, day=1)

    datum_jahreshauptversammlung_auswertung = datum_jahreshauptversammlung(datum_befoerderung.value.year)
    return (
        datum_jahreshauptversammlung_auswertung,
        erster_tag_jahr,
        zeitpunkt_auswertung,
    )


@app.cell
def _(datum_auswertung, datum_jahreshauptversammlung_auswertung):
    datum_jhv = mo.ui.date(
        start=datum_auswertung.value+dt.timedelta(days=1),
        value=datum_jahreshauptversammlung_auswertung.date()
    )
    return (datum_jhv,)


@app.cell
def _(datum_jhv):
    mo.md(rf"""Datum Jahreshauptversammlung: {datum_jhv}""")
    return


@app.cell
def _():
    df_stamm = db.lese_stammdaten()
    df_dienstgrad = db.lese_dienstgrade()
    df_quali = db.lese_qualifikationen()
    return df_dienstgrad, df_quali, df_stamm


@app.cell
def _(df_stamm):
    df_rollen = db.lese_rollen()

    df_rollen = df_rollen.join(
        df_stamm.select(['FEUERnetz-ID', 'Geburtsdatum']), on='FEUERnetz-ID', how="left"
    )
    return (df_rollen,)


@app.cell
def _(df_rollen, zeitpunkt_auswertung):
    df_rollen_grouped_rolle = (
        df_rollen
        .sort(by='Start')
        .filter(
            pl.col('Start').le(zeitpunkt_auswertung),
            pl.col('Rolle').str.to_lowercase().str.contains("mitglied"),
            pl.col('Einheit').str.contains("Extern").not_(),
            pl.col('Ende').is_null() | pl.col('Ende').gt(zeitpunkt_auswertung)
        )
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Rolle").first().alias("Rolle"))
    )
    return (df_rollen_grouped_rolle,)


@app.cell
def _(df_rollen, zeitpunkt_auswertung):
    df_rollen_grouped_einheit = (
        df_rollen
        .sort(by='Start')
        .filter(
            pl.col('Start').le(zeitpunkt_auswertung),
                pl.col('Rolle').str.to_lowercase().str.contains("mitglied"),
                pl.col('Einheit').str.contains("Extern").not_(),
                pl.col('Ende').is_null() | pl.col('Ende').gt(zeitpunkt_auswertung),
                (
                    pl.col('Einheit').str.contains("Einheit") |
                    pl.col('Einheit').str.contains("Unterstützung") |
                    pl.col('Einheit').str.contains("Ehren") |
                    pl.col('Einheit').str.contains("Kinder") |
                    pl.col('Einheit').str.contains("Jugend")
                )
        )
        .group_by('FEUERnetz-ID')
        .agg(
            pl.col("Einheit").first().alias("Einheit Aktuell"),
            pl.col("Start").first().alias("Einheit Aktuell Start"),
        )
    )
    return (df_rollen_grouped_einheit,)


@app.cell
def _(df_rollen):
    df_rollen_grouped_eintritt = (
        df_rollen
        .sort(by='Start')
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias("Eintritt Feuerwehr"))
    )
    return (df_rollen_grouped_eintritt,)


@app.cell
def _(df_rollen, zeitpunkt_auswertung):
    df_rollen_grouped_dienstzeit = (
        df_rollen
        .sort(by='Start')
        .filter(
            pl.col('Start').le(zeitpunkt_auswertung),
            pl.col('Rolle').str.starts_with("Mitglied"),
        )
        .with_columns(
            pl.col('Ende').fill_null(zeitpunkt_auswertung)
        ).with_columns(
            pl.col('Ende').shift().over('FEUERnetz-ID').alias('Ende Prev')
        ).with_columns(
            pl.when(
                pl.col('Start') < pl.col('Ende Prev')
            )
            .then(pl.col('Ende Prev'))
            .otherwise(pl.col('Start'))
            .over('FEUERnetz-ID')
            .alias('Start')
        ).with_columns(
            (pl.col('Ende') - pl.col('Start')).alias('Dienstzeit')
        )
        .group_by('FEUERnetz-ID')
        .sum()
    )
    return (df_rollen_grouped_dienstzeit,)


@app.cell
def _(df_rollen, zeitpunkt_auswertung):
    df_rollen_grouped_dienstzeit_aktiv = (
        df_rollen
        .sort(by='Start')
        .with_columns(
            pl.col('Ende').fill_null(zeitpunkt_auswertung),

            pl.datetime(
                year=pl.col('Geburtsdatum').dt.year() + 10,
                month=pl.col('Geburtsdatum').dt.month(),
                day=pl.col('Geburtsdatum').dt.day()
            ).alias('Start Aktiv'),

            pl.datetime(
                year=pl.col('Geburtsdatum').dt.year() + 67,
                month=pl.col('Geburtsdatum').dt.month(),
                day=pl.col('Geburtsdatum').dt.day()
            ).dt.offset_by(by='-1d')
            .alias('Ende Aktiv')
        )
        .filter(
            pl.col('Einheit').str.contains("Ehren").not_()
        )
        .filter(
            pl.col('Start').le(zeitpunkt_auswertung),
            pl.col('Rolle').str.starts_with("Mitglied"),
        )
        .with_columns(
            pl.col('Ende').fill_null(zeitpunkt_auswertung)
        )
        .with_columns(
            pl.col('Ende').shift().over('FEUERnetz-ID').alias('Ende Prev')
        )
        .with_columns(
            pl.when(
                pl.col('Start') < pl.col('Ende Prev')
            )
            .then(pl.col('Ende Prev'))
            .otherwise(pl.col('Start'))
            .over('FEUERnetz-ID')
            .alias('Start')
        )
        .with_columns(
            pl.when(
                pl.col('Start') < pl.col('Start Aktiv')
            )
            .then(pl.col('Start Aktiv'))
            .otherwise(pl.col('Start'))
            .alias('Start'),

            pl.when(
                pl.col('Ende') > pl.col('Ende Aktiv')
            )
            .then(pl.col('Ende Aktiv'))
            .otherwise(pl.col('Ende'))
            .alias('Ende'),
        )
        .with_columns(
            (pl.col('Ende') - pl.col('Start')).alias('Dienstzeit Aktiv')
        )
        .with_columns(
            pl.when(pl.col('Dienstzeit Aktiv').lt(pl.duration(days=0)))
            .then(pl.duration(days=0))
            .otherwise(pl.col('Dienstzeit Aktiv'))
            .alias('Dienstzeit Aktiv')
        )
        .group_by('FEUERnetz-ID')
        .sum()
    )
    return (df_rollen_grouped_dienstzeit_aktiv,)


@app.cell
def _(df_rollen, erster_tag_jahr, zeitpunkt_auswertung):
    df_rollen_personalbewegung = (
        df_rollen.filter(
            pl.col("Rolle").str.to_lowercase().str.contains("mitglied"),
            pl.col("Einheit").str.contains("Extern").not_(),
            pl.col("Einheit").str.contains("Gruppe").not_(),
            pl.col("Einheit").str.contains("Vorgeplant").not_(),
            (
                pl.col("Start").ge(erster_tag_jahr) & pl.col("Start").le(zeitpunkt_auswertung)
            ) |
            (
                pl.col("Ende").ge(erster_tag_jahr) & pl.col("Ende").le(zeitpunkt_auswertung)
            ),
        ).sort("Start")

        .with_columns(
            pl.when(
                pl.col("Ende").is_null(),
                pl.col("Start").ge(erster_tag_jahr),
                pl.col("Start").le(zeitpunkt_auswertung)
            )
            .then(pl.lit('Neuaufnahme'))
            .when(
                pl.col("Start").ge(erster_tag_jahr),
                pl.col("Start").le(zeitpunkt_auswertung),
                pl.col("Ende").ge(erster_tag_jahr),
                pl.col("Ende").le(zeitpunkt_auswertung)
            )
            .then(pl.lit('Aufnahme und Austritt in einem Jahr'))
            .when(
                pl.col("Ende").ge(erster_tag_jahr),
                pl.col("Ende").le(zeitpunkt_auswertung)
            )
            .then(pl.lit('Ausgetreten'))
            .otherwise(pl.lit('Personalbewegung'))
            .alias('Personalbewegung')
        )
    )
    return (df_rollen_personalbewegung,)


@app.cell
def _(df_rollen, erster_tag_jahr, zeitpunkt_auswertung):
    df_rollen_personalbewegung_vor = (
        df_rollen.filter(
            pl.col("Rolle").str.to_lowercase().str.contains("mitglied"),
            pl.col("Einheit").str.contains("Extern").not_(),
            pl.col("Einheit").str.contains("Gruppe").not_(),
            pl.col("Einheit").str.contains("Vorgeplant").not_(),        
            (
                pl.col("Start").lt(erster_tag_jahr)
            ),
        ).sort("Start")

        .with_columns(
            pl.when(
                pl.col("Ende").is_null() | pl.col("Ende").le(zeitpunkt_auswertung)
            )
            .then(pl.lit('Übertritt vor'))
            .otherwise(pl.lit('Personalbewegung'))
            .alias('Personalbewegung')
        )
    )
    return (df_rollen_personalbewegung_vor,)


@app.cell
def _(df_rollen, zeitpunkt_auswertung):
    df_rollen_personalbewegung_folge = (
        df_rollen.filter(
            pl.col("Rolle").str.to_lowercase().str.contains("mitglied"),
            pl.col("Einheit").str.contains("Extern").not_(),
            pl.col("Einheit").str.contains("Gruppe").not_(),
            pl.col("Einheit").str.contains("Vorgeplant").not_(),        
            (
                pl.col("Start").gt(zeitpunkt_auswertung)
            ),
        ).sort("Start")

        .with_columns(
            pl.when(
                pl.col("Ende").is_null() | pl.col("Ende").gt(zeitpunkt_auswertung)
            )
            .then(pl.lit('Übertritt folge'))
            .otherwise(pl.lit('Personalbewegung'))
            .alias('Personalbewegung')
        )
    )
    return (df_rollen_personalbewegung_folge,)


@app.cell
def _(
    df_rollen_personalbewegung,
    df_rollen_personalbewegung_folge,
    df_rollen_personalbewegung_vor,
):
    fn_ids_personalbewegung = df_rollen_personalbewegung.group_by('FEUERnetz-ID').len().filter(pl.col('len').eq(1)).select(pl.implode('FEUERnetz-ID')).to_series()

    df_rollen_personalbewegung_grouped_single = (
        df_rollen_personalbewegung.filter(
            pl.col('FEUERnetz-ID').is_in(fn_ids_personalbewegung)
        )
        .group_by('FEUERnetz-ID')
        .agg(
            pl.col("Personalbewegung").first().alias('Personalbewegung'),
            pl.col("Einheit").first().alias('Einheit Alt_'),
        )
    )

    df_rollen_personalbewegung_grouped_multiple = (
        df_rollen_personalbewegung.filter(
            pl.col('FEUERnetz-ID').is_in(fn_ids_personalbewegung).not_()
        )
        .sort(['Name', 'Vorname', 'Start'])
        .group_by('FEUERnetz-ID')
        .agg(
            pl.col("Einheit").first().alias('Einheit Alt'),
        )
    )

    df_rollen_personalbewegung_vor_grouped =  (
        df_rollen_personalbewegung_vor.filter(
            pl.col('FEUERnetz-ID').is_in(fn_ids_personalbewegung)
        )
        .group_by('FEUERnetz-ID')
        .agg(
            pl.col("Einheit").last().alias('Einheit Vor')
        )
    )

    df_rollen_personalbewegung_folge_grouped =  (
        df_rollen_personalbewegung_folge.filter(
            pl.col('FEUERnetz-ID').is_in(fn_ids_personalbewegung)
        )
        .group_by('FEUERnetz-ID')
        .agg(
            pl.col("Einheit").first().alias('Einheit Folge')
        )
    )
    return (
        df_rollen_personalbewegung_folge_grouped,
        df_rollen_personalbewegung_grouped_multiple,
        df_rollen_personalbewegung_grouped_single,
        df_rollen_personalbewegung_vor_grouped,
    )


@app.cell
def _(df_quali):
    df_quali_grouped_grundasubildung = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').str.contains('Truppmann'))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias('Truppmann'))
    )

    df_quali_grouped_truppfuehrer = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').str.contains('Truppführer'))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias('Truppführer'))
    )

    df_quali_grouped_gruppenfuehrer = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').str.contains('Gruppenführer'))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias('Gruppenführer'))
    )

    df_quali_grouped_zugfuehrer = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').str.contains('Zugführer'))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias('Zugführer'))
    )

    df_quali_grouped_verbandsfuehrer = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').str.contains('Verbandsführer'))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias('Verbandsführer'))
    )

    df_quali_grouped_stabsarbeit = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').str.contains('Stabsarbeit'))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias('Stabsarbeit'))
    )

    df_quali_grouped_ldf = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').str.contains('Leiter einer Feuerwehr'))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias('Leiter einer Feuerwehr'))
    )
    return (
        df_quali_grouped_grundasubildung,
        df_quali_grouped_gruppenfuehrer,
        df_quali_grouped_ldf,
        df_quali_grouped_stabsarbeit,
        df_quali_grouped_truppfuehrer,
        df_quali_grouped_verbandsfuehrer,
        df_quali_grouped_zugfuehrer,
    )


@app.cell
def _(df_quali):
    df_quali_grouped_atemschutz = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').eq('Atemschutztauglichkeit (AGT)'))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias('Atemschutzgeräteträger'))
    )

    df_quali_grouped_csa = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').eq('Träger von Chemikalienschutzanzügen (CSA)'))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias('Chemikalienschutzanzug'))
    )

    df_quali_grouped_g26 = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').eq('G26.3'))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Ende").last().alias('G26.3'))
    )
    return (
        df_quali_grouped_atemschutz,
        df_quali_grouped_csa,
        df_quali_grouped_g26,
    )


@app.cell
def _(df_quali):
    df_quali_grouped_fuehrerschein_c1 = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').is_in(["C1", "C1E"]))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias('Führerschein C1'))
    )

    df_quali_grouped_fuehrerschein_c = (
        df_quali
        .sort(by='Start')
        .filter(pl.col('Qualifikation').is_in(["C", "CE"]))
        .group_by('FEUERnetz-ID')
        .agg(pl.col("Start").first().alias('Führerschein C'))
    )
    return df_quali_grouped_fuehrerschein_c, df_quali_grouped_fuehrerschein_c1


@app.cell
def _(df_dienstgrad, zeitpunkt_auswertung):
    df_dienstgrad_grouped = (
        df_dienstgrad
        .sort('Ernannt ab')
        .filter(pl.col('Ernannt ab').le(zeitpunkt_auswertung))
        .group_by('FEUERnetz-ID')
        .agg(pl.col('Ernannt ab').last().alias('Dienstgrad Ernennung'))
    )
    return (df_dienstgrad_grouped,)


@app.cell
def _(
    datum_auswertung,
    df_dienstgrad_grouped,
    df_quali_grouped_atemschutz,
    df_quali_grouped_csa,
    df_quali_grouped_fuehrerschein_c,
    df_quali_grouped_fuehrerschein_c1,
    df_quali_grouped_g26,
    df_quali_grouped_grundasubildung,
    df_quali_grouped_gruppenfuehrer,
    df_quali_grouped_ldf,
    df_quali_grouped_stabsarbeit,
    df_quali_grouped_truppfuehrer,
    df_quali_grouped_verbandsfuehrer,
    df_quali_grouped_zugfuehrer,
    df_rollen_grouped_dienstzeit,
    df_rollen_grouped_dienstzeit_aktiv,
    df_rollen_grouped_einheit,
    df_rollen_grouped_eintritt,
    df_rollen_grouped_rolle,
    df_rollen_personalbewegung_folge_grouped,
    df_rollen_personalbewegung_grouped_multiple,
    df_rollen_personalbewegung_grouped_single,
    df_rollen_personalbewegung_vor_grouped,
    df_stamm,
    ehrung_land,
    ehrung_verband,
    erster_tag_jahr,
):
    df_joined = (
        df_stamm
        # Aktuelle Einheit
        .join(df_rollen_grouped_einheit, on='FEUERnetz-ID', how="left")
        # Eintrittsdatum in der Feuerwehr
        .join(df_rollen_grouped_eintritt, on='FEUERnetz-ID', how="left")
        # Aktuelle Rolle
        .join(df_rollen_grouped_rolle, on='FEUERnetz-ID', how="left")

        # Ernennungsdatum Dienstgrad
        .join(df_dienstgrad_grouped, on='FEUERnetz-ID', how="left")

        # Personalwechsel
        .join(df_rollen_personalbewegung_grouped_single, on='FEUERnetz-ID', how="left")
        .join(df_rollen_personalbewegung_grouped_multiple, on='FEUERnetz-ID', how="left")
        .join(df_rollen_personalbewegung_vor_grouped, on='FEUERnetz-ID', how="left")
        .join(df_rollen_personalbewegung_folge_grouped, on='FEUERnetz-ID', how="left")

        # Dienstzeiten
        .join(df_rollen_grouped_dienstzeit.select(['FEUERnetz-ID', 'Dienstzeit']), on='FEUERnetz-ID', how="left")
        .join(df_rollen_grouped_dienstzeit_aktiv.select(['FEUERnetz-ID', 'Dienstzeit Aktiv']), on='FEUERnetz-ID', how="left")

        # Einsatzfunktionen und Lehrgänge nach FwDV2    
        .join(df_quali_grouped_grundasubildung, on='FEUERnetz-ID', how="left")
        .join(df_quali_grouped_truppfuehrer, on='FEUERnetz-ID', how="left")
        .join(df_quali_grouped_gruppenfuehrer, on='FEUERnetz-ID', how="left")
        .join(df_quali_grouped_zugfuehrer, on='FEUERnetz-ID', how="left")
        .join(df_quali_grouped_verbandsfuehrer, on='FEUERnetz-ID', how="left")
        .join(df_quali_grouped_stabsarbeit, on='FEUERnetz-ID', how="left")
        .join(df_quali_grouped_ldf, on='FEUERnetz-ID', how="left")

        # Atemschutz / ABC I / G26.3
        .join(df_quali_grouped_g26, on='FEUERnetz-ID', how="left")
        .join(df_quali_grouped_atemschutz, on='FEUERnetz-ID', how="left")
        .join(df_quali_grouped_csa, on='FEUERnetz-ID', how="left")

        # Führerscheine Klasse C(E) und/oder C1(E)
        .join(df_quali_grouped_fuehrerschein_c1, on='FEUERnetz-ID', how="left")
        .join(df_quali_grouped_fuehrerschein_c, on='FEUERnetz-ID', how="left")

    ).with_columns(pl.col("Einheit Alt_").fill_null(pl.col("Einheit Alt"))
    ).with_columns(pl.col("Einheit Alt").fill_null(pl.col("Einheit Alt_"))
    ).with_columns([

        # Geschlecht anzeigen
        pl.when(pl.col("Anrede").eq("Herr"))
            .then(pl.lit("M"))
            .when(pl.col("Anrede").eq("Frau"))
            .then(pl.lit("W"))
            .otherwise(None)
            .alias("Geschlecht"),

        # Alter in Jahren ermitteln
        pl.when(
            pl.date(
                pl.col("Geburtsdatum").dt.year(),
                datum_auswertung.value.month,
                datum_auswertung.value.day,
            )
            >= pl.col("Geburtsdatum")
        )
            .then(datum_auswertung.value.year - pl.col("Geburtsdatum").dt.year())
            .otherwise(
                datum_auswertung.value.year - pl.col("Geburtsdatum").dt.year() - 1
            )
            .alias("Alter"),

        # Aktuelle Abteilung
        pl.when(pl.col('Einheit Aktuell').str.starts_with('Einheit'))
            .then(pl.lit('Einsatzabteilung'))
            .otherwise(pl.col('Einheit Aktuell').str.split(by=' ').list.first()).alias('Abteilung'),

        # Ortsteil zur Abteilung
        pl.col('Einheit Aktuell').str.split(by=' ').list.last().alias('Ortsteil'),

        # Personalbewegung vertiefen
        pl.when(
            pl.col('Personalbewegung').str.contains('Jahr'),
            pl.col('Einheit Vor').is_not_null(),
        ).then(None).when(
            pl.col('Personalbewegung').eq('Neuaufnahme'),
            pl.col('Einheit Aktuell').ne(pl.col('Einheit Vor')),
        ).then(None).when(
            pl.col('Einheit Aktuell').str.contains('Einheit'),
            pl.col('Einheit Vor').str.contains('Jugend') | pl.col('Einheit Alt').str.contains('Jugend'),
        ).then(
            pl.lit('Jugendfeuerwehr -> Einsatzabteilung')
        ).when(
            pl.col('Einheit Folge').str.contains('Ehren'),
            pl.col('Einheit Vor').str.contains('Einheit'),
        ).then(
            pl.lit('Einsatzabteilung -> Ehrenabteilung')
        ).when(
            pl.col('Einheit Aktuell').str.contains('Unterstützung') | pl.col('Einheit Folge').str.contains('Unterstützung'),
            pl.col('Einheit Vor').str.contains('Einheit') | pl.col('Einheit Alt').str.contains('Einheit'),
        ).then(
            pl.lit('Einsatzabteilung -> Unterstützungseinheit')
        ).when(
            pl.col('Einheit Aktuell').str.contains('Einheit') | pl.col('Einheit Folge').str.contains('Einheit'),
            pl.col('Einheit Vor').str.contains('Unterstützung') | pl.col('Einheit Alt').str.contains('Unterstützung'),
        ).then(
            pl.lit('Unterstützungseinheit -> Einsatzabteilung')
        ).when(
            pl.col('Einheit Aktuell').str.contains('Ehren'),
            pl.col('Einheit Vor').str.contains('Unterstützung'),
        ).then(
            pl.lit('Unterstützungseinheit -> Ehrenabteilung')
        ).when(
            pl.col('Einheit Aktuell Start').lt(erster_tag_jahr),
            pl.col('Personalbewegung').eq('Neuaufnahme'),
        ).then(None).when(
            pl.col('Einheit Aktuell').is_null(),
            pl.col('Einheit Folge').str.contains('Ehren'),
        ).then(
            pl.lit('Übertritt Ehrenabteilung')
        ).otherwise(
            pl.col('Personalbewegung')
        ).alias('Personalbewegung'),

    ]).with_columns([

        # Altersgruppe ermitteln           
        pl.when(pl.col("Einheit").str.len_chars().eq(0))
            .then(None)
            .when(pl.col("Alter").lt(6))
            .then(pl.lit("> 6"))
            .when(pl.col("Alter").lt(10))
            .then(pl.lit("6 - 9"))
            .when(pl.col("Alter").lt(18))
            .then(pl.lit("10 - 17"))
            .when(pl.col("Alter").lt(28))
            .then(pl.lit("18 - 27"))
            .when(pl.col("Alter").lt(38))
            .then(pl.lit("28 - 37"))
            .when(pl.col("Alter").lt(48))
            .then(pl.lit("38 - 47"))
            .when(pl.col("Alter").lt(58))
            .then(pl.lit("48 - 57"))
            .when(pl.col("Alter").lt(68))
            .then(pl.lit("58 - 67"))
            .otherwise(pl.lit("> 67"))
            .alias("Altersgruppe"),

        # Im aktiven Dienst?
        pl.when(pl.col("Einheit Aktuell").str.len_chars().eq(0))
            .then(None)
            .when(pl.col("Alter").ge(67))
            .then(False)
            .when(pl.col("Alter").lt(10))
            .then(False)
            .when(pl.col("Abteilung").str.contains("Ehren"))
            .then(False)
            .otherwise(True)
            .alias("Aktiver Dienst"),

        # Ehrungen ermitteln
        pl.when(pl.col("Einheit Aktuell").str.len_chars().eq(0))
            .then(None)
            .when(
                pl.col("Alter").ge(10),
                pl.col("Alter").lt(67),
                pl.col("Abteilung").str.contains("Ehren").not_(),
                pl.col("Rolle").str.starts_with("Mitglied"),
                (pl.col('Dienstzeit Aktiv').dt.total_days() / 365.25).cast(int).is_in(ehrung_land),
            )
            .then(
                pl.format(
                    "Land - {} Jahre", (pl.col('Dienstzeit Aktiv').dt.total_days() / 365.25).cast(int)
                )
            )
            .when(
                pl.col("Rolle").str.contains("Zweit").not_(),
                (pl.col('Dienstzeit').dt.total_days() / 365.25).cast(int).is_in(ehrung_verband),
            )
            .then(
                pl.format("Verband - {} Jahre", (pl.col('Dienstzeit').dt.total_days() / 365.25).cast(int))
            )
            .otherwise(None)
            .alias("Ehrung"),

        # Dienstzeit von Tage in Jahre umrechnen
        (pl.col('Dienstzeit').dt.total_days() / 365.25).cast(int).alias('Dienstzeit Jahre'),
        (pl.col('Dienstzeit Aktiv').dt.total_days() / 365.25).cast(int).alias('Dienstzeit Aktiv Jahre'),

        # Mitglied in der Einsatzabteilung
        pl.col('Abteilung').eq('Einsatzabteilung').alias('Einsatzabteilung'),

    ]).with_columns(
        pl.col("Ortsteil").fill_null(pl.col("Einheit Alt").str.split(by=' ').list.last()),
        pl.col("Abteilung").fill_null(pl.col("Einheit Alt").str.split(by=' ').list.first().str.replace('Einheit', 'Einsatzabteilung')),
    ).drop('Einheit Alt_')
    return (df_joined,)


@app.cell
def _(datum_befoerderung, df_joined):
    df_promo = df_joined.filter(
        pl.col('Abteilung').eq('Einsatzabteilung') | pl.col('Abteilung').eq('Unterstützungseinheit'),
        pl.col('Rolle').str.starts_with('Mitglied')
    ).with_columns(
        #Beförderungen ermitteln

        ## Übertritt von der Jugendfeuerwehr in die Einsatzabteilung -> Feuerwehrmann / -frau
        pl.when(
            pl.col('Dienstgrad Ernennung').is_null(),
            pl.col('Einheit Alt').str.contains('Jugendfeuerwehr')
        )
        .then(pl.lit('FFr / FM'))

        ## Bei Neuaufnahme und Mitgliedschaft von 6 Monaten -> Feuerwehrmann / -frau    
        .when(
            pl.col('Dienstgrad Ernennung').is_null(),
            pl.col('Personalbewegung').eq('Neuaufnahme'),
            pl.col('Einheit Aktuell Start').dt.offset_by('6mo').le(datum_befoerderung.value)
        )
        .then(pl.lit('FFr / FM'))

        ## Anwärter und Mitgliedschaft von 6 Monaten -> Feuerwehrmann / -frau    
        .when(
            pl.col('Einheit Aktuell Start').dt.offset_by('6mo').le(datum_befoerderung.value),
            pl.col('Dienstgrad FF(lang)').str.contains('Anwärter')
        )
        .then(pl.lit('FFr / FM'))

        ## Wenn sonst kein Dienstgrad vergeben ist
        .when(
            pl.col('Dienstgrad Ernennung').is_null(),
        )
        .then(pl.lit('FFrA / FMA'))

        ## Führungskräfte inkl. Lehrgang

        ### Beförderung zum Stadtbrandinspektor
        .when(
            pl.col('Dienstgrad FF').ne("StBI"),
            pl.col('Stabsarbeit').le(datum_befoerderung.value),
            pl.col('Leiter einer Feuerwehr').le(datum_befoerderung.value),       
        )
        .then(pl.lit('StBI'))

        ### Beförderung zum Brandoberinspektor
        .when(
            pl.col('Dienstgrad FF').eq("BI"),
            pl.col('Verbandsführer').le(datum_befoerderung.value),      
        )
        .then(pl.lit('BOI'))

        ### Beförderung zum Brandinspektor
        .when(
            pl.col('Dienstgrad FF').is_in(["OBM", "HBM"]),
            pl.col('Zugführer').le(datum_befoerderung.value),      
        )
        .then(pl.lit('BI'))

        ### Beförderung vom Oberfeuerwehrmann zum Brandmeister
        .when(
            pl.col('Dienstgrad FF').is_in(["OFFr", "OFM"]),
            pl.col('Dienstgrad Ernennung').dt.offset_by('1y').le(datum_befoerderung.value),
            pl.col('Gruppenführer').le(datum_befoerderung.value),      
        )
        .then(pl.lit('BM'))

        ### Beförderung zum Brandmeister
        .when(
            pl.col('Dienstgrad FF').is_in(["HFFr", "HFM", "UBM"]),
            pl.col('Gruppenführer').le(datum_befoerderung.value),      
        )
        .then(pl.lit('BM'))

        ### Beförderung vom Hauptfeuerwehrmann zum Unterbrandmeister
        .when(
            pl.col('Dienstgrad FF').is_in(["HFFr", "HFM"]),
            pl.col('Truppführer').le(datum_befoerderung.value),
        )
        .then(pl.lit('UBM'))

        ### Beförderung vom Oberfeuerwehrmann zum Unterbrandmeister
        .when(
            pl.col('Dienstgrad FF').is_in(["OFFr", "OFM"]),
            pl.col('Dienstgrad Ernennung').dt.offset_by('1y').le(datum_befoerderung.value),
            pl.col('Truppführer').le(datum_befoerderung.value),
        )
        .then(pl.lit('UBM'))


        ## Beförderung mit entsprechender Dienstzeit

        ### Beförderung vom Feuerwehrmann zum Oberfeuerwehrmann
        .when(
            pl.col('Dienstgrad FF').is_in(["FFr", "FM"]),
            pl.col('Truppmann').le(datum_befoerderung.value),
            pl.col('Dienstgrad Ernennung').dt.offset_by('2y').le(datum_befoerderung.value),        
        )
        .then(pl.lit('OFFr / OFM'))

        ### Beförderung vom Oberfeuerwehrmann zum Hauptfeuerwehrmann
        .when(
            pl.col('Dienstgrad FF').is_in(["OFFr", "OFM"]),
            pl.col('Dienstgrad Ernennung').dt.offset_by('5y').le(datum_befoerderung.value),        
        )
        .then(pl.lit('HFFr / HFM'))

        ### Beförderung vom Brandmeister zum Oberbrandmeister
        .when(
            pl.col('Dienstgrad FF').eq('BM'),
            pl.col('Dienstgrad Ernennung').dt.offset_by('2y').le(datum_befoerderung.value),   
        )
        .then(pl.lit('OBM'))

        ### Beförderung vom Oberbrandmeister zum Hauptbrandmeister
        .when(
            pl.col('Dienstgrad FF').eq('OBM'),
            pl.col('Dienstgrad Ernennung').dt.offset_by('5y').le(datum_befoerderung.value),        
        )
        .then(pl.lit('HBM'))

        .alias('Beförderung')
    ).with_columns(


        # Beförderungsdatum ermitteln

        # Beförderung zum Stadtbrandinspektor
        pl.when(
            pl.col('Beförderung').eq('StBI'),
            pl.col('Leiter einer Feuerwehr').ge(datum_befoerderung.value)
        )
        .then(pl.col('Leiter einer Feuerwehr'))

        .when(
            pl.col('Beförderung').eq('StBI'),
            pl.col('Stabsarbeit').ge(datum_befoerderung.value)
        )
        .then(pl.col('Stabsarbeit'))

        # Beförderung zum Brandoberinspektor
        .when(
            pl.col('Beförderung').eq('BOI'),
            pl.col('Verbandsführer').ge(datum_befoerderung.value)
        )
        .then(pl.col('Verbandsführer'))

        # Beförderung zum Brandinspektor
        .when(
            pl.col('Beförderung').eq('BI'),
            pl.col('Zugführer').ge(datum_befoerderung.value)
        )
        .then(pl.col('Zugführer'))

        # Beförderung zum Brandmeister -> Beförderungsdatum entspricht Abschlussdatum Lehrgang Gruppenführer-Basis
        .when(pl.col('Beförderung').eq('BM'))
        .then(pl.col('Gruppenführer'))

        # Beförderung zum Unterbrandmeister
        .when(
            pl.col('Beförderung').eq('UMB'),
            pl.col('Truppführer').ge(datum_befoerderung.value)
        )
        .then(pl.col('Truppführer'))

        # Beförderung vom Anwärter zum Feuerwehrmann -> Beförderungsdatum entspricht Eintrittsdatum plus 6 Monate
        .when(
            pl.col('Beförderung').eq('FFr / FM'),
            pl.col('Dienstgrad FF(lang)').str.contains('Anwärter'),
        )
        .then(pl.col('Dienstgrad Ernennung').dt.offset_by('6mo'))

        .when(
            pl.col('Beförderung').eq('FFr / FM'),
            pl.col('Personalbewegung').eq('Neuaufnahme'),
        )
        .then(pl.col('Einheit Aktuell Start').dt.offset_by('6mo'))

        # Beförderung zum Feuerwehrmann bei Übertritt aus der Jugendfeuerwehr
        .when(
            pl.col('Beförderung').eq('FFr / FM'),
            pl.col('Einheit Alt').str.contains('Jugendfeuerwehr'),
        )
        .then(pl.col('Geburtsdatum').dt.offset_by('18y'))

        # Alle anderen Beförderungen auf 'datum_befoerderung' setzen
        .otherwise(pl.datetime(
            year=datum_befoerderung.value.year,
            month=datum_befoerderung.value.month,
            day=datum_befoerderung.value.day
        ))

        .alias('Beförderungs Datum')

    )
    return (df_promo,)


@app.cell
def _(df_joined, df_promo):
    df = df_joined.join(df_promo['FEUERnetz-ID', 'Beförderung', 'Beförderungs Datum'], on='FEUERnetz-ID', how="left")
    return (df,)


@app.cell
def _():
    ende = dt.datetime.now()
    return (ende,)


@app.cell
def _(df):
    mo.ui.dataframe(
        df=df.filter(
            # pl.col('Vorname').eq('Max'),
            # pl.col('Nachname').eq('Mustermann'),
            # pl.col('Dienstgrad Ernennung').is_not_null(),
            # pl.col('Abteilung').is_not_null(),
            # pl.col('Abteilung').eq('Einsatzabteilung') |
            # pl.col('Abteilung').eq('Unterstützungseinheit'),
            # pl.col('Personalbewegung').eq('Neuaufnahme'),
            # pl.col('Dienstzeit').dt.total_days().gt(365),
            # pl.col('Dienstgrad FF(lang)').str.contains('Anwärter'),
            # pl.col('Beförderung').is_not_null(),
            # pl.col('Einheit Alt').is_not_null(),
            # pl.col('Einheit Aktuell').is_not_null(),
            # pl.col('Beförderung').eq('FFrA / FMA'),
        )
    )
    return


@app.cell
def _(ende, start):
    mo.md(rf"""Dauer für Berechnung der Daten: {(ende-start).total_seconds():.2f} Sekunden""")
    return


@app.cell
def _(df):
    df.filter(
        pl.col('Rolle').is_not_null() | pl.col('Personalbewegung').is_not_null()
    ).with_columns(
        pl.col('Dienstzeit').dt.total_days(),
        pl.col('Dienstzeit Aktiv').dt.total_days(),
    ).write_csv(
        os.path.join(db.ORDNER_AUSGABE, 'personaldaten.csv'),
        date_format=db.DATUM_AUSGABE,
    )
    return


@app.cell
def _(datum_auswertung, datum_befoerderung, ehrung_land, ehrung_verband):
    def export_daten_jahresbericht(df: pl.DataFrame) -> None:
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
            pl.col('Nachname'),
            pl.col('Vorname'),
            pl.col('Ortsteil'),
            pl.col('Dienstgrad FF'),
            pl.col('Beförderung'),
            pl.col('Beförderungs Datum'),
        ).write_csv(
            os.path.join(db.ORDNER_AUSGABE, f'befoerderungen_{datum_befoerderung.value.year}.csv')
        )

        df.filter(
            pl.col('Rolle').is_not_null(),
            pl.col('Ehrung').is_not_null(),
        ).select(
            pl.col('Nachname'),
            pl.col('Vorname'),
            pl.col('Ortsteil'),
            pl.col('Dienstgrad FF'),
            pl.col('Beförderung'),
            pl.col('Ehrung'),
        ).write_csv(
            os.path.join(db.ORDNER_AUSGABE, f'ehrungen_{datum_befoerderung.value.year}.csv')
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
            os.path.join(db.ORDNER_AUSGABE, f'ehrenabteilung_{datum_auswertung.value.year}.csv')
        )

        (df.filter(pl.col('Personalbewegung').is_not_null())
        .group_by(['Ortsteil', 'Abteilung', 'Personalbewegung'])
        .agg(pl.col("Nachname").count())
        .rename({"Nachname": "Anzahl"})
        .write_csv(
            os.path.join(db.ORDNER_AUSGABE, f'personalbewegung_{datum_auswertung.value.year}.csv')
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
    return (export_daten_jahresbericht,)


@app.cell
def _(df, export_daten_jahresbericht):
    mo.ui.button(
        label='Erstelle Daten Jahresbericht',
        on_click=lambda _: export_daten_jahresbericht(df)
    )
    return


@app.cell
def _():
    switch_grafik = mo.ui.switch(label = 'Erstelle Grafiken')
    switch_grafik
    return (switch_grafik,)


@app.cell
def _(switch_grafik):
    switch_grafik_value = switch_grafik.value
    return (switch_grafik_value,)


@app.cell
def _(df, zeitpunkt_auswertung):
    df_grafik = df.filter(
        pl.col('Rolle').is_not_null()
    ).with_columns(
        pl.when(pl.col('G26.3').ge(zeitpunkt_auswertung))
        .then(True)
        .otherwise(False)
        .alias('G26.3 bool')
    )
    return (df_grafik,)


@app.cell
def _(df, switch_grafik_value):
    def grafik_mitglieder_alter_box(df: pl.DataFrame, show: bool = False) -> plt.gca:
        if not switch_grafik_value: return

        plt.figure()
        g = sns.histplot(
            df.to_pandas(),
            x="Alter",
            hue='Geschlecht',
            hue_order=['M', 'W'],
            palette="deep",
            multiple='stack',
            bins=range(6, df.select(pl.max("Alter")).item(), 2)
        )
        plt.axvline(10, linestyle=':', color='blue')
        plt.axvline(18, linestyle=':', color='green')
        plt.axvline(60, linestyle=':', color='orange')
        plt.axvline(67, linestyle=':', color='red')

        g.figure.suptitle('Altersverteilung Gesamt')
        g.set(
                xlabel='Alter',
                ylabel='Anzahl',
            )

        sns.move_legend(g, "upper right")

        plt.savefig(os.path.join(db.pfad_grafik, 'Mitglieder_alter_box.png'), bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_mitglieder_alter_box(df, switch_grafik_value)
    return


@app.cell
def _(df_grafik, switch_grafik_value):
    def grafik_mitglieder_alter(df: pl.DataFrame, show: bool = False) -> plt.gca:
        if not switch_grafik_value: return

        plt.figure()
        g = sns.displot(
            data=df.to_pandas(),
            x='Alter',
            hue='Abteilung',
            hue_order=['Kinderfeuerwehr', 'Jugendfeuerwehr', 'Einsatzabteilung', 'Unterstützungseinheit', 'Ehrenabteilung'],
            palette='deep',
            multiple='stack',
            col='Geschlecht',
            col_order=['M', 'W'],
            fill=True,
            binwidth=5,
            element='bars',
        )

        g.figure.suptitle('Altersverteilung Gesamt nach Abteilungen')

        g.set(
                xlabel='Alter',
                ylabel='Anzahl',
            )

        g.legend.set_title('Abteilung')

        plt.savefig(os.path.join(db.pfad_grafik, 'Mitglieder_alter.png'), bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_mitglieder_alter(df_grafik, switch_grafik_value)
    return


@app.cell
def _(abteilungen, df_grafik, switch_grafik_value):
    def grafik_mitglieder_alter_box_orga(df: pl.DataFrame, show: bool = False) -> plt.gca:
        if not switch_grafik_value: return

        plt.figure()
        g = sns.boxplot(
            data=df.to_pandas(),
            x="Alter",
            y="Abteilung",
            hue='Geschlecht',
            order=abteilungen,
            hue_order=['M', 'W'],
            palette="deep",
        )
        plt.axvline(10, linestyle=':', color='blue')
        plt.axvline(18, linestyle=':', color='green')
        plt.axvline(60, linestyle=':', color='orange')
        plt.axvline(67, linestyle=':', color='red')

        g.figure.suptitle('Altersverteilung nach Abteilung')
        g.set(
            ylabel=None,
            xlabel='Alter'
        )

        sns.move_legend(g, "lower right")

        output_file = os.path.join(db.pfad_grafik, 'Mitglieder_alter_box_orga.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_mitglieder_alter_box_orga(df_grafik, switch_grafik_value)
    return


@app.cell
def _(df_grafik, ortsteile, switch_grafik_value):
    def grafik_mitlgieder_einheit(df: pl.DataFrame, show: bool = False) -> plt.gca:
        if not switch_grafik_value: return

        plt.figure()
        g = sns.boxplot(
            data=df.sort(by='Ortsteil').to_pandas(),
            x="Alter",
            y="Ortsteil",
            order=ortsteile,
            hue='Geschlecht',
            hue_order=['M', 'W'],
            palette="deep",
        )
        plt.axvline(10, linestyle=':', color='blue')
        plt.axvline(18, linestyle=':', color='green')
        plt.axvline(60, linestyle=':', color='orange')
        plt.axvline(67, linestyle=':', color='red')

        g.figure.suptitle('Altersverteilung je Einheit')
        g.set(
            ylabel=None,
            xlabel='Alter'
        )

        output_file = os.path.join(db.pfad_grafik, 'Mitglieder_einheit.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_mitlgieder_einheit(df_grafik, switch_grafik_value)
    return


@app.cell
def _(df_grafik, ortsteile, switch_grafik_value):
    def grafik_einheit_fuehrungskraefte(df: pl.DataFrame, show: bool = False) -> plt.gca:
        if not switch_grafik_value: return

        fig = plt.figure()
        g = sns.boxplot(
            data=df.filter(
                pl.col('Gruppenführer').is_not_null(),
                pl.col('Alter').lt(67),
                pl.col('Abteilung').eq('Einsatzabteilung')
            ).sort(by=['Ortsteil']).to_pandas(),
            x="Alter",
            y="Ortsteil",
            order=ortsteile,
            hue='Geschlecht',
            #kind='swarm',
            palette='deep'
        )
        plt.axvline(18, linestyle=':', color='green')
        plt.axvline(60, linestyle=':', color='orange')
        plt.axvline(67, linestyle=':', color='red')

        g.figure.suptitle('Altersverteilung Führungskräfte')
        g.set(
            ylabel=None,
            xlabel='Alter'
        )

        output_file = os.path.join(db.pfad_grafik, 'Mitglieder_einheit_FK.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_einheit_fuehrungskraefte(df_grafik, switch_grafik_value)
    return


@app.cell
def _(abteilungen, df_grafik, ortsteile, switch_grafik_value):
    def grafik_mitglieder_einheit_detail(df: pl.DataFrame, ortsteil: str, show: bool = False):
        if not switch_grafik_value: return

        plt.figure()
        g = sns.displot(
            data=df.filter(pl.col('Ortsteil').eq(ortsteil)).sort(by=["Altersgruppe"]).to_pandas(),
            x='Alter',
            hue='Abteilung',
            hue_order=abteilungen,
            palette='deep',
            multiple='stack',
            col='Geschlecht',      
            col_order=['M', 'W'],
            fill=True,
            binwidth=5,
            element='bars',
        )

        ax1, ax2 = g.axes[0]
        ax1.axvline(18, linestyle=':', color='green')
        ax1.axvline(60, linestyle=':', color='orange')
        ax1.axvline(67, linestyle=':', color='red')
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

        ax2.axvline(18, linestyle=':', color='green')
        ax2.axvline(60, linestyle=':', color='orange')
        ax2.axvline(67, linestyle=':', color='red')
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

        g.figure.suptitle(f'Altersverteilung in {ortsteil}')
        g.set(
            ylabel='Anzahl',
            xlabel='Alter'
        )

        output_file = os.path.join(db.pfad_grafik, f'Mitglieder_alter_{ortsteil}.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafiken_einheit_detail = []

    if switch_grafik_value:
        for ortsteil in ortsteile:
            grafiken_einheit_detail.append(grafik_mitglieder_einheit_detail(df_grafik, ortsteil, switch_grafik_value))

    grafiken_einheit_detail
    return


@app.cell
def _(df_grafik, switch_grafik_value):
    def grafik_mitglieder_jufw_kifw(df: pl.DataFrame, show: bool = False):
        if not switch_grafik_value: return

        plt.figure()
        g = sns.displot(
            data=df.filter(pl.col.Abteilung.eq('Kinderfeuerwehr') | pl.col.Abteilung.eq('Jugendfeuerwehr')).to_pandas(),
            x='Alter',
            hue='Geschlecht',
            hue_order=['W','M'],
            col='Abteilung',
            col_order=['Kinderfeuerwehr', 'Jugendfeuerwehr'],
            palette='deep',
            multiple='stack',
            fill=True,
            binwidth=1,
            element='bars',
        )

        g.figure.suptitle('Altersverteilung Kinder- und Jugendfeuerwehr')
        g.set(
            ylabel='Anzahl',
            xlabel='Alter'
        )

        output_file = os.path.join(db.pfad_grafik, 'Mitglieder_KiFw_JFw_alter.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_mitglieder_jufw_kifw(df_grafik, switch_grafik_value)
    return


@app.cell
def _(df_grafik, ortsteile, switch_grafik_value):
    def grafik_agt_einheit(df: pl.DataFrame, show: bool = False):
        if not switch_grafik_value: return

        plt.figure()
        g = sns.countplot(
            data=df.filter(
                pl.col('Aktiver Dienst'),
                pl.col('Abteilung').eq('Einsatzabteilung'),
                pl.col('Atemschutzgeräteträger').is_not_null(),
                pl.col.Alter.le(67),
            ).to_pandas(),
            x='Ortsteil',
            order=ortsteile,
            hue='G26.3 bool',
            hue_order=[True, False],
            palette='deep',
            linewidth=1,
            edgecolor='black'
        )

        g.figure.suptitle('Übersicht Atemschutzgeräteträger je Einheit')
        g.set(
            xlabel=None,
            ylabel='Anzahl',
        )

        plt.legend(labels=['tauglich', 'nicht tauglich'])

        output_file = os.path.join(db.pfad_grafik, 'AGT_einheiten.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_agt_einheit(df_grafik, switch_grafik_value)
    return


@app.cell
def _(df_grafik, switch_grafik_value):
    def grafik_agt_alter(df: pl.DataFrame, show: bool = False):
        if not switch_grafik_value: return

        plt.figure()
        g = sns.histplot(
            data=df.filter(
                pl.col('Aktiver Dienst'),
                pl.col('Abteilung').eq('Einsatzabteilung'),
                pl.col('Atemschutzgeräteträger').is_not_null(),
                pl.col.Alter.le(67),
            ).to_pandas(),
            x="Alter",
            hue='G26.3 bool',
            palette="deep",
            multiple='stack',
            bins=range(18, 67, 3),
        )

        g.figure.suptitle('Übersicht Atemschutzgeräteträger Gesamt')
        g.set(
            xlabel=None,
            ylabel='Alter',
        )

        plt.legend(labels=['tauglich', 'nicht tauglich'])

        plt.axvline(18, linestyle=':', color='green')
        plt.axvline(60, linestyle=':', color='orange')
        plt.axvline(67, linestyle=':', color='red')

        output_file = os.path.join(db.pfad_grafik, 'AGT_alter.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_agt_alter(df_grafik, switch_grafik_value)
    return


@app.cell
def _(df_grafik, ortsteile, switch_grafik_value):
    def grafik_csa_einheit(df: pl.DataFrame, show: bool = False):
        if not switch_grafik_value: return

        plt.figure()
        g = sns.countplot(
            data=df.filter(
                pl.col('Aktiver Dienst'),
                pl.col('Abteilung').eq('Einsatzabteilung'),
                pl.col('Chemikalienschutzanzug').is_not_null(),
                pl.col.Alter.le(67),
            ).to_pandas(),
            x='Ortsteil',
            order=ortsteile,
            hue='G26.3 bool',
            hue_order=[True, False],
            palette='deep',
            linewidth=1,
            edgecolor='black'
        )

        g.figure.suptitle('Übersicht Chemikalienschutzanzugträger je Einheit')
        g.set(
            xlabel=None,
            ylabel='Anzahl'
        )
        plt.legend(labels=['tauglich', 'nicht tauglich'])

        output_file = os.path.join(db.pfad_grafik, 'CSA_einheiten.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_csa_einheit(df_grafik, switch_grafik_value)
    return


@app.cell
def _(df_grafik, switch_grafik_value):
    def grafik_csa_alter(df: pl.DataFrame, show: bool = False):
        if not switch_grafik_value: return

        plt.figure()
        g = sns.histplot(
            data=df.filter(
                pl.col('Aktiver Dienst'),
                pl.col('Abteilung').eq('Einsatzabteilung'),
                pl.col('Chemikalienschutzanzug').is_not_null(),
                pl.col.Alter.le(67),
            ).to_pandas(),
            x="Alter",
            hue='G26.3 bool',
            palette="deep",
            multiple='stack',
            bins=range(18, 67, 3),
        )

        plt.legend(labels=['tauglich', 'nicht tauglich'])

        plt.axvline(18, linestyle=':', color='green')
        plt.axvline(60, linestyle=':', color='orange')
        plt.axvline(67, linestyle=':', color='red')

        g.figure.suptitle('Übersicht Chemikalienschutzanzugträger Gesamt')
        g.set(
            ylabel=None,
            xlabel='Alter'
        )

        output_file = os.path.join(db.pfad_grafik, 'CSA_alter.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_csa_alter(df_grafik, switch_grafik_value)
    return


@app.cell
def _(df_grafik, ortsteile, switch_grafik_value):
    def grafik_lkw_einheit(df: pl.DataFrame, show: bool = False):
        if not switch_grafik_value: return

        plt.figure()
        g = sns.countplot(
            data=df.filter(
                pl.col('Aktiver Dienst'),
                pl.col('Abteilung').eq('Einsatzabteilung'),
                pl.col('Führerschein C').is_not_null(),
                pl.col.Alter.le(67),
            ).to_pandas(),
            x='Ortsteil',
            order=ortsteile,
            hue='Geschlecht',
            hue_order=['M', 'W'],
            palette='deep',
            linewidth=1,
            edgecolor='black'
        )

        g.figure.suptitle('Übersicht Führerscheininhaber:innen Klasse C je Einheit')
        g.set(
            xlabel=None,
            ylabel='Anzahl'
        )

        output_file = os.path.join(db.pfad_grafik, 'LKW_einheit.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_lkw_einheit(df_grafik, switch_grafik_value)
    return


@app.cell
def _(df_grafik, switch_grafik_value):
    def grafik_lkw_alter(df: pl.DataFrame, show: bool = False):
        if not switch_grafik_value: return

        plt.figure()
        g = sns.histplot(
            data=df.filter(
                pl.col('Aktiver Dienst'),
                pl.col('Abteilung').eq('Einsatzabteilung'),
                pl.col('Führerschein C').is_not_null(),
                pl.col.Alter.le(67),
            ).to_pandas(),
            x="Alter",
            hue='Geschlecht',
            hue_order=['M', 'W'],
            palette="deep",
            multiple='stack',
            bins=range(18, 67, 3),
        )

        g.yaxis.set_major_locator(MaxNLocator(integer=True))

        plt.axvline(18, linestyle=':', color='green')
        plt.axvline(60, linestyle=':', color='orange')
        plt.axvline(67, linestyle=':', color='red')

        g.figure.suptitle('Übersicht Führerscheininhaber:innen Klasse C Gesamt')
        g.set(
            ylabel=None,
            xlabel='Alter'
        )

        output_file = os.path.join(db.pfad_grafik, 'LKW_alter.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_lkw_alter(df_grafik, switch_grafik_value)
    return


@app.cell
def _(df_grafik, ortsteile, switch_grafik_value):
    def grafik_mitglieder_aufnahme(df: pl.DataFrame, show: bool = False):
        if not switch_grafik_value: return

        plt.figure()
        g = sns.countplot(
            data=df.filter(pl.col("Personalbewegung").eq('Neuaufnahme')).to_pandas(),
            y="Ortsteil",
            order=ortsteile,
            hue='Abteilung',
            palette='deep',
            linewidth=1,
            edgecolor='black'
        )

        g.figure.suptitle('Übersicht neuer Mitglieder')
        g.set(xlabel='Anzahl')
        g.xaxis.set_major_locator(MaxNLocator(integer=True))

        output_file = os.path.join(db.pfad_grafik, 'Mitglieder_neu.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_mitglieder_aufnahme(df_grafik, switch_grafik_value)
    return


@app.cell
def _(df_grafik, switch_grafik_value):
    # TODO: Funktion üperprüfen
    def grafik_mitglieder_verlust(df: pl.DataFrame, show: bool = False):
        if not switch_grafik_value: return

        plt.figure()
        g = sns.countplot(
            data=df.filter(pl.col("Einheit Ehemals").is_not_null()).to_pandas(),
            y="Einheit Ehemals",
            hue='Geschlecht',
            hue_order=['M', 'W'],
            palette='deep',
            linewidth=1,
            edgecolor='black'
        )

        g.figure.suptitle('Übersicht ausgeschiedener Mitglieder')
        g.set(xlabel='Anzahl')
        g.xaxis.set_major_locator(MaxNLocator(integer=True))

        output_file = os.path.join(db.pfad_grafik, 'Mitglieder_verlust.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafik_mitglieder_verlust(df_grafik, switch_grafik_value)
    return


@app.cell
def _(df_grafik, ortsteile, switch_grafik_value):
    # TODO: Funktion üperprüfen
    def grafik_mitglieder_wechsel(df: pl.DataFrame, ortsteil: str, show: bool = False):
        if not switch_grafik_value: return

        data=df.filter(
            pl.col("Personalbewegung").str.contains('->'),
            pl.col('Ortsteil').eq(ortsteil)
        )
        if not data.height > 0:
            return None
        plt.figure()
        g = sns.countplot(
            data=data.to_pandas(),
            y='Einheit Aktuell',
            hue="Einheit Alt",
            palette='deep',
            linewidth=1,
            edgecolor='black'
        )

        g.figure.suptitle(f'Personalwechsel {ortsteil}')
        g.set(xlabel='Anzahl')
        g.xaxis.set_major_locator(MaxNLocator(integer=True))

        # plt.legend(bbox_to_anchor=(1.04, 0), loc="lower left")

        output_file = os.path.join(db.pfad_grafik, f'Mitglieder_wechsel_{ortsteil}.png')
        plt.savefig(output_file, bbox_inches = 'tight')

        plt.tight_layout()
        return plt.gca()

    grafiken_einheit_wechsel = []

    if switch_grafik_value:
        for ortsteil_wechsel in ortsteile:
            grafiken_einheit_wechsel.append(grafik_mitglieder_wechsel(df_grafik, ortsteil_wechsel, switch_grafik_value))

    grafiken_einheit_wechsel
    return


if __name__ == "__main__":
    app.run()
