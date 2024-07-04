import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

import vl_convert as vlc

from pathlib import Path
from typing import List

# set locale to pt-BR
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')

# disable logging
import logging
logging.getLogger().addHandler(logging.NullHandler())

# model
@st.cache_data
def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    # set date variables to right format
    for column in df.columns:
        if column.endswith(('_date', '_timestamp')):
            df[column] = pd.to_datetime(df[column])

    return df

@st.cache_data
def extract_purchase_dates(data: pd.DataFrame) -> pd.Series:
    timestamps = data.order_purchase_timestamp.dt.to_period('M').copy()
    timestamps = timestamps.sort_values()
    timestamps = timestamps.dt.strftime('%B %Y')
    timestamps = timestamps.drop_duplicates()

    return timestamps

def extract_orders_delivery_stats(data: pd.DataFrame) -> pd.DataFrame:
    # load orders delivery infos
    order_delivery_info = data[
        ['order_id', 'order_status', 'order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
    ].copy()
    order_delivery_info.drop_duplicates(subset=['order_id'], inplace=True)
    order_delivery_info.drop('order_id', axis=1, inplace=True)
    order_delivery_info.columns = ['status', 'purchase_date', 'delivery_date', 'estimated_date']

    return order_delivery_info

@st.cache_data
def extract_orders_volume(data: pd.DataFrame) -> pd.DataFrame:
    # count orders per period
    orders_volume = pd.DataFrame({ 'volume' : range(data.shape[0]) })
    orders_volume = orders_volume.groupby([data.order_purchase_timestamp.dt.strftime('%m %Y')]).size().reset_index()
    orders_volume.rename({ 'order_purchase_timestamp' : 'date', 0 : 'volume' }, axis=1, inplace=True)

    orders_volume.date = pd.to_datetime(orders_volume.date, format='%m %Y') + pd.offsets.MonthEnd(0)

    return orders_volume

@st.cache_data
def extract_order_delivery_details(data: pd.DataFrame, selected_period: str) -> List[int]:
    orders_volume = extract_orders_volume(data)
    orders_stats = extract_orders_delivery_stats(data)

    if selected_period != 'todo':
        orders_volume = orders_volume[orders_volume.date.dt.strftime('%B %Y') == selected_period]
        orders_stats = orders_stats[orders_stats.purchase_date.dt.strftime('%B %Y') == selected_period]

    orders_count = 0
    orders_pendent = 0
    orders_delivered = 0
    orders_late = 0
    orders_avarage_late_delivery_time = 0

    deliverd_orders = orders_stats[orders_stats.status == 'delivered']
    late_orders = orders_stats[orders_stats.delivery_date.dt.to_period('D') > orders_stats.estimated_date.dt.to_period('D')]

    orders_count = orders_volume.volume.sum()
    orders_delivered = deliverd_orders.shape[0]
    orders_pendent = orders_count - orders_delivered
    orders_late = late_orders.shape[0]
    orders_avarage_late_delivery_time = (late_orders.delivery_date - late_orders.estimated_date).dt.days.mean()

    if orders_avarage_late_delivery_time is np.nan:
        orders_avarage_late_delivery_time = 0
    else:
        orders_avarage_late_delivery_time = int(orders_avarage_late_delivery_time)

    return [orders_count, orders_pendent, orders_delivered, orders_late, orders_avarage_late_delivery_time]

@st.cache_data
def extract_scores_mean(data: pd.DataFrame, selected_period: str) -> float:
    orders = data
    if selected_period != 'todo':
        orders=orders[orders.order_purchase_timestamp.dt.strftime('%B %Y') == selected_period]

    return orders.review_score.mean()

@st.cache_data
def count_reviews_topic(data: pd.DataFrame, selected_period: str) -> List[str]:
    orders = data
    if selected_period != 'todo':
        orders=orders[orders.order_purchase_timestamp.dt.strftime('%B %Y') == selected_period]

    topics = orders.complaint.to_list()

    product_topic_count = topics.count('Product')
    delivery_topic_count = topics.count('Delivery')

    return product_topic_count, delivery_topic_count

# view
def plot_order_volume(data: pd.DataFrame, selected_period: str):
    orders_volume = extract_orders_volume(data)

    # line plot
    chart = alt.Chart(orders_volume).mark_line(
        strokeWidth=6,
    ).encode(
        x=alt.X('date:T', axis=alt.Axis(title='', format='%B %Y', labelFontSize=13)),
        y=alt.Y('volume:Q', axis=alt.Axis(title='Quantidade de pedidos', titleFontSize=18, labelFontSize=13)),
        tooltip=[
            alt.Tooltip('date:T', title='Data', format='%B %Y'),
            alt.Tooltip('volume:Q', title='Volume')
        ]
    ).interactive(bind_y=False)

    present_chart = chart

    if selected_period != 'todo':
        selected_df = orders_volume[orders_volume.date.dt.strftime('%B %Y') == selected_period].copy()

        selection_rule = alt.Chart(selected_df).mark_rule(
            color='#F97',
            strokeWidth=5,
            opacity=1.0
        ).encode(
            x=alt.X('date:T', axis=alt.Axis(title='', format='%B %Y', domain=False)),
            tooltip=[
                alt.Tooltip('date:T', title='Data', format='%B %Y')
            ]
        )

        selection_point = alt.Chart(selected_df).mark_circle(
            color='#F97',
            opacity=1.0,
            size=250,
        ).encode(
            x=alt.X('date:T', axis=alt.Axis(title='', format='%B %Y')),
            y=alt.Y('volume:Q', axis=alt.Axis(title='')),
            tooltip=[
                alt.Tooltip('date:T', title='Data', format='%B %Y'),
                alt.Tooltip('volume:Q', title='Volume')
            ]
        )

        present_chart = chart + selection_rule + selection_point

    present_chart['usermeta'] = {
        "embedOptions": {
            "formatLocale": vlc.get_format_locale('pt-BR'),
            "timeFormatLocale": vlc.get_time_format_locale('pt-BR')
        }
    }

    st.altair_chart(present_chart, use_container_width=True)

def date_selection(data: pd.DataFrame):
    dates = extract_purchase_dates(data)

    selection = st.selectbox(
        "Período",
        tuple(['Todo'] + list(map(lambda date: date.capitalize(), dates.to_list()))),
        0
    )

    return selection.lower()

def format_value_to_readable_format(value: int) -> str:
    if value < 10**3:
        return str(value)
    
    if value < 10**6:
        return f'{value / 10**3:.1f} mil'
    
    return f'{value / 10**6:.1f} mi'

def show_metrics(data: pd.DataFrame, selected_period: str):

    # extract metrics
    [
        orders_count,
        orders_pendent,
        orders_delivered,
        orders_late,
        orders_avarage_late_delivery_time
    ] = extract_order_delivery_details(data, selected_period)

    # format values
    orders_count = format_value_to_readable_format(orders_count)
    orders_pendent = format_value_to_readable_format(orders_pendent)
    orders_delivered = format_value_to_readable_format(orders_delivered)
    orders_late = format_value_to_readable_format(orders_late)
    orders_avarage_late_delivery_time = format_value_to_readable_format(orders_avarage_late_delivery_time) + ' dias'

    # display metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(':blue[Pedidos]', value=orders_count)
    col2.metric(':blue[Pendentes]', value=orders_pendent)
    col3.metric(':blue[Entregues]', value=orders_delivered)
    col4.metric(':blue[Atrasados]', value=orders_late)
    col5.metric(':blue[Média de atraso]', value=orders_avarage_late_delivery_time)

def show_review_analysis_panel(data: pd.DataFrame, selected_period: str):
    mean_score = extract_scores_mean(data, selected_period)
    satisfaction_percentage = 100 * (mean_score - 1) / 4

    product_reclamation, delivery_reclamation = count_reviews_topic(data, selected_period)

    st.markdown('<h2 style=\'text-align: center; white-space: nowrap; font-size: 2vw;\'>Satisfação dos Compradores</h2>', unsafe_allow_html=True)

    st.markdown('''<h1 style='text-align: center;
                white-space: nowrap;
                font-size: 3.2vw;
                '>  😔 🤨 😐 😌 😁  </h1>''', unsafe_allow_html=True)
    
    st.progress(int(satisfaction_percentage))
    st.markdown(f'<h3 style=\'text-align: center;\'>{satisfaction_percentage:.1f}%</h3>', unsafe_allow_html=True)

    st.markdown('#')

    c1, c2 = st.columns(2)
    c1.metric('Reclamação de produtos', product_reclamation)
    c2.metric('Reclamação de entregas', delivery_reclamation)

def main_page():
    st.set_page_config(
        page_title='E-Commerce Dashboard',
        layout='wide',
        page_icon='📶'
    )

    st.markdown('# 📶E-Commerce Brasileiro')

    data = load_dataset(Path('artifacts/data_preprocessing/data.csv'))

    selected_period = date_selection(data)
    st.markdown('#####')

    col1, col2 = st.columns([0.7, 0.3], gap='large')
    with col1:
        show_metrics(data, selected_period)

        st.markdown('###')

        plot_order_volume(data, selected_period)

    with col2:
        show_review_analysis_panel(data, selected_period)

    # share data font
    st.caption('**Fonte:** dados gratuitos da Olist obtidos neste link https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce')

main_page()