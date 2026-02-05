import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")

with app.setup:
    # Initialization code that runs before all other cells
    import os
    import math
    import marimo as mo
    import polars as pl
    import datetime as dt

    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    import seaborn as sns

    from database import database as db

    import database.fn_config as fn_config


@app.cell
def _():
    datums_format = "%d.%m.%Y"
    return (datums_format,)


@app.cell
def _():
    postleitzahlen = db.postleitzahl_list()
    return (postleitzahlen,)


@app.cell
def _():
    jahr_heute = dt.datetime.now().year

    datum_auswertung_start = mo.ui.date(
        value=dt.date(jahr_heute, 1, 1)
    )

    datum_auswertung_ende = mo.ui.date(
        value=dt.date(jahr_heute, 12, 31)
    )
    return datum_auswertung_ende, datum_auswertung_start


@app.cell
def _(datum_auswertung_ende, datum_auswertung_start):
    mo.md(
        rf"""
    ## Auswertungszeitraum
    {datum_auswertung_start} bis {datum_auswertung_ende}
    """
    )
    return


@app.cell
def _(datum_auswertung_ende, datum_auswertung_start):
    date_start = datum_auswertung_start.value
    date_ende = datum_auswertung_ende.value

    if date_start >= date_ende:
        date_start = date_ende - dt.timedelta(days=1)

    zeitpunkt_auswertung_start = dt.datetime(
        date_start.year,
        date_start.month,
        date_start.day
    )

    zeitpunkt_auswertung_ende = dt.datetime(
        date_ende.year,
        date_ende.month,
        date_ende.day
    )
    return zeitpunkt_auswertung_ende, zeitpunkt_auswertung_start


@app.cell
def _(postleitzahlen, zeitpunkt_auswertung_ende, zeitpunkt_auswertung_start):
    df_einsatz = db.lese_einsatzdaten()

    df_einsatz = df_einsatz.filter(
        pl.col('Beginn').ge(zeitpunkt_auswertung_start),
        pl.col('Beginn').le(zeitpunkt_auswertung_ende),
    )

    anzahl_einsaetze = df_einsatz.height
    anzahl_einsaetze_extern = df_einsatz.filter(pl.col('Postleitzahl').is_in(postleitzahlen).not_()).height

    df_einsatz = df_einsatz.filter(
        pl.col('Status').eq('freigegeben'),
    )

    anzahl_einsaetze_offen = anzahl_einsaetze -df_einsatz.height

    df_einsatz = df_einsatz.filter(
        pl.col('Postleitzahl').is_in(postleitzahlen),
    )
    return (
        anzahl_einsaetze,
        anzahl_einsaetze_extern,
        anzahl_einsaetze_offen,
        df_einsatz,
    )


@app.cell
def _(
    anzahl_einsaetze,
    anzahl_einsaetze_extern,
    anzahl_einsaetze_offen,
    datum_auswertung_ende,
    datum_auswertung_start,
    datums_format,
):
    mo.md(
        rf"""
    ## Auswerteangaben

    - Zeitraum {datum_auswertung_start.value.strftime(datums_format)} bis {datum_auswertung_ende.value.strftime(datums_format)}
    - Anzahl Einsätze gesamt: **{anzahl_einsaetze}**
    - Anzahl Einsätze extern: **{anzahl_einsaetze_extern}**
    - Anzahl offener Einsatzberichte: **{anzahl_einsaetze_offen}**

    Weitere Auswertungen erfolgen mit den bereits freigegebenen Einsatzberichten.
    """
    )
    return


@app.cell
def _(df_einsatz):
    df_details = db.lese_einsatz_einheiten_details()
    df_details = df_details.filter(
        # pl.col('Beginn').ge(zeitpunkt_auswertung_start),
        # pl.col('Beginn').le(zeitpunkt_auswertung_ende),
        pl.col('Einsatznummer').is_in(df_einsatz.select('Einsatznummer').to_series().to_list()),
    )

    df_details = df_details.with_columns([
        (pl.col('Diff. Alarm-S3 Sek.')/60).alias('Diff. Alarm-S3 Min.'),
        (pl.col('Diff. S3-S4 Sek.')/60).alias('Diff. S3-S4 Min.'),
        ((pl.col('Ende S2') - pl.col('Alarm')).dt.total_seconds()/60/60).alias('Gesamtdauer'),
    ])
    return (df_details,)


@app.cell
def _():
    # mo.ui.dataframe(df=df_einsatz)
    return


@app.cell
def _():
    # mo.ui.dataframe(df=df_details)
    return


