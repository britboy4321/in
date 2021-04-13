import os
from datetime import datetime
from dateutil import *
class Newviewmodel:
    def __init__(self, items):
        self.items1 = items
    @property
    def items(self):
        return self.items1

class Todo:
    def __init__(self, id, title, carddate, status="Todo"):
        self.id = id
        self.title = title
        self.status = status
        self.carddate = carddate

    @classmethod
    def from_mongo_card(cls, card):
        id = ""
        title = ""
        status = "Todo"            # Will be overwritten by app 
        mongodate = datetime.today().strftime('%Y-%m-%d')
        