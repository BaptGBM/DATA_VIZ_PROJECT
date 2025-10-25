import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json
from utils.prep import categorize_power

def display_overview_tab(df_filtered):

    st.header("Map of charging stations")
    st.map(df_filtered, latitude='consolidated_latitude', longitude='consolidated_longitude')
    
    st.subheader("Filtered selection statistics")
    # KPi qui s'adapte au data filtrés: df_filtered
    if not df_filtered.empty:
        kpi_d1, kpi_d2, kpi_d3 = st.columns(3)
        kpi_d1.metric("Number of terminals selected", f"{len(df_filtered):,}")
        kpi_d2.metric("Total load points", f"{int(df_filtered['nbre_pdc'].sum()):,}")
        kpi_d3.metric("Average power (kW)", f"{df_filtered['puissance_nominale'].mean():.2f}")
    else:
        st.warning("No terminals match the selected filters.")

    st.subheader("Detailed filtered data")
    df_display = df_filtered.copy()
    if 'geometry' in df_display.columns:
        df_display['geometry'] = df_display['geometry'].astype(str)
    st.dataframe(df_display)

def evolution_nb_bornes(df):
    #-----------------------Graph 1-----------------
    st.subheader("Evolution of Terminal Installations Over Time")
    df_time = df.dropna(subset=['date_mise_en_service'])
    # convertit la colonne de date en un format date-heure correct, nécessaire pour le rééchantillonnage.
    #  errors=coerce transforme tout format de date invalide en NaT.
    df_time['date_mise_en_service'] = pd.to_datetime(df_time['date_mise_en_service'])


    # divide by quarter ou trimestre ('Q')
    installations_par_trimestre = df_time.set_index('date_mise_en_service').resample('Q').size()

    installations_par_trimestre = installations_par_trimestre[
        (installations_par_trimestre.index.year >= 2015) & 
        (installations_par_trimestre.index.year <= 2025)
    ]
    installations_par_trimestre.index.name = "Trimestre"
    st.write("This graph shows the number of new charging stations installed each quarter. There has been a clear acceleration in deployment in recent years.")
    st.line_chart(installations_par_trimestre)
    st.write("Post-2020 acceleration: We are seeing a radical change of scale. Before 2020, quarterly installations were modest. After that, they exploded, with peaks exceeding 7,000 stations per quarter, reflecting strong political and industrial will. A dynamic of “sprints”: The curve is not linear but consists of peaks and troughs. This may reflect waves of deployment linked to subsidy programs, operators' annual targets, or seasonal effects.")

    st.write("---")

    # ------------------- GRAPH 2-------------------------
    st.subheader("Evolution timeline by power category")
    df_time['categorie_puissance'] = df_time['puissance_nominale'].apply(categorize_power)
    power_evolution = df_time.groupby([pd.Grouper(key='date_mise_en_service', freq='Q'), 'categorie_puissance']).size().reset_index(name='count')
    power_evolution_pivot = power_evolution.pivot(index='date_mise_en_service', columns='categorie_puissance', values='count').fillna(0)

    category_order = ["Slow (< 22 kW)","Fast (22-50 kW)", "Rapid (50-150 kW)", "Ultra-Fast (>= 150 kW)"]
    power_evolution_pivot = power_evolution_pivot.reindex(columns=category_order, fill_value=0)
    
    power_evolution_filtered = power_evolution_pivot[power_evolution_pivot.index.year >= 2015]
    
    st.write("This chart shows the composition of the network over time. There has been a marked increase in the proportion of fast and ultra-fast charging stations in recent years, a sign of the network's maturity.")
    st.area_chart(power_evolution_filtered)
    st.write("""
This timeline is the most revealing, as it shows the qualitative transformation of the network.
The “slow” beginnings: Until 2019, the network consisted almost exclusively of slow and accelerated charging stations (in blue), suitable for charging in the city or at the office.
The explosion of “fast”: From 2021 onwards, the share of fast and ultra-fast charging stations (in red) increases dramatically. This is a sign that the national strategy has changed to meet the needs of long journeys and drastically reduce waiting times, a key factor for mass adoption.""")
    st.write("---") 

        # ----------------------------- GRAPH 3----------------------- ---
    st.subheader("Cumulative growth in the number of terminals")
    parc_installe_cumul = installations_par_trimestre.cumsum()
    #calcul al somme de toutes les bornes
    parc_installe_cumul.name = "Total number of terminals in service"

    st.write("""This curve shows the evolution of the total number of terminals in service over time. We can see growth accelerating sharply from 2020-2021.""")
        
    st.line_chart(parc_installe_cumul)
    st.write(""" This last curve is the result of all these efforts. It represents the total number of charging stations available to drivers.
The “S” curve of innovation: We can clearly see the signature of a technology reaching maturity: a slow start-up phase lasting several years, followed by an inflection point around 2020 where growth becomes exponential.
A staggering change of scale: The number of charging stations has more than doubled in just two or three years, from around 40,000 to over 100,000. This is tangible proof that the transition is underway.
Transition Question: This impressive growth is no accident. But who are the players, the “builders” behind these figures? We will explore this in the next tab.""")

