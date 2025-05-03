from flask import render_template, jsonify, Flask, request, redirect, send_from_directory, url_for, abort, session
from app import app, db
from app.api import FragranceAPI #created API object to interact with API
from dotenv import load_dotenv
from app.models import Brands, Fragrances, Accords, Notes #tables in db
import json, os
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func
from slugify import slugify

#load .env variables and collect paths to website data
load_dotenv()
API = FragranceAPI()

def slug_brand (brand):
    return slugify(brand, regex_pattern=r"[^\w\s&\*-]") #custom patter to slugify

app.jinja_env.filters['slugify'] = slug_brand #initialise slugify as a filter in Jinja to be used in templates

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

#LOADING NEEDED DATA FOR INDEX PAGE
#CHECKING DB BEFORE APP LAUNCH FOR ALL FRAGS
data = load_data(os.getenv("__FRAGS_PATH"))
concs = load_data(os.getenv("__CONCS_PATH"))
check_db(API, data["fragrances"])

#returns all brands held in the database - with all info
def get_all_brands():
    brands = Brands.query.all()
    return brands

#sorts the brands into a hashset based off each letter
def sort_brands(brands):
    letterSet = {}
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        letterSet[c] = []
    letterSet["*"] = []
    
    for b in brands:
        if b.name[0].upper() in letterSet:
            letterSet[b.name[0].upper()].append(b)
        else:
            letterSet["*"].append(b)
    return letterSet

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

#returns the fragrances associated with a specific brand when given a brand's ID
def get_brand_frags(b_id):
    return Fragrances.query.filter_by(b_id=b_id).all()

@app.route('/')
@app.route('/HOME')
@app.route('/home')
def index():
    nts = data["info"]["nts"] # form: { "str":"str", ... }
    accs = data["info"]["accs"] # form: { "str":"str", ... }
    frags = get_lim_frags(3)
    return render_template('index.html', frags = frags, concs = concs, nts = nts, accs = accs)

@app.route('/all/brands')
def all_brands():
    brands = get_all_brands()
    brandSet = sort_brands(brands)
    return render_template('all-brands.html', brandSet = brandSet)

@app.route('/brands/<slug>')
def selected_brand(slug):
    #check to see if brand exist. Select brand is true.
    brand = next(
        (b for b in Brands.query.all() if slug_brand(b.name) == slug),
        None
    )
    if not brand:
        abort(404)

    frags = get_brand_frags(brand.id) #collect all frags related to the brand
    return render_template('explore-brand.html', b_name = brand.name, frags = frags)

@app.route('/personal/web')
def redirect_web():
    return redirect(os.getenv("__PERSONAL_WEB"))

@app.route('/personal/github')
def redirect_gh():
    return redirect(os.getenv("__PERSONAL_GITHUB"))

@app.route('/personal/linkedin')
def redirect_ln():
    return redirect(os.getenv("__PERSONAL_LINKEDIN"))

@app.route('/personal/instagram')
def redirect_ig():
    return redirect(os.getenv("__PERSONAL_INSTAGRAM"))