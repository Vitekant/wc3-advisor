from typing import Callable
import uuid
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

@st.cache_data()
def load_armor_data():
    df = pd.read_csv("data/armour.csv", comment='#', index_col=["Attack Type"])
    # print(df.set_index(df['Attack Type']))
    # print(df)
    return df

@st.cache_data
def load_units_data():
    df = pd.read_csv("data/units.csv", comment='#')
    df['Id'] = df['Unit'].str.replace(' ', '_').str.replace('.','').str.lower()
    df["Icon"] = df["Icon"].fillna('default.png')
    df['Icon'] = "static/icons/" +  df['Race'].str.lower().str.replace(' ','_') + "/" + df['Icon']
    return df
    
armor_data = load_armor_data()
units = load_units_data()


def strip_percent(v: str) -> int:
        return int(str(v).removesuffix('%'))

def find_attack_data(units: pd.DataFrame, armor_data: pd.DataFrame, treshold_fn: Callable[[int], bool]) -> dict[str, list[str]]:
    effectivness = {}
    for attack, armor_row in armor_data.iterrows():
        meets_criteria = []
        for armor, damage in armor_row.items():
            if treshold_fn(strip_percent(damage)):
                meets_criteria.append(armor)
        effectivness[attack] = meets_criteria
    attack_against = {}
    for attack, meets_criteria in effectivness.items():
        attack_against[attack] = units[units['Armor Type'].isin(meets_criteria)]['Id']
    return attack_against

def load_good_attack_data(units: pd.DataFrame, armor_data: pd.DataFrame) -> dict[str, list[str]]:
    return find_attack_data(units, armor_data, treshold_fn=lambda attack: attack > 100)

def load_bad_attack_data(units: pd.DataFrame, armor_data: pd.DataFrame) -> dict[str, list[str]]:
    return find_attack_data(units, armor_data, treshold_fn=lambda attack: attack < 100)

def find_defense_data(units: pd.DataFrame, armor_data: pd.DataFrame, treshold_fn: Callable[[int], bool]) -> dict[str, list[str]]:
    effectivness = {}
    for armor_type, attack_data in armor_data.items():
        meets_criteria = []
        for attack, damage in attack_data.items():
            if treshold_fn(strip_percent(damage)):
                meets_criteria.append(attack)
        effectivness[armor_type] = meets_criteria
    
    defense_against = {}
    for armor, meets_criteria in effectivness.items():
        defense_against[armor] = units[units['Attack Type'].isin(meets_criteria)]['Id']
    return defense_against

def load_bad_defense_data(units: pd.DataFrame, armor_data: pd.DataFrame) -> dict[str, list[str]]:
    return find_defense_data(units, armor_data, treshold_fn=lambda armour: armour > 100)


def load_good_defense_data(units: pd.DataFrame, armor_data: pd.DataFrame) -> dict[str, list[str]]:
    return find_defense_data(units, armor_data, treshold_fn=lambda armour: armour < 100)

@st.cache_data
def load_effectivness_data(units: pd.DataFrame, armor_data: pd.DataFrame) -> dict[str, dict[str, list[str]]]:
    attack_effective_against = load_good_attack_data(units, armor_data)
    attack_bad_against = load_bad_attack_data(units, armor_data)
    defense_bad_against = load_bad_defense_data(units, armor_data)
    defense_good_against = load_good_defense_data(units, armor_data)
    return {
        "good_attack": attack_effective_against,
        "bad_attack": attack_bad_against,
        "bad_defense": defense_bad_against,
        "good_defense": defense_good_against
    }

effectivness = load_effectivness_data(units, armor_data)

def find_excelent_targets_for(unit: pd.Series) -> pd.DataFrame:
    good_attack = effectivness["good_attack"].get(unit["Attack Type"], [])
    good_defense = effectivness["good_defense"].get(unit["Armor Type"], [])
    return list(set(good_attack) & set(good_defense))

def find_good_targets_for(unit: pd.Series) -> pd.DataFrame:
    good_attack = effectivness["good_attack"].get(unit["Attack Type"], [])
    bad_defense = effectivness["bad_defense"].get(unit["Armor Type"], [])
    good_defense = effectivness["good_defense"].get(unit["Armor Type"], [])
    return list(set(good_attack) - set(bad_defense) - set(good_defense))

def find_counters_for(unit: pd.Series) -> pd.DataFrame:
    bad_attack = effectivness["bad_attack"].get(unit["Attack Type"], [])
    bad_defense = effectivness["bad_defense"].get(unit["Armor Type"], [])
    return list(set(bad_defense) | set(bad_attack))


def prepare_units_tab():


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
    # print(df_filtered)

    def row_filtered(row: pd.Series) -> pd.Series:
        r = row[['Gold', 'Wood', 'Population', 'Hit Points', 'Armor Type', 'Attack Type', 'Armor', 'Speed', 'Range']]
        r.name = row['Unit']
        return r

    def render_unit_details(unit: pd.Series, unit_container):
        with unit_container:
            with st.container():
                # st.header(row["Unit"])
                st.image("./" + unit["Icon"])
                # print(row_filtered(row))
                st.dataframe(row_filtered(unit))
                excellent_targets = find_excelent_targets_for(unit)
                if excellent_targets:
                    with st.expander("Great against:"):
                        st.write(excellent_targets)
                good_targets = find_good_targets_for(unit)
                # good_targets = list(set(good_targets) - set(excellent_targets))
                if good_targets:
                    with st.expander("Good against:"):
                        for target in good_targets:
                            target_unit = units[units['Id'] == target].iloc[0]
                            def load_target():
                                print(target_unit)
                                render_unit_details(target_unit, unit_container)
                            create_unit_button(target_unit, key_suffix=f"-{uuid.uuid4()}", button_fn=load_target)
                with st.expander("Countered by:"):
                    st.write(find_counters_for(unit))

    def gen_unit_dialog(row):
        @st.dialog(row['Unit'])
        def unit_details():
            empty_container = st.empty()
            with empty_container:
                render_unit_details(row, empty_container)
  
        return unit_details

    def create_unit_button(unit: pd.Series, key_suffix="", button_fn=None):
        if st.button("", type = "primary", key = unit['Id']+key_suffix, help=unit["Unit"], use_container_width=True):
            if button_fn:
                pass
                # print("Function")
                # button_fn()
            else:
                print("Default")
                gen_unit_dialog(unit)()
        st.markdown(
        f"""
        <style>
        div.st-key-{unit['Id']}{key_suffix} div button {{
            background: url(./app/{unit['Icon']})!important;
            background-size: 64px 64px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True)
    
    with st.container(key="units"):
        columns = st.columns(len(df_filtered), gap="small")
        col_idx = 0
        for idx, row in df_filtered.iterrows():
            with columns[col_idx]:
                create_unit_button(row)
            col_idx += 1

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

def prepare_armor_tab():
    armor = load_armor_data()
    # print(armor.reset_index(drop=True).set_index(armor['Attack Type'], drop=True))
    # print(armor.columns)
    def strip_percent(v: str) -> int:
        return int(str(v).removesuffix('%'))
    st.dataframe(armor.style.map(lambda v: "color:green" if strip_percent(v) > 100 else ("color:red" if strip_percent(v) < 100 else "")))

with units_tab:
    prepare_units_tab()

with armour_tab:
    prepare_armor_tab()