import streamlit as st
import pandas as pd

def load_transctions(path):
    df = pd.read_excel(path);

    df['Produto'] = df['Produto'].str.split('-').str[0]

    return df[df['Movimentação'] == 'Transferência - Liquidação']

def run():
    st.markdown('### Investimentos')

    investiments_df = load_transctions('data/b3.xlsx')

    assets_count_df = investiments_df.copy()
    assets_count_df.loc[assets_count_df['Entrada/Saída'] == 'Debito', 'Quantidade'] *= -1
    assets_count_df = assets_count_df.groupby('Produto').sum('Quantidade').reset_index()

    st.dataframe(assets_count_df)


    st.dataframe(investiments_df)


    