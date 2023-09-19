import json
from pathlib import Path
import requests
import plotly.express as px
import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import os
import base64

TITLE = "DW Metrics"
PAGE_ICON ="ico_potfolio.ico"


current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()


# Credentials
config_assets = current_dir / "hashed_pw_assets.yaml"
config_Dash = current_dir / "hashed_pw_dash.yaml"

hashed_pw_db_water = current_dir / "H_pkl_pw_water_db.pkl"

pp_logo_portfolio = current_dir / "files" /  "logo_portfolio.png"
linkpic_code = current_dir / "files" /  "code.png"

# CSS
css_file = current_dir / "main.css"

locked_water_DB_p = current_dir / "files" / "DB_Water.xlsx"
locked_water_DB = str(locked_water_DB_p)

# My Tutos :
# size :
space = 15
tuto_space = 70

tuto_W_metrics_p = current_dir / "files" / "tuto_water_metrics.mp4"
tuto_W_metrics = str(tuto_W_metrics_p)

# lotties :
lottie_water = current_dir / "files" / "water.json"

def load_lottiefile(filepath : str):
    with open(filepath, "r") as f:
        return json.load(f)


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# Clickable img
@st.cache_data
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

@st.cache_data
def get_img_with_href(local_img_path, target_url, width, loc):
    img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f'''
        <a href="{target_url}" target="_{loc}" style="display: flex; justify-content: center; align-items: center;">
            <img src="data:image/{img_format};base64,{bin_str}" width="{width}" class="img-hover-effect">
        </a>'''
    return html_code


"""====================================== Water Metrics ======================================"""

@st.cache_data 
def get_data_from_water_DB(water_DB):
    water_df = pd.read_excel(io=water_DB, sheet_name=0)

    water_df['Country'] = water_df['Country'].astype(str)
    water_df['Year'] = water_df['Year'].astype(int)
    water_df['Population'] = water_df['Population'].astype(float)
      
    water_df['rate_NAT_Safe'] = (water_df['NAT_Safe'] / water_df['Population'])*100

    water_df = water_df[(water_df['Population'] >= 4000000)]

    return water_df


# scatter geo --- NAT ---
@st.cache_data
def scatter_Country(water_df, proj_type):
    NAT_df = water_df.loc[:,["Continent","Country", "ISO3", 'Year', 'Population',
        'urban_percent', "NAT_Safe", "NAT_Basic", "NAT_Limited", "NAT_Unimproved",
        ]]

    NAT_df['Population_mean'] = NAT_df.groupby('Country')['Population'].transform('mean')

    NAT_df = NAT_df.groupby(["Continent","Country", "ISO3"], as_index=False).agg({
        'Population_mean' : 'mean',
        'Population' : 'sum',
        'urban_percent' : 'sum',
        'NAT_Safe':'sum',
        'NAT_Basic':'sum',
        'NAT_Limited':'sum',
        'NAT_Unimproved':'sum',
        }).round(2)

    NAT_df['NAT_Safe'] = round((NAT_df["NAT_Safe"]/NAT_df["Population"])*100,1)
    NAT_df['NAT_Basic'] = round((NAT_df["NAT_Basic"]/NAT_df["Population"])*100,1)
    NAT_df['NAT_Limited'] = round((NAT_df["NAT_Limited"]/NAT_df["Population"])*100,1)
    NAT_df['NAT_Unimproved'] = round((NAT_df["NAT_Unimproved"]/NAT_df["Population"])*100,1)

    NAT_df.rename(columns = {
        'urban_percent' : '%Urban',
        'NAT_Safe':'%Safe',
        'NAT_Basic':'%Basic',
        'NAT_Limited':f'%Limited',
        'NAT_Unimproved':'%Unimproved',
        }, inplace = True)

    NAT_df['Population'] = NAT_df['Population_mean']/1000000

    NAT_df_geo_scat = NAT_df.loc[:,["Continent", "Country", "ISO3", 'Population',
        '%Safe', '%Basic', f'%Limited', '%Unimproved']]
    

    fig = px.scatter_geo(NAT_df_geo_scat, locations='ISO3', color='%Safe', size='Population', 
                         
        projection=proj_type, 
        
        color_continuous_scale=[(0, '#C20000'), (0.3, '#FF6666'), (0.5, '#5372CB'), (1, '#001BDD')],
        range_color=[0, 100],

        hover_data={'Country':True, 'Population':True, '%Safe':True, '%Basic': True, f'%Limited': True,
            f'%Unimproved':True, 'ISO3':False, },

        height=550)
    
    fig.update_geos(
        showcoastlines=True,
        coastlinecolor="black",
        coastlinewidth=0.5,
        showland=True,
        landcolor="#757A48",
        showocean=True,
        oceancolor="#4BB4A7",
        showcountries=False,
        countrycolor="black",
        countrywidth=1,
        showframe=False)
    
    fig.update_traces(hovertemplate=('Country : %{customdata[0]}<br>'+
        'Population: %{customdata[1]:.1f} M<br>' + 

        '%Safe : %{customdata[2]}%<br>' + '%Basic : %{customdata[3]}%<br>'+
        '%Limited : %{customdata[4]}%<br>' + '%Unimproved : %{customdata[5]}%<br>'), 
        )
    
    
    fig.update_layout(
        geo_bgcolor='#010001',
        font=dict(color='black',size=15),
        )
   
    
    return fig



