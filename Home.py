import streamlit as st

st.set_page_config(
    page_title="HUSTLE Report",
    layout="wide"
)

st.sidebar.success("Select Page")

st.title("Home")

# Define the content for each letter
hustle_details = {
    "H": ("Help", """
        <ul style='text-align: left;'>
            <li>Volunteer at ASC</li>
            <li>Volunteer at HackUSU</li>
        </ul>
    """),
    "U": ("Unite", """
        <ul style='text-align: left;'>
            <li>Innovation Labs</li>
        </ul>
    """),
    "S": ("Share", """
        <ul style='text-align: left;'>
            <li>Five-Slide Friday</li>
            <li>TICKET Competition</li>
        </ul>
    """),
    "T": ("Teach", """
        <ul style='text-align: left;'>
            <li>Teaching Assistant</li>
            <li>Lead Cohort Project</li>
        </ul>
    """),
    "L": ("Learn", """
        <ul style='text-align: left;'>
            <li>Open Forums</li>
            <li>PyData Meetups</li>
        </ul>
    """),
    "E": ("Engage", """
        <ul style='text-align: left;'>
            <li>Cohort Project</li>
            <li>Competition</li>
            <li>Presentation</li>
        </ul>
    """)
}

# Create columns for each letter
columns = st.columns(len(hustle_details))

# Add content to each column
for col, (letter, (subheader, description)) in zip(columns, hustle_details.items()):
    col.markdown(
        f"""
        <div style='text-align: center; border: 2px solid #165A7D; background-color: #165A7D; color: white; padding: 20px; margin: 10px; border-radius: 10px;'>
            <h1 style='margin: 0;'>{letter}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    col.markdown(f"<h3 style='text-align: center;'>{subheader}</h3>", unsafe_allow_html=True)
    col.markdown(f"{description}", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

st.header("Mission") 

st.markdown(
    """
    1. Empower all students through **immersive, hands-on, real-world** challenges and experiences.
    2. Provide incredible **value to our external partners** and serve as an economic driver for the region.
    3. Develop cross-disciplinary teams that address **complex analytical problems** and create **technological innovations**.
    """
)
st.markdown("<hr>", unsafe_allow_html=True)

#%% Point Values
st.header("Participation Values")

st.markdown("Five Slide Friday : 1")
st.markdown("Innovation Lab : 1")
st.markdown("Open Forum : 2")
st.markdown("Student Showcase : 2")
st.markdown("TICKET Competition : 1")
st.markdown("Five Slide Friday : 1")
st.markdown("Teaching Assistant : 5")