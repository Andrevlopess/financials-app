import streamlit as st
import plotly.express as px
import pandas as pd
from utils.helpers import default_column_configs

def run(earnings_df: pd.DataFrame):
        
    st.subheader('Assets Transactions')
    # earnings_df['Asset'] = earnings_df['Description'].str[-7:].str.strip().str.upper()
    # earnings_df = earnings_df.iloc[:, [0,1,2,5,4,3]] 

    
    st.dataframe(earnings_df, column_config=default_column_configs)

    monthly_df = earnings_df.copy()
    monthly_df['Month'] = monthly_df['Date'].dt.to_period('M')

    monthly_grouped_df = monthly_df.groupby('Month')['Amount'].sum().reset_index().sort_values(by='Month', ascending=False)


    st.subheader('Montly Earnings')
    col1, col2 = st.columns([1,2])

    col1.dataframe(monthly_grouped_df, column_config=default_column_configs)

    monthly_grouped_df['Month'] = monthly_grouped_df['Month'].astype(str)

    fig = px.bar(monthly_grouped_df,
                    x='Month', y="Amount", text_auto='%.2f',
                title="Earnings by month")

    col2.plotly_chart(fig, use_container_width=True)

    # MONTY EARNINGS BY ASSET
    st.subheader('Montly Earnings By Asset') 

    asset_select = st.selectbox('Select an asset', monthly_df['Asset'].unique())

    monthly_asset_grouped_df = monthly_df[monthly_df['Asset'] == asset_select].groupby(['Month', 'Asset'])['Amount'].sum().reset_index()

    monthly_asset_grouped_df['Month'] = monthly_asset_grouped_df['Month'].astype(str)


    fig = px.bar(monthly_asset_grouped_df, x='Month', y='Amount', text_auto='%.2f', title=f"{asset_select} montly earnings by asset")
    st.plotly_chart(fig, use_container_width=True)

    # FII GROUP
    st.subheader('Assets Earnings')
    assets_df = earnings_df.groupby('Asset')['Amount'].sum().reset_index().sort_values('Amount', ascending=False)

    col1, col2 = st.columns([1,2])

    col1.dataframe(assets_df, column_config={  
                    "Asset": st.column_config.TextColumn('Asset'),
                    "Amount": st.column_config.NumberColumn('Amount', format='%.2f BRL' ),
                })

    fig = px.pie(assets_df,
                values='Amount', 
                names="Asset",
                title="Earnings by Asset")

    col2.plotly_chart(fig, use_container_width=True)