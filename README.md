# BDD_PROJECT

### Présentation Du Projet :

Notre projet consiste à récupérer en temps réel des données sur les jeux vidéo les plus populaires à travers des plateformes en ligne telles que Twitch et Steam. Nous avons utilisé 4 API différentes pour obtenir ces données, que nous avons ensuite stockées dans une base de données MongoDB afin de pouvoir les étudier et analyser leur corrélation. Pour gérer et visualiser ces données, nous avons développé une interface web en utilisant Python (Streamlit), qui permet de réaliser des opérations CRUD pour gérer les données récupérées depuis les API

### Mongodb : 
Pour cette analyse, nous avons utilisé MongoDB pour stocker les données récupérées via des API de jeux vidéo. Nous avons créé deux bases de données dans MongoDB, l'une pour stocker les données en temps réel et l'autre pour stocker l'historique de ces données. Chacune de ces bases contient des collections qui regroupent les données par jeu vidéo. En utilisant MongoDB, nous avons pu stocker de grandes quantités de données de manière efficace et les utiliser pour créer des visualisations et des analyses en temps réel

### Présentation des 4 API utilisés :
#### API Twitch Top Games :
L'API 'https://api.twitch.tv/helix/games/top' de Twitch fournit des données sur les jeux les plus populaires actuellement en direct sur la plateforme. Elle permet de récupérer des informations telles que le nom du jeu, l'ID du jeu ainsi que le nombre de spectateurs actuellement regardant ces diffuseurs. Cette API est utilisée pour obtenir des informations sur les tendances actuelles sur Twitch et pour découvrir les jeux les plus populaires sur la plateforme.
 ##### Les paramètres possibles pour cette API incluent :
 - First : nombre de résultats à renvoyer (par défaut : 20, maximum : 100)
-  before/after : un curseur de pagination pour renvoyer les résultats avant ou après un ID de jeu spécifique
- language : pour filtrer les résultats en fonction de la langue utilisée par les diffuseurs
##### La réponse de l'API est un objet JSON qui contient les clés suivantes :
-	data : tableau d'objets contenant les informations de chaque jeu (nom, ID, nombre de diffuseurs en direct, nombre de spectateurs)
-	pagination : objet contenant des informations de pagination (curseurs avant et après)
 ##### Les clés possibles pour chaque objet de jeu dans le tableau data sont :
 - id : identifiant unique du jeu
-	name : nom du jeu
-	box_art_url : URL d'une image de l'affiche du jeu
-	igdb_id : L'identifiant utilisé par IGDB pour identifier ce jeu.

####	API Twitch Streams Game : 
L'API "https://api.twitch.tv/helix/streams?game_id=" de Twitch fournit des données sur les flux en direct pour un jeu spécifique sur la plateforme. Il permet de récupérer des informations telles que le nom du diffuseur, l'ID du flux, le titre du flux, le nombre de spectateurs actuel pour ce flux, ainsi que d'autres informations liées au flux. Cette API est utilisée pour obtenir des informations sur les flux en direct pour un jeu spécifique sur Twitch.

 ##### Les paramètres possibles pour cette API incluent :
 - game_id : l'identifiant unique du jeu pour lequel récupérer les flux en direct (requis)
-	first : nombre de résultats à renvoyer (par défaut : 20, maximum : 100)
-	after/before : un curseur de pagination pour renvoyer les résultats avant ou après un ID de flux spécifique
-	language : pour filtrer les résultats en fonction de la langue utilisée par les diffuseurs

 #####	La réponse de l'API est un objet JSON qui contient les clés suivantes :
 - data : tableau d'objets contenant les informations de chaque flux (nom du diffuseur, ID du flux, titre du flux, nombre de spectateurs, etc.)
-	pagination : objet contenant des informations de pagination (curseurs avant et après)

 #####	Les clés possibles pour chaque objet de flux dans le tableau data sont :
- id : identifiant unique du flux
-	user_id: identifiant unique du diffuseur
-	user_name : nom d'affichage du diffuseur
-	game_id : identifiant unique du jeu diffusé
-	title : titre du flux
-	viewer_count : nombre de spectateurs actuellement regardant le flux
- started_at : date et heure de début du flux.

#### Exemple des données qu’on a récupérer des 2 API :
``` javascript
 "data": [
    {"id_game":"27471"
     "name":"Minecraft"
     "started_at" :"2023-01-23T21:05:04Z"
     "total_viewer" :359209}]
```
#### API Steam : 
L'API 'https://store.steampowered.com/charts/mostplayed/' de Steam fournit des données sur les jeux les plus joués sur la plateforme Steam. Elle permet de récupérer des informations telles que le nom du jeu, l'ID du jeu, le nombre d'utilisateurs actuellement en ligne pour ce jeu, le nombre total d'utilisateurs ayant joué à ce jeu. Cette API est utilisée pour obtenir des informations sur les tendances de jeux les plus populaires sur Steam et pour découvrir les jeux les plus joués sur la plateforme. On a récupéré ces informations en utilisant un scraping, il n'y a donc pas de paramètres spécifiques.
 ##### La réponse de l'API est un objet JSON qui contient les clés suivantes :
- Rank : la classe du jeu
-	Name : nom du jeu
-	joueur_acts : le nombre de joueurs actuellement en ligne pour ce jeu

 



