url1 = "https://hotels4.p.rapidapi.com/properties/v2/list"

payload = {
	"currency": "USD",
	"eapid": 1,
	"locale": "en_US",
	"siteId": 300000001,
	"destination": { "regionId": "6054439" },
	"checkInDate": {
		"day": 10,
		"month": 10,
		"year": 2023
	},
	"checkOutDate": {
		"day": 15,
		"month": 10,
		"year": 2023
	},
	"rooms": [
		{
			"adults": 2,
			"children": [{ "age": 5 }, { "age": 7 }]
		}
	],
	"resultsStartingIndex": 0,
	"resultsSize": 200,
	"sort": "PRICE_LOW_TO_HIGH",
	"filters": { "price": {
			"max": 150,
			"min": 100
		} }
}

url2 = "https://hotels4.p.rapidapi.com/locations/v3/search"

querystring = {"q": "new york", "locale": "en_US", "langid": "1033", "siteid": "300000001"}


