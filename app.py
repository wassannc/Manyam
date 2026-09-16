import streamlit as st
from config import FORMS
from utils import load_odk_data, load_manyam_google_sheets
import pandas as pd

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
    total_list, working_hhs = load_manyam_google_sheets()

    st.title("📊 Impact Assessment")
    
    # ------------------------------------------
    # VILLAGE FILTER
    # ------------------------------------------
    
    village_col = "Village"
    
    if village_col in total_list.columns:
    
        villages = (
            total_list[village_col]
            .dropna()
            .astype(str)
            .str.strip()
        )
    
        # Remove blank values AND duplicate village names
        villages = sorted(
            villages[villages != ""].unique().tolist()
        )
    
        village_options = ["All Villages"] + villages

        selected_village = st.selectbox(
            "Select Village",
            village_options
        )
        # ------------------------------------------
        # FILTER DATA FOR SELECTED VILLAGE
        # ------------------------------------------
        
        if selected_village == "All Villages":

            total_village_df = total_list.copy()
            working_hhs_village = working_hhs.copy()
        
        else:
        
            total_village_df = total_list[
                total_list["Village"]
                .astype(str)
                .str.strip()
                .eq(selected_village)
            ].copy()
        
            working_hhs_village = working_hhs[
                working_hhs["Village"]
                .astype(str)
                .str.strip()
                .eq(selected_village)
            ].copy()
    
    else:
        st.error(
            f"Village column '{village_col}' not found in Total list."
        )
        st.stop()
        # ------------------------------------------
        # FILTER WORKING HHs FOR SELECTED VILLAGE
        # ------------------------------------------
    
        working_village_col = "Village"
    
        working_hhs_village = working_hhs[
            working_hhs[working_village_col]
            .astype(str)
            .str.strip()
            .eq(selected_village)
        ].copy()

    try:
        # Load Google Sheet data
        total_list, working_hhs = load_manyam_google_sheets()
        
        # ------------------------------------------
        # COVERAGE
        # ------------------------------------------
        
        st.subheader("Coverage")
        
        total_households = len(total_village_df)
        
        working_households = len(working_hhs_village)
        
        total_gps = (
            total_village_df["Panchayat"]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )
        
        total_villages = (
            total_village_df["Village"]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total GPs", total_gps)
        
        with col2:
            st.metric("Total Villages", total_villages)
        
        with col3:
            st.metric("Total Households", total_households)
        
        with col4:
            st.metric("Working Households", working_households)
        # -------------------------------
        # CHECK INCOME COLUMNS
        # -------------------------------

        baseline_col = "Baseline Income"
        endline_col = "Endline Income"

        if baseline_col not in working_hhs.columns:

            st.error(
                f"Column not found: {baseline_col}"
            )

        elif endline_col not in working_hhs.columns:

            st.error(
                f"Column not found: {endline_col}"
            )

        else:

            # ------------------------------------------
            # HOUSEHOLD INCOME IMPACT
            # ------------------------------------------
            
            baseline_col = "Baseline Income"
            endline_col = "Endline Income"
            
            if baseline_col not in working_hhs_village.columns:
                st.error(f"Column not found: {baseline_col}")
            
            elif endline_col not in working_hhs_village.columns:
                st.error(f"Column not found: {endline_col}")
            
            else:
            
                # --------------------------------------
                # SELECTED VILLAGE ONLY
                # --------------------------------------
            
                baseline = pd.to_numeric(
                    working_hhs_village[baseline_col],
                    errors="coerce"
                )
            
                endline = pd.to_numeric(
                    working_hhs_village[endline_col],
                    errors="coerce"
                )
            
                # Keep HHs having both baseline and endline
                valid = baseline.notna() & endline.notna()
            
                baseline_valid = baseline[valid]
                endline_valid = endline[valid]
            
                # --------------------------------------
                # INCOME CALCULATIONS
                # --------------------------------------
            
                avg_baseline = baseline_valid.mean()
                avg_endline = endline_valid.mean()
            
                avg_change = avg_endline - avg_baseline
            
                if avg_baseline > 0:
                    percentage_change = (
                        avg_change / avg_baseline
                    ) * 100
                else:
                    percentage_change = 0
            
                # Household-level income change
                change = endline_valid - baseline_valid
            
                increased = int((change > 0).sum())
                decreased = int((change < 0).sum())
                no_change = int((change == 0).sum())
            
                valid_households = len(change)
            
                # --------------------------------------
                # HOUSEHOLD INCOME IMPACT
                # --------------------------------------
            
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
            
                # --------------------------------------
                # HOUSEHOLDS BY INCOME CHANGE
                # --------------------------------------
            
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
                    f"Working HHs in {selected_village} "
                    f"with both baseline and endline income data."
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
    # ------------------------------------------
    # ADDITIONAL INCOME BY INTERVENTION
    # ------------------------------------------
    
    st.subheader("Additional Income by Intervention")
    
    # Intervention columns where -ai means Additional Income
    intervention_ai_cols = {
        "Eco Farmponds": "Eco Farmponds-ai",
        "Solar Irrigation": "Solar Irrigation-ai",
        "Fish WB's": "Fish_WB's-ai",
        "Mobile Irrigation": "Mobile Irrigation-ai",
        "BRC": "BRC-ai",
        "ASC": "ASC-ai",
        "Processing Hubs": "Processing Hubs-ai",
        "Cashew/RoFR": "Cashew/RoFR-ai",
        "Turmeric": "Turmeric-ai",
        "Crop Diversity": "Crop Diversity-ai",
        "BYP_NS": "BYP_NS-ai",
        "BYP_BFE": "BYP_BFE-ai"
    }
    
    impact_rows = []
    
    working_hh_count = len(working_hhs_village)
    
    for intervention, col in intervention_ai_cols.items():
    
        if col not in working_hhs_village.columns:
            continue
    
        income = pd.to_numeric(
            working_hhs_village[col],
            errors="coerce"
        ).fillna(0)
    
        # HHs having additional income from this intervention
        covered_hhs = int((income > 0).sum())
    
        # Total additional income
        total_additional_income = income.sum()
    
        # Average among HHs receiving additional income
        if covered_hhs > 0:
            avg_additional_income = (
                total_additional_income / covered_hhs
            )
        else:
            avg_additional_income = 0
    
        # Percentage of working HHs
        if working_hh_count > 0:
            coverage_pct = (
                covered_hhs / working_hh_count
            ) * 100
        else:
            coverage_pct = 0
    
        impact_rows.append({
            "Intervention": intervention,
            "HHs Covered": covered_hhs,
            "% of Working HHs": coverage_pct,
            "Total Additional Income": total_additional_income,
            "Avg. Additional Income / HH": avg_additional_income
        })
    
    
    impact_table = pd.DataFrame(impact_rows)
    # ------------------------------------------
    # DISPLAY TABLE
    # ------------------------------------------
    
    if not impact_table.empty:
    
        display_table = impact_table.copy()
    
        display_table["% of Working HHs"] = (
            display_table["% of Working HHs"]
            .round(1)
            .astype(str)
            + "%"
        )
    
        display_table["Total Additional Income"] = (
            display_table["Total Additional Income"]
            .round(0)
            .apply(lambda x: f"₹{x:,.0f}")
        )
    
        display_table["Avg. Additional Income / HH"] = (
            display_table["Avg. Additional Income / HH"]
            .round(0)
            .apply(lambda x: f"₹{x:,.0f}")
        )
    
        st.dataframe(
            display_table,
            use_container_width=True,
            hide_index=True
        )
    # ------------------------------------------
    # GRAPH
    # ------------------------------------------
    
    if not impact_table.empty:
    
        chart_df = impact_table[
            ["Intervention", "Avg. Additional Income / HH"]
        ].copy()
    
        chart_df = chart_df.sort_values(
            "Avg. Additional Income / HH",
            ascending=False
        )
    
        st.bar_chart(
            chart_df.set_index("Intervention")
        )

    # ==========================================
    # INCOME CHANGE BY NUMBER OF INTERVENTIONS
    # ==========================================
    
    st.subheader("Income Change by Number of Covered Interventions")
    
    intervention_col = "Covered interventions"
    
    if intervention_col not in working_hhs.columns:
    
        st.warning(
            f"Column not found: {intervention_col}"
        )
    
    else:
    
        impact_df = working_hhs_village[
            [intervention_col, baseline_col, endline_col]
        ].copy()
    
        # Convert to numeric
        impact_df[intervention_col] = pd.to_numeric(
            impact_df[intervention_col],
            errors="coerce"
        )
    
        impact_df[baseline_col] = pd.to_numeric(
            impact_df[baseline_col],
            errors="coerce"
        )
    
        impact_df[endline_col] = pd.to_numeric(
            impact_df[endline_col],
            errors="coerce"
        )
    
        # Keep households with all required values
        impact_df = impact_df.dropna(
            subset=[
                intervention_col,
                baseline_col,
                endline_col
            ]
        )
    
        # Keep 1 to 6 interventions
        impact_df = impact_df[
            impact_df[intervention_col].between(1, 6)
        ]
    
        # Calculate income change
        impact_df["Income Change"] = (
            impact_df[endline_col]
            - impact_df[baseline_col]
        )
    
        # Group by number of interventions
        intervention_summary = (
            impact_df
            .groupby(intervention_col)
            .agg(
                HHs=(intervention_col, "size"),
                Avg_Baseline=(baseline_col, "mean"),
                Avg_Endline=(endline_col, "mean"),
                Avg_Change=("Income Change", "mean")
            )
            .reset_index()
        )
    
        # Percentage change
        intervention_summary["Change_%"] = (
            intervention_summary["Avg_Change"]
            / intervention_summary["Avg_Baseline"]
            * 100
        )
    
        # Rename columns
        intervention_summary = intervention_summary.rename(
            columns={
                intervention_col: "No. of Covered Interventions",
                "Avg_Baseline": "Avg Baseline Income",
                "Avg_Endline": "Avg Endline Income",
                "Avg_Change": "Avg Income Change",
                "Change_%": "Change %"
            }
        )
    
        # Format
        intervention_summary[
            "Avg Baseline Income"
        ] = intervention_summary[
            "Avg Baseline Income"
        ].round(0)
    
        intervention_summary[
            "Avg Endline Income"
        ] = intervention_summary[
            "Avg Endline Income"
        ].round(0)
    
        intervention_summary[
            "Avg Income Change"
        ] = intervention_summary[
            "Avg Income Change"
        ].round(0)
    
        intervention_summary[
            "Change %"
        ] = intervention_summary[
            "Change %"
        ].round(1)
    
        st.dataframe(
            intervention_summary,
            use_container_width=True,
            hide_index=True
        )

        # ==========================================
        # GRAPH - INCOME CHANGE BY NO. OF INTERVENTIONS
        # ==========================================
    
        st.subheader("Average Income Change by Number of Covered Interventions")
    
        chart_df = intervention_summary[
            ["No. of Covered Interventions", "Change %"]
        ].copy()
    
        chart_df = chart_df.set_index(
            "No. of Covered Interventions"
        )
    
        st.bar_chart(
            chart_df,
            y="Change %",
            x_label="Number of Covered Interventions",
            y_label="Average Income Change (%)"
        )
