"""
Copyright (C) 2025 Ayrik Nabirahni. This file
is apart of the Wikipull project, and licensed under
the GNU AGPL-3.0-or-later. See LICENSE and README for more details.
"""

import pandas as pd
import requests

version = '1.0.0'

def wikipull_version():
    return version

def wikipull(wiki_id: str, target_data: str, scrub_references: bool = True):
    """
    Pulls data from a Wikipedia page's subject table
    
    Args:
        wiki_id (str): The wiki id for the page, which can be found in the last part of the Wikipedia url; E.g. "kepler-22" for https://en.wikipedia.org/wiki/Kepler-22
        target_data (str): The table row which you'd like to pull the data for; E.g. "Mass"
        scrub_references (bool): Set to True by default. Whether you'd like the reference to be included (square brackets + number); E.g. G5V[4].
    """

    def get_wiki_data(wiki_id, target_data):
        wikipedia_url = 'https://en.wikipedia.org/wiki/' + wiki_id.lower()
        wikipedia_html = requests.get(wikipedia_url, headers={'User-Agent': 'Mozilla/5.0'})
        star_table = pd.read_html(wikipedia_html.content)[0]
        
        first_column = star_table.columns[0]
        pulled_row = star_table.loc[star_table[first_column] == target_data]
        pulled_value = pulled_row.iloc[0, 1]
        return pulled_value
        
    def parse_wiki_data(infotable_string, scrub_references):
        infotable_string_list = []

        for char in infotable_string: # put all processing in this loop
            if char == '[' and scrub_references == True: # STOP ONCE REFERENCE REACHED
                break
            else:
                infotable_string_list.append(char)

        infotable_string_joined = ''.join(infotable_string_list)
        return infotable_string_joined

    pulled_wiki = get_wiki_data(wiki_id, target_data)
    infotable_string = parse_wiki_data(pulled_wiki, scrub_references)
    return infotable_string