# Evo --- NAT ---
@st.cache_data
def get_kpi_rates(water_df):
    water_df = water_df[['Population', 'NAT_Safe', 'NAT_Basic', 'NAT_Limited', 'NAT_Unimproved']]
    
    water_df_sum = water_df.sum()

    tot_NAT = water_df_sum['NAT_Safe'] + water_df_sum['NAT_Basic'] + water_df_sum['NAT_Limited'] + water_df_sum['NAT_Unimproved']

    Safe = round((water_df_sum['NAT_Safe']/tot_NAT)*100,2)
    Basic = round((water_df_sum['NAT_Basic']/tot_NAT)*100,2)
    Limited = round((water_df_sum['NAT_Limited']/tot_NAT)*100,2)
    Unimproved = round((water_df_sum['NAT_Unimproved']/tot_NAT)*100,2)
    
    return [Safe, Basic, Limited, Unimproved]


@st.cache_data
def get_chart_evo(water_df):

    df_evo = water_df.groupby(["Year"], as_index=False).agg({
    'Population' : 'sum',
    'NAT_Safe':'sum',
    'NAT_Basic':'sum',
    'NAT_Limited':'sum',
    'NAT_Unimproved':'sum',
    }).round(2)

    df_evo.rename(columns = {
    'NAT_Safe':'%Safe',
    'NAT_Basic':'%Basic',
    'NAT_Limited':f'%Limited',
    'NAT_Unimproved':'%Unimproved',
    }, inplace = True)

    df_evo['%Safe'] = round((df_evo["%Safe"]/df_evo["Population"])*100,1)
    df_evo['%Basic'] = round((df_evo["%Basic"]/df_evo["Population"])*100,1)  
    df_evo[f'%Limited'] = round((df_evo[f"%Limited"]/df_evo["Population"])*100,1) 
    df_evo['%Unimproved'] = round((df_evo["%Unimproved"]/df_evo["Population"])*100,1) 

    df_evo['Population'] = round(df_evo['Population'] / 1000000,1)

    df_evo.sort_values(["Year"], ascending=True, inplace=True)

    # Create the figure 
    trace1_0 = go.Bar(x=df_evo['Year'], y=df_evo['Population'], name="Population (M)",
        marker=dict(color='#00692A'),text=df_evo['Population'].apply(lambda x: round(x, 0)), textposition='auto',) # .apply(lambda x: '{:.0f}'.format(x))
    
    trace1_1 = go.Scatter(x=df_evo['Year'], y=df_evo['%Safe'], yaxis='y2', name="%Safe",
        line=dict(width=3, color='#3636B8', dash='solid'), marker=dict(size=7, color='#3636B8'))

    trace2_1 = go.Scatter(x=df_evo['Year'], y=df_evo['%Basic'], yaxis='y2',name="Basic",
        line=dict(width=3, color='#4489CB', dash='solid'), marker=dict(size=7, color='#4489CB'))

    trace2_2 = go.Scatter(x=df_evo['Year'], y=df_evo[f'%Limited'], yaxis='y2', name=f"%Limited",
        line=dict(width=3, color='#CD5B00', dash='solid'), marker=dict(size=7, color='#CD5B00'))
    
    trace2_3 = go.Scatter(x=df_evo['Year'], y=df_evo[f'%Unimproved'], yaxis='y2', name="%Unimproved",
        line=dict(width=3, color='#CF1A1A', dash='solid'), marker=dict(size=7, color='#CF1A1A'))

    # Create a figure and add the traces to it
    fig = go.Figure()
    fig.add_traces([trace1_0, trace1_1, trace2_1, trace2_2, trace2_3])

    # Update the layout to include two y-axes
    fig.update_layout(
        yaxis=dict(title="Population (M)"), #  tickfont=dict(color='black'),

        yaxis2=dict(title="Rates %", overlaying='y', side='right'), # tickfont=dict(color='black'), gridcolor='rgba(0,0,0,0.3)'
            
        xaxis=dict(tickvals=df_evo['Year'], ticktext=df_evo['Year']), # tickfont=dict(color='black')

        # yaxis_title=dict(font=dict(color='black')),
        # yaxis2_title=dict(font=dict(color='black')),
        
        font=dict(size=12, family='Arial Black', ), # color='black'
        legend=dict(orientation="h", x=0.1, y=1.2, font=dict(size=12,family='Arial Black', ))) # color='black'

    return fig



