import plotly.express as px
from datetime import timedelta, datetime
import streamlit as st
import pandas as pd
import json
import os
from tabs import earnings_tab, payments_tab, credits_tab, investiments_tab

st.set_page_config(page_title="Finance App", page_icon="👌", layout="wide")

categoty_file = 'categories.json'

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": []
    }

if os.path.exists(categoty_file):
    with open(categoty_file, 'r') as f:
        st.session_state.categories = json.load(f)

def save_categories():
    with open(categoty_file, 'w') as f:
        json.dump(st.session_state.categories, f)

def categorize_transactions(df):
    df['Category'] = 'Uncategorized'

    for category, keywords in st.session_state.categories.items():
        
        if category == 'Uncategorized' or not keywords:
            continue

        lowered_keywords = [keyword.lower().strip() for keyword in keywords]

        for index, row in df.iterrows():
            details = row['Details'].lower().strip()

            if details in lowered_keywords:
                df.at[index, 'Category'] = category

    return df

def load_transactions(file):
    try:

        df = pd.read_csv(file, sep=";")
        df.columns = [col.strip() for col in df.columns]

        df['Amount'] = df['Amount'].str.replace('.', '')
        df['Amount'] = df['Amount'].str.replace(',', '.').astype(float)

        df['Balance'] = df['Balance'].str.replace('.', '')
        df['Balance'] = df['Balance'].str.replace(',', '.').astype(float)
        
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")


        # df.to_json('teste.json')
        return df
        # return categorize_transactions(df)
    
    except Exception as e:
        st.error(f"Error while processing file: {str(e)}")
        return None

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()

    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True
    
    return False

def main():
    st.title('Finance Dashboard')

    # uploaded_file = st.file_uploader('Upload your transaction csv file', type=['csv'])
    uploaded_file = None
    
    if uploaded_file is None:
        uploaded_file = 'data/extrato.csv'

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

        if df is not None:
            debits_df = df[df['Amount'] < 0].copy()
            credits_df = df[df['Amount'] > 0].copy()

            earnings_df = credits_df[credits_df['Historic'] == 'Crédito Evento B3'][['Date', 'Description', 'Amount']]
            earnings_df['Description'] = earnings_df['Description'].str[-7:].str.strip().str.upper()
            earnings_df = earnings_df.rename(columns={'Description': 'Asset'})

            total_payments = credits_df['Amount'].sum()
            total_dividends = earnings_df['Amount'].sum()

            first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            this_month_earnings = earnings_df[earnings_df['Date'] >= first_day_of_month]['Amount'].sum()
            
            col1, col2 = st.columns(2)

            col1.metric('Total incoming', f'{total_payments:,.2f} BRL')
            col2.metric(
                'Total dividends (12M)',
                f'{total_dividends:,.2f} BRL',
                delta=f'{this_month_earnings:.2f} this month'
            )
            

            all_tab, credit_tab, debit_tab, earnings, investiments = st.tabs(['Todas as transações', 'Entradas (Créditos)', 'Saídas (Débitos)', 'Proventos', 'Investimentos'])

            default_column_configs = {
                                'Date': st.column_config.DateColumn('Date', format='DD/MM/YYYY'),
                                "Description": st.column_config.TextColumn('Description', width='large'),
                                "Amount": st.column_config.NumberColumn('Amount', format='%.2f BRL', ),
                                'Balance': st.column_config.NumberColumn('Balance', format='%.2f BRL'),
            }
            with all_tab:
                st.dataframe(df, 
                            height=600,
                            column_config=default_column_configs,
                            use_container_width=True,
                            hide_index=True)
                
                grouped_df = df.groupby('Historic')['Amount'].sum().reset_index()
                st.dataframe(grouped_df,
                            column_config=default_column_configs,
                            use_container_width=True,
                            hide_index=True)

            with credit_tab:
                credits_tab.run(credits_df)
        
            with debit_tab:
                payments_tab.run(debits_df)
              
            with earnings:
                earnings_tab.run(earnings_df)
 
            with investiments:
                investiments_tab.run()
 
main()