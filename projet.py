import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime
import re
import seaborn as sns
import matplotlib.pyplot as plt
import requests
import json
import plotly.graph_objs as go
from plotly.offline import plot
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pandas.io.json import json_normalize
from IPython.display import clear_output
st.set_page_config(layout="wide")
import plotly.express as px
import plotly.graph_objs as go

#connection a la base de données en local 

client = pymongo.MongoClient("mongodb://127.0.0.1:27017/lmdb?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.6.1")

#titre 

st.markdown(f"""
<div style= " padding-top:60px; padding-bottom:60px;">
   <h1 style="text-align: center"> Analyse des jeux les plus populaire sur Twitch et Steam  </h1>
</div>
""", unsafe_allow_html=True)

#création des deux dbb et des collection
db2 = client["base_historique"]
collection_avec_historique = db2["collection_historique"]


db = client["base_sans_historique"]
collection_sans_historique = db["collections_sans_historiques"]

data = list(collection_avec_historique.find())
df_plot = pd.DataFrame(data)
#api key twitch
headers = {
    "Client-Id": "9orvggc3ntj27cz7zjxr5l0g6pn8hk",
    "Authorization": "Bearer 5xmnmgqdqppbk38q9f4fnizgc6osc9"
}
st.sidebar.markdown("## Liste des jeux:")


limit=100


#Get sur api twitch et ajout a la bdd avec historique
def twitch_save():

    now = datetime.now()
    current_time = datetime(now.year, now.month, now.day, now.hour,now.minute)
    
    db = client["base_historique"] 
    collection_avec_historique = db["collection_hist_jeux_twitch"]
    games_response = requests.get('https://api.twitch.tv/helix/games/top', headers=headers,params={"first":limit})
    games_response_json = json.loads(games_response.text)
    topgames_data = games_response_json['data']
    topgames_df = pd.DataFrame.from_dict(json_normalize(topgames_data), orient='columns')
    for game in topgames_df.iterrows():
        id_game = game[1]['id']
        name = game[1]['name']
        url = "https://api.twitch.tv/helix/streams?game_id={}".format(id_game)
        response = requests.get(url, headers=headers)
        data = response.json()['data']
        viewer_count_list = []
        total_viewer = 0
        for stream in data:
            viewer_count = stream['viewer_count']
            total_viewer += viewer_count
            user_name = stream['user_name']
            started_at = stream['started_at']
            viewer_count_list.append({'user_name':user_name,'viewer_count':viewer_count})
        json_obj = {'total_viewer':total_viewer,'started_at':started_at, 'date':current_time}
      
        collection_avec_historique.update_one({'id_game': id_game,'name':name,}, {'$push': {'history': json_obj}}, upsert=True)

#Scrapping sur la page steam et ajout a la bdd avec historique
def steam_save():

    now = datetime.now()
    current_time = datetime(now.year, now.month, now.day, now.hour,now.minute)
    
    db = client["base_historique"]
    collection_avec_historique = db["collection_hist_jeux_steam"]    
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)
    browser.get('https://store.steampowered.com/charts/mostplayed/')
    WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'tr')))
    elem= browser.find_elements(By.TAG_NAME, 'tr')
    ranks= browser.find_elements(By.CLASS_NAME, 'weeklytopsellers_RankCell_34h48')
    names= browser.find_elements(By.CLASS_NAME, 'weeklytopsellers_GameName_1n_4-')
    joueur_acts= browser.find_elements(By.CLASS_NAME, 'weeklytopsellers_ConcurrentCell_3L0CD')

    data = {
        'rank' : [int(rank.text) for rank in ranks],
        'name' : [name.text for name in names],
        'joueur_acts' : [int(joueur_act.text.replace("\u202f", "").replace(" ", "")) for joueur_act in joueur_acts]
    }
  
    df = pd.DataFrame(data)
  
    data_list = df.to_dict(orient="records")

    for game in data_list:
        game_id = game["name"]
        json_obj = {'rank': game["rank"],'joueur_acts': game["joueur_acts"], 'date':current_time}
        collection_avec_historique.update_one({'name': game_id}, {'$push': {'history': json_obj}}, upsert=True)
    browser.quit()
