from collections import defaultdict
from pathlib import Path
# import time

from pandas import read_csv
from loguru import logger
import streamlit as st

from dana import get_or_create_dana

# from util import ANSWER_DICT


TITLE: str = 'Proactive Temperaure, Occupancy and Carbon Monitoring for HVAC Systems'

CWD_PATH: Path = Path(__file__).parent

DATA_FILE_PATH: Path = CWD_PATH / 'hvac_measurements.csv'

MONITORING_PROBLEMS: dict[str, str] = {
    'Temperature Fluctuation': 'identify any temperature fluctuation issue from the data, and recommend what to do',
    'Occupancy Monitoring': 'identify any Occupancy issue from the data, and recommend what to do',
    'CO / CO2 Sensing': 'analyze CO / CO2  data and identify any cleaning needs',
}

# ANSWER_MAP = {
#     'Temperature Fluctuation': 'ans1',
#     'Occupancy Monitoring': 'ans2',
#     'CO / CO2 Sensing': 'ans3',
# }

st.set_page_config(page_title=TITLE,
                   page_icon=None,
                   layout='wide',
                   initial_sidebar_state='auto',
                   menu_items=None)

st.title(body=TITLE, anchor=None, help=None)

st.image(str(CWD_PATH / 'hvac.png'))


st.dataframe(data=read_csv(DATA_FILE_PATH),
             width=None, height=None,
             use_container_width=False,
             hide_index=True,
             column_order=None,
             column_config=None,
             key=None,
             on_select='ignore',
             selection_mode='multi-row')


if 'dana_analyses' not in st.session_state:
    st.session_state.dana_analyses: defaultdict[str, str] = defaultdict(str)

for monitored_issue, problem in MONITORING_PROBLEMS.items():
    if st.button(label=f'_monitor_: {monitored_issue}',
                 on_click=None, args=None, kwargs=None,
                 type='primary',
                 disabled=False,
                 use_container_width=False):
        # Uncomment for demo to sleep for 35 seconds and reliably reveal pre-made answer
        # with st.spinner(text='_analyzing..._'):
        #     time.sleep(35)  # Wait for 4 seconds
        #     solution = ANSWER_DICT.get(ANSWER_MAP[monitored_issue], "No solution available for this issue.")  # Fetch from dictionary
        #     st.session_state.dana_analyses[monitored_issue] = solution

        with st.spinner(text='_analyzing..._'):
            logger.level('DEBUG')

            st.session_state.dana_analyses[monitored_issue]: str = \
                get_or_create_dana(use_semikong_lm=False).solve(problem=problem)

    if (solution := st.session_state.dana_analyses[monitored_issue]):
        st.markdown(body=solution.replace('$', r'\$'))
