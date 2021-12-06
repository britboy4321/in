# SETUP INFO

# Flask

from flask import Flask, render_template, request, redirect, g, url_for, session
from flask_login import LoginManager, login_required, current_user
from flask_login.utils import login_user

# Loggly 

import logging.config

from loggly.handlers import HTTPSHandler
from logging import Formatter
import os, sys
print ("Current working directory : %s" % os.getcwd()    )


# from flask import LoginManager and login required
import requests                     # Import the whole of requests
import json                         # May not be needed
import os        # Secrets  (local only)
import pymongo   # required for new mongo database  
from datetime import datetime, timedelta   # Needed for Mongo dates for 'older' records seperation
from todo_app.todo import User              #Import simple user class
from oauthlib.oauth2 import WebApplicationClient # Security prep work


# import pytest   (Module 3 not completed yet but will need this stuff)
from todo_app.models.view_model import ViewModel
from todo_app.todo import Todo

app = Flask(__name__)


app.secret_key = os.environ["SECRET_KEY"]

##  Set token for module 13 - loggly

LOGGLY_TOKEN = os.environ["LOGGLY_TOKEN"]

#################################
#  MODULE 10 LOGIN MANAGER SETUP
#################################
login_manager = LoginManager()
client_id=os.environ["client_id"] 
Clientsecurity = WebApplicationClient(client_id)
LOG_LEVEL=os.environ["LOG_LEVEL"]
@login_manager.unauthorized_handler
def unauthenticated():
    print("Unauthorised, yet!")
    app.logger.info("Unauthorised, yet")

    result = Clientsecurity.prepare_request_uri("https://github.com/login/oauth/authorize")

    print(result)
    return redirect(result)

	# Github OAuth flow when unauthenticated

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

print ("Program starting right now") 
mongopassword=os.environ["mongopassword"]           # Secure password
# hardcoded password to go here if necessary                   
#Set up variables we'll be using...  
client = pymongo.MongoClient('mongodb+srv://britboy4321:' + mongopassword + '@cluster0.qfyqb.mongodb.net/myFirstDatabase?w=majority')


login_manager.init_app(app)
client_id=os.environ["client_id"]                   # Possibly not needed, defined earlier
client_secret=os.environ["client_secret"]           # For security
app.logger.debug("Getting Mongo connection string")
mongodb_connection_string = os.environ["MONGODB_CONNECTION_STRING"]
app.logger.debug("Setting client")
client = pymongo.MongoClient(mongodb_connection_string)
db = client.gettingStarted              # Database to be used
app.logger.debug("Database to be used is... $s:", db)

olddate = (datetime.now() - timedelta(days=5))   # Mongo: Used to hide staff unavailable for more than 5 days in dropdown

# olddate = (datetime.now() + timedelta(days=5))  #Uncomment this line to check 'older items'
                                                  # work without having to hang around for 5 days!
################################
print ("Program starting right now")

@app.route('/', methods = ["GET","PUT"])
@login_required
def index():

    mongosuperlist=[]               # The name of the Mongo OVERALL staff list with all items in it  
    mongo_view_model=[]             # The name of the Mongo AVAILABLE staff list (section of collection)
    mongo_view_model_doing=[]       # The name of the Mongo OFFSITE staff list (section of collection)
    mongo_view_model_done=[]        # The name of the Mongo UNAVAILABLE staff list (section of collection)
    mongo_view_model_olddone=[]     # Staff not available for 5 days+ (long term unavailable) stored here (section of collection) - seperated so they don't clog up 

    mongosuperlist = list(db.newposts.find()) 
 
    if LOGGLY_TOKEN is not None:
        handler = HTTPSHandler(f'https://logs-01.loggly.com/inputs/{LOGGLY_TOKEN}/tag/todo-app')
        handler.setFormatter(Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
       )
        app.logger.addHandler(handler)


