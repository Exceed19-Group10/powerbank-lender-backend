from typing import Union
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from database.database import user_database, powerbank_database


router = APIRouter(
        prefix="/powerbank",
        tags=["powerbank"],
        responses={404: {"description": "Not found"}},
    )


class User(BaseModel):
    user_ID: int
    password: str
    username: str
    user_dept: str
    user_fee: Union[None, int]


class PowerBank(BaseModel):
    powerbank_ID: int
    borrow_mai: int
    yu_mai: int
    user_ID: Union[None, int]
    username: Union[None, str]
    user_dept: Union[None, str]
    start_time: Union[None, datetime]
    end_time: Union[None, datetime]
    late_mai: Union[None, int]

class BorrowLaewNaRequestBody(BaseModel):
    user_ID: int
    password: str


@router.get('/all-powerbank')
def get_all_powerbank():
    powerbank_list = list(powerbank_database.find({}, {"_id":False}))
    return {"all_powerbank": powerbank_list}


@router.get('/get-powerbank/{powerbank_ID}')
def get_powerbank(powerbank_ID: int):
    return list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))[0]


@router.put('/borrow-laew/{powerbank_ID}')
def borrow_laew_naaaa(powerbank_ID: int, body: BorrowLaewNaRequestBody):
    powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))
    something = powerbank.pop(0)
    print(body)
    all_users = list(user_database.find({"user_ID": body.user_ID, "password": body.password}, {'_id': False}))
    if not len(all_users):
        raise HTTPException(401, "Authentication Error because UserID and Password doesn't match.")
    user = all_users.pop(0)
    if user["user_fee"] != 0:
        raise HTTPException(406, "You haven't paid your fee.")
    powerbank_database.update_one(something, {"$set": 
                                                {   
                                                    "borrow_mai": 1,
                                                    "yu_mai": 0,
                                                    "user_ID": body.user_ID,
                                                    "username": user["username"],
                                                    "user_dept": user["user_dept"],
                                                    "start_time": datetime.now().timestamp(),
                                                    "end_time": (datetime.now() + timedelta(hours=1)).timestamp()
                                                }
                                            }
                                        )
    return {   
                "powerbank_ID": powerbank_ID,
                "borrow_mai": 1,
                "yu_mai": 0,
                "user_ID": body.user_ID,
                "username": user["username"],
                "user_dept": user["user_dept"],
                "start_time": datetime.now().timestamp(),
                "end_time": (datetime.now() + timedelta(hours=5)).timestamp()
            }


@router.put('/return-laew/{powerbank_ID}')
def return_powerbank(powerbank_ID: int):
    powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))
    try:
        something = powerbank.pop(0)
    except IndexError as e:
        raise HTTPException(406, f"ID:{powerbank_ID} is not our powerbank.") from e
    powerbank_database.update_one(something, {"$set": {"yu_mai": 1}})
    return list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))[0]


# @router.put('/pai-laew/{powerbank_ID}')
# def pai_leaw_naaaa(powerbank_ID: int):
#     powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))
#     something = powerbank.pop(0)
#     powerbank_database.update_one(something, {"$set": {"yu_mai": 0}})
#     return list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))[0]


@router.put('/check-dai-mai/{powerbank_ID}')
def confirm_return(powerbank_ID: int):
    powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False}))
    something = powerbank.pop(0)
    if something["yu_mai"] == 1:
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


@router.put('/fee/{powerbank_ID}')
def fee(powerbank_ID: int):
    powerbank = powerbank_database.find({"powerbank_ID": powerbank_ID}, {'_id': False})
    something = powerbank.pop(0)
