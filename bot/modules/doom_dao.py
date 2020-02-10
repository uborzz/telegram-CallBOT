from dataclasses import asdict, dataclass
from datetime import datetime

from pymongo.collection import Collection


@dataclass
class DoomedUser:
    uid: int
    first_name: str
    chat_id: int
    ts_doom: datetime
    ts_lib: datetime
    ts_reset: datetime

    @property
    def asdict(self):
        return asdict(self)


class DoomDAO:
    def __init__(self, db: Collection):
        self.db = db

    def find(self, uid: int, chat_id: int) -> DoomedUser:
        db_user = self.db.find_one({"uid": uid, "chat_id": chat_id}, {"_id": 0})
        return DoomedUser(**db_user) if db_user else None

    def doom(self, user: DoomedUser):
        self.db.insert_one(user.asdict)

    def undoom(self, user: DoomedUser):
        self.db.delete_one(user.asdict)

    def clear(self, time_now: datetime):
        self.db.delete_many({"ts_reset": {"$gt": time_now}})
