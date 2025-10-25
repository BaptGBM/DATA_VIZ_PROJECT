import pandas as pd
import geopandas as gpd

def prepare_data(df):
    colonnes_a_garder = [
        'nom_operateur', 'adresse_station', 'consolidated_longitude', 
        'consolidated_latitude', 'puissance_nominale', 'prise_type_ef', 
        'prise_type_2', 'prise_type_combo_ccs', 'prise_type_chademo', 
        'prise_type_autre', 'paiement_acte', 'paiement_cb', 
        'paiement_autre', 'condition_acces', 'reservation', 'date_mise_en_service','nbre_pdc'
    ]
    
    df_prepared = df[colonnes_a_garder].copy()

    df_prepared['date_mise_en_service'] = pd.to_datetime(df_prepared['date_mise_en_service'], errors='coerce')
    df_prepared['puissance_nominale'] = pd.to_numeric(df_prepared['puissance_nominale'], errors='coerce')

    cols_to_normalize = [
        'prise_type_ef', 'prise_type_2', 'prise_type_combo_ccs', 
        'prise_type_chademo', 'prise_type_autre',
        'paiement_acte', 'paiement_cb', 'paiement_autre'
    ]
    true_values = ['true', '1']
    for col in cols_to_normalize:
        if col in df_prepared.columns:
            df_prepared[col] = df_prepared[col].str.lower().isin(true_values)


    df_prepared['nom_operateur'].fillna('Opérateur non spécifié', inplace=True)
    df_prepared['paiement_cb'].fillna(False, inplace=True)
    df_prepared['paiement_autre'].fillna(False, inplace=True)
    df_prepared['paiement_acte'].fillna(False, inplace=True)
    

    df_prepared['nom_operateur'] = df_prepared['nom_operateur'].str.split('|').str[0].str.strip().str.upper()
    mapping_operateurs = {
        'TOTALENERGIES CHARGING SERVICES': 'TOTALENERGIES',
        'TOTALENERGIES MARKETING FRANCE': 'TOTALENERGIES',
        'TOTAL MARKETING FRANCE': 'TOTALENERGIES',
        'TOTAL CHARGING SERVICES': 'TOTALENERGIES',
        'TOTAL ÉNERGIE': 'TOTALENERGIES',
        'ATLANTE FRANCE': 'ATLANTE',
        'FRESHMILE SAS': 'FRESHMILE',
        'CENTRE D\'EXPLOITATION FRESHMILE': 'FRESHMILE',
        'BOUYGUES ENERGIES & SERVICES': 'BOUYGUES E&S',
        'BOUYGUES ENERGIES ET SERVICES': 'BOUYGUES E&S',
        'BOUYGUES ENERGIES SERVICES': 'BOUYGUES E&S',
        'CHARGEPOINT': 'CHARGEPOINT',
        'CHARGE POINT': 'CHARGEPOINT',
        'TESLA FRANCE SARL': 'TESLA',
        'LIDL FRANCE': 'LIDL',
        'IZIVIA': 'IZIVIA',
        'MOVIVE_IZIVIA': 'IZIVIA',
        'ELECTROMAPS': 'ELECTROMAPS',
        'WAAT - PROUDREED': 'WAAT',
        'WAAT SAS': 'WAAT',
        'IONITY': 'IONITY',
        'SHELL RECHARGE': 'SHELL RECHARGE',
        'GREENFLUX': 'GREENFLUX',
        'ALLEGO': 'ALLEGO',
        'DRIVECO': 'DRIVECO',
        'VIRTA': 'VIRTA',
        'EVBOX': 'EVBOX',
        'SPIE CITYNETWORKS': 'SPIE',
        'SPIE CITYNETWORKS': 'SPIE',
        'ZUNDER (GRUPO EASYCHARGER S.A)': 'ZUNDER',
        'ALDI MARCHE COLMAR': 'ALDI',
        'ALDI MARCHE CESTAS SARL': 'ALDI',
        'ALDI MARCHE CAVAILLON (ALDI MARCHE)': 'ALDI',
        'AUTORECHARGE SAS':'AUTORECHARGE',
        'EASY CHARGE SERVICES':'EASY CHARGE',
        'SAS E-MOTUM': 'E-MOTUM',
        'EV MAP SAS': 'EV MAP',
        'BP FRANCE': 'BP',
        'BP PULSE': 'BP',
        'ZEPHYRE SAS': 'ZEPHYRE',
        'NORMATECH LODMI':'NORMATECH',
        'MOBILIZE FAST CHARGE NETWORK FRANCE': 'MOBILIZE FAST CHARGE',
        'SAP LABS FRANCE SAS': 'SAP LABS',
        'SAP LABS FRANCE': 'SAP LABS',
        'CHARGEPOINT AUSTRIA GMBH': 'CHARGEPOINT', 
        'SYNDICAT DÉPARTEMENTAL ÉNERGIE AUBE (SDEA)': 'SDEA',
        "SYNDICAT MIXTE DÉPARTEMENTAL D'ÉNERGIES DU CALVADOS (SDEC ÉNERGIE)": 'SDEC ÉNERGIE',
        "SYNDICAT INTERCOMMUNAL D'ELECTRICITÉ DE CÔTE D'OR (SICECO21)": 'SICECO21',
        "SYNDICAT DÉPARTEMENTAL D'ÉNERGIE DE LA HAUTE-GARONNE (SDEHG)": 'SDEHG',
        "SYNDICAT D'ENERGIE ET DES DÉCHETS DE LA MARNE (SDED52)": 'SDED52',
        'MORBIHAN ÉNERGIES': 'MORBIHAN ÉNERGIES',
        'NAN': 'OPÉRATEUR NON SPÉCIFIÉ',
        'NON CONCERNÉ': 'OPÉRATEUR NON SPÉCIFIÉ',
        'PAS DITINERANCE': 'OPÉRATEUR NON SPÉCIFIÉ',
    }
    df_prepared['nom_operateur'] = df_prepared['nom_operateur'].replace(mapping_operateurs)
    

    # ------------------------------------- JOINTURE SPATIALE -----------------------------------
    gdf_departements = gpd.read_file("data/departements-version-simplifiee.geojson")
    df_bornes_gps = df_prepared.dropna(subset=['consolidated_longitude', 'consolidated_latitude']).copy()

    gdf_bornes = gpd.GeoDataFrame(
        df_bornes_gps,
        geometry=gpd.points_from_xy(df_bornes_gps.consolidated_longitude, df_bornes_gps.consolidated_latitude),
        crs="EPSG:4326"
    )

    gdf_final = gpd.sjoin(gdf_bornes, gdf_departements, how="inner", predicate='within')
    gdf_final.rename(columns={'code': 'departement'}, inplace=True)
    df_final = pd.DataFrame(gdf_final.drop(columns=['geometry', 'index_right', 'nom']))

    return df_final

def categorize_power(power):
    if pd.isna(power) or power <= 0:
        return "Slow (< 22 kW)"
    elif power < 22:
        return "Slow (< 22 kW)"
    elif 22 <= power < 50:
        return "Fast (22-50 kW)"
    elif 50 <= power < 150:
        return "Rapid (50-150 kW)"
    else: 
        return "Ultra-Fast (>= 150 kW)"
