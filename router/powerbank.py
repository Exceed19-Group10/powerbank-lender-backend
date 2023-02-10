from typing import Union
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from datetime import datetime
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


@router.get('/all-powerbank')
def get_all_powerbank():
    pass


@router.put('/borrow-laew')
def borrow_laew_naaaa(user_ID: int, password: str, powerbank_ID: int):
    pass


@router.put('/all-status')
def all_powerbank_status():
    pass


@router.put('/return-laew')
def return_powerbank(powerbank_ID: int):
    pass


@router.put('/pai-laew')
def pai_leaw_naaaa(powerbank_ID: int):
    pass
