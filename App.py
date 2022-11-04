#!/usr/bin/env python
# coding: utf-8

# In[8]:


#Importing packeges


# In[ ]:

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import openpyxl
import plotly.express as px
import plotly.graph_objects as go
import folium
import branca
import geopandas as gpd
import matplotlib.pyplot as plt
from streamlit_folium import folium_static
import matplotlib.dates
from dateutil import relativedelta
from PIL import Image

# In[ ]:


#Reading files


# In[35]:


expl = pd.read_csv('exploitatievergunning.csv')
expl_coords = pd.read_csv('expl_coords')
bvlk = pd.read_excel('bevolkingsprognose-020.xlsx')
file_path = 'stadsdelen all 2022-11-01 12.13.16.geojson'
stadsdelen2 = gpd.read_file(file_path)
overlast = pd.read_excel('overlastindex.xlsx')


# In[ ]:


#Making expl usefull


# In[11]:


expl['begindatum_dt'] = pd.to_datetime(expl['begindatum'])
expl['einddatum_dt'] = pd.to_datetime(expl['einddatum'])
expl['datum_vandaag'] = pd.to_datetime('today').normalize()


# In[12]:


expl['dagen_geldig'] = expl['einddatum_dt'].dt.to_period('D').view(dtype='int64') - expl['datum_vandaag'].dt.to_period('D').view(dtype='int64')
expl['maanden_geldig'] = expl['einddatum_dt'].dt.to_period('M').view(dtype='int64') - expl['datum_vandaag'].dt.to_period('M').view(dtype='int64')


# In[13]:


expl['geldig/verlopen'] = np.where(expl['dagen_geldig'] < 0, 'verlopen', 'geldig' )


# In[14]:


expl['zaak_specificatie'] = expl['zaak_specificatie'].str.lower()
expl['zaak_categorie'] = expl['zaak_categorie'].str.lower()


# In[15]:


expl2 = expl
expl2 = expl.sort_values(by= 'begindatum')
expl2.reset_index(inplace=True)
expl2['tellen'] = expl2.index
expl2['tellen'] = expl2['tellen'] + 1


# In[ ]:


#Making expl_coords usefull


# In[16]:


expl_coords = expl_coords.dropna(subset=['Lat', 'Lon', 'zaaknaam'])
expl_coords[['o_tijden_terras_zo_do_van', 'o_tijden_terras_zo_do_tot', 'o_tijden_terras_vr_za_van', 'o_tijden_terras_vr_za_tot']] = expl_coords[['o_tijden_terras_zo_do_van', 'o_tijden_terras_zo_do_tot', 'o_tijden_terras_vr_za_van', 'o_tijden_terras_vr_za_tot']].fillna('Onbekend')
expl_coords[['openingstijden_zo_do_van', 'openingstijden_zo_do_tot', 'openingstijden_vr_za_van', 'openingstijden_vr_za_tot']] = expl_coords[['openingstijden_zo_do_van', 'openingstijden_zo_do_tot', 'openingstijden_vr_za_van', 'openingstijden_vr_za_tot']].fillna('Onbekend')
expl_coords.isna().sum()


# In[17]:


expl_coords['begindatum_dt'] = pd.to_datetime(expl_coords['begindatum'])
expl_coords['einddatum_dt'] = pd.to_datetime(expl_coords['einddatum'])
expl_coords['datum_vandaag'] = pd.to_datetime('today').normalize()


# In[18]:


expl_coords['dagen_geldig'] = expl_coords['einddatum_dt'].dt.to_period('D').view(dtype='int64') - expl_coords['datum_vandaag'].dt.to_period('D').view(dtype='int64')
expl_coords['maanden_geldig'] = expl_coords['einddatum_dt'].dt.to_period('M').view(dtype='int64') - expl_coords['datum_vandaag'].dt.to_period('M').view(dtype='int64')


# In[19]:


expl_coords['geldig/verlopen'] = np.where(expl_coords['dagen_geldig'] < 0, 'verlopen', 'geldig' )


# In[20]:


