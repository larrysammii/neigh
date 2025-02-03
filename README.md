# Neigh
(WIP, there's nothing in here why are you reading this?) 
Get HKJC horse racing data -> ML -> Profit.

## Overview
HKJC's website has zero rizz and is skibidi toilet.

## Game Plan
### Get Data
1. (Should I?) Reverse engineering HKJC's api
2. Write a scraper (Not sure if real time streaming live odds is possible)
3. Clean the data
4. Pump the data into a Postgres db

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