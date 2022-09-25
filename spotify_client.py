
import webbrowser
from urllib.parse import urlencode
import base64
import requests
import pandas as pd
import json
import datetime
import pyautogui
import clipboard
import time


class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    code = None
    url = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__ (self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        """Return base64 encoded string"""
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id == None or client_secret == None:
            raise Exception("You must set client_id and client_secret!")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    def get_token_data(self):
        client_id = self.client_id
        auth_headers = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": "http://localhost:8080/callback",
        "scope": "user-library-read"
        }
        webbrowser.open("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))
        time.sleep(7)
        url = self.url
        pyautogui.click(0, 200) 
        pyautogui.press('f6')
        pyautogui.hotkey('ctrl', 'c') 
        url = clipboard.paste()
        return {
            "grant_type": "authorization_code",
            "code": url[36:],
            "redirect_uri": "http://localhost:8080/callback"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
           return print("Failed")
        access_data=r.json()
        now = datetime.datetime.now()
        access_token = access_data['access_token']
        expires_in = access_data['expires_in']
        expires = now + datetime.timedelta(seconds = expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return print("Success")

    def get_access_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        return headers

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def base_search(self, query_params):
        access_token = self.get_access_token()
        headers = self.get_access_header()
        endpoint ="https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r=requests.get(lookup_url, headers = headers)
        if r.status_code not in range (200,299):
            return {}
        return r.json()

    def search(self, query = None, operator = None, operator_query = None, search_type = "artist"):
        if query == None:
            raise Exception("A query is required")
        if isinstance(query,dict):
            query = " ".join([f"{k}:{v}" for k,v in query.items()])
        if operator != None and operator_query != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({'q': query, 'type': search_type.lower()})
        print(query_params)
        return self.base_search(query_params)

    def get_resource(self, lookup_id, resource_type = "album", version = "v1"):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_access_header()
        r = requests.get(endpoint, headers = headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()


    def get_album(self, _id):
        return self.get_resource(_id,resource_type = 'albums')

    def get_artist(self, _id):
        return self.get_resource(_id,resource_type = 'artists')



