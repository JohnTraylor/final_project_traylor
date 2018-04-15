import requests
import json
from bs4 import BeautifulSoup
import plotly.plotly as py
import pandas as pd
import sqlite3
import plotly.graph_objs as go

CACHE_FNAME = 'final_proj_cache.json'
COUNTRIESJSON = 'countries.json'
DBNAME = 'peace_corps.db'

#####  region, country, # current volunteers, work sectors, offical language

## Table one: region, country, offical language

## Table two: country, # current volunteers, work sectors

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def cacher(url):

	unique_ident = (url)
	if unique_ident in CACHE_DICTION:
		return CACHE_DICTION[unique_ident]

	else:
		resp = requests.get(url)
		CACHE_DICTION[unique_ident] = resp.text
		dumped_json_cache = json.dumps(CACHE_DICTION)
		fw = open(CACHE_FNAME,"w")
		fw.write(dumped_json_cache)
		fw.close() # Close the open file
		return CACHE_DICTION[unique_ident]

class Country:

	def __init__(self, dict_in = None, country = ''):
		self.name = country
		self.region = dict_in[country]["Region"]
		self.population = dict_in[country]["Population"]
		self.languages = dict_in[country]["Official Language"]
		self.volunteers_to_date = dict_in[country]["Volunteers to Date"]
		self.current_volunteers = dict_in[country]["Current Volunteers"]
		self.work_sectors = dict_in[country]["Work Sectors"]
		self.latlng = str(dict_in[country]["Coordinates"]).replace("(", "").replace(")", "")  
		self.link = dict_in[country]["Link"]

class Language:
	
	def __init__(self, dict_in = None, language = ""):

		self.language = language
		self.countries_spoken = str(dict_in[language]["Spoken In"]).replace("[", "").replace("]", "").replace("'", "")
		self.currently_speaking = dict_in[language]["Current Volunteers Speaking"]
		self.past_speaking = dict_in[language]["Past Volunteers Speaking"]
     
def get_all_countries():
	country_dict = {} #dict {Country:{Current Volunteers, Work Sectors, Link, Volunteers to Date, Official Language, Population, Region, Coordinates}}
	url_main = "https://www.peacecorps.gov/countries/"

	resp = cacher(url_main)
	soup = BeautifulSoup(resp, 'html.parser')
	country_cards = soup.find_all(class_ = "country-card--current")
	
	for card in country_cards:
		country_dict[card.find(class_ = "country-card__title").text.strip()] = {"Current Volunteers": int(card.find(class_ = "country-card__volunteers").text.strip().split()[0]),
		"Work Sectors": card.find_all(class_ = "tooltip"),
		"Link": card.find("a").attrs["href"]}
	
	for country in country_dict:
		sectors_list = []
		for sector in country_dict[country]["Work Sectors"]:
			sector = sector.text
			sectors_list.append(sector)

		country_dict[country]["Work Sectors"] = str(sectors_list).replace("[", "").replace("]", "").replace("'", "") 
	
	country_base_url = "https://www.peacecorps.gov"
	for country in country_dict:
		country_url = country_base_url + country_dict[country]["Link"]
		resp = cacher(country_url)
		soup = BeautifulSoup(resp, 'html.parser')
		
		try:
			data = soup.find_all(class_ = "info-box__text")
			data_clean = []
			for thing in data:
				part = thing.text.strip()
				data_clean.append(part)

			volunteers_2date = data_clean[0].split()[4]
			country_languages = data_clean[2]
			
		except (AttributeError, IndexError):
			volunteers_2date = 0
			country_languages = "Unknown"

		country_dict[country]["Volunteers to Date"] = int(volunteers_2date)
		country_dict[country]["Official Language"] = country_languages

		for country in country_dict:
			if country_dict[country]["Work Sectors"] == []:
				country_dict[country]["Work Sectors"] = "Unknown"
			else:
				pass

	with open (COUNTRIESJSON, mode="r", encoding="utf-8") as json_file:
	#json_file = codecs.open(COUNTRIESJSON, mode='r', encoding='utf-8', errors='ignore')
		json_temp = json_file.read()
		file_dict = json.loads(json_temp)
	
	for country in file_dict:
		if country["name"] in country_dict:
			country_dict[country["name"]]["Population"] = country["population"]
			country_dict[country["name"]]["Coordinates"] = str((country["latlng"][0], country["latlng"][1])).replace("(", "").replace(")", "")
			country_dict[country["name"]]["Region"] = country["region"]
		else: 
			pass

	country_dict_final = {}
	for key in country_dict:
		if "Population" in country_dict[key]:
			country_dict_final[key] = country_dict[key]

	country_dict_final["South Africa"] = {'Current Volunteers': 129, 'Work Sectors': 'Education, Health', 'Link': '/south-africa', 'Volunteers to Date': 1539, 'Official Language': 'English, Afrikaans', 'Population': 55653654, 'Coordinates': "-29.0, 24.0", 'Region': 'Africa'}
	
	return country_dict_final

