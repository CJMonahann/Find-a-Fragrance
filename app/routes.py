from flask import render_template, jsonify, Flask, request, redirect, send_from_directory, url_for, abort, session
from app import app, db
from app.api import FragranceAPI #created API object to interact with API
from dotenv import load_dotenv
from app.models import Brands, Fragrances, Accords, Notes #tables in db
import json, os
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func

#load .env variables and collect paths to website data
load_dotenv()
API = FragranceAPI()

#used to load data from a .json file when given a path
def load_data(path):
    with open(path, "r") as file:
        data = json.load(file)
    return data

def check_db(API, j_brands):

    with app.app_context():
        db_brands = [b.name for b in Brands.query.all()] #brand names held in db
    
    if len(j_brands) != len(db_brands):
        populate_db(j_brands, API)

#load up fragrances - from given brands -  before the website is made available
def populate_db(brands, API):
    for b in brands: #the entire list of all brand names
        with app.app_context():
                if not Brands.query.filter_by(name=b).first(): #if brand not already had
                    new_brand = Brands(name=b)
                    db.session.add(new_brand)
                    db.session.commit()

                b_id = Brands.query.filter_by(name=b).first().id #to be used as brand foreign key in frag
                res = API.ret_fragrances(b)
                for frag in res: #returns a brand-specific list of dictionaries. Dicts are the frags
                     if not Fragrances.query.filter_by(perfume=frag["perfume"]).first(): #if frag not already had

                        new_frag = Fragrances(b_id = b_id,
                                              api_id_1 = frag.get("_id"),
                                              api_id_2 = frag.get("id"),
                                              perfume = frag.get("perfume"),
                                              desc = frag.get("description"),
                                              rating = frag.get("rating") if frag["rating"] else 0,
                                              img = frag.get("image"),
                                              url = frag.get("url")
                                            )
                        db.session.add(new_frag)
                        db.session.commit()

                        #get id of newly committed frag to be used as foreign key in coming relations
                        f_id = Fragrances.query.filter_by(perfume=frag["perfume"]).first().id
                        for acc in frag["accords"]:
                            new_acc = Accords(f_id = f_id, acc = acc)
                            db.session.add(new_acc)
                            db.session.commit()

                        for nt in frag["notes"]:
                            new_note = Notes(f_id = f_id, nt = nt)
                            db.session.add(new_note)
                            db.session.commit()    

data = load_data(os.getenv("__FRAGS_PATH"))
check_db(API, data["fragrances"])

#returns all fragrances held in the database - with all info
def get_all_frags():
    frags = Fragrances.query\
    .join(Brands, Fragrances.b_id == Brands.id)\
    .options(
        joinedload(Fragrances.accords),
        joinedload(Fragrances.notes),
        joinedload(Fragrances.brand)
    )\
    .all()

    return frags

#returns a randomized, limited number of fragrances - with all info
def get_lim_frags(num=5):
    frags = Fragrances.query\
    .join(Brands, Fragrances.b_id == Brands.id)\
    .options(
        joinedload(Fragrances.accords),
        joinedload(Fragrances.notes),
        joinedload(Fragrances.brand)
    )\
    .order_by(func.random())\
    .limit(num)\
    .all()

    return frags

@app.route('/')
@app.route('/HOME')
@app.route('/home')
def index():
    nts = data["info"]["nts"] # form: { "str":"str", ... }
    accs = data["info"]["accs"] # form: { "str":"str", ... }
    frags = get_lim_frags(3)
    return render_template('index.html', frags = frags, nts = nts, accs = accs)