#Scrapping sur la page des best channel twith par jeu et ajout a la bdd avec historique
  
def chanel_save():
    now = datetime.now()
    current_time = datetime(now.year, now.month, now.day, now.hour,now.minute)
    db = client["base_historique"]
    collection_avec_historique = db["collection_hist_chanel"]
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)

    for page in range(1, 6):
        page_url = "https://twitchtracker.com/games/average-channels?page=" + str(page)
        browser.get(page_url)
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'div')))
        elem= browser.find_elements(By.CLASS_NAME, 'ranked-item')
        ranks= browser.find_elements(By.CLASS_NAME, 'ri-position')
        names= browser.find_elements(By.CLASS_NAME, 'ri-name')
        chanels= browser.find_elements(By.CLASS_NAME, 'ri-value')
    
        data = {
            'rank' : [int(float(rank.text.replace("#", ""))) for rank in ranks],
            'name' : [name.text for name in names],
            'chanel' : [int(float(chanel.text.replace("K", "")) * 1000 if "K" in chanel.text else chanel.text) for chanel in chanels]}

        df = pd.DataFrame(data)

        data_list = df.to_dict(orient="records")
            
        for game in data_list:
            game_id = game["name"]
            json_obj = {'rank': game["rank"], 'chanel': game["chanel"], 'date': current_time}
            collection_avec_historique.update_one({'name': game_id}, {'$push': {'history': json_obj}}, upsert=True)
    browser.quit()

#Projection des données des api chanel et twitch dans une nouvelle collection
def merge_hist_twitch_chanel():
    result = client['base_historique']['collection_hist_jeux_twitch'].aggregate([
        {
            '$lookup': {
                'from': 'collection_hist_chanel', 
                'localField': 'name', 
                'foreignField': 'name', 
                'as': 'collection_hist_chanel'
            }
        },
        {
            '$unwind': '$collection_hist_chanel'
        },
        {
            '$project': {
                '_id': 0,
                'id_game': 1,
                'name': 1,
                'total_viewer': {'$arrayElemAt': ['$history.total_viewer', -1]}, 
                'date': {'$arrayElemAt': ['$collection_hist_chanel.history.date', -1]}, 
                'joueur_acts': {'$arrayElemAt': ['$history.joueur_acts', -1]},
                'chanel': {'$arrayElemAt': ['$collection_hist_chanel.history.chanel', -1]}
                                            
            }
        }
    ])
    for item in result:
        client['base_historique']['collection_hist_twitch_chanel'].update_one({'id_game': item['id_game'], 'name': item['name']}, {'$push': {'history': item}}, upsert=True)
        
#Projection des données de la nouvelle collection et de steam dans une nouvelle collection
def merge_hist_twitch_chanel_steam():
    result = client['base_historique']['collection_hist_twitch_chanel'].aggregate([
        {
            '$lookup': {
                'from': 'collection_hist_jeux_steam', 
                'localField': 'name', 
                'foreignField': 'name', 
                'as': 'collection_hist_jeux_steam'
            }
        },
        {
            '$unwind': '$collection_hist_jeux_steam'
        },
        {
            '$project': {
                '_id': 0,
                'id_game': 1,
                'name': 1,
                'total_viewer': {'$arrayElemAt': ['$history.total_viewer', -1]}, 
                'date': {'$arrayElemAt': ['$history.date', -1]}, 
                'joueur_acts': {'$arrayElemAt': ['$history.joueur_acts', -1]},
                'chanel': {'$arrayElemAt': ['$history.chanel', -1]},
                'joueur_acts': {'$arrayElemAt': ['$collection_hist_jeux_steam.history.joueur_acts', -1]},
                'rank': {'$arrayElemAt': ['$collection_hist_jeux_steam.history.rank', -1]}
            }
        }
    ])
    for item in result:
        client['base_historique']['collection_historique'].update_one({'id_game': item['id_game'], 'name': item['name']}, {'$push': {'history': item}}, upsert=True)





