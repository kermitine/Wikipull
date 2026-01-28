"""
Copyright (C) 2025 Ayrik Nabirahni. This file
is apart of the Wikipull project, and licensed under
the GNU AGPL-3.0-or-later. See LICENSE and README for more details.
"""

import pandas as pd
import requests

version = '1.2.0'

def wikipull_version():
    return version

def wikipull(wiki_id: str, target_data: str, scrub_references: bool = True, scrub_spaces: bool = False, measurement_with_uncertainty: bool = False):
    """
    Pulls data from a Wikipedia page's subject table
    
    Args:
        wiki_id (str): The wiki id for the page, which can be found in the last part of the Wikipedia url; E.g. "kepler-22" for https://en.wikipedia.org/wiki/Kepler-22
        target_data (str): The table row which you'd like to pull the data for; E.g. "Mass"
        scrub_references (bool): Set to True by default. Whether you'd like the reference to be included (square brackets + number); E.g. "G5V[4]" -> "G5V"
        scrub_spaces (bool): Set to False by default. Strips all whitespace characters from the string, which makes it easier to parse it further in the future by iterating; E.g. "1.66 +3.55 -2.77" -> "1.66+3.55-2.77".
        measurement_with_uncertainty (bool): Set to False by default. If the data which you're pulling is a quantitative measurement with uncertainties, return a dictionary with the keys "nominal", "lower_uncertainty", "higher_uncertainty"; "E.g. 1.66 +3.55 -2.77" -> dict["nominal"] = 1.66, dict["lower_uncertainty"] = 2.77, dict["upper_uncertainty"] = 3.55
    """

    def get_wiki_data(wiki_id, target_data):
        wikipedia_url = 'https://en.wikipedia.org/wiki/' + wiki_id.lower()
        wikipedia_html = requests.get(wikipedia_url, headers={'User-Agent': 'Mozilla/5.0'})
        star_table = pd.read_html(wikipedia_html.content)[0]
        
        first_column = star_table.columns[0]
        pulled_row = star_table.loc[star_table[first_column] == target_data]
        pulled_value = pulled_row.iloc[0, 1]
        return pulled_value
        
    def parse_wiki_data(infotable_string, scrub_references, scrub_spaces, measurement_with_uncertainty):
        infotable_string_list = []
        list_of_accepted_symbols_filter =  ['+', '−', '-', '±']
        plus_minus_combined = False
        infotable_string_list = []
        nominal_value_list = []
        nominal_done = False
        upper_diff_value_list = []
        upper_diff_done = False
        lower_diff_value_list = []



        if measurement_with_uncertainty == True: # force them if measurement_with_uncertainty is true
            scrub_references = True
            scrub_spaces = True


        for char in infotable_string: # put all processing in this loop
            if char == '[' and scrub_references == True: # STOP ONCE REFERENCE REACHED
                break
            elif char.isspace() and scrub_spaces == True: # pass onto next char if space found
                continue
            else:
                infotable_string_list.append(char)

        infotable_string_filtered = ''.join(infotable_string_list)


        if measurement_with_uncertainty == True:
            for char in infotable_string_filtered:
                if char not in list_of_accepted_symbols_filter and nominal_done == False and upper_diff_done == False:
                    nominal_value_list.append(char)
                elif char == '+':
                    nominal_done = True
                    continue
                elif char == '±':
                    nominal_done = True
                    plus_minus_combined = True
                    continue
                elif char not in list_of_accepted_symbols_filter and nominal_done == True and upper_diff_done == False and plus_minus_combined == True:
                    upper_diff_value_list.append(char)
                    lower_diff_value_list.append(char)
                elif char not in list_of_accepted_symbols_filter and nominal_done == True and upper_diff_done == False and plus_minus_combined == False:
                    upper_diff_value_list.append(char)
                elif char == '−' or char == '-':
                    upper_diff_done = True
                    continue
                elif char not in list_of_accepted_symbols_filter and nominal_done == True and upper_diff_done == True:
                    lower_diff_value_list.append(char)

            joined_nominal = ''.join(nominal_value_list)
            joined_upper_diff = ''.join(upper_diff_value_list)
            joined_lower_diff = ''.join(lower_diff_value_list)

            if joined_nominal == '' or joined_nominal == None:
                joined_nominal = 0
            if joined_upper_diff == '' or joined_upper_diff == None:
                joined_upper_diff = 0
            if joined_lower_diff == '' or joined_lower_diff == None:
                joined_lower_diff = 0
        
            dict = {
                "lower_uncertainty": joined_lower_diff,
                "nominal": joined_nominal,
                "higher_uncertainty": joined_upper_diff
            }

            return dict

        else:
            return infotable_string_filtered

    pulled_wiki = get_wiki_data(wiki_id, target_data)
    infotable_string = parse_wiki_data(pulled_wiki, scrub_references, scrub_spaces, measurement_with_uncertainty)
    return infotable_string