@app.cell
def _():
    minuten_ausruecken = mo.ui.number(start=0, value=15, label='Ausrücken [Minuten]')
    minuten_anfahrt = mo.ui.number(start=0, value=15, label='Anfahrt [Minuten]')
    stunden_gesamt = mo.ui.number(start=0, value=15, label='Gesamtdauer [Stunden]')
    return minuten_anfahrt, minuten_ausruecken, stunden_gesamt


@app.cell
def _():
    mo.md(r"""Filter für Einsatzzeiten.""")
    return


@app.cell
def _(minuten_anfahrt, minuten_ausruecken, stunden_gesamt):
    mo.hstack([
        minuten_ausruecken, minuten_anfahrt, stunden_gesamt
    ])
    return


@app.cell
def _(df_details, minuten_anfahrt, minuten_ausruecken, stunden_gesamt):
    mo.ui.dataframe(
        df=df_details.filter(
            pl.col('Diff. Alarm-S3 Min.').ge(minuten_ausruecken.value) |
            pl.col('Diff. S3-S4 Min.').ge(minuten_anfahrt.value) |
            pl.col('Gesamtdauer').ge(stunden_gesamt.value)
        )
    )
    return


@app.cell
def _(df_details):
    df_details.write_csv(os.path.join(db.ORDNER_AUSGABE, 'einsatzdetails.csv'), decimal_comma=True)
    return


@app.cell
def _(df_details, df_einsatz):
    def ausrueckezeiten_fahrzeug(kennung: str = None, ortsteil: list[str] = None, x_tick_rotation: int = 0):
        df_fzg = df_details.filter(
                pl.col('Fahrzeug').str.contains('privat').not_()
            )

        df_fzg = df_fzg.with_columns(
            pl.when(pl.col('Einsatznummer').is_nan()).then(pl.lit('Ja')).otherwise(pl.lit('Nein')).alias('Stammeinheit')
        ).sort('Fahrzeug')

        if kennung:
            df_fzg = df_fzg.filter(
                pl.col('Fahrzeug').str.contains(kennung)
            )

        df_est = df_einsatz.filter(
            pl.col('Einsatznummer').is_in(df_fzg.select('Einsatznummer').to_series().to_list()),
        )

        if ortsteil:
            df_est = df_est.filter(
                pl.col('Ortsteil').is_in(ortsteil)
            )

            df_fzg = df_fzg.with_columns(
                pl.when(
                    pl.col('Einsatznummer').is_in(df_est.select('Einsatznummer').to_series().to_list()),
                ).then(pl.lit('Ja')).otherwise(pl.lit('Nein')).alias('Stammeinheit')
            )

        fig, axes = plt.subplots(1, 3)

        sns.boxplot(
            ax=axes[0],
            data=df_fzg,
            x='Fahrzeug',
            y='Diff. Alarm-S3 Min.',
            hue='Stammeinheit' if ortsteil else None,
            hue_order=['Ja', 'Nein'] if ortsteil else None,
        )

        sns.boxplot(
            ax=axes[1],
            data=df_fzg,
            x='Fahrzeug',
            y='Diff. S3-S4 Min.',
            hue='Stammeinheit' if ortsteil else None,
            hue_order=['Ja', 'Nein'] if ortsteil else None,
        )

        sns.boxplot(
            ax=axes[2],
            data=df_fzg,
            x='Fahrzeug',
            y='Gesamtdauer',
            # showfliers=False,
            hue='Stammeinheit' if ortsteil else None,
            hue_order=['Ja', 'Nein'] if ortsteil else None,
        )

        fig.figure.suptitle('Fahrzeug-Statuszeiten')

        if kennung:
            fig.figure.suptitle(f'Statuszeiten {kennung}')

        axes[0].set(
            xlabel=None,
            ylabel='Zeit Alarm bis Ausrücken [Min]',
        )

        axes[1].set(
            xlabel=None,
            ylabel='Zeit Ausrücken bis Eintreffen [Min]'
        )

        axes[2].set(
            xlabel=None,
            ylabel='Gesamtdauer [h]'
        )

        axes[0].tick_params(axis='x', labelrotation = x_tick_rotation)
        axes[1].tick_params(axis='x', labelrotation = x_tick_rotation)
        axes[2].tick_params(axis='x', labelrotation = x_tick_rotation)

        plt.tight_layout()

        datei_name_list = ['Statuszeiten']
        if kennung:
            datei_name_list.append(kennung)
        if ortsteil != None:
            datei_name_list.append(*ortsteil)

        datei_name = '_'.join(datei_name_list)

        output_file = os.path.join(db.ORDNER_AUSGABE, db.ORDNER_AUSGABE_GRAFIK, datei_name+'.png')
        plt.savefig(output_file, bbox_inches = 'tight')


        return plt.gca()
    return (ausrueckezeiten_fahrzeug,)


