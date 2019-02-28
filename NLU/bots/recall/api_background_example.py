url = "http://localhost:3000/api/person/background"

payload = "forname=Frasier"
headers = {
    'Content-Type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache",
    'Postman-Token': "eba2e688-d642-4681-9108-99a0b29a4998"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)