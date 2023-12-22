'''
This program visits 'https://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;template=results;type=batting', 
and dextracts the stats for Men's test batting records and saves all the stats as a csv file.
'''

# Libraries used
import os
import requests
from bs4 import BeautifulSoup

# Third party libraries
import pandas as pd

# Functions
# Saving data frame
def save_df(df, file_name='test_batting.csv', seperate_folder=True):
    # 1st create a Data folder, if parameter is set true
    if seperate_folder:
        os.makedirs('Data', exist_ok=True)
        path = 'Data/'
    else: path = ''

    # creating the path
    path += file_name
    
    df.to_csv(path)
    return None

# Seperating names and teams
def span_split(df, inplace=True):
    if not inplace: df = df.copy()
    Start, End = pd.Series(index=range(len(df))), pd.Series(index=range(len(df)))
    for i in range(len(df)):
        span = df['Span'].iloc[i]
        start_year, end_year = span.split('-')
        Start.iloc[i] = start_year
        End.iloc[i] = end_year
    
    df['Start'] = Start
    df['End'] = End
    df.drop('Span', axis=1, inplace=True)
    if not inplace: return df
    return None

# removing span and adding start and end year
def player_team_split(df, inplace=True):
    
    if not inplace: df = df.copy()
    Team = pd.Series(index=range(len(df)))
    for i in range(len(df)):
        player = df['Player'].iloc[i]
        start_paren = player.find('(')
        if player.find('/')>=0: start_char = player.find('/')
        else: start_char = start_paren
        end_char = player.find(')')

        player_name = player[:start_paren-1]
        player_team = player[start_char+1 :end_char]
    
        df['Player'].iloc[i] = player_name
        Team.iloc[i] = player_team
    
    df['Team'] = Team
    if not inplace: return df
    return None

# int main()
if __name__=='__main__':
    # Prompt for how many number of pages
    print('How many pages worth of data ? 1-63 , -1 for all (each page has 50 entries, total 3142 )')
    n_pages = int(input())

    # base_url contains a placeholder {} for the page number. 
    base_url = 'https://stats.espncricinfo.com/ci/engine/stats/index.html?class=1;orderby=runs;page={};template=results;type=batting'

    for pagenum in range(1, n_pages+1):
        
        print(f'Visiting page number {pagenum}. ', end='')
        # updating url for page number
        url = base_url.format(pagenum)
        
        # Sending the HTTP request to fetch the webpage
        response = requests.get(url)
        if response.status_code != 200: # Some error in HTTP request
            print(f'Some error in HTTP request! Response status code = {response.status_code} !!')
            break

        # making a soup for reading data
        soup = BeautifulSoup(response.content, 'html5lib')

        # Extracting the desired table
        table_class = 'engineTable' # Name of the table's class
        tables = soup.find_all('table', class_=table_class) # returns all tables with `table_class`
        # Finding the table which doesnt have style attribute (thats our table)
        desired_table=None
        for table in tables:
            if not (table.has_attr('style')):
                desired_table = table
                break
        table = desired_table

        t_head = table.find('thead')
        t_body = table.find('tbody')

        # The desired table is fetched!!
        if pagenum==1: # When visiing the 1st page, creating dataframe and extracting the table columns headings
            cols = dict()
            for tr in t_head.find_all('tr'):
                for th in t_head.find_all('th'):
                    cols[th.text.strip()] = None

            cols.pop('') # this column was given to include links
            # DataFrame part
            df = pd.DataFrame(cols, index=[0])
        

        # Now making all the entries in the given page of the table
        for row in t_body.find_all('tr'):
            for col, td in zip(cols.keys() ,row.find_all('td')):
                # This message pops as an entry when reached more than the max page number
                if td.text.strip() == 'No records available to match this query': break 
                cols[col] = td.text.strip()
            df_new_entry = pd.DataFrame(cols, index=[0])
            df = pd.concat([df, df_new_entry], ignore_index=True)
        
        print(f'Page {pagenum} parsed. Total {len(df)-1} entries made') # Beacause will delete the 1st NONE row later on

    # All data parsed. Deleting the 1st row created while making the df
    df.drop([0], inplace=True)

    # All in all, its raw data :/
        # Some data transformation
    player_team_split(df)
    span_split(df)
        # Reordering columns
    df = df[['Player','Team' ,'Start' ,'End' ,'Mat', 'Inns' ,'NO' ,'Runs' ,'HS' ,'Ave' ,'100' ,'50' ,'0']] 


    # Take a look at the final df before saving it
    print("\nHere's your data: \n")
    print(df)

    # Final prompt, save or not 
    save_char = input('\nDo you want to save the dataframe as an csv file ? (y/n): ')
    if save_char.casefold() == 'y':
        # input prompt for filename
        file_name = input('File name (-- for default): ')
        print('Saving the dataframe...')
        if file_name=='--': save_df(df) # default value
        else: save_df(df, file_name) # given name
        print('Dataframe saved as a csv')
    else:
        print('Not saving the dataframe...') # ehhh..?

    print('\n--- G O O D B Y E ---')
