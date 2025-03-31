import requests, os
from dotenv import load_dotenv

load_dotenv('.env')

class FragranceAPI:
	def __init__(self):
		self.__url = os.getenv("__API_URL")
		self.__KEY = os.getenv("__API_KEY")
		self.__HOST = os.getenv("__API_HOST")
		
	#getter methods for class fields
	def get_url(self):
		return self.__url

	def get_key(self):
		return self.__KEY
	
	def get_host(self):
		return self.__HOST
	
	def ret_fragrances(self, brand = ""):
		querystring = {"q":brand} #leaves query as default so that all fragrances will be returned

		headers = {
			"x-rapidapi-key": self.get_key(),
			"x-rapidapi-host": self.get_host()
		}

		response = requests.get(self.get_url(), headers=headers, params=querystring)

		response = response.json() #returns a list containing a disctionary. Main dict containts sub-dicts: [{ {1}, {2}, ... }]

		return response
