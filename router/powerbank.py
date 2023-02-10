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
    all_users = list(user_database.find({"user_ID": body.user_ID, "password": body.password}, {'_id': False}))
    if not len(all_users):
        raise HTTPException(401, "UserID and Password doesn't match.")
    user = all_users.pop(0)
    powerbank_database.update_one(something, {"$set": 
                                                {
                                                    "borrow_mai": 1,
                                                    "yu_mai": 0,
                                                    "user_ID": body.user_ID,
                                                    "username": user["username"],
                                                    "user_dept": user["user_dept"],
                                                    "start_time": datetime.now().timestamp(),
                                                    "end_time": (datetime.now() + timedelta(hours=5)).timestamp()
                                                }
                                            }
                                        )
    return something


@router.put('/return-laew')
def return_powerbank(powerbank_ID: int):
    pass


@router.put('/pai-laew')
def pai_leaw_naaaa(powerbank_ID: int):
    pass
