import streamlit as st
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static
import branca.colormap as cmp
import numpy as np
import plotly.express as px
import base64
import altair as alt

logo = "Downloads/logo_pole_emploi.jpg"
im = Image.open('Downloads/logo_pole_emploi.jpg')
st.set_page_config(page_title='Employee Turnover',page_icon=im,initial_sidebar_state='auto')

st.sidebar.markdown("# Bienvenue")
st.sidebar.markdown("## Choisir des filtres")

st.markdown(
    """
    <style>
    .container {
        display: inline-flex;
    }
    .logo-text {
        font-weight:300 !important;
        font-size:40px !important;
        padding-top: 1x !important;
    }
    .logo-img {
        float:right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="container">
        <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(logo, "rb").read()).decode()}">
        <center> <p class="logo-text">DYNAMIQUE DE L'EMPLOI EN FRANCE  </p> </center>
    </div>
    """,
    unsafe_allow_html=True
)

def main():
    
    df = pd.read_csv('Downloads/dpae-par-departement-x-grand-secteur.csv',sep=';')
    df = df.fillna(0)
    cols = ['Code région', 'Région', 'Code ancienne région', 'Ancienne région',
       'Code département', 'Département','Durée de contrat', 'Nature de contrat', 'Année', 'Trimestre',
       'Dernier jour du trimestre', 'DPAE (brut)', 'DPAE (cvs)']
    df[cols] = df[cols].replace('_calage_','CVS',regex=True)
    df["Grand secteur d'activité"] = df["Grand secteur d'activité"].replace('_calage_','404_CVS',regex=True)
    df["Grand secteur d'activité"] = df["Grand secteur d'activité"].str[4:]
    df[['DPAE (brut)','DPAE (cvs)']]=df[['DPAE (brut)','DPAE (cvs)']].astype(int)
    df = df.rename(columns={'Code région':'code'})
    df[['code','Année']] = df[['code','Année']].astype(str)
    
    #st.dataframe(df)
    #aggregating by region for the map
    df2 = df[['code','Région','DPAE (brut)','DPAE (cvs)']].groupby(['Région','code']).agg('sum').reset_index()
    
    st.markdown('#')
     
    json_fr = f"regions.geojson"

    fr = folium.Map(location = [46.232192999999995,2.209666999999996],tiles="CartoDB positron",name='Carte de France',zoom_start = 5)

  

    folium.Choropleth(
        geo_data= json_fr,
        name="choropleth",
        data=df2,
        columns=['code',"DPAE (brut)",'DPAE (cvs)'],
        key_on="properties.code",
        fill_color = 'YlOrRd',
        fill_opacity=0.8,
        line_opacity=0.1,
        legend_name='DPAE (brut)').add_to(fr)
    folium.features.GeoJson('regions.geojson', name="Régions", popup=folium.features.GeoJsonPopup(fields=["nom"])).add_to(fr)
    

    folium_static(fr)
    st.markdown("<p style='color:red;'>Lorsque vous dézommez sur la carte, vous pourrez également voir les DOM-TOM </p>",unsafe_allow_html=True)
    
    
    st.markdown('<hr>',unsafe_allow_html=True)
    
    region_choice = st.sidebar.multiselect("Région", df["Région"].sort_values().unique())
    if len(region_choice) == 0:
        departement_choice = st.sidebar.multiselect("Département", df["Département"].sort_values().unique())
    else:
        departement_choice = st.sidebar.multiselect("Département", (df["Département"][df['Région'].isin(region_choice)]).sort_values().unique())
    
    year_choice = st.sidebar.multiselect("Année", df["Année"].sort_values().unique(),default=['2020'])
    #if len(year_choice)>0:
     #   trimestre_choice = st.sidebar.multiselect("Trimestre", (df["Trimestre"][df['Année'].isin(year_choice)]).sort_values().unique())
    #else:
      #  st.sidebar.warning("Choisissez une année avant de pouvoir choisir un trimestre")
        
    activity_area = st.sidebar.multiselect("Secteur d'activité", df["Grand secteur d'activité"].sort_values().unique())
    contract_type = st.sidebar.multiselect("Nature de contrat", df["Nature de contrat"].unique())
    
    pie = px.pie(df[df['Région'].isin(region_choice) | df["Département"].isin(departement_choice) | df["Année"].isin(year_choice) | df["Grand secteur d'activité"].isin(activity_area)],values='DPAE (brut)',names="Nature de contrat",title="Proportion par type de contrat (filtres rattachés : Région, Département, Année, Secteur)")
    st.plotly_chart(pie)
    
    st.markdown("<center>Une très grande proportion de CDD parmi tous les DPAE, les entreprises semblent avoir du mal à faire signer des CDI en France ! </center>",unsafe_allow_html=True)
    
    st.markdown('#')
    st.markdown('<hr>',unsafe_allow_html=True)
    
    bar1 = px.bar(df[df['Région'].isin(region_choice) | df["Département"].isin(departement_choice) | df["Année"].isin(year_choice) | df["Nature de contrat"].isin(contract_type)],x="Grand secteur d'activité",y="DPAE (brut)",title="Proportion par type de contrat (filtres rattachés : Région, Département, Année, Nature Contrat)")
    st.plotly_chart(bar1)
    
    st.markdown('#')
    st.markdown('<hr>',unsafe_allow_html=True)
    
    df3 = df[['Année','Région','DPAE (brut)','DPAE (cvs)']].groupby(['Région','Année']).agg('sum').reset_index()
    
    lin = alt.Chart(df).mark_line().encode(
        x="Année",
        y = "DPAE (brut)",
        color="Nature de contrat").properties(
        title='Évolution DPAE depuis 2000',height=700,width=800)
    
    
    st.altair_chart(lin)
    st.write("La pandémie du Coronavirus a eu un réel impact sur l'emploi")
    st.info("Fact : La précarité a augmenté de 7,5% sur l'année 2020")
    
    st.markdown('#')
    st.markdown('#')
    st.markdown('<hr>',unsafe_allow_html=True)
    
    minimum = df['DPAE (brut)'][df['Région'].isin(region_choice) | df["Département"].isin(departement_choice) | df["Année"].isin(year_choice) | df["Grand secteur d'activité"].isin(activity_area) | df["Nature de contrat"].isin(contract_type)].min()
    maximum = df['DPAE (brut)'][df['Région'].isin(region_choice) | df["Département"].isin(departement_choice) | df["Année"].isin(year_choice) | df["Grand secteur d'activité"].isin(activity_area) | df["Nature de contrat"].isin(contract_type)].max()
    
    col1,col2 = st.columns(2)
    col1.metric('Minimum enregistré sur un trimestre',value=minimum)
    col2.metric('Maximum enregistré sur un trimestre',value=maximum)
    
    st.markdown('#')
    st.markdown('#')
    st.markdown('<hr>',unsafe_allow_html=True)
    
    st.dataframe((df[df['Région'].isin(region_choice) | df["Département"].isin(departement_choice) | df["Année"].isin(year_choice) | df["Grand secteur d'activité"].isin(activity_area) | df["Nature de contrat"].isin(contract_type)]).head())
    st.success("Vous pouvez utilisez tous les filtres sur le dataframe")
    
    @st.cache
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    csv = convert_df(df)

    st.download_button(
     label="Download cleaned data as CSV",
     data=csv,
     file_name='2000_2021_dpae_par_departement.csv',
     mime='text/csv')
    
    
    st.sidebar.markdown('#')
    
    link2 = '[METADATA](https://open.urssaf.fr/explore/dataset/dpae-par-region-x-na38/information/?dataChart=eyJxdWVyaWVzIjpbeyJjaGFydHMiOlt7InR5cGUiOiJjb2x1bW4iLCJmdW5jIjoiU1VNIiwieUF4aXMiOiJkcGFlX2N2cyIsInNjaWVudGlmaWNEaXNwbGF5Ijp0cnVlLCJjb2xvciI6InJhbmdlLVBhaXJlZCIsInBvc2l0aW9uIjoiY2VudGVyIn1dLCJ4QXhpcyI6ImRlcm5pZXJfam91cl9kdV90cmltZXN0cmUiLCJtYXhwb2ludHMiOiIiLCJ0aW1lc2NhbGUiOiJtb250aCIsInNvcnQiOiIiLCJzZXJpZXNCcmVha2Rvd24iOiJuYXR1cmVfZGVfY29udHJhdCIsInNlcmllc0JyZWFrZG93blRpbWVzY2FsZSI6IiIsInN0YWNrZWQiOiJub3JtYWwiLCJjb25maWciOnsiZGF0YXNldCI6ImRwYWUtcGFyLXJlZ2lvbi14LW5hMzgiLCJvcHRpb25zIjp7fX19XSwiZGlzcGxheUxlZ2VuZCI6dHJ1ZSwiYWxpZ25Nb250aCI6dHJ1ZSwic2luZ2xlQXhpcyI6dHJ1ZSwidGltZXNjYWxlIjoiIn0%3D)'
    st.sidebar.markdown(link2, unsafe_allow_html=True)
    
    st.sidebar.markdown("##")
    
    link = '[GitHub](https://github.com/AkramBensalemPSB/PSB)'
    st.sidebar.markdown(link, unsafe_allow_html=True)
    
    st.sidebar.write('PAR BENSALEM AKRAM TRADEMARKS')
    
    
    
    
    
    
if __name__ == '__main__':
        main()