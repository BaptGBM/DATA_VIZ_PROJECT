import streamlit as st


def display_intro():
    st.header("The European Framework: Ambitious Goals for an Inevitable Revolution")
    st.markdown("""
    
The transition to electric mobility is no longer an option, but a revolution dictated by the European Union's climate strategy. At the heart of this transformation is the “Fit for 55” legislative package, which imposes a strict roadmap for the automotive sector: a 55% reduction in CO₂ emissions for new cars by 2030, followed by a total ban on the sale of new combustion engine vehicles (gasoline, diesel, and hybrid) from 2035.

This radical strategy addresses three vital issues:

**The Environmental Imperative**: Achieving carbon neutrality by 2050 and improving air quality in cities.

**Energy sovereignty:** Reducing Europe's dependence on oil and gas imports.

**Industrial competition**: Stimulating innovation so that the European automotive industry remains a world leader in the face of competition from the US and China.

The success of this transition depends entirely on the construction of a dense, reliable, and accessible charging network. This interactive dashboard invites you to explore this critical infrastructure to understand its growth, the strategies of the players building it, and whether its distribution across the territory is equitable.""")
    

    st.subheader("How to navigate this analysis?")
    st.markdown("""
    Each tab in this application tells a chapter of the story. Use the filters on the left to explore the data from different angles ont the overwiew map.

    - **Data Preparation:** Take a look behind the scenes of my analysis. I explain how I cleaned, enriched, and validated the raw data to ensure the relevance of this dashboard.
    - **Overview:** Start with a global view. Where are the terminals located and what are the key figures?
    - **Temporal Analysis:** Immerse yourself in the story of exponential growth. How has the network evolved, in terms of quantity and quality, over the years?
    - **Market Analysis:** Meet the network builders. Who are the market leaders and what are their deployment strategies?
    - **Geographic Analysis:** Explore France's two speeds. Is coverage of the territory uniform or are there “charging deserts”?
    - **Operator Comparison Tool:** Become an analyst! Choose up to three operators and compare their power strategies and growth dynamics in real time.
                """)

    st.info(""" **A note about our data:** The information comes from `data.gouv.fr`(https://data.europa.eu/data/datasets/5448d3e0c751df01f85d0572?locale=en) and is based on a **declarative** model. Each operator is responsible for the quality of its data. Our data cleaning work, detailed in the first tab, aims to correct inconsistencies, but coverage or quality biases may remain.""")

    st.write("---") 