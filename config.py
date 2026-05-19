FORMS = {
    "1. NF- Register": {
        "form_id": "NF- Register",
        "columns": ["plot_reg.date","plot_reg.block","plot_reg.gp","plot_reg.village","plot_reg.farmer_name","plot_reg.spouse","plot_reg.season","Crop Model Final","plot_reg.main_crop","plot_reg.sowing_date"],
        "block_col": "plot_reg.block"
    },
    "1.1 NF- Activities": {
        "form_id": "NF- Activities",
        "columns": ["Primary_details.date","Primary_details.block","Primary_details.gp","Primary_details.village","Primary_details.farmer_name","Primary_details.plot_ext","crop_activity","Nf_activites.nf_inputs","Nf_activites.Other_nf_input","Nf_activites.Qty_other_nfinput"],
        "block_col": "Primary_details.block"
    },
    "2.Bio Resource Center- (BRC)": {
        "form_id": "BRC_Units",
        "columns": ["SubmissionDate","table_list_pd.block","table_list_pd.brc_unit","table_list_pd.product_name","table_list_pd.brc_sale_date","table_list_pd.dj_sale_farmer","table_list_pd.gender","table_list_pd.sale_village","table_list_sd.sale_qty","table_list_sd.total_income","table_list_cd.crops","table_list_cd.crop_ext"],
        "block_col": "table_list_pd.block"
    },
      "3. Livestock": {
        "form_id": "Livestock",
        "columns": ["table_list_df.Month","table_list_df.Monthly_MIS","table_list_df.block","table_list_df.gp","table_list_df.village","table_list_df.livestock_type","table_list_df.Farmer"],
        "block_col": "table_list_df.block"
    },
    "Intensification of Orchards": {
        "form_id": "Orchards_Intensification",
        "columns": ["SubmissionDate","basic_info.block","basic_info.gp","basic_info.village","basic_info.orchard_type","basic_info.farmer_add","type"],
        "block_col": "basic_info.block"
    },
    "Micro Enterprizes": {
        "form_id": "Micro Enterprizes",
        "columns": ["SubmissionDate","table_list_pd.block","table_list_pd.gp","table_list_pd.village","table_list_pd1.farmer_name","table_list_pd1.processing_hub_tool","table_list_pd1.processing_date","table_list_pd1.processed_for","table_list_pd2.processing_farmer_village","table_list_pd2.processing_farmer","table_list_pd2.processing_qty_kgs","table_list_pd2.rent_amount","table_list_pd3.Data_sub_by"],
        "block_col": "table_list_pd.block"
    },
    "Meetings&Trainings": {
        "form_id": "Capacity_building",
        "columns": ["CB_info.block","CB_info.gp","CB_info.village","CB_info.Trainining_type","CB_info.Event_name","CB_info.Event_mode","Cb_info1.from_date","Cb_info1.days","Cb_info1.male","Cb_info1.female","Cb_info1.total_members","Cb_info1.Event_place"],
        "block_col": "CB_info.block"
    }
}
