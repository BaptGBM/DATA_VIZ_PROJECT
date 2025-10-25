
import streamlit as st
from sections.intro import display_intro
from utils.io import load_data
from utils.prep import prepare_data, categorize_power
from utils.filters import display_logical_filters
from utils.viz import display_top_departements_chart, display_carte_by_depart, display_top_op, camembert_op,evolution_nb_bornes,display_overview_tab, display_datapreprocessing, display_top_operators_by_department_chart, display_operator_comparator_tab
from sections.conclusion import display_conclusion_tab

st.set_page_config(page_title="Dashboard Bornes de Recharge", layout="wide")


@st.cache_data
def get_cleaned_data():
    df_raw = load_data(path="data/station_electrique.csv")

    df_prepared = prepare_data(df_raw)
    return df_prepared


df = get_cleaned_data()
st.sidebar.header("Filters")

display_intro()


#------------------------------------AFFICHAGE-----------------------------------------------------------------
st.title("Analysis of the Electric Vehicle Charging Station Network in France")
df_filtered = display_logical_filters(df)

# --- ------------------------------KPIs GÉNÉRAUX-------------------------------------------
st.subheader("Overall statistics for the French network")
kpi_g1, kpi_g2, kpi_g3 = st.columns(3)
kpi_g1.metric("Total number of terminals", f"{len(df):,}")
kpi_g2.metric("Total load points", f"{int(df['nbre_pdc'].sum()):,}")
kpi_g3.metric("Average power (kW)", f"{df['puissance_nominale'].mean():.2f}")



# --- ----------------------------ORGANISATION EN ONGLETS ---------------------------------------
st.write("---") 

tab_carte, tab_temporel, tab_market, tab_geo, tab_comparateur, tab_prep= st.tabs([
    "Overview (Map)",
    "Time Series Analysis", 
    "Market Analysis", 
    "Spatial Analysis",
    "Supplier Comparison",
    "Data Preprocessing",
])


#-----------------------ONGLET PREPROCESSING------------------------------------------
with tab_prep:
    st.info(" Backstage: From raw data to analysis")
    st.subheader(" Source, Limitations, and Bias of Data")
    st.markdown(
        """
        The data used in this dashboard comes from the consolidated file of electric vehicle charging stations, published on **data.gouv.fr**.

        It is crucial to understand that this data is collected on a **declarative basis**: each developer is responsible for declaring their own infrastructure. This collection method introduces several **potential biases**:
        - **Coverage bias:** Some smaller or less diligent operators may not report all of their stations, resulting in an underestimation of the actual number of stations.
        - **Quality bias:** The accuracy of the information (address, power, etc.) depends on the rigor of each operator.

        In addition, our cleaning process, particularly for geographic analysis, **excludes charging stations without valid GPS coordinates**. This means that our maps represent a subset of the most complete data, not the entire raw file.
        """
    )
    st.write("---")
    st.write(
        "A relevant analysis always begins with careful data preparation."
        "The original dataset, although rich, presented many challenges: unnecessary columns, inconsistent formats, "
        "missing values and need for enrichment."
    )
    
    df_raw_sample = load_data(path="data/station_electrique.csv").head()
    df_clean_sample = df.head()

    # ------------------ BEFORE/AFTER------------------------
    st.subheader("Overview: Before vs. After cleaning")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Raw data**")
        st.dataframe(df_raw_sample)
    with col2:
        st.write("**Cleaned and enriched data**")
        st.dataframe(df_clean_sample)

    st.write("---")

    display_datapreprocessing(df)
    
#--------------------------------ONGLET CARTE-------------------------------------------------------
with tab_carte:
    display_overview_tab(df_filtered)

#--------------------------------ONGLET ANALYSE TEMPORELLE6--------------------------------------------------------
with tab_temporel:
    st.info("These three graphs tell a powerful story: that of a revolution in progress. Not only has the rollout of charging stations accelerated exponentially since 2020, but the very nature of the network has been transformed, evolving from a “slow” local infrastructure to an increasingly powerful network, tailored for the future.""")
    evolution_nb_bornes(df)
    