def get_languages(data):
	country_data = data
			#create language dictionary {"language": {[country 1, country 2, ...], "Volunteers" : #volunteer speakers}}
	lang_list = []
	for country in country_data:
		lang = country_data[country]["Official Language"].split()
		lang_list.append(lang)

	lang_list_refine = []
	for langes in lang_list:
		for item in langes:
			lang_list_refine.append(item)

	lang_list_refine1 = []
	for item in lang_list_refine:
		if "," in item:
			item = item.replace(",", "")
			lang_list_refine1.append(item)
		else:
			lang_list_refine1.append(item)

	lang_list_refine2 = list(set(lang_list_refine1))

	lang_dict = {}

	for lang in lang_list_refine2:
		lang_dict[lang] = {}
		lang_dict[lang]["Spoken In"] = []  
		lang_dict[lang]["Current Volunteers Speaking"] = 0
		lang_dict[lang]["Past Volunteers Speaking"] = 0
		for country in country_data:
			if lang in country_data[country]["Official Language"]:
				lang_dict[lang]["Spoken In"].append(country)
				lang_dict[lang]["Current Volunteers Speaking"] += country_data[country]["Current Volunteers"]
				lang_dict[lang]["Past Volunteers Speaking"] += country_data[country]["Volunteers to Date"]

	return lang_dict 

def countryfier():
	country_dict = get_all_countries()
	country_dict_keys = country_dict.keys()

	countries = []
	for key in country_dict_keys:
		countries.append(Country(country_dict, key))

	return countries

def languageifier():
	language_dict = get_languages(get_all_countries())
	language_dict_keys = language_dict.keys()

	languages = []
	for key in language_dict_keys:
		languages.append(Language(language_dict, key))

	return languages

def init_db(db_name):
    #code to create a new database goes here
	try:
		conn = sqlite3.connect(db_name)
		cur = conn.cursor()
	except Exception as e:
		print(e)

	statement = '''
	DROP TABLE IF EXISTS 'Countries';
	'''
	cur.execute(statement)

	statement = '''
	DROP TABLE IF EXISTS 'Languages';
	'''
	cur.execute(statement)
	conn.commit()

	statement_countries = '''
	CREATE TABLE 'Countries' ('Id' INTEGER PRIMARY KEY AUTOINCREMENT,
	'Name' TEXT,
	'Region' TEXT,
	'Population' INTEGER,
	'Languages' TEXT,
	'PastVolunteers' INTEGER,
	'CurrentVolunteers' INTEGER,
	'WorkSectors' TEXT,
	'Coordinates' TEXT);'''

	statement_languages = '''
	CREATE TABLE 'Languages' ('Id' INTEGER PRIMARY KEY AUTOINCREMENT,
	'Language' TEXT NOT NULL,
	'SpokenIn' TEXT NOT NULL,
	'CurrentVolunteersSpeaking' INTEGER NOT NULL,
	'PastVolunteersSpeaking' INTEGER NOT NULL);'''

	cur.execute(statement_countries)
	cur.execute(statement_languages)
	conn.commit()
		
    #close database connection
	conn.close()

init_db(DBNAME)

def insert_countries_data():
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except Exception as e:
		print(e)

	countries_data = countryfier()

	for row in countries_data: 
		insertion = (None,
		row.name,
		row.region,
		row.population,  
		row.languages, 
		row.volunteers_to_date,
		row.current_volunteers, 
		row.work_sectors,
		row.latlng
		)

		statement = 'INSERT INTO "Countries" '
		statement += 'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'

		cur.execute(statement, insertion)

	conn.commit()
	conn.close()