def display_top_op(df_filtered):
    st.subheader("Power profile of the 10 largest operators")
    top_10_operateurs = df_filtered['nom_operateur'].value_counts().nlargest(10).index
        
    df_top10 = df_filtered[df_filtered['nom_operateur'].isin(top_10_operateurs)]
    # Créer un nouevelle colonne pour faciliter la visualisation basé sur les catégories de la fonction catagegorize_power dans utils.prep.py    
    df_top10['categorie_puissance'] = df_top10['puissance_nominale'].apply(categorize_power)

    chart = alt.Chart(df_top10).mark_bar().encode(
        x=alt.X('nom_operateur:N', title='Operator'),  
        y=alt.Y('count():Q', title='Number of Terminals'),
            
        xOffset='categorie_puissance:N',# xOffset crée l'effet groupé

        #  couleur différente à chaque catégorie de puissance
        color=alt.Color('categorie_puissance:N',
                        title='Power Category',
                        sort=["Lente (< 22 kW)", "Accélérée (22-50 kW)", "Rapide (50-150 kW)", "Ultra-rapide (>= 150 kW)"]),
            
        tooltip=['nom_operateur', 'categorie_puissance', 'count()']
            
    ).properties(
        title="Breakdown of the fleet by power for the Top 10"
    )
        
    st.write("""This graph reveals the strategies of the main players. Some, such as Tesla, focus almost exclusively on ultra-fast charging, while others offer a more varied mix to cover different needs (city, highway, etc.).”""") 
    st.altair_chart(chart, use_container_width=True)

    st.write("""This chart is the centerpiece. It does not cover the entire market, but focuses on the 10 most influential players in order to analyze their strategy.
Two Leadership Models: The graph highlights two distinct strategies for domination. On the one hand, Bouygues E&S and Freshmile base their leadership on volume, with a huge fleet of “Slow” and “Accelerated” charging stations. Their strength lies in their local network coverage (cities, car parks).
The Race for Power: On the other hand, players such as Power Dot and Tesla are pursuing a power-focused strategy. A significant portion of their network consists of “fast” and “ultra-fast” charging stations. They are targeting the market for long journeys and rapid recharging during the day.
Players such as Lidl and TotalEnergie illustrate a third approach: integrating charging as a customer service. Their networks, although substantial, offer a mix of power levels designed to attract customers while they shop.""") 
    st.write("---") 

def camembert_op(df):
    st.subheader("Overall distribution of terminals by operator (market share for France as a whole)")
    op_counts = df['nom_operateur'].value_counts()
        
    top_10_op = op_counts.nlargest(10)
    # Calcule la somme de toutes les bornes des opérateurs qui ne sont pas dans le top 10
    autres_sum = op_counts.iloc[10:].sum()
        
    if autres_sum > 0:
        top_10_op['Others'] = autres_sum
            
    df_pie = top_10_op.reset_index()# Transforme la série en un DataFrame pour qu'il soit utilisable par Altair.
    df_pie.columns = ['Opérateur', 'Nombre de Bornes']

    chart_pie = alt.Chart(df_pie).mark_arc(innerRadius=70, outerRadius=120).encode(
            theta=alt.Theta(field="Nombre de Bornes", type="quantitative"),#angle de chaque part du camembert proportionnel au nombre de bornes
            color=alt.Color(field="Opérateur", type="nominal",# couleur différente pour chaque opérateur.
                        legend=alt.Legend(title="Operators", symbolLimit=25)),
            tooltip=['Opérateur', 'Nombre de Bornes']
    ).properties(
        title="Overall market shares of the top 10 operators"
    )
    st.write("This graph shows market concentration across the entire territory. It remains fixed to serve as a reference, regardless of the filters applied.")
    st.altair_chart(chart_pie, use_container_width=True)

