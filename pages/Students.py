#%%
import streamlit as st
import pandas as pd
import plotly.express as px

#%% Layout
st.set_page_config(
    "HUSTLE Report",
    layout="wide"
)

st.title("Student HUSTLE Report")

#%% Totals Prep
event_counts = pd.read_csv("outputs/event_counts.csv").drop(columns="A-Number")
event_counts['Full Name'] = event_counts['First Name'] + ' ' + event_counts['Last Name']

#%% Multi-Select Filter
selected_students = st.multiselect(
    "Choose students",
    options=["All Students"] + event_counts['Full Name'].sort_values().tolist(),
    default=["All Students"]
)

if "All Students" in selected_students:
    filtered_event_counts = event_counts
else:
    filtered_event_counts = event_counts[event_counts['Full Name'].isin(selected_students)]

# Additional Filters: Max Graduation Date and Minimum Points
col1, col2 = st.columns(2)  # Ensure two columns are explicitly defined

# Filter by Max Graduation Date
with col1:
    max_grad_date = st.selectbox(
        "Graduates Before:",
        options=["All Dates"] + sorted(event_counts['Graduation Date'].dropna().unique().tolist()),
        index=0
    )

# Filter by Minimum Points
with col2:
    min_points = st.number_input(
        "Minimum Points",
        min_value=int(event_counts['Total'].min()),
        max_value=int(event_counts['Total'].max()),
        value=int(event_counts['Total'].min())
    )

# Apply Filters
if max_grad_date != "All Dates":
    filtered_event_counts = filtered_event_counts[filtered_event_counts['Graduation Date'] <= max_grad_date]

filtered_event_counts = filtered_event_counts[filtered_event_counts['Total'] >= min_points]

#%% Totals Section
st.header("Summary")

total_students = len(filtered_event_counts)
st.metric(label="Total Students in Report", value=total_students)

st.dataframe(
    filtered_event_counts.drop(columns="Full Name").set_index(["First Name", "Last Name", "Total"]),
    use_container_width=True
)

#%% Bar Chart Section
st.header("Point Distribution")
fig = px.histogram(
    filtered_event_counts,
    x="Total",
    nbins=10,
    color_discrete_sequence=["#165A7D"]
)
st.plotly_chart(fig)

#%% Events Section
st.header("Event Attendance")
events = pd.read_csv("outputs/student_events.csv")

# Filter Events by Selected Students
if "All Students" in selected_students:
    student_events = events
else:
    # Filter by first and last names from the filtered_event_counts
    selected_first_last_names = [(row['First Name'], row['Last Name']) for _, row in filtered_event_counts.iterrows()]
    student_events = events[events.set_index(['First Name', 'Last Name']).index.isin(selected_first_last_names)]

# Total Checkins
total_attended = len(student_events)
st.metric(label="Total Checkins", value=total_attended)

# Display the filtered Events DataFrame
st.dataframe(
    student_events,
    use_container_width=True,
    hide_index=True,
    column_config={
        "First Name": st.column_config.Column(width="medium"),
        "Last Name": st.column_config.Column(width="medium"),
        "Event": st.column_config.Column(width="medium"),
        "Date": st.column_config.Column(width="medium"),
    }
)
# %%