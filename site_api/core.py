from config_data.config import RAPID_API_HOST, RAPID_API_KEY

import requests

url = "https://hotels-com-provider.p.rapidapi.com/v2/hotels/search"

querystring = {"domain":"AE","sort_order":"PRICE_LOW_TO_HIGH","locale":"en_GB","checkout_date":"2023-09-27",
			   "region_id":"1565","adults_number":"1","checkin_date":"2023-09-26",
			   "available_filter":"SHOW_AVAILABLE_ONLY","meal_plan":"FREE_BREAKFAST",
			   "guest_rating_min":"8","price_min":"10","page_number":"1","children_ages":"4,0,15",
			   "amenities":"WIFI,PARKING","price_max":"500","lodging_type":"HOTEL,HOSTEL,APART_HOTEL",
			   "payment_type":"PAY_LATER,FREE_CANCELLATION","star_rating_ids":"3,4,5"}

headers = {
	"X-RapidAPI-Key": RAPID_API_KEY,
	"X-RapidAPI-Host": RAPID_API_HOST
}

response = requests.get(url, headers=headers, params=querystring)

for _ in range(5):
	try:
		print(response.json()["properties"][_]["name"])
	except:
		print(f"Найдено {_} отелей")

url1 = "https://hotels-com-provider.p.rapidapi.com/v2/regions"

querystring1 = {"locale":"en_GB","query":"Киев","domain":"AE"}

response = requests.get(url1, headers=headers, params=querystring1)

print(response.json()["data"][0]["gaiaId"])
