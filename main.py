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
        "<https://speckle.xyz/streams/71504ff93d/commits/9c9b8620e3>",
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

# Parameters
parameters = commit_data[selected_category][0]["parameters"].get_dynamic_memeber_names()