#------------------------------ONGLET ANALYSE DES OPERATEURS -----------------------------------------------
with tab_market:
    st.info("""This tab provides an overview of the forces dominating the French charging market. In two stages, I first identify the 10 largest operators in the country, then delve into their strategic DNA to understand how they have built their leadership. The analysis reveals an already structured market, led by players with very different visions.""")
    display_top_op(df)
    camembert_op(df)
    st.write("""This graph reveals a significant concentration of power in the French charging market. Far from being a fragmented ecosystem, the network is in fact dominated by a handful of major players. The ten largest operators are not just leaders; they collectively account for more than half of all charging stations, demonstrating an already structured and mature market where a few “giants” dictate the pace.""")
    


#------------------------------ONGLET COMPARATEUR--------------------------
with tab_comparateur:
    st.info(""" This tab is an investigative tool that allows you to dissect and compare the strategies of market players. By selecting Tesla, Bouygues E&S, and TotalEnergies, we witness a veritable “clash of the titans,” illustrating three radically opposed visions of electric mobility: the high-tech pioneer, the regional integrator, and the energy giant undergoing radical change. """)
    display_operator_comparator_tab(df, categorize_power)
    st.write(""" A comparison of the strategies of Tesla, Bouygues E&S, and TotalEnergies reveals three distinct visions of electric mobility that coexist in the French market. 
             Tesla embodies the technological pioneer, which, buoyed by its early and continuous growth, has built a proprietary ecosystem consisting almost exclusively of ultra-fast Superchargers designed for long journeys.
              In contrast, Bouygues E&S positions itself as the local builder, whose growth through “major projects” has resulted in a huge network of slow and fast charging stations designed to cover the country for everyday use. Finally, TotalEnergies illustrates the giant in transition: its recent massive acceleration in high-power charging reflects its hybrid strategy, which consists of transforming its historic network of gas stations to cover all market segments. This analysis shows that there is not one, but several charging markets, where user choice is dictated by usage: the speed of a Supercharger for a long trip, the availability of a local charging station for overnight charging, or the convenience of a station on the way to vacation.""")


#-------------------------------ONGLET ANALYSE SPATIABLE -------------------------------------
with tab_geo:
    st.info("""This tab tells the story of the territorial development of the charging network in three acts. The first act provides a national overview: a map of France that reveals a clear divide between well-equipped areas and “charging deserts.” The second act puts this observation into figures by ranking the leading departments. Finally, the third act provides the tools for a local survey, enabling users to discover who the dominant players are, department by department.""")
    display_carte_by_depart(df)
    st.write("""
This map shows the overall situation and regional inequalities. It is immediately apparent that infrastructure is heavily concentrated in the departments of large urban areas such as Paris and its suburbs, Lyon, and Marseille, as well as along major transport routes. This “red” France of metropolitan areas contrasts sharply with a large “empty diagonal” of recharge, stretching from the northeast to the southwest, which appears in blue. 
These territories, often the most rural, are clearly under-equipped, which is a major obstacle to the adoption of electric vehicles and creates a risk of social and territorial divide.""")
    st.write("---")    
    display_top_departements_chart(df)
    st.write(""" This bar chart puts names and figures to the leaders in deployment revealed by the map. It provides quantitative evidence of the concentration of infrastructure and allows for an unambiguous ranking of the most advanced territories. The ranking confirms the overwhelming dominance of Paris, which occupies the top spot on the podium. The rest of the top 20 is a faithful reflection of France's major urban areas, including the departments of cities such as Lyon, Marseille, and Bordeaux. The message is therefore clear: terminals are mainly located where the population and economic activity are most dense.""")
    st.write("""---""")
    display_top_operators_by_department_chart(df)
    st.write(""" This final tool transforms the user into an analyst. By selecting a department, they can discover the local competitive landscape and answer the question 'who dominates where?'""")

st.write("---")
display_conclusion_tab()