expl_coords['legend'] = np.where(expl_coords['maanden_geldig'] < 0, 'Verlopen', '')
expl_coords['legend'] = np.where((expl_coords['maanden_geldig'] > 0) & (expl_coords['maanden_geldig'] <=6), '0-6 maanden',expl_coords['legend'])
expl_coords['legend'] = np.where((expl_coords['maanden_geldig'] > 6) & (expl_coords['maanden_geldig'] <=12), '6-12 maanden', expl_coords['legend'])
expl_coords['legend'] = np.where((expl_coords['maanden_geldig'] > 12) & (expl_coords['maanden_geldig'] <=18), '12-18 maanden', expl_coords['legend'])
expl_coords['legend'] = np.where((expl_coords['maanden_geldig'] > 18) & (expl_coords['maanden_geldig'] <=30), '18-30 maanden', expl_coords['legend'])
expl_coords['legend'] = np.where((expl_coords['maanden_geldig'] > 30), 'Meer dan 30 maanden', expl_coords['legend'])


# In[ ]:


#Making bvlk usefull


# In[22]:


bvlk = pd.read_excel('bevolkingsprognose-020.xlsx')
bvlk['inwoners'] = bvlk['Unnamed: 1']
bvlk = bvlk.drop(columns=['Unnamed: 1','Unnamed: 2','Unnamed: 3','Unnamed: 4','Unnamed: 5'], axis=1)
bvlk = bvlk.drop(index=[0, 1, 2, 11, 12, 13], axis=0)
bvlk = bvlk.reset_index()
bvlk = bvlk.drop(columns=['index'], axis=1)
bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'] = bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'].str.replace('A: ', '')
bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'] = bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'].str.replace('B: ', '')
bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'] = bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'].str.replace('E: ', '')
bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'] = bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'].str.replace('F: ', '')
bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'] = bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'].str.replace('K: ', '')
bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'] = bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'].str.replace('M: ', '')
bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'] = bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'].str.replace('N: ', '')
bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'] = bvlk['Prognose stadsdelen 2022, aantal personen per 1 januari'].str.replace('T: ', '')


# In[ ]:


#Making choropleth usefull


# In[23]:


stadsdelen2['geoid'] = stadsdelen2.index.astype(str)
stadsdelen2 = stadsdelen2[['geoid', 'naam', 'geometry', 'code']]


# In[24]:


stadsdelen = pd.merge(stadsdelen2, bvlk, left_on='naam', right_on='Prognose stadsdelen 2022, aantal personen per 1 januari', how='left')
stadsdelen = stadsdelen.drop(index=[1], axis=0)


# In[ ]:


#Making color producer


# In[25]:


def color_producer(type):
    if type == 'Verlopen':
       return 'red'
    elif type == '0-6 maanden':
       return 'lightsalmon'
    elif type == '6-12 maanden':
       return 'orange'
    elif type == '12-18 maanden':
       return 'yellow'
    elif type == '18-30 maanden':
        return 'lightgreen'
    elif type == 'Meer dan 30 maanden':
       return 'green'


# In[ ]:


#Making a legend


# In[26]:


#  ik heb een functie gevonden op het internet voor het toevoegen van een categorische legenda:
# (bron: https://stackoverflow.com/questions/65042654/how-to-add-categorical-legend-to-python-folium-map)

def add_categorical_legend(folium_map, title, colors, labels):
    if len(colors) != len(labels):
        raise ValueError("colors and labels must have the same length.")

    color_by_label = dict(zip(labels, colors))
    
    legend_categories = ""     
    for label, color in color_by_label.items():
        legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"
        
    legend_html = f"""
    <div id='maplegend' class='maplegend'>
      <div class='legend-title'>{title}</div>
      <div class='legend-scale'>
        <ul class='legend-labels'>
        {legend_categories}
        </ul>
      </div>
    </div>
    """
    script = f"""
        <script type="text/javascript">
        var oneTimeExecution = (function() {{
                    var executed = false;
                    return function() {{
                        if (!executed) {{
                             var checkExist = setInterval(function() {{
                                       if ((document.getElementsByClassName('leaflet-bottom leaflet-left').length) || (!executed)) {{
                                          document.getElementsByClassName('leaflet-bottom leaflet-left')[0].style.display = "flex"
                                          document.getElementsByClassName('leaflet-bottom leaflet-left')[0].style.flexDirection = "column"
                                          document.getElementsByClassName('leaflet-bottom leaflet-left')[0].innerHTML += `{legend_html}`;
                                          clearInterval(checkExist);
                                          executed = true;
                                       }}
                                    }}, 100);
                        }}
                    }};
                }})();
        oneTimeExecution()
        </script>
      """
   

    css = """

    <style type='text/css'>
      .maplegend {
        z-index:9999;
        float:right;
        background-color: rgba(255, 255, 255, 1);
        border-radius: 5px;
        border: 2px solid #bbb;
        padding: 10px;
        font-size:12px;
        positon: relative;
      }
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 0px solid #ccc;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    """

    folium_map.get_root().header.add_child(folium.Element(script + css))

    return folium_map


