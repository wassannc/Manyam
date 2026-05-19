import streamlit as st
from config import FORMS
from utils import load_odk_data
st.set_page_config(page_title="MIS Tracking-IINF", layout="wide")
st.title("📊 MIS Tracking - IINF")

st.sidebar.title("Menu")

main_section = st.sidebar.radio(
    "Select Section",
    ["MIS-Status", "MIS-Reports"]
)

if main_section == "MIS-Reports":
    page = st.sidebar.radio(
        "Select Form",
        list(FORMS.keys())
    )
else:
    page = "MIS-Status"

if page == "MIS-Status":
    import pandas as pd
    import calendar

    st.title(" MIS Status")

    # ---------------- FILTERS ----------------
    col1, col2 = st.columns(2)

    with col1:
        all_blocks = set()

        for form_name, config in FORMS.items():
            df_temp = load_odk_data(config["form_id"])
            col = config.get("block_col")

            if col and col in df_temp.columns:
                all_blocks.update(df_temp[col].dropna().unique())

        all_blocks = sorted(all_blocks)

        selected_block = st.selectbox(
            "Select Block",
            ["All"] + list(all_blocks)
        )

    with col2:
        months = ["All"] + [calendar.month_name[i] for i in range(1, 13)]
        selected_month = st.selectbox("Select Month", months)

    # ---------------- DATA DISPLAY ----------------
    forms_list = list(FORMS.items())
    cols_per_row = 2

    for i in range(0, len(forms_list), cols_per_row):
        cols = st.columns(cols_per_row)

        for j in range(cols_per_row):
            if i + j >= len(forms_list):
                break

            form_name, config = forms_list[i + j]
            df = load_odk_data(config["form_id"])
            block_col = config.get("block_col")

            # -------- APPLY FILTERS --------

            # Landscape filter
            if selected_block != "All" and block_col in df.columns:
                df = df[df[block_col] == selected_block]

            # Month filter
            date_cols = ["__system.submissionDate", "meta.submissionDate"]
            date_col = None

            for col in date_cols:
                if col in df.columns:
                    date_col = col
                    break

            if selected_month != "All" and date_col:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                month_num = list(calendar.month_name).index(selected_month)
                df = df[df[date_col].dt.month == month_num]

            # -------- UI --------
            with cols[j]:
                st.markdown(f"#### 📦 {form_name}")

                if df.empty:
                    st.write("No data")
                    continue

                st.caption(f"Total: {len(df)}")

                if block_col and block_col in df.columns:
                    grouped = (
                        df.groupby(block_col)
                        .size()
                        .reset_index(name="Count")
                        .sort_values("Count", ascending=False)
                    )

                    grouped.columns = ["Block", "Count"]

                    st.dataframe(grouped, use_container_width=True, height=200)

                else:
                    st.warning(f"{block_col} not found")

elif page in FORMS:
    st.title(f"📥 {page}")

    config = FORMS[page]
    df = load_odk_data(config["form_id"])
    if "plot_reg.crop_model" in df.columns:
        df["Crop Model Final"] = df["plot_reg.crop_model"]

        if "plot_reg.Other_cropmodel" in df.columns:
            df.loc[
                df["plot_reg.crop_model"].str.lower().str.contains("others", na=False),
                "Crop Model Final"
            ] = df["plot_reg.Other_cropmodel"]
    
    if df.empty:
        st.warning("No data found")
    else:
        # Select only required columns
        columns = config.get("columns", [])
        available_cols = [col for col in columns if col in df.columns]

        df_filtered = df[available_cols]

        st.dataframe(df_filtered, use_container_width=True)

        # Download button
        st.download_button(
            label="⬇ Download CSV",
            data=df_filtered.to_csv(index=False),
            file_name=f"{page}_report.csv",
            mime="text/csv"
        )