def insert_languages_data():
	try:
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
	except Exception as e:
		print(e)

	language_data = languageifier()
	
	for row in language_data:
		insertion = (None,
		row.language,
		row.countries_spoken,
		row.currently_speaking,  
		row.past_speaking 
		)

		statement = 'INSERT INTO "Languages" '
		statement += 'VALUES (?, ?, ?, ?, ?)'

		cur.execute(statement, insertion)

	conn.commit()
	conn.close()

insert_countries_data()
insert_languages_data()


def map_command(input_1):

	## World Map Scatter Plot that displays a point for each Peace Corps country with a hover caption that displays number of current volunteers and the languages they speak.

	conn =sqlite3.connect(DBNAME)
	cur = conn.cursor()

	selector = "SELECT C.Name, C.CurrentVolunteers, C.Coordinates "
	fromer = "FROM Countries AS C"
	orderer = ""
	limiter = ""
	joiner = ""
	wherer = ""

	statement = selector + fromer + joiner + wherer + orderer + limiter
	cur.execute(statement)
	data = cur.fetchall()
	conn.close()

	coords_tuples = []
		
	for country in data:
		coords = country[2].strip().split(",")
		coord_tuple = (float(coords[0]), float(coords[1]), country[0], int(country[1]))
		coords_tuples.append(coord_tuple)

	lat_vals = []
	lon_vals = []
	country_names = []
	country_volunteers = []

	for tupe in coords_tuples:
		if tupe[0] != "":
			lat_vals.append(tupe[0])
			lon_vals.append(tupe[1])
			country_names.append(tupe[2])
			country_volunteers.append(tupe[3])

	data = [ dict(
        type = 'choropleth',
        locations = country_names,
        locationmode = "country names",
        z = country_volunteers,
        text = 'Current Volunteers',
        colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
            [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
        autocolorscale = False,
        reversescale = True,
        marker = dict(
            line = dict (
                color = 'rgb(180,180,180)',
                width = 0.5
            ) ),
        colorbar = dict(
            autotick = False,
            tickprefix = '',
            title = 'Current Volunteers'),
      ) ]

	layout = dict(
    title = 'Current Volunteers Serving in Peace Corps Countries<br>Source:\
            <a href="https://www.peacecorps.gov/countries/">\
            Peace Corps Countries</a>',
    geo = dict(
        showframe = False,
        showcoastlines = False,
        projection = dict(
            type = 'Mercator'
        )
    )
)

	fig = dict( data=data, layout=layout )
	py.plot( fig, validate=False, filename='d3-world-map' )

def most_volunteers_population_ratio_command(input_2):

	 ## Bar graph that displays the top five countries by past volunteer / country population ratio. 

	conn =sqlite3.connect(DBNAME)
	cur = conn.cursor()

	selector = "SELECT C.Name, C.PastVolunteers, C.Population "
	fromer = "FROM Countries AS C "
	orderer = ""
	limiter = ""
	joiner = ""
	wherer = ""

	statement = selector + fromer + joiner + wherer + orderer + limiter
	cur.execute(statement)
	data = cur.fetchall()
	conn.close()

	country_tuples = []

	for country in data:
		if country[1] != 0:
			country_tuple = (country[0], country[1]/country[2])
			country_tuples.append(country_tuple)
		else:
			pass

	country_tuples_sorted = sorted(country_tuples, key = lambda country: country[1], reverse = True)[:5]

	countries = []
	volunteer_ratios = []
	for thing in country_tuples_sorted: 
		countries.append(thing[0])
		volunteer_ratios.append(thing[1])
	
	trace0 = go.Bar(
    x= countries ,
    y= volunteer_ratios ,
    text= countries ,
    marker=dict(
        color='rgb(158,202,225)',
        line=dict(
            color='rgb(8,48,107)',
            width=1.5,
        )
    ),
    opacity=0.6
)

	data = [trace0]
	layout = go.Layout(
    title='Past Volunteer to Country Population Ratio',
)

	fig = go.Figure(data=data, layout=layout)
	py.plot(fig, filename='text-hover-bar')

def languages_pie_chart(input_3):

	 ## Pie chart that displays languages spoken by past volunteers by percentage 

	conn =sqlite3.connect(DBNAME)
	cur = conn.cursor()

	selector = "SELECT L.Language, L.PastVolunteersSpeaking "
	fromer = "FROM Languages AS L"
	orderer = ""
	limiter = ""
	joiner = ""
	wherer = ""

	statement = selector + fromer + joiner + wherer + orderer + limiter
	cur.execute(statement)
	data = cur.fetchall()
	conn.close()

	language_tuples = []

	for language in data:
		if language[1] > 2000:
			language_tuples.append(language)

	languages = []
	speakers = []

	for tupe in language_tuples:
		languages.append(tupe[0])
		speakers.append(tupe[1])

	labels = languages
	values = speakers

	trace = go.Pie(labels=labels, values=values)

	py.plot([trace], filename='basic_pie_chart')

def volunteer_population_region_command(input_4):

	 ## 4.)	Bar graph that displays the current volunteer population of world regions.

	conn =sqlite3.connect(DBNAME)
	cur = conn.cursor()

	selector = "SELECT C.Region, C.CurrentVolunteers "
	fromer = "FROM Countries AS C "
	orderer = "ORDER BY C.CurrentVolunteers DESC"
	limiter = ""
	joiner = ""
	wherer = ""

	statement = selector + fromer + joiner + wherer + orderer + limiter
	cur.execute(statement)
	data = cur.fetchall()
	conn.close()

	Europe = 0
	Africa = 0
	Americas = 0
	Asia = 0 
	Oceania = 0

	for region in data:
		if region[0] == "Europe":
			Europe += region[1]
		elif region[0] == "Africa":
			Africa += region[1]
		elif region[0] == "Americas":
			Americas += region[1]
		elif region[0] == "Asia":
			Asia += region[1]
		elif region[0] == "Oceania":
			Oceania += region[1]
		else:
			pass

	region_tuples = [("Europe", Europe), ("Africa", Africa), ("Americas", Americas), ("Asia", Asia),("Oceania", Oceania)]

	regions = []
	volunteers = []

	for tupe in region_tuples:
		regions.append(tupe[0])
		volunteers.append(tupe[1])

	trace0 = go.Bar(
    x= regions ,
    y= volunteers ,
    text= regions ,
    marker=dict(
        color='rgb(158,202,225)',
        line=dict(
            color='rgb(8,48,107)',
            width=1.5,
        )
    ),
    opacity=0.6
)

	data = [trace0]
	layout = go.Layout(
    title='Current Volunteers by Region',
)

	fig = go.Figure(data=data, layout=layout)
	py.plot(fig, filename='text-hover-bar')


def process_command(command):

	if "1" in command:
		print("Your map will open in a web-browser")
		results = map_command(command)
		return results
	elif "2" in command:
		print("Your graph will open in a web-browser")
		results = most_volunteers_population_ratio_command(command)
		print
		return results
	elif "3" in command:
		print("Your chart will open in a web-browser")
		results = languages_pie_chart(command)
		return results
	elif "4" in command:
		print("Your graph will open in a web-browser")
		results = volunteer_population_region_command(command)
		return results
	elif "help" in command:
		print("1 - World Map displaying the number of current volunteers in each Peace Corps country.\n2 - Bar Graph that displays the top five countries by past volunteer & country population ratio.\n3 - Pie Chart that displays languages spoken by past volunteers by percentage.\n4 - Bar graph that displays the current volunteer population of world regions.\nexit - Quits the program\n\n")
	elif "exit" in command:
		print("Thanks for using the Peace Corps database!")
		quit()

if __name__=="__main__":

	possible_commands = ["1", "2", "3", "4", "exit", "help"]

	def process_command_2(user_input):
		print("\n")
		if user_input not in possible_commands:
			print("Please type a valid command, or help...")
		else:
			return process_command(user_input)

	print("\n\nWelcome to this Peace Corps Volunteer Database.\nTry one of these commands to learn about Peace Corps countrires and volunteers.\n\n1 - World Map displaying the number of current volunteers in each Peace Corps country.\n2 - Bar Graph that displays the top five countries by past volunteer & country population ratio.\n3 - Pie Chart that displays languages spoken by past volunteers by percentage.\n4 - Bar graph that displays the current volunteer population of world regions.\n\n")

	user_command = ""
	
	while True:
	
		user_command = input("").lower()
		
		process_command_2(user_command)