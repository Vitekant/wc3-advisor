import altair as alt
import pandas as pd
import streamlit as st
import base64

ICON_DIR = './images/icons/'

# Show the page title and description.
st.set_page_config(page_title="Warcraft III Advisor", page_icon="./images/favicon.png")
col1, col2 = st.columns(2)
with col1:
    st.image('./images/reforged_logo.webp')
with col2:
    st.title("Warcraft III Advisor")
    st.write(
        """
        WC3 data gathered and presented in easily accessible form.
        """
    )

units_tab, armour_tab = st.tabs(['Units', 'Armour'])



# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
# @st.cache_data
# def load_data():
#     df = pd.read_csv("data/movies_genres_summary.csv")
#     return df


def prepare_units_tab():
    @st.cache_data
    def load_units_data():
        df = pd.read_csv("data/units.csv", comment='#')
        df['Id'] = df['Unit'].str.replace(' ', '_').str.replace('.','').str.lower()
        df["Icon"] = df["Icon"].fillna('default.png')
        df['Icon'] = "static/icons/" +  df['Race'].str.lower().str.replace(' ','_') + "/" + df['Icon']
        return df

    units = load_units_data()
    # print(units)
    # df = load_data()

    # Show a multiselect widget with the genres using `st.multiselect`.
    races = st.multiselect(
        "Races",
        units['Race'].unique(),
        default=["Human", "Night Elf", "Orc", "Undead"],
    )

    # # Show a slider widget with the years using `st.slider`.
    # years = st.slider("Years", 1986, 2006, (2000, 2016))

    # Filter the dataframe based on the widget input and reshape it.
    df_filtered = units[(units["Race"].isin(races))]#& (df["year"].between(years[0], years[1]))]
    # df_reshaped = df_filtered.pivot_table(
    #     index="year", columns="genre", values="gross", aggfunc="sum", fill_value=0
    # )
    # df_reshaped = df_reshaped.sort_values(by="year", ascending=False)

    # df_filtered['Icon'] = ICON_DIR +  df_filtered['Race'].str.lower() + "/" + df_filtered['Icon']

    def row_filtered(row: pd.Series) -> pd.Series:
        r = row[['Gold', 'Wood', 'Population', 'Hit Points', 'Armor Type', 'Attack Type', 'Armor', 'Speed', 'Range']]
        r.name = row['Unit']
        return r

    def gen_unit_dialog(row):
        @st.dialog(row['Unit'])
        def unit_details():
            # st.header(row["Unit"])
            st.image("./" + row["Icon"])
            # print(row_filtered(row))
            st.dataframe(row_filtered(row))
        
        return unit_details

    
    with st.container(key="units"):
        columns = st.columns(len(df_filtered), gap="small")
        col_idx = 0
        for idx, row in df_filtered.iterrows():
            # print(row)
            # st.write(row["Unit"])
            with columns[col_idx]:
                with st.container(key=f"container{col_idx}"):
                    # st.button(row["Unit"])
                    if st.button("", type = "primary", key = row['Id'], help=row["Unit"], use_container_width=True):
                        gen_unit_dialog(row)()
                    st.markdown(
                    f"""
                    <style>
                    div.st-key-{row['Id']} div button {{
                        background: url(./app/{row['Icon']})!important;
                        background-size: 64px 64px !important;
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True)
            col_idx += 1

    # for idx, row in df_filtered.iterrows():
    #     # print(row)
    #     # st.write(row["Unit"])
    #     # if st.button("", type = "primary", key = row['Id'], help=row["Unit"]):
    #     #     unit_details(row)
    #     st.markdown(
    #     f"""
    #     <style>
    #     div.st-key-{row['Id']} div button {{
    #         background: url(./app/{row['Icon']})!important;
    #         background-size: 64px 64px !important;
    #     }}
    #     </style>
    #     """,
    #     unsafe_allow_html=True)


    # Display the data as a table using `st.dataframe`.
    # column_config = {
    #     # "year": st.column_config.TextColumn("Year"),
    #     "Icon": st.column_config.ImageColumn("Icon")
    # }
    # img = Image.open("images/top_spiderman.png")
    # with st.popover("[![Click me](app/static/abomination.png)]"):
    #     st.markdown("Hello World 👋")
    # st.button(st.image('./images/icons/undead/abomination.png'))
        # unit_details()
    if st.button("", type = "primary", key = "abomination"):
        unit_details("Abomination")
    if st.button("", type = "primary", key = "acolyte"):
        unit_details("Acolyte")
    # st.button("![abomination](app/static/abomination.png)")
    # st.image('./images/icons/undead/abomination.png')
    st.markdown(
        """
        <style>
        .st-key-units .stColumn {
            min-width: 64px;
        }
        button[kind="primary"] {
            background: transparent;
            width: 64px;
            height: 64px;
            border-radius: 0;
            border: none;
            padding: 0!important;
            color: black !important;
            text-decoration: none;
            cursor: pointer;
            border: none !important;
        }
        button[kind="primary"]:hover {
            background: transparent;
            text-decoration: none;
            color: black !important;
        }
        button[kind="primary"]:focus {
            background: transparent;
            outline: none !important;
            box-shadow: none !important;
            color: black !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
# st.markdown(
#             "![this is an image link](app/static/abomination.png)"
#         )
images = []
# with open("./images/icons/undead/abomination.png", "rb") as image:
#     encoded = base64.b64encode(image.read()).decode()
#     images.append(f"data:image/jpeg;base64,{encoded}")

# clicked = clickable_images(
#     [
#         # st.image('/images/icons/undead/abomination.png'),
#         # "/images/icons/undead/abomination.png",
#         images[0],
#         # "https://images.unsplash.com/photo-1565372195458-9de0b320ef04?w=700",
#         # "https://images.unsplash.com/photo-1582550945154-66ea8fff25e1?w=700",
#         # "https://images.unsplash.com/photo-1591797442444-039f23ddcc14?w=700",
#         # "https://images.unsplash.com/photo-1518727818782-ed5341dbd476?w=700",
#     ],
#     # titles=[f"Image #{str(i)}" for i in range(5)],
#     titles = ["Abomination"],
#     div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap"},
#     img_style={"margin": "5px", "height": "64px"},
# )

# if clicked > 0:
#     unit_details()
# # a = True
# if a:
#     unit_details()
# st.dataframe(
#     df_filtered,
#     use_container_width=True,
#     column_config=column_config,
# )


# Display the data as an Altair chart using `st.altair_chart`.
# df_chart = pd.melt(
#     df_reshaped.reset_index(), id_vars="year", var_name="genre", value_name="gross"
# )
# chart = (
#     alt.Chart(df_chart)
#     .mark_line()
#     .encode(
#         x=alt.X("year:N", title="Year"),
#         y=alt.Y("gross:Q", title="Gross earnings ($)"),
#         color="genre:N",
#     )
#     .properties(height=320)
# )
# st.altair_chart(chart, use_container_width=True)
@st.cache_data()
def load_armor_data():
    df = pd.read_csv("data/armour.csv", comment='#', index_col=["Attack Type"])
    # print(df.set_index(df['Attack Type']))
    # print(df)
    return df

def prepare_armor_tab():
    armor = load_armor_data()
    # print(armor.reset_index(drop=True).set_index(armor['Attack Type'], drop=True))
    # print(armor.columns)
    st.dataframe(armor)

with units_tab:
    prepare_units_tab()

with armour_tab:
    prepare_armor_tab()