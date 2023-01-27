# BDD_PROJECT

### Présentation Du Projet :

Notre projet consiste à récupérer en temps réel des données sur les jeux vidéo les plus populaires à travers des plateformes en ligne telles que Twitch et Steam. Nous avons utilisé 4 API différentes pour obtenir ces données, que nous avons ensuite stockées dans une base de données MongoDB afin de pouvoir les étudier et analyser leur corrélation. Pour gérer et visualiser ces données, nous avons développé une interface web en utilisant Python (Streamlit), qui permet de réaliser des opérations CRUD pour gérer les données récupérées depuis les API
### But Du Projet : 
Le but de ce projet est de récupérer les données sur les jeux les plus streamés sur Twitch et les jeux les plus joués sur Steam, puis d'établir une corrélation entre ces deux sources d'informations en utilisant une analyse de données. Le but final est de découvrir les tendances et les similitudes entre les jeux les plus populaires sur ces deux plateformes de jeux en ligne
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
``` javascript
"data": [
     {Rank : 1
     Name : "Counter-Strike: Global Offensive"
     joueur_acts : 526696}]

```
#### API Chanels:
 L'API "https://twitchtracker.com/games/average-channels?page=" fournit des données sur les chaînes moyennes pour chaque jeu de Twitch pour offrir des analyses et des statistiques sur les jeux les plus populaires sur la plateforme. On a récupéré ces informations en utilisant un scraping, il n'y a donc pas de paramètres spécifiques 

##### La réponse de l'API est un objet JSON qui contient les clés suivantes :
-	Rank : la classe du jeu
-	Name : nom du jeu
-	Chanel : les chaînes moyennes pour chaque jeu de Twitch
``` javascript
"data": [
       {Rank :1
       Name : "Fortnite"
```
### Utilisation de l’interface web Streamlit :
Pour l’interface de notre projet on a utilisé streamlit, cette interface web permet de gérer les données récupérées depuis les API en utilisant une base de données MongoDB. Elle permet de :
-	Sélectionner la base de données à afficher (soit les données les plus récentes, soit les données historiques) 
-	Mettre à jour les données en utilisant les différentes API
-	Rechercher des jeux par ID, et afficher des informations sur les jeux sélectionnés
-	Effectuer des opérations de CRUD pour un jeu donné.
-	Voir la représentation des différents graphiques utilisées pour l’étude de la corrélation.


  Pour utiliser cette interface, vous pouvez sélectionner la base de données à afficher, mettre à jour les données en utilisant les boutons appropriés, rechercher des jeux en saisissant l'ID de celui-ci, et effectuer des opérations de CRUD en saisissant l'ID de jeu.
 
 ### Explication des graphiques utilisé :
 On a utilisé des visualisations de données pour explorer les données et identifier les tendances et les relations entre les différentes variables. Les visualisations incluent des graphiques à barres, des graphiques à bulles, des graphiques en dégradé et des graphiques à lignes pour montrer l'évolution des données au fil du temps. Ces visualisations ont permis de mettre en évidence les tendances et les relations intéressantes dans les données, et ont été utilisées pour soutenir les conclusions de l'analyse.
 #### graphiques à barres 1: 
 Ce plot est une représentation graphique des données récupérées à partir de l'API Twitch il affiche le nombre de vues total pour chaque jeu en fonction du nom du jeu. Les données sont triées par ordre décroissant de vues totales pour que les jeux les plus populaires apparaissent en haut du graphique
 #### graphiques à barres 2: 
 Ce plot est une représentation graphique des données récupérées à partir de l'API Steam, il affiche le nombre de joueurs actifs pour chaque jeu en utilisant un diagramme à barres
 #### graphiques en dégradé : 
 Ce plot est une représentation graphique en barres qui montre la corrélation entre le nombre de joueurs actifs sur Steam et le nombre de spectateurs sur Twitch pour chaque jeu vidéo, Le graphique est également coloré en fonction de la colonne joueurs actifs pour montrer la corrélation entre les deux données
 #### graphiques en bulles :
 Ce plot est une représentation graphique en bulles qui montre les relations entre différentes variables tel que le nom du jeu, le nombre de chaînes Twitch qui diffusent le jeu, le nombre de spectateurs Twitch pour ce jeu, et le nombre de joueurs actifs sur Steam pour ce jeu. Les bulles représentent les jeux vidéo, avec leur taille dépendant du nombre de joueurs actifs sur Steam, et leur couleur dépendant du nom du jeu. Les abscisses représentent le nombre de chaînes Twitch qui diffusent le jeu, et les ordonnées représentent le nombre de spectateurs Twitch pour ce jeu
 #### graphiques en lignes : 
  Ce plot est une représentation graphique qui utilise les données de l'historique d’un jeux données pour afficher l'évolution du nombre de joueurs actifs et du nombre de spectateurs sur les plateformes de streaming en fonction de la date. Il permet de visualiser comment ces deux métriques ont évolué au fil du temps et de comparer les tendances entre elles. Pour comprendre comment l'intérêt des joueurs et des spectateurs évolue en fonction des dates

 ### Conclusion : 
Après analyse des données, nous pouvons conclure qu'il n'y a pas nécessairement de corrélation entre le nombre de joueurs sur Steam et le nombre de vues sur Twitch. Cependant, nous pouvons voir que les mêmes grands jeux dominent le marché et représentent à quatre ou cinq 50 % du marché. 
De plus, nous avons observé une corrélation très importante entre le nombre de streams sur Twitch et le nombre de joueurs actuels. 
Enfin, en fonction du public visé par un jeu, l'historique sera totalement différent. Par exemple, un jeu plus axé sur la jeunesse sera plus dépendant des horaires (sortie scolaire, week-end...) qu'un jeu destiné à un public plus âgé.