def twitch():
    db = client["base_sans_historique"]
    collection_sans_historique = db["collection_jeux_twitch"]
    games_response = requests.get('https://api.twitch.tv/helix/games/top', headers=headers,params={"first":limit})
    games_response_json = json.loads(games_response.text)
    topgames_data = games_response_json['data']
    topgames_df = pd.DataFrame.from_dict(json_normalize(topgames_data), orient='columns')
    for game in topgames_df.iterrows():
        id_game = game[1]['id']
        name = game[1]['name']
        url = "https://api.twitch.tv/helix/streams?game_id={}".format(id_game)
        response = requests.get(url, headers=headers)
        data = response.json()['data']
        viewer_count_list = []
        total_viewer = 0
        for stream in data:
            viewer_count = stream['viewer_count']
            total_viewer += viewer_count
            user_name = stream['user_name']
            started_at = stream['started_at']
            viewer_count_list.append({'user_name':user_name,'viewer_count':viewer_count})
        json_obj = {'id_game':id_game,'name':name,'total_viewer':total_viewer,'started_at':started_at}
        collection_sans_historique.update_one({'id_game': id_game}, {'$set': json_obj}, upsert=True)

def steam():
    db = client["base_sans_historique"]
    collection_sans_historique = db["collection_jeux_steam"]
    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)
    browser.get('https://store.steampowered.com/charts/mostplayed/')
    WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'tr')))
    elem= browser.find_elements(By.TAG_NAME, 'tr')
    ranks= browser.find_elements(By.CLASS_NAME, 'weeklytopsellers_RankCell_34h48')
    names= browser.find_elements(By.CLASS_NAME, 'weeklytopsellers_GameName_1n_4-')
    joueur_acts= browser.find_elements(By.CLASS_NAME, 'weeklytopsellers_ConcurrentCell_3L0CD')
    collection_sans_historique.delete_many({})
    data = {
        'rank' : [int(rank.text) for rank in ranks],
        'name' : [name.text for name in names],
        'joueur_acts' : [int(joueur_act.text.replace("\u202f", "").replace(" ", "")) for joueur_act in joueur_acts]
    }



    df = pd.DataFrame(data)
    print(df)
    data_list = df.to_dict(orient="records")
    collection_sans_historique.insert_many(df.to_dict("records"))
    browser.quit()

def channels():
    db = client["base_sans_historique"]
    collection_sans_historique = db["collection_channels"]
    collection_sans_historique.delete_many({})

    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)
  
    for page in range(1, 6):
        page_url = "https://twitchtracker.com/games/average-channels?page=" + str(page)
        browser.get(page_url)
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'div')))
        elem= browser.find_elements(By.CLASS_NAME, 'ranked-item')
        ranks= browser.find_elements(By.CLASS_NAME, 'ri-position')
        names= browser.find_elements(By.CLASS_NAME, 'ri-name')
        chanels= browser.find_elements(By.CLASS_NAME, 'ri-value')

        # Extract the relevant information from the elements and create a list of dictionaries
        data = {
            'rank' : [int(float(rank.text.replace("#", ""))) for rank in ranks],
            'name' : [name.text for name in names],
            'chanel' : [int(float(chanel.text.replace("K", "")) * 1000 if "K" in chanel.text else chanel.text) for chanel in chanels]
        }

        df = pd.DataFrame(data)
        print(df)

        # Insert the data into the collection
        data_list = df.to_dict(orient="records")
        collection_sans_historique.insert_many(df.to_dict("records"))
     



