import requests
import json
import os

nb = 0
shortcodes = []

username = input("Please enter the username : ")

url = "https://www.instagram.com/%s/?__a=1" % (username)
http_resp = requests.get(url)
if http_resp.status_code == 200:
    raw_json = http_resp.json()
    id = int(raw_json['graphql']['user']['id'])

    url = 'https://www.instagram.com/graphql/query/?query_hash=472f257a40c653c64c666ce877d59d2b&variables={"id":"%d","first":"50"}' % (id)

    http_resp = requests.get(url)

    if http_resp.status_code == 200:
        raw_json = http_resp.json()
        c_len = len(raw_json['data']['user']['edge_owner_to_timeline_media']['edges'])
        nb = nb + c_len

        i = 0
        while i != c_len:
            shortcodes.append(
                raw_json['data']['user']['edge_owner_to_timeline_media']['edges'][i]['node']['shortcode'])
            i = i + 1

        if raw_json['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'] == True:
            isMore = True
        else:
            isMore = False

        while isMore:
            end_cursor = raw_json['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

            url = 'https://www.instagram.com/graphql/query/?query_hash=472f257a40c653c64c666ce877d59d2b&variables={"id":"%d","first":"50","after":"%s"}' % (id,end_cursor)

            http_resp = requests.get(url)

            if http_resp.status_code == 200:
                raw_json = http_resp.json()

                if raw_json['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page'] == True:
                    isMore = True
                else:
                    isMore = False

                c_len = len(raw_json['data']['user']['edge_owner_to_timeline_media']['edges'])
                nb = nb + c_len

                i = 0
                while i != c_len:
                    shortcodes.append(
                        raw_json['data']['user']['edge_owner_to_timeline_media']['edges'][i]['node']['shortcode'])
                    i = i + 1

        shortcodes.reverse()

        n = 0
        
        for code in shortcodes:
            print(f"[{n+1}/{nb}] Processing {code} ... ")
            
            url = "https://www.instagram.com/p/%s/?__a=1" % (code)
            http_resp = requests.get(url)

            if http_resp.status_code == 200:
                raw_json = http_resp.json()

                if "edge_sidecar_to_children" in raw_json['graphql']['shortcode_media']:
                    nb_jpg = len(raw_json['graphql']['shortcode_media']['edge_sidecar_to_children']['edges'])
                    i = 0

                    while i != nb_jpg:
                        os.makedirs(os.path.dirname(f"out/{id}/{n}-{code}_{i}.jpg"), exist_ok=True)
                        img = requests.get(raw_json['graphql']['shortcode_media']['edge_sidecar_to_children']['edges'][i]['node']['display_url'])
                        with open(f"out/{id}/{n}-{code}_{i}.jpg", "wb") as jpg:
                            jpg.write(img.content)

                        i = i + 1

                else:
                    
                    os.makedirs(os.path.dirname(f"out/{id}/{n}-{code}_0.jpg"), exist_ok=True)
                    img = requests.get(
                        raw_json['graphql']['shortcode_media']['display_url'])
                    with open(f"out/{id}/{n}-{code}_0.jpg", "wb") as jpg:
                        jpg.write(img.content)
                n = n + 1
