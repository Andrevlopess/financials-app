import pandas as pd
import streamlit as st
from utils.helpers import default_column_configs

def run(debits_df):
    st.subheader('Payments Summary')

    total_payments = debits_df['Amount'].sum()

    st.metric('Total payments', f'{total_payments:,.2f} BRL')

    st.dataframe(debits_df, 
                column_config=default_column_configs,
                use_container_width=True,
                hide_index=True)