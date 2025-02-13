# Neigh
(WIP, there's nothing in here why are you reading this?) 

Get HKJC horse racing data.

## Overview
HKJC's website has zero rizz and is skibidi toilet.

## Game Plan
### Get Data
1. (Should I?) Reverse engineering HKJC's api
2. Write a scraper (Not sure if real time streaming live odds is possible)
3. Clean the data
4. Pump the data into a Postgres db

### Working On...
- [ ] [Horse Profile](https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId=HK_2023_J456&Option=1)

### Endpoints to scrape
'https://racing.hkjc.com/racing/information/English/Racing/JKCScheduledRides.aspx',
 'https://racing.hkjc.com/racing/information/English/Racing/Localtrackwork.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/newhorse.asp',
 'https://racing.hkjc.com/racing/english/racing-info/racing_course_time.aspx',
 'https://racing.hkjc.com/racing/information/english/Racing/summary.aspx',
 'https://racing.hkjc.com/racing/information/English/Reports/RaceReportFull.aspx',
 'https://racing.hkjc.com/racing/information/English/Racing/ExceptionalFactors.aspx',
 'https://racing.hkjc.com/racing/information/English/tnc/tncStat.aspx',
 'https://member.hkjc.com/member/english/horse-owner/list-of-bloodstock-agents.aspx',
 'https://racing.hkjc.com/racing/information/english/Horse/HorseFormerName.aspx',
 'https://racing.hkjc.com/racing/information/English/Racing/TNCEntries.aspx',
 'https://campaign.hkjc.com/en/racing/conghua-movement-records.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/racing_rules_instr.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/tnc-odds-chart.aspx',
 'https://racing.hkjc.com/racing/information/English/racing/Entries.aspx',
 'https://racing.hkjc.com/racing/information/English/Racing/RaceReportExt.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/racing_course_select.aspx',
 'https://racing.hkjc.com/racing/information/English/Racing/JockeysRides.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/handicap_policy.asp',
 'https://racing.hkjc.com/racing/information/English/racing/RaceCard.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/jkc-odds-chart.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/pps_import_critieria.asp',
 'https://racing.hkjc.com/racing/information/English/Trainers/TrainerRanking.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/racing_weather.asp',
 'https://racing.hkjc.com/racing/information/English/Jockey/JockeyRanking.aspx',
 'https://racing.hkjc.com/racing/information/English/racing/Changes.aspx',
 'https://racing.hkjc.com/racing/information/English/Racing/VeterinaryRecord.aspx',
 'https://racing.hkjc.com/racing/information/English/Horse/LatestOnHorse.aspx',
 'https://racing.hkjc.com/racing/information/english/Horse/SelectHorse.aspx',
 'https://racing.hkjc.com/racing/information/english/Trackwork/TrackworkSearch.aspx',
 'https://www.hkjc.com/english/pp_formsheet/Veterinary_Pre-Import_Exam_Protocol_Version_Eng.pdf',
 'https://racing.hkjc.com/racing/information/English/Racing/Fixture.aspx',
 'https://racing.hkjc.com/racing/information/english/Jkc/JkcStat.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/fwb_declared_starters.asp',
 'https://racing.hkjc.com/racing/information/English/racing/Draw.aspx',
 'https://bet.hkjc.com/en/racing/wp/',
 'https://racing.hkjc.com/racing/information/English/racing/TTAutoPick.aspx',
 'https://racing.hkjc.com/racing/information/English/VeterinaryRecords/OveRecord.aspx',
 'https://racing.hkjc.com/racing/speedpro/english/formguide/formguide.html',
 'https://racing.hkjc.com/racing/information/english/Trainers/TrainerFavourite.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/ppo_performance_current.asp',
 'https://racing.hkjc.com/racing/information/english/Jockey/JockeyFavourite.aspx',
 'https://racing.hkjc.com/racing/English/tipsindex/tips_index.asp',
 'https://racing.hkjc.com/racing/information/English/Reports/CORunning.aspx',
 'https://campaign.hkjc.com/en/racing/jtcombo_debutants_statistics.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/reg_approved_gear.aspx',
 'https://racing.hkjc.com/racing/information/English/racing/LocalResults.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/last-run-reminder.aspx',
 'https://racing.hkjc.com/racing/information/English/Racing/FormLine.aspx',
 'https://racing.hkjc.com/racing/information/English/Horse/LatestOnHorse.aspx?View=Horses/clas/',
 'https://racing.hkjc.com/racing/english/racing-info/rdf/raceday_focus_1.asp',
 'https://racing.hkjc.com/racing/information/English/Racing/TrainersEntries.aspx',
 'https://racing.hkjc.com/racing/information/english/Horse/Btresult.aspx',
 'https://racing.hkjc.com/racing/english/racing-info/racing_course.aspx'

### ML
1. Random Forest
2. Feature selection (Permutation Importance)
3. ...

### Play with it
> Python 3.12
> Please.

```zsh
git clone {this repo}
```

```zsh
uv venv
```
```zsh
source .venv/bin/activate
```
```zsh
uv pip install -r requirements.txt
```

## Future Work
Probably need to dockerize the whole thing.

## Disclaimer
For education purpose only obviously. 