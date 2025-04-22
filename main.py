import streamlit as st
import pandas as pd
import plotly.express as px
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
        df = pd.read_csv(file)
        df.columns = [col.strip() for col in df.columns]
        df['Amount'] = df['Amount'].str.replace(',', '').astype(float)
        df['Date'] = pd.to_datetime(df['Date'], format="%d %b %Y")

        return categorize_transactions(df)
    
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
    

    if uploaded_file is not None:
        df = load_transactions(uploaded_file)

        if df is not None:
            debits_df = df[df['Debit/Credit'] == 'Debit'].copy()
            credits_df = df[df['Debit/Credit'] == 'Credit'].copy()

            st.session_state.debits_df = debits_df.copy()
        
            tab1, tab2 = st.tabs(['Expenses (Debits)', 'Payments (Credits)'])

            with tab1:
                new_category = st.text_input('New category name')
                add_button = st.button('Add Category')

                if add_button and new_category:
                    if new_category not in st.session_state.categories:
                        st.session_state.categories[new_category] = []
                        save_categories()
                        st.rerun()

                st.subheader("Your expenses")
                edited_df = st.data_editor(st.session_state.debits_df[['Date', 'Details', 'Amount', 'Category']],
                                           column_config={
                                               'Date': st.column_config.DateColumn('Date', format='DD/MM/YYYY'),
                                               'Amount': st.column_config.NumberColumn('Amount', format="%.2f BRL"),
                                               'Category': st.column_config.SelectboxColumn(
                                                   'Category',
                                                   options=list(st.session_state.categories.keys())
                                               )
                                           },
                                           hide_index=True,
                                           use_container_width=True,
                                           key="category_editor"
                                           )
                save_button = st.button('Apply Changes', type="primary")
                if save_button:
                    for index, row in edited_df.iterrows():
                        new_category = row['Category']

                        if new_category == st.session_state.debits_df.at[index, 'Category']:
                            continue

                        details = row['Details']
                        st.session_state.debits_df.at[index, 'Category'] = new_category
                        add_keyword_to_category(new_category, details)

                # st.write(debits_df)
                st.subheader('Expense Summary')
                category_totals = (st.session_state.debits_df
                                    .groupby('Category')
                                    .agg(
                                        Amount=('Amount', 'sum'),
                                        Count=('Amount', 'count')
                                    )
                                    .reset_index()
                                    )
                category_totals = category_totals.sort_values('Amount', ascending=False)

                st.dataframe(
                    category_totals,
                    column_config={
                        "Amount": st.column_config.NumberColumn('Amount',format="%.2f BRL")
                    },
                    use_container_width=True,
                    hide_index=True              
                    )

                fig = px.pie(
                    category_totals,
                    values="Amount",
                    names="Category",
                    title="Expenses by category"
                )
                st.plotly_chart(fig, use_container_width=True)
            with tab2:
                st.subheader('Payments Summary')

                total_payments = credits_df['Amount'].sum()

                st.metric('Total payments', f'{total_payments:,.2f} BRL')
                st.write(credits_df)




main()