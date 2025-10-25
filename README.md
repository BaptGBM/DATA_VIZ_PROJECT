# Analysis of the Electric Vehicle Charging Network in France

You can see the dashboard on streamlit community cloud on this link : https://datavizproject-kb4jc2idu9acceik5y9fwe.streamlit.app/
#Project Description

This project is an interactive dashboard developed with Streamlit that provides an in-depth analysis of the deployment of electric vehicle charging stations in France.
 The application is built around a "data storytelling" narrative that explores the network's temporal growth, the strategies of key operators, the geographical distribution of infrastructure, and offers interactive comparison tools.

This project was completed as part of the "Data Analysis and visualization" course.

**Author:** GRIMBAUM BAPTISTE
---

##  How to Run the Application

To run the project on your local machine, follow these steps:

1.  **Prerequisites:** Ensure you have Python installed.

2.  **Clone the project:**
    ```bash
    git clone [https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories)
    cd [project-folder-name]
    ```

3.  **Install dependencies:**
    All necessary libraries are listed in the `requirements.txt` file. Install them with the following command:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    Once the dependencies are installed, launch the Streamlit application:
    ```bash
    streamlit run app.py
    ```
    The application should automatically open in your web browser.

---

## Project Structure

The project is organized into several modules for better readability and maintenance:

-   app.py: The main script that acts as the "orchestrator" for the application.
-   utils/: A folder containing utility modules:
    -   io.py: Functions for loading data.
    -   prep.py: A comprehensive script for data cleaning, transformation, and enrichment (including the spatial join).
    -   filters.py: The module that generates the sidebar filters and applies the filtering logic.
    -   viz.py: A library of all functions that create and display the visualizations.
-   data/: Contains the raw datasets (.csv and .geojson).
-   .streamlit/: The configuration folder for the application's theme.
-   sections/
        - intro.py : containing the introduction and the context
        - conclusion.py: containing the synthesis conclusion of the dashboard

---

## data sources 

* **Charging stations:** Consolidated file from data.gouv.fr
* **Department boundaries:** GeoJSON file from https://github.com/gregoiredavid/france-geojson
* **Data license:** The data is used under Open License 2.0 / Etalab