#Setting up the page
image = Image.open('legenda.jpg')

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed")

st.title('VA-eindopdracht')


#Folium filters

col_filter1, col_filter2 = st.columns(2)
with col_filter1:
   foliumfilter1 = st.selectbox("Choropleth on/off",("On","Off"))

with col_filter2:
    st.image(image, caption='Legenda', use_column_width=False)


#Making the folium map


# In[27]:

if (foliumfilter1 == 'On'):
    m = folium.Map(location=[52.371661, 4.889955], zoom_start=11.5)

    folium.TileLayer(
         tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        max_zoom=6
        # name='darkmatter',
        # control=False,
        # opacity=0.7
    ).add_to(m)

    colors = []

    for x in expl_coords['legend'].unique().tolist():
        colors.append(color_producer(x))

    # Voer eerst de code in de cel hieronder uit, voordat de functie add_categorical_legend werkt
    m = add_categorical_legend(m, 'Aantal maanden geldig',
                             colors = colors,
                           labels = expl_coords['legend'].unique().tolist())

    folium.Choropleth(geo_data=stadsdelen,
                    data=stadsdelen,
                    columns=['geoid', 'inwoners'],
                    key_on='feature.id',
                    fill_color='Blues',                  
                    legend_name='Aantal inwoners'
                    ).add_to(m)
    features = {}
    for row in pd.unique(expl_coords["legend"]):
        features[row] = folium.FeatureGroup(name=row)
    
    for i, x in expl_coords.iterrows():

        html="<strong>Naam:</strong> " + x['zaaknaam'] + "<br><strong>Adres:</strong> " + x['adres'] + "<br><strong>Categorie:</strong> " + x['zaak_categorie'] + "<br><strong>Openingstijden op vergunning:</strong>" + "<br><br>Van zondag t/m donderdag: " + "<br>Van: " + x['openingstijden_zo_do_van'] + " Tot " + x['openingstijden_zo_do_tot'] + "<br><br>Vrijdag en zaterdag: " + "<br>Van: " + x['openingstijden_vr_za_van'] + " Tot " + x['openingstijden_vr_za_tot'] + "<br><br><strong>Geldigheid:</strong> " + x['geldig/verlopen']
        iframe = branca.element.IFrame(html=html, width=500, height=300)
        popup = folium.Popup(iframe, max_width=2650) 
        folium.Circle(radius=10, color=color_producer(x['legend']), fill_color=color_producer(x['legend']), fill_opacity=1, popup=popup, location=[expl_coords['Lat'][i], expl_coords['Lon'][i]]).add_to(m).add_to(features[x['legend']])
    
    for row in pd.unique(expl_coords["legend"]):
        features[row].add_to(m)
    
    folium.LayerControl().add_to(m)
    
    folium_static(m, width=1200)
    
else:
    m = folium.Map(location=[52.371661, 4.889955], zoom_start=11.5)

    folium.TileLayer(
         tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        max_zoom=6
        # name='darkmatter',
        # control=False,
        # opacity=0.7
    ).add_to(m)

    colors = []

    for x in expl_coords['legend'].unique().tolist():
        colors.append(color_producer(x))

    # Voer eerst de code in de cel hieronder uit, voordat de functie add_categorical_legend werkt
    m = add_categorical_legend(m, 'Aantal maanden geldig',
                             colors = colors,
                           labels = expl_coords['legend'].unique().tolist())

#     for i, x in expl_coords.iterrows():

#         html="<strong>Naam:</strong> " + x['zaaknaam'] + "<br><strong>Adres:</strong> " + x['adres'] + "<br><strong>Categorie:</strong> " + x['zaak_categorie'] + "<br><strong>Openingstijden op vergunning:</strong>" + "<br><br>Van zondag t/m donderdag: " + "<br>Van: " + x['openingstijden_zo_do_van'] + " Tot " + x['openingstijden_zo_do_tot'] + "<br><br>Vrijdag en zaterdag: " + "<br>Van: " + x['openingstijden_vr_za_van'] + " Tot " + x['openingstijden_vr_za_tot'] + "<br><br><strong>Geldigheid:</strong> " + x['geldig/verlopen']
#         iframe = branca.element.IFrame(html=html, width=500, height=300)
#         popup = folium.Popup(iframe, max_width=2650) 
#         folium.Circle(radius=10, color=color_producer(x['legend']), fill_color=color_producer(x['legend']), fill_opacity=1, popup=popup, location=[expl_coords['Lat'][i], expl_coords['Lon'][i]]).add_to(m)

    folium_static(m, width=1200)

