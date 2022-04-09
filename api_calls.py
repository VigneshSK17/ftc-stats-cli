import os
from dotenv import load_dotenv

from datetime import datetime 
import json
from pprint import pprint
import requests

def get_auth(regionCode = None):
    load_dotenv()
    if os.getenv('USER') == None or os.getenv('TOKEN') == None:
        raise Exception("API Username and Token are not configured. Create an .env file with valid USER and TOKEN variables.")

    response = requests.get('http://ftc-api.firstinspires.org/v2.0/2021/leagues', auth=(os.getenv('USER'), os.getenv('TOKEN')))
    if response.status_code == 401:
        raise Exception("Either API Username or Token are not valid. Please configure the .env file with the correct values for the USER and TOKEN variables")

    if regionCode != None:
        return [x for x in json.loads(response.content)['leagues'] if x['region'] == regionCode]

    return (os.getenv('USER'), os.getenv('TOKEN'))

def get_date(auth, season: int, leagueCode: str):
    api_str = f"http://ftc-api.firstinspires.org/v2.0/{season}/events"

    response = requests.get(api_str, auth=auth)

    j = json.loads(response.content)

    dates = []
    for i in j['events']:
        if i['leagueCode'] == leagueCode:
            date = datetime.fromisoformat(i['dateStart'])
            dates.append(f"{str(date.month).zfill(2)}/{str(date.day).zfill(2)}/{date.year - 2000}")
            print(f"{len(dates)}: {dates[-1]}")

    print()
    while True:
        try:
            comp = int(input('Input the number corresponding to the date of the competition: '))
            if comp > len(dates) or comp < 1:
                raise ValueError
        except ValueError:
            continue
        else:
            break

    return dates[comp - 1]

## Get teams
def get_teams(auth, season: int, regionCode: str, parentLeagueCode: str):
    response = requests.get(f"http://ftc-api.firstinspires.org/v2.0/{season}/leagues/members/{regionCode}/{parentLeagueCode}", auth=auth)
    return json.loads(response.content)['members']

# NOTE: Run this to get region codes
def main():
    while True:
        try:
            region = input('Enter a valid region code: ')
            if get_auth(region) == []:
                raise ValueError
        except ValueError:
            continue
        else:
            pprint(get_auth(region))
            print("\n-----\nNote:")
            print("code -> leagueCode")
            print("parentLeagueCode -> parentLeagueCode")
            break

if __name__ == "__main__":
    main()