@app.cell
def _(df_details, df_einsatz):
    df_elw_details = df_details.filter(
        pl.col('Fahrzeug').str.contains('ELW')
    )

    df_elw = df_einsatz.filter(
        pl.col('Einsatznummer').is_in(df_elw_details.select('Einsatznummer').to_series().to_list())
    )

    anzahl_elw_einsaetze_gesamt = df_elw.height
    return (anzahl_elw_einsaetze_gesamt,)


@app.cell
def _(df_details, df_einsatz):
    df_dlk_details = df_details.filter(
        pl.col('Fahrzeug').str.contains('DLK')
    )

    df_dlk = df_einsatz.filter(
        pl.col('Einsatznummer').is_in(df_dlk_details.select('Einsatznummer').to_series().to_list())
    )

    anzahl_dlk_einsaetze_gesamt = df_dlk.height
    return (anzahl_dlk_einsaetze_gesamt,)


@app.cell
def _(df_details, df_einsatz):
    df_rw_details = df_details.filter(
        pl.col('Fahrzeug').str.contains('DLK')
    )

    df_rw = df_einsatz.filter(
        pl.col('Einsatznummer').is_in(df_rw_details.select('Einsatznummer').to_series().to_list())
    )

    anzahl_rw_einsaetze_gesamt = df_rw.height
    return (anzahl_rw_einsaetze_gesamt,)


@app.cell
def _(df_details, df_einsatz):
    df_gwl_details = df_details.filter(
        pl.col('Fahrzeug').str.contains('GW-L2')
    )

    df_gwl = df_einsatz.filter(
        pl.col('Einsatznummer').is_in(df_gwl_details.select('Einsatznummer').to_series().to_list())
    )

    anzahl_gwl_einsaetze_gesamt = df_gwl.height
    return (anzahl_gwl_einsaetze_gesamt,)


@app.cell
def _(anzahl_elw_einsaetze_gesamt):
    mo.md(
        rf"""
    ## Sonderfahrzeuge
    Ein ELW ist im Auswertezeitraum in insgesamt **{anzahl_elw_einsaetze_gesamt}** Einsätzen eingesetzt worden.
    """
    )
    return


@app.cell
def _(ausrueckezeiten_fahrzeug):
    ausrueckezeiten_fahrzeug('ELW', ['Brünen'])
    return


@app.cell
def _(anzahl_dlk_einsaetze_gesamt):
    mo.md(rf"""Eine DLK ist im Auswertezeitraum in insgesamt **{anzahl_dlk_einsaetze_gesamt}** Einsätzen eingesetzt worden.""")
    return


@app.cell
def _(ausrueckezeiten_fahrzeug):
    ausrueckezeiten_fahrzeug('DLK', ['Hamminkeln'])
    return


@app.cell
def _(anzahl_rw_einsaetze_gesamt):
    mo.md(rf"""Ein RW ist im Auswertezeitraum in insgesamt **{anzahl_rw_einsaetze_gesamt}** Einsätzen eingesetzt worden.""")
    return


@app.cell
def _(ausrueckezeiten_fahrzeug):
    ausrueckezeiten_fahrzeug('RW', ['Hamminkeln'])
    return


@app.cell
def _(anzahl_gwl_einsaetze_gesamt):
    mo.md(rf"""Ein 1.GW-L2 ist im Auswertezeitraum in insgesamt **{anzahl_gwl_einsaetze_gesamt}** Einsätzen eingesetzt worden.""")
    return


@app.cell
def _(ausrueckezeiten_fahrzeug):
    ausrueckezeiten_fahrzeug('GW-L2', ['Hamminkeln'])
    return


@app.cell
def _():
    mo.md(r"""## Statuszeiten je Einheit""")
    return


@app.cell
def _(ausrueckezeiten_fahrzeug):
    ausrueckezeiten_fahrzeug('HMM.1', x_tick_rotation=90)
    return


@app.cell
def _(ausrueckezeiten_fahrzeug):
    ausrueckezeiten_fahrzeug('HMM.2', x_tick_rotation=90)
    return


@app.cell
def _(ausrueckezeiten_fahrzeug):
    ausrueckezeiten_fahrzeug('HMM.3', x_tick_rotation=90)
    return


@app.cell
def _(ausrueckezeiten_fahrzeug):
    ausrueckezeiten_fahrzeug('HMM.4', x_tick_rotation=90)
    return


@app.cell
def _(ausrueckezeiten_fahrzeug):
    ausrueckezeiten_fahrzeug('HMM.5', x_tick_rotation=90)
    return


@app.cell
def _(ausrueckezeiten_fahrzeug):
    ausrueckezeiten_fahrzeug('HMM.6', x_tick_rotation=90)
    return


if __name__ == "__main__":
    app.run()
