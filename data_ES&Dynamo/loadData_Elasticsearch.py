from variables import *  

es = Elasticsearch()
json_list = []

for cuisine_type in cuisine_types:
    offset = 0
    for i in range(0, 1):
        offset += 50
        PARAMETERS = {
            'term': 'restaurant',
            'location': 'New York',
            'radius': 40000,
            'categories': cuisine_type,
            'limit': 50,
            'offset': offset,
            'sort_by': 'best_match'
        }
        response = requests.get(url=ENDPOINT, params=PARAMETERS, headers=HEADERS)
        business_data = response.json()

        for biz in business_data['businesses']:
            if biz['id'] not in json_list:
                dictionary = "{\"businessId\": " + '"'+biz['id']+'"' + ", \"cuisine\": " + '"'+biz['categories'][0]['alias']+'"' + "}"
                json_list.append(dictionary)

count = 0
for res in json_list:
    count += 1
    response = requests.put(ES_URL, headers=headers, data=res, auth=(ES_USER, ES_PASS))
    print(response.text)  