#Getting data for filter                                                                                 
df_verlopen = expl_coords.loc[expl_coords['legend'] == 'Verlopen']
df_06 = expl_coords.loc[expl_coords['legend'] == '0-6 maanden']
df_612 = expl_coords.loc[expl_coords['legend'] == '6-12 maanden']
df_1218 = expl_coords.loc[expl_coords['legend'] == '12-18 maanden']
df_1830 = expl_coords.loc[expl_coords['legend'] == '18-30 maanden']
df_30 = expl_coords.loc[expl_coords['legend'] == 'Meer dan 30 maanden']


#using filter

       

# In[28]:


stadsdelen_merge = pd.merge(stadsdelen2, bvlk, left_on='naam', right_on='Prognose stadsdelen 2022, aantal personen per 1 januari', how='left')
stadsdelen_merge = stadsdelen_merge.drop(index=[1], axis=0)
stadsdelen_merge.rename(columns={'naam': 'stadsdeel'}, inplace=True)


# In[40]:


overlast.rename(columns={'Unnamed: 0': 'stadsdeel'}, inplace=True)
# # overlast = overlast.drop(columns=['Unnamed: 8'])
overlast2 = overlast.merge(stadsdelen_merge, on='stadsdeel')
overlast2.drop(columns=['geoid', 'geometry', 'code', 'Prognose stadsdelen 2022, aantal personen per 1 januari'], inplace=True)


# In[ ]:

overlast_totaal2 = overlast
overlast_totaal2 = overlast.drop(index=[7])
overlast_totaal_long2 = pd.melt(overlast_totaal2, id_vars='stadsdeel', value_vars=[2014, 2015, 2016, 2017, 2018, 2019, 2020], value_name='Amsterdam', var_name= 'jaar')
fig6 = px.line(overlast_totaal_long2, x='jaar', y='Amsterdam', color='stadsdeel', labels={"jaar": "Jaren", "value": "Overlast index score"}, title='Verloop overlastindex per stadsdeel')

#fig 1


# In[41]:


fig1 = px.scatter(overlast2, x='inwoners', y=[2014, 2015, 2016, 2017, 2018, 2019, 2020], labels={"inwoners": "Aantal inwoners per stadsdeel", "value": "Overlast index score", "variable": "Jaargang"}, title='Overlast index door de jaren heen per stadsdeel')
fig1.show()


# In[ ]:


#Fig 2


# In[42]:


fig2 = px.box(overlast, y=[2014, 2015, 2016, 2017, 2018, 2019, 2020], labels={"variable": "Jaar van waarneming", "value": "Overlast index score"}, title= 'Som index scores per stadsdeel door de jaren heen')
fig2.show()


# In[ ]:


#Fig 3


# In[45]:


aantal_per_categorie = pd.DataFrame(expl['zaak_categorie'].value_counts().reset_index())
aantal_per_categorie.columns = ['zaak_categorie', 'count']


# In[46]:


fig3 = px.bar(aantal_per_categorie, x='zaak_categorie', y = 'count', text_auto='.2s', 
                labels={'count':'Aantal', 'zaak_categorie':'Zaak cetegorie'}, title= 'Aantal vergunningen per categorie')

fig3.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'})
fig3.update_traces(marker_color='rgb(166,189,219)', textfont_size=9, textangle=0, textposition="outside", cliponaxis=False)
fig3.show()


# In[ ]:


#regressielijn maken van de overlastindex
overlast_totaal = overlast
overlast_totaal = overlast.drop(index=[0,1,2,3,4,5,6])
overlast_totaal_long = pd.melt(overlast_totaal, id_vars='stadsdeel', value_vars=[2014, 2015, 2016, 2017, 2018, 2019, 2020], value_name='Amsterdam', var_name= 'jaar')
overlast_totaal_long =overlast_totaal_long.drop(columns=['stadsdeel'])
fig5 = px.scatter(overlast_totaal_long, x='jaar', y='Amsterdam', trendline="ols", labels={"jaar": "Jaar van waarneming", "Amsterdam": "Overlast index score"}, title='Gemiddelde overlast index van alle stadsdelen')

#Fig 4


# In[47]:


