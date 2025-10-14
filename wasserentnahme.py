import marimo

__generated_with = "0.16.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # Initialization code that runs before all other cells
    import os
    import marimo as mo
    import polars as pl
    import pandas as pd

    import folium

    from database import database as db

    import database.fn_config as fn_config
    return db, fn_config, folium, mo, os, pd, pl


@app.cell
def _(fn_config):
    config_allgemein = fn_config.config_object["allgemein"]
    return (config_allgemein,)


@app.cell
def _(db):
    df_wasser = db.lese_wasserentnahmestellen()
    list_plz = db.postleitzahl_list()
    return df_wasser, list_plz


@app.cell
def _(config_allgemein, mo):
    # Name der Kommune
    name_input = mo.ui.text(
        label='Name der Kommune',
        value=config_allgemein['kommune_name']
    )
    name_input
    return


@app.cell
def _(list_plz, mo):
    # Postleitzahl der Kommune
    plz_input = mo.ui.dropdown(
        options=list_plz,
        label='Postleitzahl',
        value=list_plz[0]
    )
    plz_input
    return


@app.cell
def _(config_allgemein, mo):
    # Amtlicher Gemeindeschlüssel (AGS)
    ags_input = mo.ui.text(
        label='Amtlicher Gemeindeschlüssel (AGS)',
        value=config_allgemein['kommune_id']
    )
    ags_input
    return (ags_input,)


@app.cell
def _(ags_input, db):
    data_geo = db.lese_geodaten(ags_input.value)
    return (data_geo,)


@app.cell
def _(df_wasser, mo):
    df_ui = mo.ui.dataframe(df=df_wasser)
    df_ui
    return (df_ui,)


@app.cell
def _(df_ui):
    df = df_ui.value
    return (df,)


@app.cell
def _(pd):
    def find_NE_SW(geoJson):
        # Extract coordinates from municipality border
        data = geoJson['geometry']['coordinates'][0]

        # create dataframe from coordinate points
        df = pd.DataFrame(data, columns = ['longitude', 'latitude'])

        # Find corner points South-West
        sw = df[['latitude', 'longitude']].min().values.tolist()

        # Find corner points North-East
        ne = df[['latitude', 'longitude']].max().values.tolist()

        # Find corner points North-West
        nw = [df.latitude.max(), df.longitude.min()]

        # Find corner points South-East
        se = [df.latitude.min(), df.longitude.max()]

        return [sw, ne], [nw, se]
    return (find_NE_SW,)


@app.cell
def _(folium):
    # Karte erstellen
    map = folium.Map(control_scale = True, zoom_start=13, max_zoom=15)
    return (map,)


@app.cell
def _(config_allgemein, data_geo, folium, map):
    # Kommunalegrenze der Karte hinzufügen
    styl = {'color':'black', 'fillColor':'#00000000', 'weight':1}

    folium.GeoJson(data = data_geo, name=config_allgemein['kommune_name'], style_function=lambda y:styl, control=False).add_to(map)
    return


@app.cell
def _(df, folium, map, pl):
    # Marker pro Wasserentnahmestelle setzen
    typen = sorted(set(df.get_column('Materialtyp').to_list()))

    for typ in typen:
        fg = folium.FeatureGroup(name=typ).add_to(map)

        df_filter = df.filter(
            pl.col('Materialtyp').eq(typ)
        )

        if typ == 'Zisterne':
            icon = 'glass-water-droplet'
            color = "beige"
        elif typ == 'Löschwasserbrunnen':
            icon = 'arrow-up-from-ground-water'
            color = "green"
        elif typ == 'Hydrant':
            icon = 'arrow-up-from-water-pump'
            color = "blue"
        else:
            icon = 'question'
            color = "gray"

        for row in df_filter.iter_rows(named=True):
            einheit_kurz = row['Ausgegeben an Einheit'].split(' ')[-1][1:5]

            if typ in ['Zisterne', 'Löschwasserbrunnen', 'Hydrant']:
                html = f"""
                    <small>{typ}</small><br>
                    <h4>{row['Bezeichner']}</h4>
                    <p>{row['Anschluss']}</p>
                    <small>{einheit_kurz}</small>
                    <br>
                    <small>Pos.: {row['Längengrad']:.6f}, {row['Breitengrad']:.5f}</small>
                """
            else:
                html = row['Bezeichner']
        
            try:
                folium.Marker(
                    location=[row['Längengrad'], row['Breitengrad']],
                    popup=folium.Popup(html, max_width=2048),
                    icon=folium.Icon(
                        color=color,
                        prefix='fa',
                        icon=icon
                    )
                ).add_to(fg)
            except Exception as e:
                print(row, e)
                print()
    return


@app.cell
def _(db, folium, map, pl):
    # Marker pro POI setzen
    df_poi = db.lese_poi()
    poi_typen = sorted(set(df_poi.get_column('Typ').to_list()))

    for poi_t in poi_typen:
        fg_poi = folium.FeatureGroup(name=poi_t).add_to(map)
        for poi in df_poi.filter(pl.col('Typ').eq(poi_t)).iter_rows(named=True):
            folium.Marker(
                location=(poi['Längengrad'], poi['Breitengrad']),
                popup=poi['Benennung'],
                icon=folium.Icon(
                    color=poi['Farbe'],
                    prefix='fa',
                    icon=poi['Icon']
                )
            ).add_to(fg_poi)
    return


@app.cell
def _(data_geo, find_NE_SW, map):
    # Karte zentreieren
    map.fit_bounds(find_NE_SW(data_geo))
    return


@app.cell
def _(folium, map):
    # Add Layer-Control to map
    folium.LayerControl(collapsed=False, hideSingleBase=True).add_to(map)
    return


@app.cell
def _(map):
    map
    return


@app.cell
def _(db, map, os):
    map.save(os.path.join(db.ORDNER_AUSGABE, 'wasserentnahmestellen.html'))
    return


if __name__ == "__main__":
    app.run()
