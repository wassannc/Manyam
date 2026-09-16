import streamlit as st
import requests
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def load_manyam_google_sheets():

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(
        "1HlLJW9CrWkKZ6xN4zd9T7IYlLaWclJTofyv_DRQXebA"
    )

    total_list = pd.DataFrame(
        spreadsheet.worksheet("Total list").get_all_records()
    )

    working_hhs = pd.DataFrame(
        spreadsheet.worksheet("Working HHs").get_all_records()
    )

    return total_list, working_hhs

ODK_URL = st.secrets["ODK_URL"]
USERNAME = st.secrets["USERNAME"]
PASSWORD = st.secrets["PASSWORD"]
PROJECT_ID = st.secrets["PROJECT_ID"]

@st.cache_data(ttl=300)
def load_odk_data(form_id):
    url = f"{ODK_URL}/v1/projects/{PROJECT_ID}/forms/{form_id}.svc/Submissions"
    
    response = requests.get(url, auth=(USERNAME, PASSWORD))

    if response.status_code != 200:
        st.error(f"Error: {response.status_code}")
        return pd.DataFrame()

    data = response.json()

    if "value" not in data:
        return pd.DataFrame()

    df = pd.json_normalize(data["value"])
    return df