# Cover --- NAT ---
@st.cache_data
def get_kpi_cov(water_df):
    water_df = water_df[['Population', 'NAT_Safe', 'NAT_Basic', 'NAT_Limited', 'NAT_Unimproved']]
    
    water_df_sum = water_df.sum()

    tot_NAT = water_df_sum['NAT_Safe'] + water_df_sum['NAT_Basic'] + water_df_sum['NAT_Limited'] + water_df_sum['NAT_Unimproved']

    Safe = round((water_df_sum['NAT_Safe']/tot_NAT)*100,1)
    Basic = round((water_df_sum['NAT_Basic']/tot_NAT)*100,1)
    Limited = round((water_df_sum['NAT_Limited']/tot_NAT)*100,1)
    Unimproved = round((water_df_sum['NAT_Unimproved']/tot_NAT)*100,1)
    
    return [Safe, Basic, Limited, Unimproved]


@st.cache_data
def get_chart_coverage_rates(water_df):
    # Aggregate data by summing up values across categories
    water_df = water_df[['Year',
        'NAT_Safe', 'NAT_Basic', 'NAT_Limited', 'NAT_Unimproved',
        'URB_Safe', 'URB_Basic', 'URB_Limited', 'URB_Unimproved',
        'RUR_Safe', 'RUR_Basic', 'RUR_Limited', 'RUR_Unimproved']]
    
    numb = len(water_df['Year'].unique())

    water_df_sum = water_df.sum()/numb

    tot_NAT = water_df_sum['NAT_Safe'] + water_df_sum['NAT_Basic'] + water_df_sum['NAT_Limited'] + water_df_sum['NAT_Unimproved']
    tot_URB = water_df_sum['URB_Safe'] + water_df_sum['URB_Basic'] + water_df_sum['URB_Limited'] + water_df_sum['URB_Unimproved']
    tot_RUR = water_df_sum['RUR_Safe'] + water_df_sum['RUR_Basic'] + water_df_sum['RUR_Limited'] + water_df_sum['RUR_Unimproved']

    Safe = [round((water_df_sum['NAT_Safe']/tot_NAT)*100,1),
            round((water_df_sum['URB_Safe']/tot_URB)*100,1),
            round((water_df_sum['RUR_Safe']/tot_RUR)*100,1),]
    
    Basic = [round((water_df_sum['NAT_Basic']/tot_NAT)*100,1),
            round((water_df_sum['URB_Basic']/tot_URB)*100,1),
            round((water_df_sum['RUR_Basic']/tot_RUR)*100,1),]
    
    Limited = [round((water_df_sum['NAT_Limited']/tot_NAT)*100,1),
            round((water_df_sum['URB_Limited']/tot_URB)*100,1),
            round((water_df_sum['RUR_Limited']/tot_RUR)*100,1),]
    
    Unimproved = [round((water_df_sum['NAT_Unimproved']/tot_NAT)*100,1),
                round((water_df_sum['URB_Unimproved']/tot_URB)*100,1),
                round((water_df_sum['RUR_Unimproved']/tot_RUR)*100,1),]

    data = [Safe, Basic, Limited, Unimproved]

    df = pd.DataFrame(data, index=['Safe', 'Basic', 'Limited', 'Unimproved'], columns=['TOTAL', 'URBAN', 'RURAL'])
    
    df_swapped = df.transpose()
    
    # Create stacked bar chart
    trace1 = go.Bar(x=df_swapped.index, y=df_swapped['Safe'], name='Safe',
                    text=df_swapped['Safe'], textposition='inside', marker=dict(color="#2A58C1"))
    
    trace2 = go.Bar(x=df_swapped.index, y=df_swapped['Basic'], name='Basic',
                    text=df_swapped['Basic'], textposition='inside', marker=dict(color="#6E8AC9"))
    
    trace3 = go.Bar(x=df_swapped.index, y=df_swapped['Limited'], name='Limited',
                    text=df_swapped['Limited'], textposition='inside', marker=dict(color="#EE6D6D"))
    
    trace4 = go.Bar(x=df_swapped.index, y=df_swapped['Unimproved'], name='Unimproved',
                    text=df_swapped['Unimproved'], textposition='inside',  marker=dict(color="#D70000"))

    data_chart = [trace1, trace2, trace3, trace4]

    layout = go.Layout(
        barmode='stack',
        )

    fig = go.Figure(data=data_chart, layout=layout)

    fig.update_layout(
        title={
        'text': "",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
        },

        # dragmode=False,

        height=480,

        yaxis_title=dict(text="Taux en %"),
        font=dict(size=12, family='Arial Black'),
        legend=dict(orientation="h", x=0.1, y=1.2, font=dict(size=12,family='Arial Black')))
    
    return fig



