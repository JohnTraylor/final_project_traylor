This is John Traylor's final project for si507 Winter 2018.

A program to database and visualize data on Peace Corps volunteers, the countries in which they serve, and the langauges they learn to speak on the job. 



****Data Sources:****

This program will access data from two sources.
1.) This program will scrape the data from each country listed on the Peace Corps website at: https://www.peacecorps.gov/countries/
Then the program will crawl into each country's website and scrape further data.  An example website: https://www.peacecorps.gov/benin/

2.) This program will also access data from the "countries.json" file provided to us for our third project.  This file has been included in the git repositorty for this project.

You do not need any API keys to access data from this project.

****Required Libraries:****

This program will require the user to have the following libraries installed:
- import requests
- import json
- import BeautifulSoup
- import plotly.plotly
- import pandas
- import sqlite3
- import plotly.graph_objs
- import unittest

****Code Structure:****

This program follows the following structure:

1.) Load in classes:
1, a.) Language: A class that describes the various languages Peace Corps volunteers learn on site in their host countries.  This class describes a language's name, countries where it is spoken, how many volunteers are currently using the language, how many past volunteers have learned the language.
1, b.) Country: A class that describes the various countries in which Peace Corps volunteers serve.  This class describes a country's name, languages spoken there, population, how many volunteers are currently serving there, etc.

2.) Load in get_functions:
2, a.) get_all_countries: A function that scrapes, crawls, and draws data from a json file.  This function returns a dictionary of countries.  example_dict = {"Benin":{"Current Volunteers": int, "Work Sectors": str, "Link": str, "Volunteers to Date": int, "Official Language": str, "Population": int, "Region": str, "Coordinates": str}}

2, b.) get_all_languages: A function that processes data from the get_all_countries function in order to produce a dictionary of langauges and corresponding information.  example_dict = {"English": {"Spoken In": str, "Current Volunteers Speaking": int, "Past Volunteers Speaking": int}

3.) Classifying data:
Data collected from the get_functions is classifeid into lists using my Language and Country classes.

4.) Initiating and populating a database:
A database called peace_corps.db is created and populated using the lists of classes outlined in part 3.

5.) Loading visualization commands:
5, a.) World Map Scatter Plot that displays a point for each Peace Corps country with a hover caption that displays number of current volunteers

5, b.) Bar graph that displays the top five countries by past volunteer / country population ratio. 

5, c.) Pie chart that displays languages spoken by past volunteers by percentage.

5, d.) Bar graph that displays the current volunteer population of world regions.

6.) Interfacing with commands:
Simple while-loop interface that processes commands



****User Guide****

Simply running the program as final_proj.py will launch the program.
The program will take a couple minutes to scrape and process data as well as set up the database.

Users will be simply presented with four options.  Pressing the following will yeild the following results:

<1> - World Map Scatter Plot that displays a point for each Peace Corps country with a hover caption that displays number of current volunteers

<2> - Bar graph that displays the top five countries by past volunteer / country population ratio. 

<3> - Pie chart that displays languages spoken by past volunteers by percentage.

<4> - Bar graph that displays the current volunteer population of world regions.

typing <help> displays a help menu.

typing <exit> exits the program.