#  Create the various lists depending on status
    counter=0                                           
    for mongo_card in mongosuperlist:
        
        #A list of mongo rows from the collection called 'newposts' 
        whatsthestatus=(mongosuperlist[counter]['status'])
        whatsthedate=(mongosuperlist[counter]['mongodate'])      # Need the date to seperate older 'Done'
        counter=counter+1                                   #Increment as need to get next list item
        if whatsthestatus == "todo":
            mongo_view_model.append(mongo_card)             # Append to the todo
        elif whatsthestatus == "doing":
            mongo_view_model_doing.append(mongo_card)       # Append to doing
        elif whatsthestatus == "done":
            if whatsthedate > olddate:
                mongo_view_model_done.append(mongo_card)        # Append to display in done - recently
            else: 
                mongo_view_model_olddone.append(mongo_card)     # Append to display in older done record            
                                                                # note: Invalid or no status won't appear at all

   # print("the current user is:  ")
    print(current_user.name)
    write_permission_user=(current_user.name)
    
    if (write_permission_user == "britboy4321"):
        current_user_role="writer"
    else:
        current_user_role="reader"

    print("CURRENT USER ROLE:")
    print(current_user_role)

   # If statement to go here:
   
    # allow_edit = (current_user.name)
    current_date = datetime.today().strftime('%d-%m-%Y')

    if (current_user_role == "writer"):                 # Can now handle multiple users
        return render_template('indexwrite.html',       # If user allowed to write: 
        passed_items_todo=mongo_view_model,             # Mongo To Do
        passed_items_doing=mongo_view_model_doing,      # Mongo Doing
        passed_items_done=mongo_view_model_done,        # Mongo Done
        passed_items_olddone=mongo_view_model_olddone,   # Old items ready to be displayed elsewhere
        write_permission_userhtml=write_permission_user,
        current_date=current_date
        )
    else:
        return render_template('indexread.html',        # If user NOT allowed to write: 
        passed_items_todo=mongo_view_model,             # Mongo To Do
        passed_items_doing=mongo_view_model_doing,      # Mongo Doing
        passed_items_done=mongo_view_model_done,        # Mongo Done
        passed_items_olddone=mongo_view_model_olddone,   # Old items ready to be displayed elsewhere
        write_permission_user=write_permission_user
        )
    

@app.route('/addmongoentry', methods = ["POST"])
@login_required
def mongoentry():
    app.logger.info("Mongo entry being added")
    write_permission_user=(current_user.name)
    if (write_permission_user == "britboy4321"):
        name = request.form['title']
        skillset = 'SQL, MongoDB, Terraform'
        skillset=os.environ["DEFAULT_SKILLS"]           # For admin purposes, adding new staff
        mongodict={'title':name,'status':'todo', 'mongodate':datetime.now().strftime('%d-%m-%Y'),'skills':skillset}
        db.newposts.insert(mongodict)
    return redirect("/")

@app.route('/move_to_doing_item', methods = ["PUT","GET","POST"])
@login_required
def move_to_doing_item():           # Called to move a 'card' to 'doing'
    app.logger.info("Mongo entry being moved to doing")
    write_permission_user=(current_user.name)
    if (write_permission_user == "britboy4321"):
        title = request.form['item_title']
        myquery = { "title": title }
        newvalues = { "$set": { "status": "doing" } }
        db.newposts.update_one(myquery, newvalues)
        for doc in db.newposts.find():  
            print(doc)
    return redirect("/")

@app.route('/move_to_done_item', methods = ["PUT","GET","POST"])
@login_required
def move_to_done_item():            # Called to move a 'card' to 'done'
    app.logger.info("Mongo entry being moved to done")
    write_permission_user=(current_user.name)
    if (write_permission_user == "britboy4321"):
        title = request.form['item_title']
        myquery = { "title": title }
        newvalues = { "$set": { "status": "done" } }
        db.newposts.update_one(myquery, newvalues)
        for doc in db.newposts.find():  
            print(doc)
    return redirect("/")

@app.route('/move_to_todo_item', methods = ["PUT","GET","POST"])
@login_required
def move_to_todo_item():            # Called to move a 'card' BACK to 'todo' (was useful)
    app.logger.warning("Mongo entry being moved back to todo - Process Issue")  # I want to keep this as WARNING as something is going wrong if done items arn't done!
    write_permission_user=(current_user.name)
    if (write_permission_user == "britboy4321"):
        title = request.form['item_title']
        myquery = { "title": title }
        newvalues = { "$set": { "status": "todo" } }
        db.newposts.update_one(myquery, newvalues)
        for doc in db.newposts.find():  
            print(doc)
    return redirect("/")

@app.route('/performsearch', methods = ["PUT","GET","POST"])
def performseach():
    searchterm = request.form['skillsearch']
    print("Current Search Term is:")
    print(searchterm)
    

    return redirect("/")


@app.route('/login/callback', methods = ["GET","POST"])
def login():

    # Get the access_token
    print("ABOUT TO PREPARE THE TOKEN REQUIRED")
    url, headers, body = Clientsecurity.prepare_token_request(
        "https://github.com/login/oauth/access_token",
        authorization_response=request.url
    )

    print("REACHED TOKEN RESPONSE")
    token_response = requests.post(
        url,
        headers=headers,
        data=body,
        auth=(client_id, client_secret)
        )

    # Now to get the users data
    print("Reached parsing into Client security")
    Clientsecurity.parse_request_body_response(token_response.text)
    url, headers, body = Clientsecurity.add_token("https://api.github.com/user")
    print("Reached user_response")    
    user_response = requests.get(url, headers=headers, data=body) 
    the_user_name = user_response.json()['login']
    print("Attempting to login user")
    login_user(User(the_user_name))
    print("Reached return")
    return redirect("/")

if __name__ == '__main__':
   
   app.run()
