# spotify-api-client
This repository is made to upload 2022's spotify api client. 

## Functions:
* ```get_token_data()```: get access token data 
* ```search(dict query, operator, operator_query,search_type)```: basic search function with operator, operator query (default search_type = 'artists')
* ```get_resource(lookup_id,resource_type,version)```: get a resource from spotify api using id, resource_type (default 'album'), version (default 'v1')
* ```get_album(_id)```: search for album using album id
* ```get_artist(_id)```: search for artist using artist id
* ```get_saved_tracks()```: search for saved tracks from a selected user. 

Initial steps:
* Set up value for client_id and client_secret
* Call the client using ```spotify = SpotifyAPI(client_id,client_secret)```
