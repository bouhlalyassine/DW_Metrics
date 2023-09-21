import io
import streamlit as st
from settings import *
from streamlit_lottie import st_lottie
import streamlit as st
from streamlit_option_menu import option_menu
import msoffcrypto
import pickle

# streamlit run Odrink.py
st.set_page_config(page_title=TITLE,
    page_icon=PAGE_ICON,
    layout="wide")

# Load Hased DB Password
file_pw_path = hashed_pw_db_water
with file_pw_path.open("rb") as l_file:
    hashed_db_passW = pickle.load(l_file)

decrypted_workbook = io.BytesIO()

with open(locked_water_DB, 'rb') as file:
    office_file = msoffcrypto.OfficeFile(file)
    office_file.load_key(password=hashed_db_passW)
    office_file.decrypt(decrypted_workbook)

water_DB = decrypted_workbook

# --- LOAD CSS, PDF & PROFIL PIC ---
with open(css_file) as f: # Load the CSS file
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

st.markdown("<h2 style=\
    'text-align : center';\
    font-weight : bold ;\
    font-family : Arial;>\
    Odrink</h2>", unsafe_allow_html=True)

with st.sidebar :
    clickable_img_logo = get_img_with_href(pp_logo_portfolio, 'https://ybouhlal.streamlit.app/', 70, "blank")
    st.markdown(clickable_img_logo, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    clickable_img = get_img_with_href(linkpic_code, 'https://github.com/bouhlalyassine/Odrink',
        170, "blank")
    st.markdown(clickable_img, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    nav_menu = option_menu(menu_title=None, options=['Home','Overview', 'Area Coverage', 'Evolution'], 
        default_index=0, orientation="vertical",
        icons=["house","view-list","bar-chart", "graph-up"],
        styles={
            "container": {"padding": "0!important"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"2px", "--hover-color": "#805E83"}
        })

st.markdown("""---""")

water_df = get_data_from_water_DB(water_DB)

if nav_menu == 'Home':
    st.markdown("<br>", unsafe_allow_html=True)
    colpi1_ac, colpi2_ac = st.columns([75, 25], gap="small")
    with colpi1_ac :
        st.info("Odrink, is a webapp that analyzes the quality of drinking water\
            worldwide from 2000 to 2020. The app consists of three modules :\
            \n● Overview : provides a global view of the quality of drinking water\
            \n● Area Coverage : shows the distribution of drinking water quality in urban and rural areas\
            \n● Evolution : tracks the changes in drinking water quality from 2000 to 2020\
            \n\n ► By applying various filters, users can focus the analysis on a particular\
                continent or country during a specific time period")

    with colpi2_ac:
        lottie_water = load_lottiefile(lottie_water)
        st_lottie(
            lottie_water,
            speed=1,
            reverse=False,
            loop=True,
            quality="high", # medium ; high ; low
            height=200)
    
    
    st.markdown("<br>", unsafe_allow_html=True)
    esp_1, col_vid_tuto, esp_2 = st.columns([space, tuto_space, space], gap="small")
    with col_vid_tuto :
        with open(tuto_W_metrics, "rb") as tuto_file:
            tuto_W_metrics_byte = tuto_file.read()
        st.video(tuto_W_metrics_byte)



if nav_menu == 'Overview':

    col1_marche, col2_marche, col3_marche = st.columns(3)
    with col1_marche:
        options_var = list(water_df["Year"].unique())
        vari = st.multiselect(label="📌 Year :",
            options=options_var,
            default=options_var[-1], label_visibility="visible") # "hidden"
        water_df_NAT_filtr = water_df[water_df["Year"].isin(vari)]

    with col2_marche:
        options_cont = ["ALL"] + list(water_df["Continent"].unique())
        cont = st.multiselect(label="📌 Continent :",
            options=options_cont,
            default="ALL", label_visibility="visible") # "hidden"
        if "ALL" in cont:
            water_df_NAT_filtr  = water_df_NAT_filtr
        else:
            water_df_NAT_filtr = water_df_NAT_filtr[water_df_NAT_filtr["Continent"].isin(cont)]

    with col3_marche:
        options_country = ["ALL"] + sorted(list(water_df_NAT_filtr["Country"].unique()))
        count = st.multiselect(label="📌 Country :",
            options=options_country,
            default="ALL", label_visibility="visible") # "hidden"
        if "ALL" in count:
            water_df_NAT_filtr  = water_df_NAT_filtr
        else:
            water_df_NAT_filtr = water_df_NAT_filtr[water_df_NAT_filtr["Country"].isin(count)]

    col_esp_range, col_range, co2_esp_range = st.columns([25,50,25])
    with col_range:
        try :
            min_val_filtr = int(water_df_NAT_filtr["rate_NAT_Safe"].min())
        except:
            min_val_filtr = 0

        values = st.slider(label  = '📌 Select the desired interval of %Safe (Drinking Water) :',
            min_value = min_val_filtr, max_value = 100,
            value = (min_val_filtr, 100), label_visibility = "visible")
        

    water_df_NAT_filtr = water_df_NAT_filtr[(water_df_NAT_filtr["rate_NAT_Safe"] <= values[1]) & 
                                            (water_df_NAT_filtr["rate_NAT_Safe"] >= values[0])]

    st.markdown("""---""")

    col0_esp1, col0_f_evo1,col0_esp2 = st.columns([39,22,39])
    with col0_f_evo1:
        rad_1 = option_menu(menu_title=None, options=['Globe', 'Map'], 
            icons=["globe", "map"],
            default_index=0, orientation="horizontal",
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {"font-size": "12px", "text-align": "left", "margin":"1px",
                            "font-weight": "bold", "--hover-color": "#D6B1D9"}
            })
    
    proj_ortho = "orthographic"
    proj_natu = "natural earth"
    
    if len(water_df_NAT_filtr) != 0 :
        if rad_1 == 'Globe':
            st.plotly_chart(scatter_Country(water_df_NAT_filtr, proj_ortho), use_container_width=True) 
        if rad_1 == 'Map':
            st.plotly_chart(scatter_Country(water_df_NAT_filtr, proj_natu), use_container_width=True)
    else :
        st.error("Please select/enter a filter")



if nav_menu == 'Area Coverage':

    col1_marche, col2_marche, col3_marche= st.columns(3)
    with col1_marche:
        options_var = sorted(list(water_df["Year"].unique()))
        vari = st.multiselect(label="📌 Year :",
            options=options_var,
            default=options_var[-1], label_visibility="visible") # "hidden"
        
        water_df_NAT_filtr = water_df[water_df["Year"].isin(vari)]

    with col2_marche:
        options_cont = ["ALL"] + sorted(list(water_df_NAT_filtr["Continent"].unique()))
        cont = st.multiselect(label="📌 Continent :",
            options=options_cont,
            default="ALL", label_visibility="visible") # "hidden"
        if "ALL" in cont:
            water_df_NAT_filtr  = water_df_NAT_filtr
        else:
            water_df_NAT_filtr = water_df_NAT_filtr[water_df_NAT_filtr["Continent"].isin(cont)]

    with col3_marche:
        options_contr = ["ALL"] + sorted(list(water_df_NAT_filtr["Country"].unique()))
        contr = st.multiselect(label="📌 Country :",
            options=options_contr,
            default="ALL", label_visibility="visible") # "hidden"
        if "ALL" in contr:
            water_df_NAT_filtr  = water_df_NAT_filtr
        else:
            water_df_NAT_filtr = water_df_NAT_filtr[water_df_NAT_filtr["Country"].isin(contr)]

    st.markdown("""---""")

    if len(water_df_NAT_filtr) != 0 :
        # Main KPI's
        len_year = len(water_df_NAT_filtr['Year'].unique())

        rate_mean_urban = round(water_df_NAT_filtr['urban_percent'].mean(),2)
        rate_mean_rural = round(100 - rate_mean_urban,2)

        val_mean_urban = round(((water_df_NAT_filtr['Population'].sum()*(rate_mean_urban/100))/len_year)/1000000,1)
        
        
        val_mean_rural = round(((water_df_NAT_filtr['Population'].sum()*(rate_mean_rural/100))/len_year)/1000000,1)


        col0, col1, col2 = st.columns([42,16,42])

        with col1:
            rad_2 = st.radio(label="Label", options=['Rates', "Population"],
                    label_visibility="collapsed", horizontal=False)

        with col0:
            urb_data = st.subheader('')

        with col2:
            rur_data = st.subheader('')

        st.markdown("""---""")

        if rad_2 == 'Rates' :
            urb_data.subheader(f"Urban Area : {rate_mean_urban:,} %".format(rate_mean_urban).replace(',', ' '))
            rur_data.subheader(f"Rural Area : {rate_mean_rural:,} %".format(rate_mean_rural).replace(',', ' '))
            st.plotly_chart(get_chart_coverage_rates(water_df_NAT_filtr), use_container_width=True)

        if rad_2 == 'Population' :
            st.plotly_chart(get_chart_coverage_values(water_df_NAT_filtr), use_container_width=True)
            urb_data.subheader(f"Urban Area : {val_mean_urban:,} M".format(val_mean_urban).replace(',', ' '))
            rur_data.subheader(f"Rural Area : {val_mean_rural:,} M".format(val_mean_rural).replace(',', ' '))

    else :
        st.error("Please select/enter a filter")



if nav_menu == 'Evolution':

    col1_marche, col2_marche = st.columns(2)
    with col1_marche:
        options_cont = ["ALL"] + list(sorted(water_df["Continent"].unique()))
        cont = st.multiselect(label="📌 Continent :",
            options=options_cont,
            default="ALL", label_visibility="visible") # "hidden"
        if "ALL" in cont:
            water_df_NAT_filtr  = water_df
        else:
            water_df_NAT_filtr = water_df[water_df["Continent"].isin(cont)]

    with col2_marche:
        options_contr = ["ALL"] + list(sorted(water_df_NAT_filtr["Country"].unique()))
        contr = st.multiselect(label="📌 Country :",
            options=options_contr,
            default="ALL", label_visibility="visible") # "hidden"
        if "ALL" in contr:
            water_df_NAT_filtr  = water_df_NAT_filtr
        else:
            water_df_NAT_filtr = water_df_NAT_filtr[water_df_NAT_filtr["Country"].isin(contr)]

    st.markdown("""---""")

    if len(water_df_NAT_filtr) != 0 :
        # Main KPI's
        all_kpi_rates = get_kpi_rates(water_df_NAT_filtr)
        mean_safe = all_kpi_rates[0]
        mean_basic = all_kpi_rates[1]
        mean_limited = all_kpi_rates[2]
        mean_unimproved = all_kpi_rates[3]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.subheader("Safe :")
            st.subheader(f"{mean_safe:,} %".format(mean_safe).replace(',', ' '))
        with col2:
            st.subheader("Basic :")
            st.subheader(f"{mean_basic:,} %".format(mean_basic).replace(',', ' '))
        with col3:
            st.subheader(f"Limited :")
            st.subheader(f"{mean_limited:,} %".format(mean_limited).replace(',', ' '))
        with col4:
            st.subheader(f"Unimproved :")
            st.subheader(f"{mean_unimproved:,} %".format(mean_unimproved).replace(',', ' '))

        st.markdown("""---""")
        
        st.plotly_chart(get_chart_evo(water_df_NAT_filtr), use_container_width=True)

    else :
        st.error("Please select/enter a filter")