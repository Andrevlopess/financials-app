import pandas as pd
import streamlit as st
from utils.helpers import default_column_configs

def run(credits_df):
     st.subheader('Incoming Summary')

     st.dataframe(credits_df, 
                 column_config=default_column_configs,
                 use_container_width=True,
                 hide_index=True)