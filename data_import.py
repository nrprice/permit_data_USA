import pandas as pd
from datetime import datetime as dt
pd.set_option("display.max_columns", 50)
pd.set_option("display.max_rows", 400000)
pd.set_option("display.width", 1000)

# Inital Import
gun_data = pd.read_csv('Assets/gun_clean.csv')
election_data = pd.read_csv('Assets/presidents.csv')
census = pd.read_csv('Assets/census_clean.csv')


# Census Data
census.drop(columns=['Unnamed: 0', 'census', 'estimates_base'],  inplace=True)
census.rename(columns={'location': 'state'}, inplace=True)

# Census Data Melted
census_melted = census.melt(id_vars='state', var_name='date', value_name='count')
census_melted['date'] = census_melted['date'].apply(lambda x: pd.to_datetime(x))
census_melted = census_melted[['date', 'state', 'count']]

# Gun Data

gun_data.drop(columns='Unnamed: 0', inplace=True)
gun_data['month'] = gun_data['month'].apply(lambda x: pd.to_datetime(x))
gun_data.rename(columns={'month': 'date'}, inplace=True)

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

census_and_party_df.to_csv('Assets/census_and_party.csv')
gun_data.to_csv('Assets/cleaned_gun_data.csv')