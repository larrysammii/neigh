from pydantic import BaseModel
from typing import List, Optional
import datetime


class Trainer(BaseModel):
    """
        "Trainer": [
        {
            "text": "C S Shum",
            "url": "/racing/information/English/Trainers/TrainerWinStat.aspx?TrainerId=SCS",
        }
    ]
    """

    text: str
    url: str


class Owner(BaseModel):
    """
        "Owner": [
        {
            "text": "Peter Lau Pak Fai",
            "url": "/racing/information/English/Horse/OwnerSearch.aspx?HorseOwner=Peter%20Lau%20Pak%20Fai",
        }
    ]
    """

    text: str
    url: str


class Sire(BaseModel):
    text: str
    url: str


class Horse(BaseModel):
    """
    "Country of Origin / Age": "IRE / 7",
    "Colour / Sex": "Bay / Gelding",
    "Import Type": "ISG",
    "Season Stakes*": "$27,741,541",
    "Total Stakes*": "$179,668,247",
    "No. of 1-2-3-Starts*": "18-3-0-23",
    "No. of starts in past 10": "0",
    "Current Stable Location": "Hong Kong",
    "Import Date": "28/06/2021",
    "Current Rating": "134",
    "Start of": "133"
    """

    country_of_origin: str
    age: int or float
    color: str
    sex: str
    import_type: str
    season_stakes: int or float
    total_stakes: int or float
    record_123_starts: str
    recent_starts: str
    stable_location: str
    import_date: datetime.date
    trainer: Trainer or List[Trainer] = None
    owner: Owner or List[Owner] = None
    current_rating: int
    season_start_rating: Optional[int] = None
    """
    {
    ,
        "Sire": [
            {
                "text": "Acclamation",
                "url": "/racing/information/English/Horse/SameSire.aspx?HorseSire=Acclamation",
            }
        ],
        "Dam": "Folk Melody",
        "Dam's Sire": "Street Cry",
        "Same Sire": ["BEAUTY CRESCENT", "KINGDOM OF RICHES", "RICH HORSE", "THE KHAN"],
    }
    """
    sire: Sire or List[Sire] = None
    dam: str
    dams_sire: str
    same_sire: List[str] = []