def merge_twitch_steam():

      result = client['base_sans_historique']['collection_jeux_twitch'].aggregate([
        {
            '$lookup': {
                'from': 'collection_jeux_steam', 
                'localField': 'name', 
                'foreignField': 'name', 
                'as': 'rank'
            }
        },
        {
            '$project': {
                '_id': 1,
                'id_game': 1,
                'name': 1,
                'started_at': 1,
                'total_viewer': 1,
                'joueur_acts': {
                    '$arrayElemAt': [
                        '$rank.joueur_acts', 0
                    ]
                },
                'rank': {
                    '$arrayElemAt': [
                        '$rank.rank', 0
                    ]
                }
            }
        },
        {
            '$out': { 'db': 'base_sans_historique', 'coll': 'collections_twitch_steam' }
        }
    ])


def merge_twitch_steam_chanel():

      result = client['base_sans_historique']['collections_twitch_steam'].aggregate([
        {
            '$lookup': {
                'from': 'collection_channels', 
                'localField': 'name', 
                'foreignField': 'name', 
                'as': 'collection_channels'
            }
        },
        {
            '$project': {
                '_id': 1,
                'id_game': 1,
                'name': 1,
                'started_at': 1,
                'total_viewer': 1,
                'joueur_acts': 1,
                'rank': 1,
                'chanel': {
                    '$arrayElemAt': [
                        '$collection_channels.chanel', 0
                    ]
                }
            }
        },
        {
            '$out': { 'db': 'base_sans_historique', 'coll': 'collections_sans_historiques' }
        }
    ])




#affichage des données en temps reel et des donées avec historique + creation des bouttons de mise a jour
options = ["Données", "Données historiques"]
selected_collection = st.sidebar.selectbox("Sélectionner la collection à afficher:", options)
if selected_collection == "Données":
    games = collection_sans_historique.find()
    if st.sidebar.button('Mettre à jour les données'):
        twitch()
        steam()
        channels()
        merge_twitch_steam()
        merge_twitch_steam_chanel()
#recherche d'un jeu par id ou par nom
    id_game = st.sidebar.text_input("Recherche par id ou par nom:")
    if id_game:
        result = collection_sans_historique.find({"$or": [{"id_game": id_game}, {"name": id_game}]})
        df_plot = pd.DataFrame(result)
        st.sidebar.dataframe(df_plot)
    for game in games:
        st.sidebar.write(game)

elif selected_collection == "Données historiques":
    games2 = collection_avec_historique.find()
    
    if st.sidebar.button('Mettre à jour les données'):
        twitch_save()
        steam_save()
        chanel_save()
        merge_hist_twitch_chanel()
        merge_hist_twitch_chanel_steam()
    id_game = st.sidebar.text_input("Recherche par id ou par nom:")
    if id_game:
        result2 = collection_avec_historique.find({"id_game": id_game})
        df_plot2 = pd.DataFrame(result2)
        st.sidebar.dataframe(df_plot2)
    for game in games2:
        st.sidebar.write(game)

#calcule et affichage de la somme de total_viewer joueur_acts et channel
col1, col2, col3 = st.columns(3)

pipeline = [{"$group": {"_id": None, "total_viewer_sum": {"$sum": "$total_viewer"}}}]
result = collection_sans_historique.aggregate(pipeline)

for res in result:
    col1.markdown(f"""
<h1 style='border: 3px #6A31E0 solid ; border-radius: 10px; padding: 20px 20px 20px 70px; margin-bottom:50px;margin-top:50px'>
Total viewer: <span style=''> 
        {res["total_viewer_sum"]}
    </span>
</h1>
""", unsafe_allow_html=True)
    
   


pipeline = [{"$group": {"_id": None, "joueur_acts": {"$sum": "$joueur_acts"}}}]
result = collection_sans_historique.aggregate(pipeline)
for res in result:
    col2.markdown(f"""

    
<h1 style='border: 3px #1271A6 solid ; border-radius: 10px; padding: 20px 20px 20px 70px; margin-bottom:50px;margin-top:50px'>
Total player: <span style=''> 
        {res["joueur_acts"]}
    </span>
</h1>


""", unsafe_allow_html=True)



