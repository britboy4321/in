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
    def from_trello_card(cls, card):
        id = card["id"]
        title = card["name"]
        status = ""
        firstcarddate = card["dateLastActivity"]
        carddate = firstcarddate[:10]               # Just need date bit, not the time etc
        currentcarddate = datetime.today().strftime('%Y-%m-%d') # Now just need today's date
        currentcarddatefor = parser.parse(currentcarddate)  # The above line turned it into a string, turn back into a date
        indateformat = datetime.strptime(carddate,'%Y-%m-%d')   


        if card["idList"] == os.environ["todo_listid"]:
            status = "Todo"
        elif card["idList"] == os.environ["done_listid"]:
            if indateformat >= currentcarddatefor:
                status = "RecentlyDone"
            else:
                status = "Done"
        elif card["idList"] == os.environ["doing_listid"]:
            status = "Doing"
        new_class_instance = cls(id, title, carddate, status)
        return new_class_instance


    @classmethod
    def from_mongo_card(cls, card):
        id = ""
        title = ""
        #id = card["id"]
        #title = card["name"]
        # status = ""
        # firstcarddate = card["dateLastActivity"]
        # carddate = firstcarddate[:10]               # Just need date bit, not the time etc
        # currentcarddate = datetime.today().strftime('%Y-%m-%d') # Now just need today's date
        # currentcarddatefor = parser.parse(currentcarddate)  # The above line turned it into a string, turn back into a date
        # indateformat = datetime.strptime(carddate,'%Y-%m-%d')   

        status = "Todo"            # Temporary - set them all to doing


#All the next section is useless as it refers to trello
#        if card["idList"] == os.environ["todo_listid"]:
#            status = "Todo"
#        elif card["idList"] == os.environ["done_listid"]:
#            if indateformat >= currentcarddatefor:
#                status = "RecentlyDone"
#            else:
#                status = "Done"
#        elif card["idList"] == os.environ["doing_listid"]:
#            status = "Doing"
#        new_class_instance = cls(id, title, carddate, status)
#        return new_class_instance
