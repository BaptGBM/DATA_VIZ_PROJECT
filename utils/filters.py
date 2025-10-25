import streamlit as st
import pandas as pd


def display_logical_filters(df):
    # -------------------------------Filtre 1 ------------------------------
    operateurs_options = ['All operators'] + sorted(df['nom_operateur'].unique())
    selected_operateur = st.sidebar.selectbox(
        "Operator :",
        options=operateurs_options
    )

    #-----------------------------FILTRE 2----------------------------------------------

    puissance_min = int(df['puissance_nominale'].min())#borne inf
    puissance_max_realiste = int(df['puissance_nominale'].quantile(0.99)) # avoid outliers/ borne sup

    selected_power = st.sidebar.slider(
        "Power range (kW):",
        min_value=puissance_min,
        max_value=puissance_max_realiste, 
        value=(puissance_min, puissance_max_realiste)
    )

    # --------------------------- Filtre 3 -----------------------------------

    pdc_min = int(df['nbre_pdc'].min())#borne inf
    pdc_max_realiste = int(df['nbre_pdc'].quantile(0.995)) #borne sup

    selected_pdc = st.sidebar.slider(
        "Number of charging points:",
        min_value=pdc_min,
        max_value=pdc_max_realiste, #
        value=(pdc_min, pdc_max_realiste)
    )

    # -------------------------------- Filtre 4 ---------------------------------
    acces_options = ['All conditions'] + ['Accès libre']+['Accès réservé']
    selected_acces = st.sidebar.selectbox(
        "Conditions of access:",
        options=acces_options
    )

    # -------------------------------- Filtre 5 -------------------------------
    prise_options = [
        'All types', 
        'Type 2', 
        'Combo CCS', 
        'CHAdeMO', 
        'Type EF / Domestique'
    ]
    selected_prise = st.sidebar.selectbox(
        "Plug type:",
        options=prise_options
    )

    # ------------------------FILTRE 6 : -------------------------
    paiement_options = [
        'Payment by credit card',
        'Pay-as-you-go',
        'Other payment methods'
    ]
    selected_paiement = st.sidebar.multiselect(
        "Accepted payment methods:",
        options=paiement_options
    )

    df_filtered = df.copy()


    # ---------------------------- LOGIC DE FILATRAGE------------------------------------------
    if selected_operateur != 'All operators':
        df_filtered = df_filtered[df_filtered['nom_operateur'] == selected_operateur]

    if selected_acces != 'All conditions':
        df_filtered = df_filtered[df_filtered['condition_acces'] == selected_acces]

    if selected_prise != 'All types':
        prise_mapping = {
            'Type 2': 'prise_type_2',
            'Combo CCS': 'prise_type_combo_ccs',
            'CHAdeMO': 'prise_type_chademo',
            'Type EF / Domestique': 'prise_type_ef'
        }
        colonne_prise = prise_mapping[selected_prise]
        
        if colonne_prise in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[colonne_prise].fillna(False) == True]
        

    if selected_paiement:
        paiement_mapping = {
            'Payment by credit card': 'paiement_cb',
            'Pay-as-you-go': 'paiement_acte',
            'Other payment methods': 'paiement_autre'
        }
        selected_cols = [paiement_mapping[opt] for opt in selected_paiement]
        df_filtered = df_filtered[df_filtered[selected_cols].any(axis=1)]

    df_filtered = df_filtered[
        df_filtered['puissance_nominale'].between(selected_power[0], selected_power[1]) &
        df_filtered['nbre_pdc'].between(selected_pdc[0], selected_pdc[1])
    ]

    return df_filtered
