from dataclasses import asdict, dataclass, field
from typing import Dict, List, Union

from pymongo.collection import Collection

from bot.zzlib import SimplifiedUser


@dataclass
class Call:
    group: int
    name: str
    owner: SimplifiedUser
    desc: str
    users: List[Union[SimplifiedUser, Dict]] = field(default_factory=list)

    def __post_init__(self):

        self.name = self.name.lower()
        self.owner = (
            SimplifiedUser(**self.owner) if type(self.owner) is dict else self.owner
        )
        self.desc = self.desc if self.desc else f"CALL: {self.name.upper()}!"
        self.users = [
            SimplifiedUser(**user) if type(user) is dict else user
            for user in self.users
        ]

    @property
    def asdict(self):
        return asdict(self)


class CallsDAO:
    def __init__(self, db: Collection):
        self.db = db

    def get_call(self, chat_id: int, call_name: str) -> Call:
        call = self.db.find_one({"group": chat_id, "name": call_name}, {"_id": 0})
        return Call(**call) if call else None

    def get_call_creator(self, chat_id: int, call_name: str) -> SimplifiedUser:
        partial = self.db.find_one(
            {"name": call_name, "group": chat_id}, {"owner": 1, "_id": 0}
        )
        return SimplifiedUser(**partial["owner"]) if partial else None

    def delete_call(self, chat_id: int, call_name: str) -> None:
        self.db.find_one_and_delete({"name": call_name, "group": chat_id})

    def get_group_calls(self, chat_id: int) -> List[Call]:
        calls = self.db.find({"group": chat_id}, {"_id": 0})
        return [Call(**call) for call in calls]

    def check_call_exists(self, chat_id: int, call_name: str) -> bool:
        call = self.db.find_one({"group": chat_id, "name": call_name.lower()})
        return True if call else False

    def create_call(self, call: Call) -> None:
        self.db.insert_one(call.asdict)

    def modify_call_description(self, name: str, chat_id: int, desc: str):
        call = self.db.find_one_and_update(
            {"name": name.lower(), "group": chat_id}, {"$set": {"desc": desc}}
        )
        return True if call else False

    def add_users_to_call(self, name: str, chat_id: int, users: List[SimplifiedUser]):
        return self.db.find_one_and_update(
            {"name": name, "group": chat_id},
            {"$addToSet": {"users": {"$each": [user.asdict for user in users]}}},
        )

    def remove_users_from_call(
        self, name: str, chat_id: int, users_ids: List[int]
    ) -> None:
        self.db.find_one_and_update(
            {"name": name, "group": chat_id},
            {"$pull": {"users": {"uid": {"$in": users_ids}}}},
            {"multi": True},
        )
