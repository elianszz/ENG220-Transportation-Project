import pandas as pd
import streamlit as st

# 1. Dataset representing transportation issues in Cuba, New Mexico
data = {
    'Issue Category': [
        'Wildlife Collisions',
        'Pavement & Potholes',
        'Freight / Heavy Truck Congestion',
        'Rural Transit Deficit',
        'Pedestrian & Bike Access',
        'Unpaved Rural Roads',
    ],
    'Severity Rating (1-10)': [9, 8, 7, 8, 6, 7],
    'Estimated Annual Incidents': [145, 320, 210, 85, 40, 190],
    'Primary Corridor / Location': [
        'US Highway 550 (MM 50–70)',
        'NM State Road 126',
        'US Highway 550 Downtown',
        'Cuba to Rio Rancho / Santa Fe routes',
        'Main Street (Downtown Cuba)',
        'County Road 11 & Rural Feeder Roads',
    ],
    'Status / Planned Fix': [
        'Proposed Wildlife Overpass & Fencing',
        'NMDOT Resurfacing Project',
        'Bypass Study / Intersection Upgrades',
        'Rio Metro Regional Transit Expansion',
        'ADA Sidewalk Improvements',
        'County Gravel Maintenance Program',
    ],
}

df = pd.DataFrame(data)

# 2. App Header
st.set_page_config(
    page_title='Cuba, NM Transportation Issues', page_icon='🚘'
)
st.title('🌵 Cuba, New Mexico – Transportation & Infrastructure Dashboard')
st.markdown("""
Cuba, NM faces unique rural transportation challenges. Situated along **US Highway 550**, 
it serves as a key freight corridor between Bernalillo and Farmington, leading to high truck volume, 
frequent wildlife crossings, and limited transit options for local residents.
""")

st.divider()

# 3. Sidebar Filters
st.sidebar.header('Filter Issues')
min_severity = st.sidebar.slider(
    'Minimum Severity Rating (1-10):',
    min_value=1,
    max_value=10,
    value=6,
    step=1,
)

filtered_df = df[df['Severity Rating (1-10)'] >= min_severity]

# 4. Raw Data View
st.subheader('📌 Transport Challenges Data')
st.dataframe(filtered_df, use_container_width=True)

# 5. Visualizations
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader('Incident Frequency by Issue')
    st.bar_chart(filtered_df.set_index('Issue Category')[
        'Estimated Annual Incidents'
    ])

with col2:
    st.subheader('Severity Comparison')
    st.bar_chart(filtered_df.set_index('Issue Category')[
        'Severity Rating (1-10)'
    ])

# 6. Detailed Issue Inspector
st.divider()
st.subheader('🔍 Key Problem Spotlight')
selected_issue = st.selectbox(
    'Select a problem area to inspect:', df['Issue Category']
)

issue_details = df[df['Issue Category'] == selected_issue].iloc[0]
st.info(f"""
**Location:** {issue_details['Primary Corridor / Location']}  
**Severity:** {issue_details['Severity Rating (1-10)']}/10  
**Estimated Annual Incidents:** {issue_details['Estimated Annual Incidents']}  
**Proposed Solution:** {issue_details['Status / Planned Fix']}
""")
