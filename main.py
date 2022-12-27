import pandas as pd
import streamlit as st

# Helpers for urls and getting authenticated clients and transports
from specklepy.api.wrapper import StreamWrapper

# Entrypoint for interacting with SpeckleServer GraphQL API
from specklepy.api.client import SpeckleClient

# Receive object from a transport given the obj id
from specklepy.api import operations

# Page config
st.set_page_config(
    page_title="Schedule App",
    page_icon="📚"
)

# Containers
header = st.container()
input = st.container()
data = st.container()

# Header
with header:
    st.title("📚 Schedule App")
    st.info(
        "Linked Schedules from Revit Data"
    )

# Inputs
with input:
    st.subheader("Inputs")
    commit_url = st.text_input(
        "Commit URL",
        "https://speckle.xyz/streams/e6c04f6c1c/commits/c230834154",
    )

# Wrapper
# helpers for urls and getting authenticated clients and transports
wrapper = StreamWrapper(commit_url)
# get an authenticated SpeckleClient if there is a local account for the server
client = wrapper.get_client()
# get an authenticated ServerTransport if there is a local account for the server
transport = wrapper.get_transport()

# Commit
# get a commit given a stream and commit id
commit = client.commit.get(wrapper.stream_id, wrapper.commit_id)
# get obj id from commit
obj_id = commit.referencedObject
# receive objects from commit
commit_data = operations.receive(obj_id, transport)

# Category dropdown
with input:
    selected_category = st.selectbox(
        "Select Category", commit_data.get_dynamic_member_names()
    )

# # Parameters
# parameters = commit_data[selected_category][0]["parameters"].get_dynamic_memeber_names()

# Get Parameter Names
def get_parameter_names(commit_data, selected_category):
    parameters = commit_data[selected_category][0][
        "parameters"
    ].get_dynamic_member_names()
    parameter_names = []
    for parameter in parameters:
        parameter_names.append(
            commit_data[selected_category][0]["parameters"][parameter]["name"]
        )
    parameter_names = sorted(parameter_names)
    return parameter_names

# Parameter selection input
# multi-select is included to prevent rerunning on new parameter selection
with input:
    form = st.form("parameter input")
    with form:
        selected_parameters = st.multiselect(
            "Select Parameters", get_parameter_names(commit_data, selected_category)
        )
        run_button = st.form_submit_button("RUN")

# Objects from selected category
category_elements = commit_data[selected_category]

# Get parameter value from parameter name
def get_parameter_by_name(element, parameter_name, dict):
    for parameter in parameters:
        key = element["parameters"][parameter]["name"]
        if key == parameter_name:
            dict[key] = element["parameters"][parameter]["value"]
    
    return dict

# Loop through each object in selected_category
with data:
    # This will be output data
    result_data = []
    # Run only when the run_button is clicked
    if run_button:
        for element in category_elements:
            dict = {}
            for s_param in selected_parameters:
                get_parameter_by_name(element, s_param, dict)
            result_data.append(dict)
    # Convert result_data to Pandas DataFrame
    result_DF = pd.DataFrame.from_dict(result_data)
    # Show Data
    st.dataframe(result_DF)
    # DataFrame to CSV
    result_CSV = result_DF.to_csv().encode("utf-8")
        # Download button
    st.download_button(
                "Download CSV",
                result_CSV,
                f"{wrapper.commit_id}.csv",
                mime="text/csv",
    )
