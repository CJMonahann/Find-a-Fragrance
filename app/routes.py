from flask import render_template, jsonify, Flask, request, redirect, send_from_directory, url_for, abort, session
from app import app, db
from app.api import FragranceAPI #created API object to interact with API
from dotenv import load_dotenv
from app.models import Brands, Fragrances, Accords, Notes #tables in db
import json, os
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import func
from slugify import slugify
import re
from sentence_transformers import SentenceTransformer
import numpy as np

#used to load data from a .json file when given a path
def load_data(path):
    with open(path, "r") as file:
        data = json.load(file)
    return data

'''
 - Load .env variables and collect paths to website data
 - Create machine learning model for creating embedded vectors
 - LOADING NEEDED DATA FOR VARIOUS PAGES
'''
load_dotenv()
DATA = load_data(os.getenv("__FRAGS_PATH"))
CONCS = load_data(os.getenv("__CONCS_PATH"))
SEASONS = load_data(os.getenv("__SNS_PATH"))
API = FragranceAPI()
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

#custom slug filter to rename brand names in the web page's url
def slug_brand (brand):
    return slugify(brand, regex_pattern=r"[^\w\s&\*-]") #custom patter to slugify

app.jinja_env.filters['slugify'] = slug_brand #initialise slugify as a filter in Jinja to be used in templates

#checks db to ensure that all brands provided in the loaded fragrances.json file are in the db
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

                        #create embedding, turning into JSON string, to be used in vector search
                        emb_str = f"{frag.get("perfume")} is a fragrance described as: {frag.get("description")}.\
                        It features notes of {', '.join(frag.get("notes"))}. Main accords include: {', '.join(frag.get("accords"))}"
                        vector = get_embedding(emb_str) #creates vector from the above string desc
                        
                        new_frag = Fragrances(b_id = b_id,
                                              api_id_1 = frag.get("_id"),
                                              api_id_2 = frag.get("id"),
                                              perfume = frag.get("perfume"),
                                              desc = frag.get("description"),
                                              rating = frag.get("rating") if frag["rating"] else 0,
                                              img = frag.get("image"),
                                              url = frag.get("url"),
                                              embedding = vector
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
                         

# Get an embedding for a piece of text
def get_embedding(text):
    return MODEL.encode(text).tolist()

#computes the cosine similarity between two vectors
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

#returns recommended colognes based off cosine similarities of all colognes
def get_recs(query_emb, MAX=9):
    frags = get_all_frags()

    #compute similarities using each frag's vector embedding
    scores = []
    for f in frags:
        if f.embedding: #if an embedding is had
            cs = cosine_similarity(query_emb, f.embedding)
            scores.append((cs, f))
    
    #sort by similarity in descending order
    scores.sort(reverse=True, key=lambda x: x[0]) #uses cs - similarity

    #return a sub-list of a given 'MAX' number of frags
    return [f for cs, f in scores[:MAX]]

#CHECKING DB BEFORE APP LAUNCH FOR ALL FRAGS
check_db(API, DATA["fragrances"])

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

#returns the fragrances associated with a specific gender identity when given a gender str
def get_gendered_frags(gender):
        pattern = fr'\b{re.escape(gender.lower())}\b'
        print(pattern)
        # Query that joins and filters all fragrances based on the 'gender' keyword provided
        frags = db.session.query(Fragrances).join(Notes).join(Accords).filter(
            func.lower(Fragrances.desc).op('REGEXP')(pattern)
        ).distinct().all()

        if not(frags): #if no frags were found matching criteria (e.g. - unisex)
            frags = get_lim_frags(30)
        
        return frags

#returns the fragrances associated with a specific season when given a season str
def get_seasoned_frags(dict):
    query = db.session.query(Fragrances).join(Notes).join(Accords)

    # Build dynamic filters
    filters = []
    
    if dict.get("keywords"):
        desc_filters = [
            func.lower(Fragrances.desc).like(f"%{word.lower()}%") for word in dict["keywords"]
        ]
        filters.append(or_(*desc_filters))
    
    if dict.get("nts"): #dict contains a list if true
        note_filters = [
            func.lower(Notes.nt).like(f"%{note.lower()}%") for note in dict["nts"]
        ]
        filters.append(or_(*note_filters))
    
    if dict.get("accs"): #dict contains a list if true
        accord_filters = [
            func.lower(Accords.acc).like(f"%{accord.lower()}%") for accord in dict["accs"]
        ]
        filters.append(or_(*accord_filters))
    
    # Apply filters
    if filters:
        query = query.filter(*filters)

    # Avoid duplicates from joins
    frags = query.distinct().all()
    return frags


@app.route('/')
@app.route('/HOME')
@app.route('/home')
def index():
    nts = DATA["info"]["nts"] # form: { "str":"str", ... }
    accs = DATA["info"]["accs"] # form: { "str":"str", ... }
    frags = get_lim_frags(3)
    return render_template('index.html', frags = frags, concs = CONCS, nts = nts, accs = accs)

@app.route('/search/desc', methods=['POST'])
def user_search():
    user_inpt = request.form['query']
    user_vect = get_embedding(user_inpt)
    frags = get_recs(user_vect)
    return render_template('user-query.html', frags = frags)

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

@app.route('/seasons/frags/<season>')
def selected_season(season):
    frags = get_seasoned_frags(SEASONS[season]) #passes: dict containing a season's frag info
    season = season[0].upper() + season[1:] #capitalize the first letter of the string
    return render_template('seasoned-frags.html', season = season, frags = frags)

@app.route('/gender/frags/<gender>')
def selected_gender(gender):
    frags = get_gendered_frags(gender)
    gender = gender[0].upper() + gender[1:]
    return render_template('gendered-frags.html', gender = gender, frags = frags)

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