pipeline = [{"$group": {"_id": None, "chanel": {"$sum": "$chanel"}}}]
result = collection_sans_historique.aggregate(pipeline)
for res in result:
    col3.markdown(f"""
<h1  style='border: 2px #fff solid ; border-radius: 10px; padding: 20px 20px 20px 70px; margin-bottom:50px;margin-top:50px'>
Total channel: <span style=''> 
        {res["chanel"]}
    </span>
</h1>
""", unsafe_allow_html=True)

# creation du boutton suppression par id et des champs necessaire

col1.markdown("## Suppression")
id_game = col1.text_input("entrer id du jeu a supprimer")
if len(id_game) > 0:
    if not id_game.isdigit():
        col1.error("Erreur: veuillez saisir un entier.")
        id_game = None
if col1.button("Suppression"):
    document = collection_sans_historique.find_one({"id_game": id_game})
    if document is None:
        col1.error("Aucun jeu trouvé avec l'ID saisi.")
    else:
        collection_sans_historique.delete_many({"id_game": id_game})
        col1.success("Jeu supprimé avec succès")

col1.markdown(f"""
<div style="margin-bottom:100px;">
    
</div>
""", unsafe_allow_html=True)


# creation du boutton modification par id et des champs necessaire

        
col2.markdown("## Modification")
# Mise à jour
id_game = col2.text_input("veuillez Entrer id du jeu à modifier")
if len(id_game) > 0:
    if not id_game.isdigit():
        col2.error("Erreur: veuillez saisir un entier.")
        id_game = None
