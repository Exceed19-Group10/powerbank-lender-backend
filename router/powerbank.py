from math import ceil
from typing import Union
from pymongo import DESCENDING
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from database.database import user_database, powerbank_database, borrower_history


router = APIRouter(
        prefix="/powerbank",
        tags=["powerbank"],
        responses={404: {"description": "Not found"}},
    )


class User(BaseModel):
    user_ID: str
    password: str
    username: str
    user_dept: str
    user_fee: Union[None, int]


class PowerBank(BaseModel):
    powerbank_ID: int
    borrow_mai: int
    yu_mai: int
    user_ID: Union[None, str]
    username: Union[None, str]
    user_dept: Union[None, str]
    start_time: Union[None, datetime]
    end_time: Union[None, datetime]


class BorrowerHistory(BaseModel): 
    powerbank_ID: int
    username: str
    borrower_time: int
    late_mai: Union[None, int]
    time: int


class BorrowLaewNaRequestBody(BaseModel):
    user_ID: str
    password: str


@router.get('/all-powerbank')
def get_all_powerbank():
    """Get all powerbank data from powerbank collection."""
    powerbank_list = list(powerbank_database.find({}, {"_id":False}))
    return {"all_powerbank": powerbank_list}


@router.get('/get-powerbank/{powerbank_ID}')
def get_powerbank(powerbank_ID: int):
    """Get specific powerbank data by powerbank_ID from powerbank collection."""
    return list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))[0]


@router.put('/borrow-laew/{powerbank_ID}')
def borrow_laew_naaaa(powerbank_ID: int, body: BorrowLaewNaRequestBody):
    """This method is used when someone borrow powerbank."""
    powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))
    try:
        something = powerbank.pop(0)
    except IndexError:
        raise HTTPException()
    # print(body)
    from_user_database = list(user_database.find({"user_ID": body.user_ID, "password": body.password}, {'_id': False}))
    if not len(from_user_database):
        raise HTTPException(401, "Authentication Error because UserID and Password doesn't match.")
    user = from_user_database.pop(0)
    if user["user_fee"] != 0:
        raise HTTPException(402, "You haven't paid your fee.")
    powerbank_database.update_one(something, {"$set": 
                                                {   
                                                    "borrow_mai": 1,
                                                    "user_ID": body.user_ID,
                                                    "username": user["username"],
                                                    "user_dept": user["user_dept"],
                                                    "start_time": (datetime.now() - timedelta(hours=7)).timestamp(),
                                                    "end_time": (datetime.now() + timedelta(seconds=30) - timedelta(hours=7)).timestamp()
                                                }
                                            }
                                        )
    updated_powerbank_data = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))
    updated_powerbank = updated_powerbank_data.pop(0)
    borrower_history.insert_one(
        {
            "powerbank_ID": powerbank_ID, 
            "user_ID": user["user_ID"], 
            "username": user["username"],
            "borrow_time": updated_powerbank["end_time"] - updated_powerbank["start_time"], 
            "late_mai": 0,
            "time": updated_powerbank["start_time"]
        }
    )
    return {   
                "powerbank_ID": powerbank_ID,
                "borrow_mai": 1,
                "yu_mai": 0,
                "user_ID": body.user_ID,
                "username": user["username"],
                "user_dept": user["user_dept"],
                "start_time": (datetime.now() - timedelta(hours=7)).timestamp(),
                "end_time": (datetime.now() + timedelta(seconds=30) - timedelta(hours=7)).timestamp()
            }


@router.put('/return-laew/{powerbank_ID}')
def return_powerbank(powerbank_ID: int):
    """This method is used when powerbank is back to its position."""
    powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))
    try:
        something = powerbank.pop(0)
    except IndexError as e:
        raise HTTPException(406, f"ID:{powerbank_ID} is not our powerbank.") from e
    powerbank_database.update_one(something, {"$set": {"yu_mai": 1}})
    return list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))[0]


@router.put('/pai-laew/{powerbank_ID}')
def pai_leaw_naaaa(powerbank_ID: int):
    """This method is used when powerbank is left from its position."""
    powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))
    try:
        something = powerbank.pop(0)
    except IndexError as e:
        raise HTTPException(406, f"ID:{powerbank_ID} is not our powerbank.") from e
    powerbank_database.update_one(something, {"$set": {"yu_mai": 0}})
    return list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))[0]


@router.put('/check-dai-mai/{powerbank_ID}')
def confirm_return(powerbank_ID: int):
    """This method is used for confirm that powerbank is really back to its position."""
    powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {"_id": False}))
    # print(powerbank)
    try:
        something = powerbank.pop(0)
    except IndexError as e:
        raise HTTPException(406, f"ID:{powerbank_ID} is not our powerbank.") from e
    user_history = list(borrower_history.find({"powerbank_ID": powerbank_ID}, {"_id": False}).sort("time", DESCENDING))
    # print(user_history)
    user = user_history.pop(0)
    if something["yu_mai"] == 1:
        if something["end_time"] < (datetime.now() - timedelta(hours=7)).timestamp():
            borrower_history.update_one(user, {"$set": {"late_mai": 1}})
        else:
            borrower_history.update_one(user, {"$set": {"late_mai": 0}})
        powerbank_database.update_one(something, {"$set": {
                                                            "borrow_mai": 0,
                                                            "user_ID": 0,
                                                            "username": "",
                                                            "user_dept": "",
                                                            "start_time": 0,
                                                            "end_time": 0
                                                        }
                                                }
                                        )
        return list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))
    raise HTTPException(400, "This powerbank is not available.")


@router.get('/fee/{powerbank_ID}')
def fee(powerbank_ID: int):
    """Calculate fee when end time is greater than 30 seconds(demo) otherwise, it will be zero."""
    powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))
    try:
        something = powerbank.pop(0)
    except IndexError as e:
        raise HTTPException(406, f"ID:{powerbank_ID} is not our powerbank.") from e
    from_user_database = list(user_database.find({"user_ID": something["user_ID"]}, {'_id': False}))
    user = from_user_database.pop(0)
    current_time = (datetime.now() - timedelta(hours=7)).timestamp() # Current time
    difference = (current_time - something["end_time"]) # Late time in second unit
    fee = (ceil(difference - 30)) * 1 if difference > 30 else 0
    user_database.update_one(user, {"$set": {"user_fee": fee}})
    return {
        "user_ID": something["user_ID"],
        "password": user["password"],
        "username": user["username"],
        "user_dept": user["user_dept"],
        "user_fee": fee
    }


@router.get('/get-history')
def borrow_history():
    """Get all user that ever borrow powerbank from us."""
    history = list(borrower_history.find({}, {"_id": False}))
    return {"user_history": history}
