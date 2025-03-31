from flask import render_template, jsonify, Flask, request, redirect, send_from_directory, url_for, abort, session
from app import app
from app.api import FragranceAPI
from dotenv import load_dotenv
import json, os

#load .env variables and collect paths to website data
load_dotenv()
frag = FragranceAPI()
frags = [] # a list of the available frags in the form: [ {1}, {2}, ... ]


#used to load data from a .json file when given a path
def load_data(path):
    with open(path, "r") as file:
        data = json.load(file)
    return data

#load up fragrances - from given brands -  before the website is made available
def collect_fragrances():
    brands = load_data(os.getenv("__FRAGS_PATH"))
    for b in brands["fragrances"]: #the entire list of all brand names
        print(b)
        res = frag.ret_fragrances(b)
        frags.extend(res)

collect_fragrances()

@app.route('/')
@app.route('/HOME')
@app.route('/home')
def index():
    print(len(frags))
    return render_template('index.html', frags=frags)
