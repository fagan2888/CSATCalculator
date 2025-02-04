'''
    File name: csat_calculator.py
    Author: Pan Wu (https://www.linkedin.com/in/panwu/)
    Date created: 4/27/2021
    Date last modified: 5/1/2021
    Python Version: 3.7
'''

import streamlit as st
import streamlit.components.v1 as components

import numpy as np
import pandas as pd
from scipy import stats

st.title('CSAT Calculator')
st.write('**Straightforward CSAT calculation with statistical rigor.**')
st.write('''Please input the survey response result on the left sidebar,
    and the following table & CSAT results will be updated accordingly:''')
# generate the side bar for survey result input, survey have 5 rating levels
# default values are set with survey result {1, 5, 3, 4, 5, 2, 1, 4, 3, 4}
default_response = [2, 1, 2, 3, 2]
n_level = 5
res_list = [
    st.sidebar.number_input(
        '# of {0}-star rating response:'.format(i+1),
        min_value=0, max_value=None, step=1, value=default_response[i],
        key='res_list_{0}'.format(i), format='%d')
    for i in range(n_level)]
survey_result = np.array(res_list)
df_survey = pd.DataFrame({'rating': range(1, 6), 'count': survey_result})
st.dataframe(df_survey)

#############################################################################
st.header('Part 1. CSAT calculation (no confidence interval)')
# calculate CSAT score and percentage without confidence interval calculation
csat_score = (df_survey['rating'] * df_survey['count']).sum() \
    / df_survey['count'].sum()
csat_percent = df_survey.query('rating >= 4')['count'].sum() \
    / df_survey['count'].sum()
st.write('... # of survey with response:  {:d}'.format(
    df_survey['count'].sum()))
st.write('... CSAT score is:         {:.2f}'.format(csat_score))
st.write('... CSAT percentage is:    {:.2f}'.format(csat_percent))

#############################################################################
st.header('Part 2. CSAT (w/ confidence interval)')
# generate the side bar for conf interval, default at 0.95
conf_level = st.sidebar.slider(
    'Please choose the confidence level:',
    0.80, 0.99, value=0.95, step=0.01)
survey_count = df_survey['count'].sum()
degrees_freedom = survey_count - 1
st.write(
    ''' Please adjust the confidence level on the left sidebar,
    now the statistical test has the following parameters:''',
    '(degree of freedom, confidence level) is ({0:d}, {1:.2f})'.format(
        degrees_freedom, conf_level))

df_survey_1 = df_survey.assign(diff=lambda x: x['rating'] - csat_score) \
        .assign(diff2=lambda x: x['diff'] ** 2 * x['count'])
std_sample = np.sqrt(df_survey_1['diff2'].sum() / degrees_freedom)
# calculate std for CSAT score
std_csat_score = std_sample / np.sqrt(survey_count)
# calculate std for CSAT percent
std_csat_percent = np.sqrt(csat_percent * (1-csat_percent) / survey_count)

# calculate confidence interval based on t test
csat_score_low, csat_score_high = stats.t.interval(
    conf_level, degrees_freedom, csat_score, std_csat_score)
csat_percent_low, csat_percent_high = stats.t.interval(
    conf_level, degrees_freedom, csat_percent, std_csat_percent)
st.write('... CSAT score is:      {0:.2f} ({1:.2f}, {2:.2f})'.format(
    csat_score, csat_score_low, csat_score_high))
st.write('... CSAT percentage is: {0:.2f} ({1:.2f}, {2:.2f})'.format(
    csat_percent, csat_percent_low, csat_percent_high))

#############################################################################
st.header('Part 3. CSAT (w/ confidence interval and finite population correction)')
survey_total = st.number_input(
    '# Total survey sent out (regardless with response or not):',
    value=survey_count, min_value=0, max_value=None, step=1,
    key='survey_total', format='%d')
# add finite population correction (use default zero to avoid nan)
fpc = np.sqrt((survey_total - survey_count) / (survey_total - 1))
default_zero = 0.00000001

# calculate confidence interval based on t test
csat_score_low_fpc, csat_score_high_fpc = stats.t.interval(
    conf_level, degrees_freedom, csat_score,
    std_csat_score * max(fpc, default_zero))
csat_percent_low_fpc, csat_percent_high_fpc = stats.t.interval(
    conf_level, degrees_freedom, csat_percent,
    std_csat_percent * max(fpc, default_zero))
st.write('... CSAT score is:      {0:.2f} ({1:.2f}, {2:.2f})'.format(
    csat_score, csat_score_low_fpc, csat_score_high_fpc))
st.write('... CSAT percentage is: {0:.2f} ({1:.2f}, {2:.2f})'.format(
    csat_percent, csat_percent_low_fpc, csat_percent_high_fpc))

st.write(' ------------- ')
st.write('''The CSAT calculation, including score and confidence interval,
    is based on formulas in this blog [CSAT: An emperor with no clothes?]
    (https://medium.com/data-science-at-microsoft/csat-an-emperor-with-no-clothes-e1c27a1b93eb)''')
st.write('''Why confidence interval is needed?
    \"* ... CSAT score is based on a subset of a population —
    just those customers who’ve responded to the survey —
    but is intended to represent the satisfaction of the entire population.
    Because not every customer responds to the survey,
    the results need to account for a degree of uncertainty.* \" ''')
st.write('''Why finite population correction may be needed?
    \"* ... CSAT is designed to measure customer satisfaction
    with a specific transaction, and companies often know how many
    customers completed that transaction.
    If the response rate for a survey is 5% or higher,
    companies should apply the finite population correction (FPC),
    which accounts for an increase in accuracy when a relatively
    large proportion of a population is sampled* \" ''')
st.write('''Have a question? Reach out to Pan on [LinkedIn]
    (https://www.linkedin.com/in/panwu/)''')

# enable Google Analytics tracking
ga_tracking = '''<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-L8DC03KQGF"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-L8DC03KQGF');
</script>'''
components.html(ga_tracking)
