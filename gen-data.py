import argparse
from email.errors import HeaderMissingRequiredValue
from cli2gui import Cli2Gui

import re
import requests
import bs4
from bs4 import BeautifulSoup
from pprint import pprint

import pandas as pd
import dataframe_image as dfi

info = {}
teams_url = "https://ftc-events.firstinspires.org/2021/"
stats_url = "http://www.ftcstats.org/2022/georgia.html"

def get_teams(region_code):
    teams_dict = {}
    with requests.Session() as s:
        with s.get(teams_url + region_code) as page:
            soup = BeautifulSoup(page.content, 'html.parser')
    teams_table = soup.findAll('table')[1]
    teams = teams_table.findAll('tr')
    for i, team in enumerate(teams):
        if i != 0:
            teams_dict[team.findAll('td')[1].string] = team.findAll('td')[0].find('a').string
    return teams_dict

def get_table():
    with requests.Session() as s:
        with s.get(stats_url) as page:
            soup = BeautifulSoup(page.content, 'html.parser')
    return soup.findAll("table")[1].findAll('tr')

def get_team_indices(team_num):
    all_teams = []
    team_indices = []
    for z in get_table():
        for counter, tag in enumerate(z, start=0):
            if counter == 3:
                if type(tag) is not bs4.element.NavigableString:
                    all_teams.append(tag)
    for i, x in enumerate(all_teams):
        if str(team_num) in str(x):
            team_indices.append(i) 
    return team_indices

def get_region(team_indices, dates):
    for index in team_indices:
        for date in dates:
            if date in str(get_table()[index + 1]):
                return index

def get_stats(team_tag):
    all_stats = []
    for tag in team_tag.findChildren('td'):
        all_stats.append(tag) 
    return all_stats

def parse_stats(all_stats):
    teleop_stats = list(filter(lambda a: a != '', re.sub('[^\d\.\ ]', '', all_stats[7].findChild('abbr')['title']).split(' ')))
    endgame_stats = list(filter(lambda a: a != '', re.sub('[^\d\.\ ]', '', all_stats[8].findChild('abbr')['title']).split(' ')))
    stats = {
        "Offensive Power Ranking (OPR)": float(all_stats[4].string),
        "Auto OPRc": float(all_stats[6].string),
        "Auto Freight": float(re.sub('[^\d\.]', '', all_stats[6].findChild('abbr')['title'])),
        "Teleop OPRc": float(all_stats[7].string),
        "Alliance High Freight": teleop_stats[0],
        "Shared Freight": float(teleop_stats[2]),
        "Endgame OPRc": float(all_stats[8].string),
        "Ducks Delivered": float(endgame_stats[0]),
        "Team Shipping Elements Capped": float(endgame_stats[2]),
        "Average Score (No Penalties)": float(all_stats[16].string),
    }
    return stats

def stats_dict_wrapper(team_num, dates):
    print(team_num)
    return parse_stats(get_stats(get_table()[get_region(get_team_indices(team_num), dates) + 1]))

def all_teams_stats_wrapper(region_code, dates, *del_teams):
    all_team_stats = {}
    teams = get_teams(region_code)
    # Remote championship teams have no stats, so removing them
    if len(del_teams) > 0:
        for team in del_teams:
            del teams[team]
    # del state_teams['SpartaBots I']
    # del state_teams['57th Mech']
    # del state_teams['ATOM']

    for team_name, team_num in teams.items():
        all_team_stats[(team_name, team_num)] = stats_dict_wrapper(team_num, dates)
    return all_team_stats

def gen_output(df, type, location):
    df = df.transpose()

    if type == "spreadsheet":
        df.to_excel(location + '.xlsx')
    elif type == "table":
        df = df.sort_values(by=['Offensive Power Ranking (OPR)'], ascending=False)

        df_styled = df.style # Styled version of dataframe
        df_styled.format(precision=1) # Make numbers round to one digit after decimal

        # Make the first row and column have crimson background and white text
        index_names = {
            'selector': '.index_name',
            # 'props': 'font-style: italic; color: darkgrey; font-weight:normal;'
            'props': 'background-color: #990000; color: white;'
        }
        # Idk
        headers = {
            'selector': 'th:not(.index_name)',
            'props': 'background-color: #990000; color: white;'
        }

        # Add the previous styles and add crimson border to each cell
        df_styled.set_properties(
            **{'border': '2px solid #990000 !important'}
        ).set_table_styles([index_names, headers])
        # Add bars to easily compare team stats
        df_styled.bar()

        dfi.export(df_styled, location + ".png")

def handle_args(args):
    dates = []

    # print(args.event_code)
    # for i in range(len(args.dates)):
    #     if i % 8 == 0:
    #         date = ''
    #     print(i)
    print(args.dates[0])
    if len(args.dates[0]) > 1:
        for date in args.dates:
            # print(date + " hi ")
            # print(''.join(date))
            dates.append(''.join(date))
    else:
        date = ''
        for i in range(len(args.dates)):
            if i % 8 == 0 and i != 0:
                dates.append(date)
                date = ''
            date += args.dates[i]
    print(dates)

    data = pd.DataFrame.from_dict(all_teams_stats_wrapper(args.event_code, dates))
    gen_output(data, args.output_type, args.output_location) 

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-e", "--event-code",
        help="selects event from which team data should be scraped from (Ex: USGADOM1)", required=True)
    parser.add_argument("-d", "--dates", type=list, nargs="+",
        help="gets dates of each event to be scraped from, date format DD/MM/YY (Ex: 10/30/21)", required=True)

    parser.add_argument("--output-type", choices=['spreadsheet', 'table'], default='spreadsheet', help="choose output format of data")
    parser.add_argument("--output-location", default='data', help="choose what output file should be named, name only (Ex: Meet1Data)")

    args = parser.parse_args()

    handle_args(args)

"""
Example of Raw Team Information from Table

<tr class="trow" style="color:#888;"> <td align="right"><p style="color:#00000000">99999</p></td> <td align="right"><a href="https://ftc-events.firstinspires.org/2021/team/9686">9686</a></td> <td><abbr title="Alpharetta, GA 8th year">Raiders of the ARC- Black</abbr></td> <td align="right">46.4</td> <td align="right">46.4</td> <td align="right">55.5</td> <td align="right"><abbr title="auto freight: 0.6">6.4</abbr></td> <td align="right"><abbr title="alliance high: 2.2 alliance mid: 0.3 shared: 0.5">16.4</abbr></td> <td align="right"><abbr title="ducks: 5.6 shared: 0.0 capped: 0.0">32.7</abbr></td> <td align="right">0.6</td> <td align="right">2.2</td> <td align="right">0.3</td> <td align="right">0.5</td> <td align="right">5.6</td> <td align="right">0.0</td> <td align="right">0.0</td> <td align="right">104.4</td> <td align="center" style="font-size: 1px; padding: 2px;"><span class="inlinebar">8:16:20:0:0:257,6:17:22:255:0:0,7:18:36:239:0:0,7:18:42:232:0:0,4:14:48:0:0:234</span></td> <td align="right"><abbr title="NP Scores: 91, 105, 123, 125, 78">125</abbr></td> <td> </td> <td>Georgia GA Western Georgia 01/29/22</td> <td align="right">16</td> <td align="right">104.4</td> <td align="right">90.2</td> <td align="right">5</td> <td align="right" sorttable_customkey="5.070464">7‑2‑0</td> </tr>
"""

@Cli2Gui(run_function=handle_args, gui="pysimpleguiqt")
def main():
    parse_args()
    # pprint(data)

if __name__ == "__main__":
    main()