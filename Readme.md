# Hockey BI
Hockey BI is a project designed to gather, store, and analyze data from the Swiss hockey league. 
By scraping data and storing it in a structured backend, this project enables in-depth analysis, player valuation insights, and actionable recommendations for fantasy hockey enthusiasts and analysts.

> [!CAUTION]
> This project is not affiliated with, endorsed by, or connected to hockeymanager.ch or its owners.
> The website hockeymanager.ch and its contents are protected by intellectual property laws and are the exclusive property of Redesign Sagl de Camorino.
> Use of this software may violate the Terms of Service of hockeymanager.ch or other applicable laws. The authors of this project do not assume any responsibility for misuse. You are solely responsible for ensuring that your use of this software complies with all legal and contractual obligations.

---

## Tools Overview

## [`tools/analysis`](tools/analysis)
Contains scripts and notebooks for analyzing data from the Swiss hockey league.

## [`tools/hockeymanager`](tools/hockeymanager)
Includes to:
- JS script to Scrape data from the [Hockey Manager website](https://www.hockeymanager.ch/).
- Notebook to transform and analyze the scraped data.

---

## Backend [`src/hmtracker`](src/hmtracker)
> [!WARNING]
> Development in progress!

This backend aim to:
- Obtain a server that continuously keep track of hockey player evolution
- Allows public to use thoses data for analysis
- Allows user to track their teams evolution
- Indicates optimal transfert for a given team

---
### Setup Instructions

#### Prerequisites
- Python 3.8 or above
- A valid [Hockey Manager account](https://www.hockeymanager.ch/)
- python dependencies `pip install -r requirements.txt`

#### Initialize the database
This creates the necessary schema and tables for the backend. Also initialize the seasons.
```shell
python hmtracker/database/creation.py <database-url>
```

#### Load the current player stats
Scrape player data from the Hockey Manager website and store it in database.
You will need your account credentials.
```shell
python hmtracker/loader/main.py -d <database-url> -u <hm-useremail> -p <password>
```
This script is aimed to be run regularly (every time player change price and performance). So better set a cron job for it.

---
### Roadmap 

#### *In progress* 
- **Load team informations** : Script to extract private team data for a player.
- **API** : Backend endpoints to interact with stored data and load private team information.

#### *Planned Features*
##### Front-end Website 
 - User friendly interface to connect to HM and load teams data.
 - Client-side scraping to ensure user credentials remain private.
 - Interactive visualizations (e.g., best players to buy/sell, performance trends).

