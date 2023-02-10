from typing import Union
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from datetime import datetime
from database.database import user_database, powerbank_database

router = APIRouter(
        prefix="/powerbank2",
        tags=["powerbank2"],
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

@router.get('/all-powerbank')
def get_all_powerbank():
    return {"all_powerbank": list(powerbank_database.find({}, {"_id":False}))}

@router.put('/borrow-laew/{user_ID}/{password}/{powerbank_ID}')
def borrow_laew_naaaa(user_ID: int, password: str, powerbank_ID: int):
    filter_powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {"_id":False}))
    powerbank = filter_powerbank.pop(0)
    filter_user = list(user_database.find({"user_ID": user_ID}, {"_id":False}))
    user = filter_user.pop(0)
    if user_ID!=user["user_ID"]:
        return HTTPException(404, "The username is wrong.")
    if password!=user["password"]:
        return HTTPException(404, "The password is wrong")
    if powerbank["borrow_mai"]==0:
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"borrow_mai":1}})
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"user_ID":user_ID}})
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"yu_mai":0}})
        return powerbank
    return HTTPException(400, "This powerbank is currently being borrow.")


@router.put('/all-status')
def all_powerbank_status():
    pass

@router.get('/return-laew/{powerbank_ID}')
def return_powerbank(powerbank_ID: int):
    filter_powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {"_id":False}))
    powerbank = filter_powerbank.pop(0)
    if powerbank["borrow_mai"]==1:
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"borrow_mai":0}})
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"user_ID":0}})
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"yu_mai":1}})
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"username":""}})
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"user_dept":""}})
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"start_time":0}})
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"end_time":0}})
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"late_mai":0}})
        return powerbank
    return HTTPException(400, "This powerbank is not borrowed.")

@router.get('/pai-laew/{powerbank_ID}')
def pai_leaw_naaaa(powerbank_ID: int):
    filter_powerbank = list(powerbank_database.find({"powerbank_ID": powerbank_ID}, {"_id":False}))
    powerbank = filter_powerbank.pop(0)
    if powerbank["yu_mai"]==powerbank["borrow_mai"]:
        powerbank_database.update_one({"powerbank_ID": powerbank_ID},{"$set":{"yu_mai":0}})
        return powerbank
    return HTTPException(400, "The powerbank is still here.")