document = collection_sans_historique.find_one({"id_game": id_game})
if document is None :
    st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #6A31E0;
        color:#ffffff;
        font-size:20;
        padding: 15px 50px;
        
    }
    div.stButton > button:hover {
        background-color: transparent;
        color:#ffffff;
        border: 1px solid #6A31E0
        }
    .st-au:hover{
    
        border: 1px solid #6A31E0
    }
    .st-au:select{
    
        border: 1px solid #6A31E0
    }
  
   
    </style>""", unsafe_allow_html=True)
    if col2.button("modification"):
    
        col2.error("Aucun jeu trouvé avec l'ID saisi.")
else:
    document = collection_sans_historique.find_one({"id_game": id_game})
    if document :
        name = document["name"]
        new_name = col2.text_input("Nouveau nom du jeu", name)
        total_viewer = document["total_viewer"]
        new_total_viewer = col2.text_input("Nouveau Nombre de viewer", total_viewer)
        if len(new_total_viewer) > 0:
            if not new_total_viewer.isdigit():
                col2.error("Erreur: veuillez saisir un entier.")
                new_total_viewer = None
        
        date = col2.date_input("Sélectionnez la nouvelle date: ", key=f'unique_date')
        time = col2.text_input("Sélectionnez la nouvelle l'heure (HH:MM:SS): ",  key=f'unique_time')
# Vérifier si la valeur saisie est valide
        if len(time) > 0:
            match = re.match("^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$",time)
            if match is None:
                col2.error("Format de l'heure non valide. Veuillez entrer l'heure au format HH:MM.")
                time = None
        new_started_at = str(date) + " " + str(time)
        joueur_acts = document.get("joueur_acts",'')
        new_joueur_acts = col2.text_input("Nouveau Nombre de joueur",joueur_acts)
        if len(new_joueur_acts) > 0:
            if not new_joueur_acts.isdigit():
                col2.error("Erreur: veuillez saisir un entier.")
                new_joueur_acts = None
        rank = document.get("rank",'')
        new_rank = col2.text_input("Nouveau rank",rank)
        if len(new_rank) > 0:
            if not new_rank.isdigit():
                col2.error("Erreur: veuillez saisir un entier.")
                new_rank = None
        chanel = document.get("chanel",'')
        new_chanel = col2.text_input("Nouveau chanel",chanel)
        if len(new_chanel) > 0:
            if not new_chanel.isdigit():
                col2.error("Erreur: veuillez saisir un entier.")
                new_chanel = None
    if col2.button("Mise à jour"):
        collection_sans_historique.update_one({"id_game": id_game}, {"$set": {"name": new_name,"joueur_acts":new_joueur_acts,"rank":new_rank,"chanel":new_chanel,'total_viewer':new_total_viewer,'started_at':new_started_at}})
        col2.success("Jeu mis à jour avec succès")

# creation du boutton insertion et des champs necessaire
col3.markdown("## Insertion")
name = col3.text_input("Nom du jeu")
id_game = col3.text_input("id du jeu")
if len(id_game) > 0:
    if not id_game.isdigit():
        col3.error("Erreur: veuillez saisir un entier.")
        id_game = None
total_viewer = col3.text_input("Nombre de viewer")
if len(total_viewer) > 0:
    if not total_viewer.isdigit():
        col3.error("Erreur: veuillez saisir un entier.")
        total_viewer = None
rank = col3.text_input("Rank")
if len(rank) > 0:
    if not rank.isdigit():
        col3.error("Erreur: veuillez saisir un entier.")
        rank = None
chanel = col3.text_input("chanel")
if len(chanel) > 0:
    if not chanel.isdigit():
        col3.error("Erreur: veuillez saisir un entier.")
        chanel = None
joueur_acts = col3.text_input("Nombre de joueur")
if len(joueur_acts) > 0:
    if not joueur_acts.isdigit():
        col3.error("Erreur: veuillez saisir un entier.")
        joueur_acts = None
if len(total_viewer) > 0:
    total_viewer = int(total_viewer)
date = col3.date_input("Sélectionnez la date: ")
time = col3.text_input("Sélectionnez l'heure (HH:MM:SS): ")
# Vérifier si la valeur saisie est valide
if len(time) > 0:
    match = re.match("^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$",time)
    if match is None:
        col3.error("Format de l'heure non valide. Veuillez entrer l'heure au format HH:MM:SS.")
        time = None
started_at = str(date) + " " + str(time)

if col3.button("Insertion"):
    json_obj = {'id_game':id_game,'name':name,'total_viewer':total_viewer,'joueur_acts':joueur_acts,'chanel':chanel,'rank':rank,'started_at':started_at}
    collection_sans_historique.insert_one(json_obj)
    col3.success("Jeu ajouté avec succès")

data = list(collection_sans_historique.find())
df_plot = pd.DataFrame(data)

df_plot['total_viewer'] = pd.to_numeric(df_plot['total_viewer'], errors='coerce')
df_plot = df_plot.sort_values("total_viewer", ascending=False)


#les deux premier plots


st.markdown(f"""
<div style="padding-top:100px;">
   <h1> Graphique en barres </h1>
</div>
""", unsafe_allow_html=True)


col_plot1, col_plot2 = st.columns(2)
total_view_plot = px.bar(df_plot, x='name', y='total_viewer', labels={'name':'Nom du jeu', 'total_viewer':'Nombre de viewer sur twitch'})
total_view_plot.update_traces(marker_color='#6A31E0')
total_view_plot.update_layout(width=1000, height=700, bargap=0.05)
col_plot1.plotly_chart(total_view_plot)

total_play_plot = px.bar(df_plot, x='name', y='joueur_acts', labels={'name':'Nom du jeu', 'joueur_acts':'Nombre de joueur sur steam'})
total_play_plot.update_traces(marker_color='#1271A6')
total_play_plot.update_layout(width=1000, height=700, bargap=0.5)
col_plot2.plotly_chart(total_play_plot)


#plot total viewer en fonction de joueur act avec couleur degradés

st.markdown(f"""
<div style="padding-top:100px;">
   <h1> Graphique en barres en degradé </h1>
