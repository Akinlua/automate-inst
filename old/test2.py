import requests

url = "https://instagram28.p.rapidapi.com/medias_v2"

querystring = {"user_id":"25025320"}

headers = {
	"x-rapidapi-key": "2a78c7b912msh50c6ff04f63c9a6p1a2853jsn23af00e22f37",
	"x-rapidapi-host": "instagram28.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())