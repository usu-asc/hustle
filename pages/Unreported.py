#%% Imports
import pandas as pd
import streamlit as st

#%% Layout
st.set_page_config(
    "HUSTLE Report",
    layout="wide"
)

st.title("Unreported Students")

#%% From Commitment Form
cf_unqualified = pd.read_csv("outputs/cf_unqualified.csv")
cf_unqualified = cf_unqualified[["First Name", "Last Name", "A-Number", "Reason"]]

#%% From OneTap
ot_unqualified = pd.read_csv("outputs/ot_unqualified.csv")
ot_unqualified = ot_unqualified[["First Name", "Last Name", "A-Number", "Reason"]]

#%% Layout Columns
col1, col2 = st.columns(2)

with col1:
    # Update metric
    if "cf_reason_filter" not in st.session_state:
        st.session_state["cf_reason_filter"] = "All"

    cf_reason_filter = st.selectbox(
        "Filter by Reason (Commitment Form)",
        options=["All"] + cf_unqualified["Reason"].unique().tolist(),
        key="cf_reason_filter"
    )

    if cf_reason_filter != "All":
        cf_filtered = cf_unqualified[cf_unqualified["Reason"] == cf_reason_filter]
    else:
        cf_filtered = cf_unqualified

    st.metric(label="From Commitment Form", value=len(cf_filtered))
    st.dataframe(
        cf_filtered.sort_values(["First Name", "Last Name"]).set_index(["First Name", "Last Name"]),
        use_container_width=True
    )

with col2:
    # Update metric
    if "ot_reason_filter" not in st.session_state:
        st.session_state["ot_reason_filter"] = "All"

    ot_reason_filter = st.selectbox(
        "Filter by Reason (OneTap)",
        options=["All"] + ot_unqualified["Reason"].unique().tolist(),
        key="ot_reason_filter"
    )

    if ot_reason_filter != "All":
        ot_filtered = ot_unqualified[ot_unqualified["Reason"] == ot_reason_filter]
    else:
        ot_filtered = ot_unqualified

    st.metric(label="From OneTap", value=len(ot_filtered))
    st.dataframe(
        ot_filtered.sort_values(["First Name", "Last Name"]).set_index(["First Name", "Last Name"]),
        use_container_width=True
    )