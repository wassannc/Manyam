import streamlit as st
import requests
import pandas as pd


# -------- MANYAM GOOGLE SHEET --------

GOOGLE_SHEET_ID = "1HlLJW9CrWkKZ6xN4zd9T7IYlLaWclJTofyv_DRQXebA"


@st.cache_data(ttl=300)
def load_manyam_google_sheets():

    # Total list
    total_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&gid=0"
    )

    # Working HHs
    working_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{GOOGLE_SHEET_ID}/gviz/tq?tqx=out:csv&gid=836274918"
    )

    total_list = pd.read_csv(total_url)
    working_hhs = pd.read_csv(working_url)

    return total_list, working_hhs


# -------- ODK --------

ODK_URL = st.secrets["ODK_URL"]
USERNAME = st.secrets["USERNAME"]
PASSWORD = st.secrets["PASSWORD"]
PROJECT_ID = st.secrets["PROJECT_ID"]


@st.cache_data(ttl=300)
def load_odk_data(form_id):

    url = f"{ODK_URL}/v1/projects/{PROJECT_ID}/forms/{form_id}.svc/Submissions"

    response = requests.get(
        url,
        auth=(USERNAME, PASSWORD)
    )

    if response.status_code != 200:
        st.error(f"Error: {response.status_code}")
        return pd.DataFrame()

    data = response.json()

    if "value" not in data:
        return pd.DataFrame()

    df = pd.json_normalize(data["value"])

    return df