@st.cache_data
def get_chart_coverage_values(water_df):

    water_df = water_df[['Year',
        'NAT_Safe', 'NAT_Basic', 'NAT_Limited', 'NAT_Unimproved',
        'URB_Safe', 'URB_Basic', 'URB_Limited', 'URB_Unimproved',
        'RUR_Safe', 'RUR_Basic', 'RUR_Limited', 'RUR_Unimproved']]
    
    water_df_sum = (water_df/1000000).sum()

    numb = len(water_df['Year'].unique())

    Safe = [round(water_df_sum['NAT_Safe']/numb,1),
            round(water_df_sum['URB_Safe']/numb,1),
            round(water_df_sum['RUR_Safe']/numb,1),]
    
    Basic = [round(water_df_sum['NAT_Basic']/numb,1),
            round(water_df_sum['URB_Basic']/numb,1),
            round(water_df_sum['RUR_Basic']/numb,1),]
    
    Limited = [round(water_df_sum['NAT_Limited']/numb,1),
            round(water_df_sum['URB_Limited']/numb,1),
            round(water_df_sum['RUR_Limited']/numb,1),]
    
    Unimproved = [round(water_df_sum['NAT_Unimproved']/numb,1),
                round(water_df_sum['URB_Unimproved']/numb,1),
                round(water_df_sum['RUR_Unimproved']/numb,1),]

    data = [Safe, Basic, Limited, Unimproved]

    df = pd.DataFrame(data, index=['Safe', 'Basic', 'Limited', 'Unimproved'], columns=['TOTAL', 'URBAN', 'RURAL'])
    
    df_swapped = df.transpose()
    
    # Create stacked bar chart   hovertemplate='Safe: %{y:.1f}<extra></extra>'
    trace1 = go.Bar(x=df_swapped.index, y=df_swapped['Safe'], name='Safe',
                    text=df_swapped['Safe'], textposition='inside', marker=dict(color="#2A58C1"))
    
    trace2 = go.Bar(x=df_swapped.index, y=df_swapped['Basic'], name='Basic',
                    text=df_swapped['Basic'], textposition='inside', marker=dict(color="#6E8AC9"))
    
    trace3 = go.Bar(x=df_swapped.index, y=df_swapped['Limited'], name='Limited',
                    text=df_swapped['Limited'], textposition='inside', marker=dict(color="#EE6D6D"))
    
    trace4 = go.Bar(x=df_swapped.index, y=df_swapped['Unimproved'],name='Unimproved',
                    text=df_swapped['Unimproved'], textposition='inside', marker=dict(color="#D70000"))

    data_chart = [trace1, trace2, trace3, trace4]

    layout = go.Layout(
        barmode='stack',
        )

    fig = go.Figure(data=data_chart, layout=layout)

    fig.update_layout(
        title={
        'text': "",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
        },
        
        # dragmode=False,

        height=480,

        xaxis_title=None,
        yaxis_title=dict(text="Popluation (M)"),
        font=dict(size=12, family='Arial Black'),
        legend=dict(orientation="h", x=0.1, y=1.2, font=dict(size=12,family='Arial Black')))
    return fig