</div>
""", unsafe_allow_html=True)


degrade_plot = px.bar(df_plot.query("rank>=1"), y = "name", x = "total_viewer",labels={'name':'Nom du jeu', 'total_viewer':'Nombre de viewer sur twitch',"joueur_acts":"Nombre de joueur sur steam"}, title = "Total viewer en fonction de joueur act",
       orientation = 'h',color = "joueur_acts",color_continuous_scale=["#6A31E0", "#fff"])
degrade_plot.update_layout(width=1600, height=700, bargap=0.05)
st.plotly_chart(degrade_plot)



#les deux graphique circulaire

st.markdown(f"""
<div style="padding-top:100px;">
   <h1> Diagramme circulaire</h1>
</div>
""", unsafe_allow_html=True)


col_pie_plot1, col_pie_plot2 = st.columns(2)
df = px.data.tips()
pie_total_viewer = px.pie(df_plot.query("rank>=1"), values='total_viewer', names='name', color_discrete_sequence=px.colors.sequential.RdBu)
col_pie_plot1.plotly_chart(pie_total_viewer)

df = px.data.tips()
Pie_joueur_acts = px.pie(df_plot, values='joueur_acts', names='name', color_discrete_sequence=px.colors.sequential.RdBu)
col_pie_plot2.plotly_chart(Pie_joueur_acts)





#Bubble_plot

st.markdown(f"""
<div style="padding-top:100px;">
   <h1> Graphique en bulle</h1>
</div>
""", unsafe_allow_html=True)


Bubble_plot = px.scatter(df_plot.query("rank>=1"), x="chanel", y="total_viewer", size="joueur_acts", color="name",hover_name="name",labels={"name":'Nom du jeu','chanel':'Nombre de chaine sur twitch', 'total_viewer':'Nombre de viewer sur twitch',"joueur_acts":"Nombre de joueur sur steam"}, log_x=True, size_max=60)
Bubble_plot.update_layout(width=1600, height=700, bargap=0.05)
st.plotly_chart(Bubble_plot)



#dernier plot 
datatest = list(collection_avec_historique.find())
df_dota2 = pd.DataFrame(datatest)


row4_spacer1, row4_1, row4_spacer2 = st.columns((.2, 7.1, .2))
with row4_1:
    st.markdown(f"""
<div style="padding-top:100px;">
   <h1> Line plot  historique </h1>
</div>
""", unsafe_allow_html=True)

 
row5_spacer1, row5_1, row5_spacer2, row5_2, row5_spacer3  = st.columns((.2, 2.3, .4, 4.4, .2))
with row5_1:
    st.markdown(f"""
    <div style="padding-top:50px;">
   <h2> liste des jeu</h2>
    </div>
    """, unsafe_allow_html=True)    
    plot_x_per_team_selected = st.selectbox ("", list(df_dota2['name'].unique()))
    if plot_x_per_team_selected:
        for i, team in enumerate(list(df_dota2['name'].unique())):
            if team == plot_x_per_team_selected:
                selected_index = i
        history_values = [doc['history'] for doc in datatest]   
        df_dota2 = pd.DataFrame(history_values[selected_index])
        df_dota2['date'] = pd.to_datetime(df_dota2['date'])
        df_dota2 = df_dota2.set_index('date')
        df_dota2 = df_dota2.sort_index()
    else:
        st.warning('Please select at least one game')


trace1 = go.Scatter(x=df_dota2.index, y=df_dota2['joueur_acts'], name='joueur_acts',   marker_color='#1271A6')
trace2 = go.Scatter(x=df_dota2.index, y=df_dota2['total_viewer'], name='total_viewer', marker_color='#6A31E0')
layout = go.Layout(title='Dota2 Joueur Act History', xaxis=dict(title='Date'), yaxis=dict(title='Number of viewers'))
fig3 = go.Figure(data=[trace1, trace2], layout=layout)
fig3.update_layout(width=1400, height=700, bargap=0.05)
st.plotly_chart(fig3)