expl2 = expl
expl2 = expl.sort_values(by= 'begindatum')
expl2.reset_index(inplace=True)
expl2['tellen'] = expl2.index
expl2['tellen'] = expl2['tellen'] + 1
fig4 = px.line(expl2, x='begindatum', y='tellen', labels={"begindatum": "Datum vergeven van vergunning", "tellen": "Aantal vergunningen"}, title='Cumulatieve som verleende vergunningen door de jaren heen')
fig4.show()

#Adding st
col1, col2 = st.columns(2)
with col1:
    tab1, tab2 = st.tabs(['Visualisatie','Informatie'])
#Aantal per cat
    with tab1:
        tab1.plotly_chart(fig3)
    with tab2:
        tab2.subheader("Informatie")
        tab2.write('Data verkregen via data platform van gemeente Amsterdam')
        tab2.write('Data bestand: Verleende exploitatievergunningen horeca met terrasgrenzen en ontheffingen')
        tab2.write('https://data.amsterdam.nl/datasets/GsY50tEkoJKCGw/verleende-exploitatievergunningen-horeca-met-terrasgrenzen-en-ontheffingen/')
with col2:
    tab3, tab4 = st.tabs(['Visualisatie','Informatie'])
#Lijnplot
    with tab3:
        tab3.plotly_chart(fig4)
    with tab4:
        tab4.subheader("Informatie")
        tab4.write('Data verkregen via data platform van gemeente Amsterdam')
        tab4.write('Data bestand: Verleende exploitatievergunningen horeca met terrasgrenzen en ontheffingen')
        tab4.write('https://data.amsterdam.nl/datasets/GsY50tEkoJKCGw/verleende-exploitatievergunningen-horeca-met-terrasgrenzen-en-ontheffingen/')

 #Adding st
col3, col4 = st.columns(2)
with col3:
    tab5, tab6 = st.tabs(['Visualisatie','Informatie'])
#scatter
    with tab5:
        tab5.plotly_chart(fig1)
    with tab6:
        tab6.subheader("Informatie")
        tab6.write('veiligheidsindex van Amsterdam waarin de overlast in verwerkt is.')
        tab6.write('Bron: https://cms.onderzoek-en-statistiek.nl/uploads/Veiligheids_Index_2020_3_c59390af4e.xlsx')
        tab6.write('bevolkingsprognose waarin het aantal inwoners wordt weergeven')
        tab6.write('Bron: https://cms.onderzoek-en-statistiek.nl/uploads/2022_bevolkingsprognose_tabel3_24f71bca0b.xlsx')
        
with col4:
    tab7, tab8 = st.tabs(['Visualisatie','Informatie'])
#Boxplot
    with tab7:
        tab7.plotly_chart(fig2)
    with tab8:
        tab8.subheader("Informatie")      
        tab8.write('veiligheidsindex van Amsterdam waarin de overlast in verwerkt is.')
        tab8.write('Bron: https://cms.onderzoek-en-statistiek.nl/uploads/Veiligheids_Index_2020_3_c59390af4e.xlsx')
        tab8.write('In 2020 is te zien dat er door de gehele stads (in ieder stadsdeel) het meest overlast is ervaren. Dit is zichtbaar omdat de upper fence en lower fence dicht bij elkaar liggen ten opzicht van andere jaargangen.')
        tab8.write('De outlier boven in de boxplot visualisatie representeerd stadsdeel centrum')
        
# #Adding st
col5,col6 = st.columns(2)
with col5:
    tab9, tab10 = st.tabs(['Visualisatie','Informatie'])
#Aantal per cat
    with tab9:
        tab9.plotly_chart(fig5)
    with tab10:
        tab10.subheader("Informatie")
        tab10.write('veiligheidsindex van Amsterdam waarin de overlast verwerkt is.')
        tab10.write('100 is de standaardwaarde. Eronder is minder dan gemiddeld, erboven is meer dan gemiddeld')
        tab10.write('Bron: https://cms.onderzoek-en-statistiek.nl/uploads/Veiligheids_Index_2020_3_c59390af4e.xlsx')
        
with col6:
    tab11, tab12 = st.tabs(['Visualisatie','Informatie'])
#Aantal per cat
    with tab11:
        tab11.plotly_chart(fig6)
    with tab12:
        tab12.subheader("Informatie")
        tab12.write('veiligheidsindex van Amsterdam waarin de overlast verwerkt is.')
        tab12.write('100 is de standaardwaarde. Eronder is minder dan gemiddeld, erboven is meer dan gemiddeld')
        tab12.write('Bron: https://cms.onderzoek-en-statistiek.nl/uploads/Veiligheids_Index_2020_3_c59390af4e.xlsx')
