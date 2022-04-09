from enum import Enum

import argparse
from bs4 import BeautifulSoup, element
from cli2gui import Cli2Gui
import re
from numpy import require
import requests

import pandas as pd
import dataframe_image as dfi

from api_calls import get_auth, get_date, get_teams

class Output(Enum):
    SPREADSHEET = 1,
    TABLE = 2

def get_table(season: int):
    stats_url = f"http://www.ftcstats.org/{season + 1}/georgia.html"

    with requests.Session() as s:
        with s.get(stats_url) as page:
            soup = BeautifulSoup(page.content, 'html.parser')
    return soup.findAll("table")[1].findAll('tr')

def get_team_indices( table: element.ResultSet, team_num: int):
    all_teams = []
    team_indices = []
    for z in table:
        for counter, tag in enumerate(z, start=0):
            if counter == 3:
                if type(tag) is not element.NavigableString:
                    all_teams.append(tag)
    for i, x in enumerate(all_teams):
        if str(team_num) in str(x):
            team_indices.append(i) 
    return team_indices

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

def stats_wrapper(auth, table, season, regionCode, parentLeagueCode, date):
    all_teams_stats = {}

    # List comprehension filters out teams who didn't play
    for team in [x for x in get_teams(auth, season, regionCode, parentLeagueCode) if get_team_indices(table, x) != []]:
        for index in get_team_indices(table, team):
            if date in str(table[index + 1]):
                all_teams_stats[team] = parse_stats(get_stats(table[index + 1]))

    return all_teams_stats

def gen_output(stats_dict, type: Output, location = "data"):
    df = pd.DataFrame.from_dict(stats_dict)
    df = df.transpose()

    if type == Output.SPREADSHEET:
        df.to_excel(location + '.xlsx')
    elif type == Output.TABLE:
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

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--season",
        help="the year number of the season, the year that the season started", required=True, type=int)
    parser.add_argument("-r", "--region-code",
        help="the region code which the event of interest is based in", required=True, type=str)
    parser.add_argument("-l", "--parent-league-code",
        help="parent league of the event of interest", required=True, type=str)
    parser.add_argument("--league-code",
        help="league of the event of interest", type=str, default=None)

    parser.add_argument("--output-type", choices=['spreadsheet', 'table'], default='spreadsheet', help="choose output format of data")
    parser.add_argument("--output-location", default='data', help="choose what output file should be named, name only (Ex: Meet1Data)")

    args = parser.parse_args()

    handle_args(args)

def handle_args(args: argparse.Namespace):
    AUTH = get_auth()
    TABLE = get_table(args.season)
    DATE = get_date(AUTH, 2021, args.parent_league_code if args.league_code == None else args.league_code)

    match args.output_type:
        case 'spreadsheet': gen_output(stats_wrapper(AUTH, TABLE, args.season, args.region_code, args.parent_league_code, DATE), Output.SPREADSHEET, args.output_location)
        case 'table': gen_output(stats_wrapper(AUTH, TABLE, args.season, args.region_code, args.parent_league_code, DATE), Output.TABLE, args.output_location)


def main():
    parse_args()

if __name__ == "__main__":
    main()