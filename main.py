import plotly.express as px
from datetime import timedelta, datetime
import streamlit as st
import pandas as pd
import json
import os

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


        df['Valor'] = df['Valor'].str.replace('.', '')
        df['Valor'] = df['Valor'].str.replace(',', '.').astype(float)

        df['Saldo'] = df['Saldo'].str.replace('.', '')
        df['Saldo'] = df['Saldo'].str.replace(',', '.').astype(float)
        
        df['Data Lançamento'] = pd.to_datetime(df['Data Lançamento'], format="%d/%m/%Y")

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

    uploaded_file = st.file_uploader('Upload your transaction csv file', type=['csv'])
    
    if uploaded_file is None:
        uploaded_file = 'extrato.csv'


    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

        if df is not None:
            debits_df = df[df['Valor'] < 0].copy()
            credits_df = df[df['Valor'] > 0].copy()

            # st.session_state.debits_df = debits_df.copy()
        
            all_tab, credit_tab, debit_tab = st.tabs(['Todas as transações', 'Entradas (Créditos)', 'Saídas (Débitos)'])

            default_column_configs = {
                                'Data Lançamento': st.column_config.DateColumn('Data Lançamento', format='DD/MM/YYYY'),
                                "Valor": st.column_config.NumberColumn('Valor', format='%.2f BRL'),
                                'Saldo': st.column_config.NumberColumn('Saldo', format='%.2f BRL'),
                            }
            with all_tab:
                st.dataframe(df, 
                            column_config=default_column_configs,
                            use_container_width=True,
                            hide_index=True)
                


                # new_category = st.text_input('New category name')
                # add_button = st.button('Add Category')

                # if add_button and new_category:
                #     if new_category not in st.session_state.categories:
                #         st.session_state.categories[new_category] = []
                #         save_categories()
                #         st.rerun()

                # st.subheader("Your expenses")
                # edited_df = st.data_editor(st.session_state.debits_df[['Data Lançamento', 'Descrição', 'Valor'
                #                                                     #    , 'Category'
                #                                                        ]],
                #                            column_config={
                #                                'Data Lançamento': st.column_config.DateColumn('Data Lançamento', format='DD/MM/YYYY'),
                #                                'Valor': st.column_config.NumberColumn('Valor', format="%.2f BRL"),
                #                             #    'Category': st.column_config.SelectboxColumn(
                #                             #        'Category',
                #                             #        options=list(st.session_state.categories.keys())
                #                             #    )
                #                            },
                #                            hide_index=True,
                #                            use_container_width=True,
                #                            key="category_editor"
                #                            )
                
                # save_button = st.button('Apply Changes', type="primary")
                # if save_button:
                #     for index, row in edited_df.iterrows():
                #         new_category = row['Category']

                #         if new_category == st.session_state.debits_df.at[index, 'Category']:
                #             continue

                #         details = row['Details']
                #         st.session_state.debits_df.at[index, 'Category'] = new_category
                #         add_keyword_to_category(new_category, details)

                # # st.write(debits_df)
                # st.subheader('Expense Summary')
                # category_totals = (st.session_state.debits_df
                #                     .groupby('Category')
                #                     .agg(
                #                         Amount=('Valor', 'sum'),
                #                         Count=('Amount', 'count')
                #                     )
                #                     .reset_index()
                #                     )
                # category_totals = category_totals.sort_values('Amount', ascending=False)

                # st.dataframe(
                #     category_totals,
                #     column_config={
                #         "Amount": st.column_config.NumberColumn('Amount',format="%.2f BRL")
                #     },
                #     use_container_width=True,
                #     hide_index=True              
                #     )

                # fig = px.pie(
                #     category_totals,
                #     values="Amount",
                #     names="Category",
                #     title="Expenses by category"
                # )
                # st.plotly_chart(fig, use_container_width=True)
            with credit_tab:

                st.subheader('Incoming Summary')

                total_payments = credits_df['Valor'].sum()

                total_dividends = credits_df[credits_df['Descrição'].str.contains('Credito Evento B3')]['Valor'].sum()

                last_month_date = datetime.now() - timedelta(days=30)

                last_month_dividents = credits_df[
                    (credits_df['Descrição'].str.contains('Credito Evento B3'))
                    & (credits_df['Data Lançamento'] >= last_month_date)
                    ]['Valor'].sum()
                
                col1, col2 = st.columns(2)
                col1.metric('Total incoming', f'{total_payments:,.2f} BRL')
                col2.metric('Total dividends (12M)', f'{total_dividends:,.2f} BRL', delta=last_month_dividents)

                st.dataframe(credits_df, 
                            column_config=default_column_configs,
                            use_container_width=True,
                            hide_index=True)

            with debit_tab:

                st.subheader('Payments Summary')

                total_payments = debits_df['Valor'].sum()

                st.metric('Total payments', f'{total_payments:,.2f} BRL')

                st.dataframe(debits_df, 
                            column_config=default_column_configs,
                            use_container_width=True,
                            hide_index=True)




main()