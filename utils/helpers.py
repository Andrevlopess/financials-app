import streamlit as st

default_column_configs = {
    'Date': st.column_config.DateColumn('Date', format='DD/MM/YYYY'),
    "Description": st.column_config.TextColumn('Description', width='large'),
    "Amount": st.column_config.NumberColumn('Amount', format='%.2f BRL', ),
    'Balance': st.column_config.NumberColumn('Balance', format='%.2f BRL'),
}