#%% ----- Imports ------
import pandas as pd
from datetime import date
from sklearn.preprocessing import MultiLabelBinarizer

#%% ----- Process Commitment Form Data -----
cf = pd.read_csv("inputs/commitment_form.csv")[["Name","A-Number","Major/Program","Expected Graduation Date"]]

# Split First and Last Names
cf[["First Name", "Last Name"]] = cf["Name"].str.title().str.split(" ", n=1, expand=True)

# Simplify Column names
cf.columns = cf.columns.str.lower().str.replace(" ", "_").str.replace("/","_").str.replace("expected_","")
cf = cf.drop(columns="name").set_index(["first_name","last_name"]).reset_index()
cf["a-number"] = cf["a-number"].str.upper()

# Graduation Dates
cf["graduation_date"] = pd.to_datetime(cf["graduation_date"], errors="coerce").dt.floor("D")
cf.loc[cf["graduation_date"].dt.year < 2023, "graduation_date"] = pd.NaT

cf["graduation_date"] = cf["graduation_date"].apply(lambda x: 
    pd.Timestamp(f"{x.year}-04-01").date() if x.month in [2, 3, 4, 5, 6] else 
    pd.Timestamp(f"{x.year}-08-01").date() if x.month in [7, 8, 9] else 
    pd.Timestamp(f"{x.year}-12-01").date() if x.month in [10, 11, 12, 1] else x
)

# Binarize Major/Program
majors = (
    cf["major_program"]
    .str.title().str.strip().str.split(", ")
    .apply(lambda x: [item.replace("Mdata", "MDATA").replace("Mmis", "MMIS").replace("Ms Statistics", "MS Statistics") for item in x])
)
cf["major_program"] = majors

#%% ----- Process OneTap Data -----
ot = pd.read_excel("inputs/one_tap.xlsx")[["name","A-Number","listName","checkedIn","checkInDate"]]

# Filter to Verified Attendance
ot = ot[ot["checkedIn"] == "Yes"]
ot = ot.drop(columns="checkedIn")

# Rename Columns
ot.columns = ["name","a-number","event","date"]

# Change Timestamp to date
ot["date"] = pd.to_datetime(ot["date"].str[0:10], format="%Y-%m-%d")

# Split Name & Fill Null A-Number
ot[["first_name","last_name"]] = ot["name"].str.title().str.split(" ", n=1, expand=True)
ot = ot.drop(columns="name").set_index(["first_name","last_name"]).reset_index()
ot["a-number"] = ot["a-number"].str.upper().fillna("Unknown")

# Get Rid of Duplicates
ot.drop_duplicates(inplace=True)

# Clean Event Names
event_map = {
    "Innovation Lab":"Innovation Lab",
    "Open Forum":"Open Forum",
    "Five-Slide Friday":"Five-Slide Friday",
    "Student Showcase (Attendee)":"Showcase (Attendee)",
    "Student Showcase (Presenter)":"Showcase (Presenter)"
}
ot['event'] = ot['event'].apply(lambda x: next((v for k, v in event_map.items() if k in x), x))

# Pivot to Find Event Counts
ot1 = ot.pivot_table(index=["first_name","last_name","a-number"],
                    columns="event",
                    values="date",
                    aggfunc="count",
                    fill_value=0).reset_index()

ot1.columns.name = None

#%% Event Counts Table
event_counts = cf.merge(ot1.drop(columns=["first_name","last_name"]), on="a-number", how="left")
event_counts.iloc[:, 5:] = event_counts.iloc[:, 5:].fillna(0)

event_counts["Student Showcase"] = (
    (event_counts["Showcase (Attendee)"] == 1) | (event_counts["Showcase (Presenter)"] == 1)
).astype(int)
event_counts.drop(columns=["Showcase (Attendee)", "Showcase (Presenter)"], inplace=True)

# Map Points to Events
points = {
    "Five-Slide Friday":1,
    "Innovation Lab":1,
    "Open Forum":2,
    "Student Showcase":2,
    "TICKET Competition":2,
}

# Calculate total points
event_counts['total'] = sum(
    event_counts[event] * points[event] 
    for event in points if event in event_counts.columns
)

event_counts1 = event_counts[(event_counts["total"] > 0) & (event_counts["last_name"].notnull())].sort_values(["total","first_name"], ascending=False).reset_index(drop=True)
event_counts1.columns = event_counts1.columns.str.replace("_", " ").str.title()
event_counts1.rename(columns={"Major Program":"Major OR Program"}, inplace=True)

#%% ----- In Commitment Form Unqualified -----
cf_unqualified = event_counts[
    (event_counts["total"] == 0) | (event_counts["last_name"].isnull())
].reset_index(drop=True)

# Strip whitespace from first and last names in both datasets
cf_unqualified["first_name"] = cf_unqualified["first_name"].str.strip()
cf_unqualified["last_name"] = cf_unqualified["last_name"].str.strip()
ot1["first_name"] = ot1["first_name"].str.strip()
ot1["last_name"] = ot1["last_name"].str.strip()

# Check if first name and last name appear in ot1
ot_names = set(ot1[["first_name", "last_name"]].itertuples(index=False, name=None))

# Update the reason column with multiple conditions
cf_unqualified["reason"] = cf_unqualified.apply(
    lambda row: "no last name" if pd.isna(row["last_name"])
    else "no a-number in onetap" if (row["first_name"], row["last_name"]) in ot_names
    else "0 hustle points",
    axis=1
)

# Format column names
cf_unqualified.columns = cf_unqualified.columns.str.replace("_", " ").str.title()
cf_unqualified.rename(columns={"Major Program": "Major OR Program"}, inplace=True)
cf_unqualified = cf_unqualified.iloc[:, list(range(5)) + [-1]]

#%% ----- In OneTap Unqualified -----
ot_unqualified = ot1[~ot1["a-number"].isin(cf["a-number"])].reset_index(drop=True).iloc[:, :3]
ot_unqualified["reason"] = ot_unqualified["a-number"].apply(
    lambda x: "no a-number in onetap" if x == "Unknown" else "a-number not found in commitment form"
)
ot_unqualified.columns = ot_unqualified.columns.str.replace("_", " ").str.title()

#%% Get List of Events for Each Student in Report
student_events = ot[ot["a-number"].isin(event_counts1["A-Number"])]
student_events.columns = student_events.columns.str.replace("_", " ").str.title()

#%% ----- TA Data (Once I Have A-Numbers) -----

#%% ----- Export Data -----
event_counts1.to_csv("outputs/event_counts.csv", index=False)
cf_unqualified.to_csv("outputs/cf_unqualified.csv", index=False)
ot_unqualified.to_csv("outputs/ot_unqualified.csv", index=False)
student_events.to_csv("outputs/student_events.csv", index=False)

ot.columns = ot.columns.str.replace("_", " ").str.title()
ot.to_csv("outputs/onetap_attendance.csv", index=False)
# %%
