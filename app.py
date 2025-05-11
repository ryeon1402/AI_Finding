import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Species Trait Viewer", layout="wide")
st.title("🌿 Species Trait Viewer (AI Result)")

# -------------------
# CSV 데이터 불러오기
# -------------------
@st.cache_data
def load_data():
    df = pd.read_csv("final Traits summary.csv")
    df = df.applymap(lambda x: x.split(" (")[0].strip() if isinstance(x, str) else x)
    return df

df = load_data()
species_list = sorted(df["species_name"].dropna().unique())

# -------------------
# trait 그룹 정의
# -------------------
trait_groups = {
    "Blossoming": ["flowering_cues", "flowering_time"],
    "Botany": ["bud_bank_location", "clonal_spread_mechanism", "flower_structural_sex_type", "genome_size", "ploidy", "root_system_type", "sex_type"],
    "Descriptive": ["flower_colour", "fruit_colour", "leaf_type", "parasitic", "plant_climbing_mechanism", "plant_growth_form", "plant_growth_substrate", "plant_height", "plant_physical_defence_structures"],
    "Fire recovery": ["fire_time_from_fire_to_50_percent_flowering", "fire_time_from_fire_to_50_percent_fruiting", "fire_time_from_fire_to_flowering", "fire_time_from_fire_to_flowering_decline", "fire_time_from_fire_to_fruiting", "fire_time_from_fire_to_peak_flowering"],
    "Fire response": ["life_history_ephemeral_class", "plant_tolerance_fire", "post_fire_flowering", "post_fire_recruitment", "resprouting_capacity", "resprouting_capacity_juvenile", "resprouting_capacity_proportion_individuals", "resprouting_capacity_time_from_germination"],
    "Germination": ["establishment_light_environment_index", "recruitment_time", "reproductive_light_environment_index", "root_structure", "seed_germination", "seed_germination_time", "seedling_establishment_conditions", "seedling_germination_location"],
    "Life history": ["life_history", "lifespan"],
    "Natural Growth": ["competitive_stratum", "dispersal_syndrome", "dispersers", "nitrogen_fixing", "resprouting_capacity_non_fire_disturbance", "sprout_depth", "stem_growth_habit", "storage_organ", "vegetative_reproduction_ability"],
    "Pollination": ["pollination_syndrome", "pollination_system"],
    "Seedbank": ["seedbank_location", "seedbank_longevity", "seedbank_longevity_class"],
    "Seeds": ["dispersal_unit", "fruiting_time", "reproductive_maturity", "seed_viability", "serotiny"],
    "Propagation": ["seed_dormancy_class", "seed_germination_treatment", "germination_treatment"],
    "Soil tolerances": ["plant_tolerance_calcicole", "plant_tolerance_salt", "plant_tolerance_soil_salinity", "plant_type_by_resource_use"],
    "Water response": ["plant_flood_regime_classification", "plant_tolerance_inundation", "plant_tolerance_snow", "plant_tolerance_water_logged_soils"]
}

# -------------------
# trait value 분해 함수 (모든 구분자 + 소문자 처리)
# -------------------
def split_trait_values(val):
    if pd.isna(val):
        return []
    return [v.strip().lower() for v in re.split(r",| - |–| to | and |\+|-", str(val)) if v.strip()]

# -------------------
# 페이지 선택
# -------------------
st.sidebar.title("🌼 Navigation")
page = st.sidebar.radio("Choose a page:", ["View Traits", "Find Flowers by Trait", "Compare Traits"])

# -------------------
# ① View Traits
# -------------------
if page == "View Traits":
    st.title("🌿 View Traits by Species")
    selected_species = st.multiselect("Select one or more species:", species_list)

    if selected_species:
        for species in selected_species:
            st.subheader(f"🌸 {species}")
            row = df[df["species_name"] == species].iloc[0]
            for group_name, traits in trait_groups.items():
                group_data = {trait: row[trait] for trait in traits if trait in row and pd.notna(row[trait])}
                if group_data:
                    st.markdown(f"**{group_name}**")
                    st.dataframe(pd.DataFrame(group_data.items(), columns=["Trait", "Value"]).set_index("Trait"))
    else:
        st.info("Please select at least one species.")

# -------------------
# ② Find Flowers by Trait
# -------------------
elif page == "Find Flowers by Trait":
    st.title("🔍 Find Flowers by Trait")
    selected_groups = st.multiselect("Select trait groups:", list(trait_groups.keys()))

    available_traits = []
    for group in selected_groups:
        available_traits.extend([trait for trait in trait_groups[group] if trait in df.columns])

    selected_traits = st.multiselect("Select traits to filter by:", options=available_traits)

    def extract_unique_values(trait):
        values = df[trait].dropna().astype(str)
        value_set = set()
        for v in values:
            v = v.lower()  # 소문자화 중요!
            for item in split_trait_values(v):
                value_set.add(item)
        return sorted(value_set)

    filters = {}
    for trait in selected_traits:
        value_options = extract_unique_values(trait)
        raw_selected_vals = st.multiselect(f"Values for **{trait}**", options=value_options)
        selected_vals = []
        for val in raw_selected_vals:
            selected_vals.extend(split_trait_values(val))
        if selected_vals:
            filters[trait] = list(set(selected_vals))

    if filters:
        filtered_df = df.copy()
        for trait, vals in filters.items():
            def match_any(val):
                val_list = split_trait_values(val)
                return any(v in val_list for v in vals)
            filtered_df = filtered_df[filtered_df[trait].apply(match_any)]

        st.subheader("🌼 Matching Species")
        if not filtered_df.empty:
            st.dataframe(filtered_df[["species_name"] + list(filters.keys())].set_index("species_name"))
        else:
            st.warning("No matching species found.")
    else:
        st.info("Please select at least one trait and value.")

# -------------------
# ③ Compare Traits
# -------------------
elif page == "Compare Traits":
    st.title("📊 Compare Traits Across Multiple Species")
    selected_species = st.multiselect("Select species to compare:", species_list)

    if selected_species:
        compare_df = df[df["species_name"].isin(selected_species)].set_index("species_name")
        st.dataframe(compare_df)
    else:
        st.info("Please select at least one species.")
