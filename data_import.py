import pandas as pd
import numpy as np
from datetime import datetime as dt
pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 400000)
pd.set_option("display.width", 1000)

# Inital Import
gun_data = pd.read_csv('Assets/input_nics_updated.csv')
election_data = pd.read_csv('Assets/input_presidents.csv')
census = pd.read_excel('Assets/input_census.xlsx', engine='openpyxl')

states_list = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
       'Colorado', 'Connecticut', 'Delaware', 'District of Columbia',
       'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana',
       'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
       'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
       'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
       'New Jersey', 'New Mexico', 'New York', 'North Carolina',
       'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
       'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee',
       'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
       'West Virginia', 'Wisconsin', 'Wyoming', 'Puerto Rico']

# Census Data
new_headers = census.iloc[2]
census = census[3:].reset_index(drop=True)
census.columns = new_headers
census = census.rename_axis(None, axis=1)
census.rename(columns={np.nan: 'state'}, inplace=True)
census.columns = [x.lower().replace(" ", "_") if type(x) == str else int(x) for x in census.columns]
census['state'] = census['state'].apply(lambda x: str(x).replace(".", ""))
census.drop(['census', 'estimates_base'], axis=1, inplace=True)
census = census[census['state'].isin(states_list)]

# Census Data Melted
census_melted = census.melt(id_vars='state', var_name='date', value_name='count')
census_melted['date'] = pd.to_datetime(census_melted['date'], format='%Y')
census_melted = census_melted[['date', 'state', 'count']]

# Gun Data
gun_data.rename(columns={'month': 'date'}, inplace=True)
gun_data = gun_data[['date', 'state', 'permit', 'handgun', 'long_gun', 'multiple']]
gun_data['date'] = pd.to_datetime(gun_data['date'])

# Election Data
election_data.columns = [x.lower().replace(' ', '_') for x in election_data.columns]
election_data.rename(columns={'year': 'date'}, inplace=True)
election_data['state'] = election_data['state'].apply(lambda x: x.title())
election_data = election_data[election_data['date'] >= 2000]
parties_list = ['REPUBLICAN', "DEMOCRAT"]
election_data = election_data[election_data['party'].isin(parties_list)].reset_index(drop=True)

# Winning Party Data
full_states_list = election_data['state'].unique()
full_years_list = election_data['date'].unique()

winning_party_df = pd.DataFrame()

for state in full_states_list:
    for year in full_years_list:
        data = election_data[(election_data['state'] == state) & (election_data['date'] == year)].drop(
            columns='total_votes_cast')

        most_votes_cast = data[data['votes_cast'] == data['votes_cast'].max()]

        winning_party_df = winning_party_df.append(most_votes_cast, ignore_index=True)

winning_party_df['date'] = winning_party_df['date'].apply(lambda x: dt(x, 1, 1))

# Census and Winning Party Combined
census_and_party_df = census_melted.merge(winning_party_df,
                                          left_on=['date', 'state'],
                                          right_on=['date', 'state'],
                                          how='outer')
census_and_party_df.drop(columns=['state_code', 'votes_cast'], inplace=True)

census_and_party_df.to_csv('Assets/output_census_and_party.csv')
gun_data.to_csv('Assets/output_cleaned_gun_data.csv')