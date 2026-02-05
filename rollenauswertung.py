import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import marimo as mo
    import polars as pl
    import datetime as dt

    from database import database as db
    from database.database import ORDNER_AUSGABE
    return ORDNER_AUSGABE, db, dt, mo, os, pl


@app.cell
def _(dt, mo):
    ui_date = mo.ui.date(value=dt.date(year=dt.datetime.now().year, month=12, day=31)+dt.timedelta(days=1))
    ui_date
    return (ui_date,)


@app.cell
def _(db):
    df = db.lese_rollen()
    return (df,)


@app.cell
def _(df, pl, ui_date):
    data = df.filter(
        pl.col('Start').le(ui_date.value),
        pl.col('Ende').is_null() |
        pl.col('Ende').gt(ui_date.value),
        pl.col('Rolle').eq('Mitglied') |
        pl.col('Rolle').eq('Zweitmitglied (Doppelmitgliedschaft)') |
        pl.col('Rolle').eq('Mitglied (Beamter)'),
        pl.col('Einheit').ne('Stadt Hamminkeln'),
        pl.col('Einheit').ne('Vorgeplante überörtliche Hilfe'),
        pl.col('Einheit').ne('Stabsstellen und Fachberater'),
        pl.col('Einheit').ne('Funkwerkstatt'),
        pl.col('Einheit').ne('IuK Gruppe'),
        pl.col('Einheit').ne('Externe Feuerwehr'),
    ).with_columns(
        pl.col('Einheit').str.split(" ").list.first().alias('Abteilung'),
        pl.col('Einheit').str.split(" ").list.last().alias('Ortsteil'),
    )

    data_uni = data.sort('Start').unique('FEUERnetz-ID', keep='first')
    data_einsatz_ist = data_uni.filter(
        pl.col('Rolle').eq('Mitglied'),
        pl.col('Abteilung').eq('Einheit'),
    )
    return data, data_einsatz_ist, data_uni


@app.cell
def _(data):
    data #.filter(pl.col('FEUERnetz-ID').is_duplicated())
    return


@app.cell
def _(ORDNER_AUSGABE, data, data_einsatz_ist, data_uni, os, pl):
    data_uni.group_by(['Ortsteil', 'Abteilung']).agg(pl.col('FEUERnetz-ID').count()).write_csv(os.path.join(ORDNER_AUSGABE, 'personal_ges_uni_pivot.csv'))
    data_einsatz_ist.group_by(['Ortsteil', 'Abteilung']).agg(pl.col('FEUERnetz-ID').count()).write_csv(os.path.join(ORDNER_AUSGABE, 'personal_einsatz_ist_pivot.csv'))
    data.group_by(['Ortsteil', 'Abteilung']).agg(pl.col('FEUERnetz-ID').count()).write_csv(os.path.join(ORDNER_AUSGABE, 'personal_ges_pivot.csv'))
    return


if __name__ == "__main__":
    app.run()
