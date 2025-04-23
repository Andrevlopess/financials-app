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


        df['Value'] = df['Value'].str.replace('.', '')
        df['Value'] = df['Value'].str.replace(',', '.').astype(float)

        df['Balance'] = df['Balance'].str.replace('.', '')
        df['Balance'] = df['Balance'].str.replace(',', '.').astype(float)
        
        df['Data'] = pd.to_datetime(df['Data'], format="%d/%m/%Y")

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
        uploaded_file = 'extrato.csv'

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

        if df is not None:
            debits_df = df[df['Value'] < 0].copy()
            credits_df = df[df['Value'] > 0].copy()
            earnings_df = credits_df[credits_df['Description'].str.contains('Credito Evento B3')]

            earnings_df['Description'] = earnings_df['Description'].str.replace('"', '').str[-7:].str.strip()

            
        
            total_payments = credits_df['Value'].sum()

            total_dividends = credits_df[credits_df['Description'].str.contains('Credito Evento B3')]['Value'].sum()

            first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            this_month_earnings = earnings_df[earnings_df['Data'] >= first_day_of_month]['Value'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric('Total incoming', f'{total_payments:,.2f} BRL')
            col2.metric(
                'Total dividends (12M)',
                f'{total_dividends:,.2f} BRL',
                delta=f'{this_month_earnings:.2f} this month'
                )
            

            all_tab, credit_tab, debit_tab, earnings = st.tabs(['Todas as transações', 'Entradas (Créditos)', 'Saídas (Débitos)', 'Proventos'])

            default_column_configs = {
                                'Data': st.column_config.DateColumn('Data', format='DD/MM/YYYY'),
                                "Description": st.column_config.TextColumn('Description', width='large'),
                                "Value": st.column_config.NumberColumn('Value', format='%.2f BRL', ),
                                'Balance': st.column_config.NumberColumn('Balance', format='%.2f BRL'),
                            }
            with all_tab:
                st.dataframe(df, 
                            height=600,
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
                # edited_df = st.data_editor(st.session_state.debits_df[['Data', 'Description', 'Value'
                #                                                     #    , 'Category'
                #                                                        ]],
                #                            column_config={
                #                                'Data': st.column_config.DateColumn('Data', format='DD/MM/YYYY'),
                #                                'Value': st.column_config.NumberColumn('Value', format="%.2f BRL"),
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
                #                         Amount=('Value', 'sum'),
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


                st.dataframe(credits_df, 
                            column_config=default_column_configs,
                            use_container_width=True,
                            hide_index=True)
            with debit_tab:

                st.subheader('Payments Summary')

                total_payments = debits_df['Value'].sum()

                st.metric('Total payments', f'{total_payments:,.2f} BRL')

                st.dataframe(debits_df, 
                            column_config=default_column_configs,
                            use_container_width=True,
                            hide_index=True)
            with earnings:

                st.subheader('Assets Transactions')
                st.dataframe(earnings_df, column_config=default_column_configs)

                monthly_df = earnings_df.copy()
                monthly_df['Month'] = monthly_df['Data'].dt.to_period('M')

                monthly_df = monthly_df.groupby('Month')['Value'].sum().reset_index()


                st.subheader('Montly Earnings')
                col1, col2 = st.columns([1,2])

                col1.dataframe(monthly_df, column_config=default_column_configs)

                monthly_df['Month'] = monthly_df['Month'].astype(str)

                fig = px.bar(monthly_df,
                              x='Month', y="Value", text_auto='%.2f',
                            title="Earnings by month")

                col2.plotly_chart(fig, use_container_width=True)

                # FII GROUP
                st.subheader('Assets Earnings')
                assets_df = earnings_df.groupby('Description')['Value'].sum().reset_index()

                col1, col2 = st.columns([1,2])

                col1.dataframe(assets_df, column_config={  
                                "Description": st.column_config.TextColumn('Asset'),
                                "Value": st.column_config.NumberColumn('Value', format='%.2f BRL' ),
                            })

                fig = px.pie(assets_df,
                            values='Value', 
                            names="Description",
                            title="Earnings by Asset")

                col2.plotly_chart(fig, use_container_width=True)







main()