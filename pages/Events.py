#%% Imports
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

#%% Set Layout
st.set_page_config(
    "HUSTLE Report",
    layout="wide"
)

st.title("Events Report")

#%% Load and process data
attendance = pd.read_csv("outputs/onetap_attendance.csv").set_index(["Event", "Date"]).sort_values(
    by=["Date", "Event", "First Name", "Last Name"],
    ascending=[False, False, True, True]
)
attendance.reset_index(inplace=True)

#%% Filters
# Event filter with "All Events" as default
event_options = ["All Events"] + attendance["Event"].unique().tolist()
event_filter = st.selectbox("Select Event:", event_options, index=0)

# Filter events conditionally
filtered_events = attendance if event_filter == "All Events" else attendance[attendance["Event"] == event_filter]

# Date filter with "Select All Dates" option integrated
date_options = ["Select All Dates"] + filtered_events["Date"].unique().tolist()
date_filter = st.multiselect("Select Date(s):", date_options, default="Select All Dates")

# Filter dates conditionally
filtered_dates = (
    filtered_events if "Select All Dates" in date_filter else filtered_events[filtered_events["Date"].isin(date_filter)]
)

# Filtered data
filtered_data = filtered_dates

#%% Display Total Check-Ins, Unique Check-Ins, and Average Attendance
if not filtered_data.empty:
    # Total check-ins
    total_checkins = len(filtered_data)
    
    # Unique check-ins based on differences in First Name, Last Name, or A-Number
    if {"First Name", "Last Name", "A-Number"}.issubset(filtered_data.columns):
        unique_checkins = len(filtered_data.drop_duplicates(subset=["First Name", "Last Name", "A-Number"]))
    else:
        unique_checkins = "N/A"  # Handle case if required columns are missing

    # Average attendance
    average_attendance = filtered_data.groupby("Date").size().mean()

    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Check-Ins", total_checkins)
    with col2:
        st.metric("Unique Profiles", unique_checkins)
    with col3:
        st.metric("Average Attendance", round(average_attendance, 2))
else:
    # Display no data metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Check-Ins", "No Data")
    with col2:
        st.metric("Unique Check-Ins", "No Data")
    with col3:
        st.metric("Average Attendance", "No Data")

#%% Line Chart of Attendance Over Time
st.header("Attendance Over Time")

if event_filter != "All Events" and not filtered_data.empty:
    # Group by date and count attendees
    attendance_over_time = filtered_data.groupby("Date").size().reset_index(name="Attendees")
    attendance_over_time["Date"] = pd.to_datetime(attendance_over_time["Date"])  # Ensure Date is datetime
    
    # Create a line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=attendance_over_time["Date"],
        y=attendance_over_time["Attendees"],
        mode="lines+markers+text",  # Add text mode
        line=dict(color="#165A7D", width=2),  # Updated line color
        text=attendance_over_time["Attendees"],  # Add value labels
        textposition="top center",  # Position labels
        showlegend=False  # Hide the legend
    ))
    
    # Update layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Attendees",
        yaxis=dict(range=[0, attendance_over_time["Attendees"].max() + 5]),  # Adjust y-axis to start at 0
        xaxis=dict(
            tickformat="%b %d",  # Format as abbreviated month and day, omitting the year
            tickvals=attendance_over_time["Date"],  # Use actual dates for tick values
            ticktext=attendance_over_time["Date"].dt.strftime("%b %d")  # Display formatted date strings
        )
    )
    
    st.plotly_chart(fig)
elif event_filter == "All Events":
    st.write("Please select a specific event to view the attendance graph.")
else:
    st.write("No data available for the selected filters.")

#%% Display Dynamic Header
if event_filter == "All Events" and "Select All Dates" in date_filter:
    st.header("Attendance for All Events on All Dates")
elif event_filter == "All Events":
    st.header(f"Attendance for All Events on {', '.join(date_filter)}")
elif "Select All Dates" in date_filter:
    st.header(f"Attendance for {event_filter} on All Dates")
else:
    st.header(f"Attendance for {event_filter} on {', '.join(date_filter)}")

#%% Display Data
st.dataframe(
    filtered_data,
    use_container_width=True,  # Ensures the DataFrame takes up the full container width
    hide_index=True,
    column_config={
        "Event": st.column_config.Column(width="medium"),
        "Date": st.column_config.Column(width="medium"),
        "First Name": st.column_config.Column(width="medium"),
        "Last Name": st.column_config.Column(width="medium"),
    }
)