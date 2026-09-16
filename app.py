import streamlit as st
from config import FORMS
from utils import load_odk_data, load_manyam_google_sheets

st.set_page_config(page_title="MIS Tracking-Manyam", layout="wide")

st.sidebar.title("Menu")

main_section = st.sidebar.radio(
    "Select Section",
    ["MIS-Status", "MIS-Reports", "MB Generator", "Impact Assessment"]
)

if main_section == "MIS-Reports":
    page = st.sidebar.radio(
        "Select Form",
        list(FORMS.keys())
    )
elif main_section == "MIS-Status":
    page = "MIS-Status"
else:
    page = None

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
# ================================
# 📘 MB GENERATOR
# ================================

if main_section == "MB Generator":
    import pandas as pd

    st.title("📘 Farm Pond MB Generator")

    # ---------------- LOAD FORMS ----------------

    df_mb1 = load_odk_data(FORMS["Farm Pond MB 1"]["form_id"])
    df_mb2 = load_odk_data(FORMS["Farm Pond MB 2"]["form_id"])

    # ---------------- PROJECT TAG ----------------

    df_mb1["project"] = "Project 1"
    df_mb2["project"] = "Project 2"

    # ---------------- MERGE DATA ----------------

    df_mb = pd.concat([df_mb1, df_mb2], ignore_index=True)

    # ---------------- CHECK ----------------

    if df_mb.empty:
        st.warning("No MB data found")

    else:

        st.success(f"Loaded {len(df_mb)} records")

        # ---------------- FARMER SELECT ----------------

        farmer_col = "pd.fish_farmer"

        farmers = sorted(
            df_mb[farmer_col]
            .dropna()
            .unique()
        )

        selected_farmer = st.selectbox(
            "Select Farmer",
            farmers
        )

        # ---------------- FILTER ----------------

        farmer_df = df_mb[
            df_mb[farmer_col] == selected_farmer
        ]

        st.write("### Farmer Data")

        st.dataframe(
            farmer_df,
            use_container_width=True
        )
# ==========================================
# IMPACT ASSESSMENT
# ==========================================

if main_section == "Impact Assessment":

    st.title("📊 Impact Assessment")

    try:
        # Load Google Sheet data
        total_list, working_hhs = load_manyam_google_sheets()

        # -------------------------------
        # HOUSEHOLD COVERAGE
        # -------------------------------

        total_households = len(total_list)
        working_households = len(working_hhs)

        st.subheader("Household Coverage")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Households",
                total_households
            )

        with col2:
            st.metric(
                "Working Households",
                working_households
            )

        # -------------------------------
        # CHECK INCOME COLUMNS
        # -------------------------------

        baseline_col = "Baseline Income"
        endline_col = "Endline income"

        if baseline_col not in working_hhs.columns:

            st.error(
                f"Column not found: {baseline_col}"
            )

        elif endline_col not in working_hhs.columns:

            st.error(
                f"Column not found: {endline_col}"
            )

        else:

            # Convert income columns to numbers
            baseline = pd.to_numeric(
                working_hhs[baseline_col],
                errors="coerce"
            )

            endline = pd.to_numeric(
                working_hhs[endline_col],
                errors="coerce"
            )

            # Keep households having both values
            valid = baseline.notna() & endline.notna()

            baseline_valid = baseline[valid]
            endline_valid = endline[valid]

            # -------------------------------
            # INCOME CALCULATIONS
            # -------------------------------

            avg_baseline = baseline_valid.mean()
            avg_endline = endline_valid.mean()

            avg_change = avg_endline - avg_baseline

            if avg_baseline > 0:
                percentage_change = (
                    avg_change / avg_baseline
                ) * 100
            else:
                percentage_change = 0

            # Household-level change
            change = endline_valid - baseline_valid

            increased = (change > 0).sum()
            decreased = (change < 0).sum()
            no_change = (change == 0).sum()

            valid_households = len(change)

            # -------------------------------
            # INCOME IMPACT
            # -------------------------------

            st.subheader("Household Income Impact")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Average Baseline Income",
                    f"₹{avg_baseline:,.0f}"
                )

            with col2:
                st.metric(
                    "Average Endline Income",
                    f"₹{avg_endline:,.0f}"
                )

            with col3:
                st.metric(
                    "Average Income Change",
                    f"₹{avg_change:,.0f}"
                )

            with col4:
                st.metric(
                    "Income Change",
                    f"{percentage_change:.1f}%"
                )

            # -------------------------------
            # HOUSEHOLDS BY CHANGE
            # -------------------------------

            st.subheader("Households by Income Change")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Income Increased",
                    increased
                )

            with col2:
                st.metric(
                    "No Change",
                    no_change
                )

            with col3:
                st.metric(
                    "Income Decreased",
                    decreased
                )

            st.caption(
                f"Income impact calculated for {valid_households} "
                f"Working HHs with both baseline and endline Income data."
            )

    except Exception as e:

        st.error(
            f"Impact Assessment error: {e}"
        )