def display_top_departements_chart(df):

    st.subheader("Density of terminals by department")
    departement_counts = df['departement'].value_counts().reset_index()
    departement_counts.columns = ['departement', 'Nombre de Bornes']
    departement_counts = departement_counts.sort_values('Nombre de Bornes', ascending=False)

    # Afficher un graphique en barres en attendant
    st.write("Top 20 departments with the most charging stations:")
    # Crée le graphique en barres avec altaire en utilisant uniquement les 20 premières lignes
    chart_bar = alt.Chart(departement_counts.head(20)).mark_bar().encode(
        x=alt.X('Nombre de Bornes:Q', title='Number of terminals'),
        # sort='-x' trie les barres sur l'axe Y en fonction de la valeur de l'axe X, de la plus grande à la plus petite.
        y=alt.Y('departement:N', sort='-x', title='Department'),
        color=alt.Color('Nombre de Bornes:Q', scale=alt.Scale(scheme='blues'), title='Number of terminals'),
        tooltip=['departement', 'Nombre de Bornes']
    ).properties(
        height=1000,
        title="Best-equipped departments"
    )
            
    st.altair_chart(chart_bar, use_container_width=True)
 
def display_carte_by_depart(df):
    st.header("Analysis of the geographic distribution of terminals")
    st.subheader("Map showing the density of terminals by department")

    if 'departement' in df.columns:
        # Ouvre et charge le fichier GeoJSON qui contient les contours des départements
        with open("data/departements-version-simplifiee.geojson", 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

        departement_counts = df['departement'].value_counts().reset_index()# Compte le nombre de bornes pour chaque département
        departement_counts.columns = ['departement', 'Nombre de Bornes']

        # Crée la figure choroplèthe avec Plotly Express.
        fig = px.choropleth(
            departement_counts,
            geojson=geojson_data,
            locations='departement',# La colonne des données qui sert de clé de jointure
            featureidkey="properties.code",# Le chemin vers la clé de jointure dans le fichier GeoJSON
            color='Nombre de Bornes',
            color_continuous_scale='RdYlBu_r',  
            range_color=(0, departement_counts['Nombre de Bornes'].max()),
        )
        fig.update_geos(
            fitbounds="locations",# Zoome automatiquement la carte sur la France
            bgcolor='#0d1117',
        )

        # MAJ les paramètres généraux de mise en page de la figure
        fig.update_layout(
            height=700,
            margin={"r": 20, "t": 30, "l": 20, "b": 20},
            paper_bgcolor='#0d1117',
            plot_bgcolor='#0d1117',
            font=dict(color='#c9d1d9', size=13),

            # Personnalise l'apparence de la légende de couleur
            coloraxis_colorbar=dict(
                title=dict(text="Number of terminals", font=dict(color='white', size=14)),
                thickness=20,
                len=0.6,
                x=1.02,
                bgcolor='rgba(13, 17, 23, 0.8)',
                bordercolor='#30363d',
                borderwidth=2,
                tickfont=dict(color='white')
            )
        )
        fig.update_traces(
            marker_line_color='rgba(255,255,255,0.3)',
            marker_line_width=1
        )
        st.plotly_chart(fig, use_container_width=True)

def display_datapreprocessing(df):
    st.subheader("Main preparation steps")
#----------------------------- PART 1 --------------------------------------------------
    st.markdown("#### 1. Column selection and handling of missing values")
    st.markdown(
        "The initial dataset contained many unnecessary columns. The first step was to **select only the columns relevant** to the analysis in order to streamline and clarify the dataset. In addition, **missing values** (`NaN`) for critical fields such as the operator name were handled, for example by replacing them with ‘Operator not specified’ to avoid errors in the analyses.")
    st.code("""
            
colonnes_a_garder = [
    'nom_operateur', 'adresse_station', 'consolidated_longitude', 
        'consolidated_latitude', 'puissance_nominale', 'prise_type_ef', 
        'prise_type_2', 'prise_type_combo_ccs', 'prise_type_chademo', 
        'prise_type_autre', 'paiement_acte', 'paiement_cb', 
        'paiement_autre', 'condition_acces', 'reservation', 'date_mise_en_service','nbre_pdc'
]
df_prepared = df[colonnes_a_garder].copy()

df_prepared['nom_operateur'].fillna('Opérateur non spécifié', inplace=True)
df_prepared['paiement_cb'].fillna(False, inplace=True)
df_prepared['paiement_autre'].fillna(False, inplace=True)
df_prepared['paiement_acte'].fillna(False, inplace=True)
    """, language='python')

    # -------------------------- MISSING DATA_MISE_EN_SERVICE----------------------------------------
    missing_dates = df['date_mise_en_service'].isnull().sum()
    df_missing_info = pd.DataFrame({
        'Information': ["missing data_mise_en_service"],
        'Number of missing values': [f"{missing_dates:,}"]
    })

    st.dataframe(df_missing_info, use_container_width=True, hide_index=True)

    st.info(
        "Rather than inventing dates, which would have skewed the analysis, undated markers were retained but **excluded from the time series graphs**. This ensures the reliability of these visualizations."
    )
    st.write("---")

# --------------------------- PART 2 ----------------------------------
    st.markdown("#### 2. Standardization of Operator Names")
    st.markdown(
        "One of the biggest challenges was the inconsistency of operator names. The same player, such as ‘TotalEnergies’, appeared under several different names. So I applied a comprehensive mapping dictionary to group all the variants under a single, unique name.")
    st.code("""

mapping_operateurs = {
    'TOTALENERGIES CHARGING SERVICES': 'TOTALENERGIES',
    'TOTALENERGIES MARKETING FRANCE': 'TOTALENERGIES',
    'BOUYGUES ENERGIES & SERVICES': 'BOUYGUES E&S',
    'TESLA FRANCE SARL': 'TESLA',
    # ... 
}
df_prepared['nom_operateur'] = df_prepared['nom_operateur'].replace(mapping_operateurs)
    """, language='python')

#-----------------------------PART 3---------------------------------------
    st.markdown("#### 3. Geographic Enrichment through Spatial Joining")
    st.markdown(
 "Postal code information was often missing or incorrect. To obtain reliable location data by department, I used **spatial join**. Using the GPS coordinates of each terminal, cross-referenced with a vector map of the departments, to determine their geographical location with certainty."  )
    st.info("vector maps of departments: https://github.com/gregoiredavid/france-geojson")
    st.code("""

gdf_bornes = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(...))
gdf_departements = gpd.read_file(...)
gdf_final = gpd.sjoin(gdf_bornes, gdf_departements, ...)
    """, language='python')

# ------------------------ PART 4------------------------------------------------------
    st.markdown("#### 4. Type Conversion and Variable Creation")
    st.markdown("""
        Finally, to make the data usable, several conversions were necessary:
- dates were converted to `datetime` format, power ratings to numerical format, and technical information (plug types) was normalized to Boolean values (True/False). 
- **New variables** were created, such as power categories (‘Slow,’ 'Fast,' etc.), to facilitate visualization."""
    )
    st.code("""

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

def categorize_power(power):
    if power < 22: return "Slow (< 22 kW)"
    elif power < 22:
        return "Slow (< 22 kW)"
    elif 22 <= power < 50:
        return "Fast (22-50 kW)"
    elif 50 <= power < 150:
        return "Rapid (50-150 kW)"
    else: 
        return "Ultra-Fast (>= 150 kW)"
    """, language='python')

def display_top_operators_by_department_chart(df):

    st.subheader("Top 5 operators by department")
    st.write("Use the drop-down menu below to explore the ranking of operators in a specific department")
    if 'departement' not in df.columns: #check que la colonne 'departement' existe bien.
        st.error("The ‘department’ column cannot be found.")
        return


    departement_list = sorted(df['departement'].unique())#tri les departements
    
    selected_dept = st.selectbox(#choix de user
        "Select a department:",
        options=departement_list,
        index=None, # Permet de n'avoir rien de sélectionné au départ
        placeholder="Select a department to see the ranking"
    )

   
    if selected_dept: # a partir du choix du user .......
        
        df_dept = df[df['departement'] == selected_dept]
        top_5_op = df_dept['nom_operateur'].value_counts().nlargest(5).reset_index()# on selecte les 5 premiers
        top_5_op.columns = ['Opérateur', 'Nombre de Bornes']

        if not top_5_op.empty:
            chart = alt.Chart(top_5_op).mark_bar().encode(
                x=alt.X('Nombre de Bornes:Q', title="Number of Terminals"),
                y=alt.Y('Opérateur:N', title="Operator", sort='-x')
            ).properties(
                title=f"Top 5 operators in the department {selected_dept}"
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info(f"No terminal data was found for the department. {selected_dept}.")

def display_operator_comparator_tab(df, categorize_power_func):
   
    st.header("Operator Comparison Tool")
    st.write(
        "Use the drop-down menu below to select up to 3 operators. "
        "All charts in this tab will update to allow you to directly compare their strategies and growth dynamics."
    )
    
    # liste de tous les opérateurs uniques.
    operator_list = sorted(df['nom_operateur'].unique())
    st.info("Select up to 3 operators to compare")

    # widget multiselec avec 3 choix 
    selected_operators = st.multiselect("Choose:",
        options=operator_list,
        default=['TOTALENERGIES', 'TESLA', 'BOUYGUES E&S'],
        placeholder="Select operators",
        max_selections=3  
    )

    st.write("---")


    if selected_operators:# check si user select au moins un opérateur
        df_selection = df[df['nom_operateur'].isin(selected_operators)].copy()

        col1, col2 = st.columns(2)#pour afficher les graphiques à coté 

        with col1:
            # ------------------------GRAPHIQUE 1 --------------------------------
            st.subheader("Composition of the fleet by power")
            df_selection['categorie_puissance'] = df_selection['puissance_nominale'].apply(categorize_power_func)
            
            chart_power = alt.Chart(df_selection).mark_bar().encode(
                x=alt.X('nom_operateur:N', title='Operator', sort='-y'),#sort='-y' trie les opérateurs par nombre total de bornes
                y=alt.Y('count():Q', title='Number of Terminals'),
                color=alt.Color('categorie_puissance:N', 
                              title='Power Category',
                              sort=["Lente (< 22 kW)", "Accélérée (22-50 kW)", "Rapide (50-150 kW)", "Ultra-rapide (>= 150 kW)"])
            ).properties(height=400)
            st.altair_chart(chart_power, use_container_width=True)

        with col2:
            # -----------------------------GRAPHIQUE 2 ---------------------------------
            st.subheader("Growth Dynamics")
            df_growth = df_selection.dropna(subset=['date_mise_en_service'])# Supprime les bornes sans date 
            
            if not df_growth.empty:## Vérifie si il reste bien des rows
                growth_data = df_growth.groupby(['nom_operateur', pd.Grouper(key='date_mise_en_service', freq='QE')]).size().reset_index(name='installations')
                # Groupe les données par opérateur ET par trimestre ('QE' = Quarter End).
                growth_data['parc_cumulé'] = growth_data.groupby('nom_operateur')['installations'].cumsum()
                growth_data = growth_data[growth_data['date_mise_en_service'].dt.year >= 2015]# à partir de 2015

                chart_growth = alt.Chart(growth_data).mark_line().encode(
                    x=alt.X('date_mise_en_service:T', title='Date'),
                    y=alt.Y('parc_cumulé:Q', title='Total number of terminals'),
                    color=alt.Color('nom_operateur:N', title='Operator'),
                    tooltip=['nom_operateur', 'date_mise_en_service', 'parc_cumulé']# Info-bulle,display ces informations sous la souris.
                ).properties(height=400)
                st.altair_chart(chart_growth, use_container_width=True)
            else:
                st.info("No time data available for this selection.")
    
    else:
        st.info("Please select at least one operator to start the comparison.")