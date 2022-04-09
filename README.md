# Data Generation CLI for FTC

## Setup
1. Install dependencies
    pip install -r requirements.txt # Install dependecies
2. [Register for an API Token](https://ftc-events.firstinspires.org/api)
3. Add API credentials as environment variables
- Create a .env file in the project directory
- Inside the file, make two variables called USER and TOKEN with the corresponding username and token inside the quotes

        USER="yourUsername"
        TOKEN="yourToken"

## Examples
### Windows
    python.exe .\gen_data_2.py -s 2021 -r USGA -l WGA22 --league-code doug22 --output-type table --output-location douglasville-meet-2

    python.exe .\gen_data_2.py -s 2021 -r USGA -l NEGA22 --league-code jc22 --output-type table --output-location jackson-meet-5      
### Mac/Linux
    python gen_data_2.py -s 2021 -r USGA -l WGA22 --league-code doug22 --output-type table --output-location douglasville-meet-2

    python gen_data_2.py -s 2021 -r USGA -l NEGA22 --league-code jc22 --output-type table --output-location jackson-meet-5      

## Help
### Windows
    python.exe .\gen_data_2.py --help

### Mac/Linux
    python gen_data_2.py --help

## TODOS
- [] Add support for parent leagues only
- [] Better support for finding league code (search by league name)