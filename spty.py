from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import spotipy.util as util
import pprint
from user_data import my_keys

class sp_UserInfo(object):
    def __init__(self):
        # Keys... Need to load from an alt file
        temp = my_keys()
        self.client_id = temp[0]
        self.client_secret = temp[1]
        self.client_user = temp[2]
        self.redirect_uri = 'http://localhost/'
        self.token = util.prompt_for_user_token(self.client_user, 'playlist-modify-private',
                        client_id=self.client_id, client_secret=self.client_secret,
                        redirect_uri=self.redirect_uri, 
                        )
        self.sp = spotipy.Spotify(auth=self.token)
        
    
class sp_Playlists(sp_UserInfo):
    # Print user play lists
    def print_user_playlists(self):
        playlists = self.sp.user_playlists(self.client_user)
        while playlists:
            for i, playlist in enumerate(playlists['items']):
                print('%4d %s %s' % (i + 1 + playlists['offset'], playlist['uri'], playlist['name']))
            if playlists['next']:
                playlists = self.sp.next(playlists)
            else:
                playlists = None
    
    # Print tracks in a play list
    def playlist_tracks(self, playlist):
        
        # print tracks in a playlist to cli
        def print_tracks(self, tracks):
            for i, item in enumerate(tracks['items']):
                track = item['track']
                print('    %d %32.32s %s' % (i, track['artists'][0]['name'], track['name']))
        
        # Find a play list ID by passings the playlists list and playlist name
        def find_playlist_id(self, playlists, playlist):
            # Loop through and find our playlist -- the index on this is weird
            for ct, i in enumerate(playlists):
                if playlists['items'][ct]['name'] == playlist:
                    return playlists['items'][ct]['id']
        
        # Get playlist tracks from playlist id
        # pass to print_tracks to display on CLI
        def playlist_tracks(self, playlist_id):
            # get tracks
            results = self.sp.user_playlist(self.client_user, playlist_id, fields="tracks,next")
            # evaluate and use show_tracks to print
            tracks = results['tracks']
            return tracks
        
        playlists = self.sp.user_playlists(self.client_user)
        
        try:
            return playlist_tracks(self, find_playlist_id(self, playlists, playlist))
        except:
            raise RuntimeError('Failed to return tracks!')

class sp_Artist(sp_UserInfo):
    def __init__(self, artist_name):
        sp_UserInfo.__init__(self)
        self.artist_name = artist_name
        self.artist_id = self.sp.search(self.artist_name, limit=1, type='artist')['artists']['items'][0]['id']
        self.top_tracks = None
        self.uri = None
        
    def get_top_tracks(self, song_ct=10):
        # Return top # of tracks for artist by Spotify popularity score
        top_tracks = self.sp.artist_top_tracks(self.artist_id, country='US')
        
        result_dict = {}
        for i in top_tracks['tracks']:
            result_dict[i['name']] = i['popularity']
            
        # sort by popularity and then splice to top 3
        t = sorted(result_dict.items(), key=lambda x:-x[1])[:song_ct]
        t = [x[0] for x in t]
        
        sorted_dict = {} # Return value with top 3 results
        for i in t:
            sorted_dict[i] = ''
        
        # Attach song URI so we can add it to a playlist later
        for i in top_tracks['tracks']:
            if i['name'] in sorted_dict:
                sorted_dict[i['name']] = i['uri']
        
        return sorted_dict
        
        
    def related_artist_list(self, artist_ct=20):
        results = self.sp.artist_related_artists(self.artist_id)
        
        results_dict = {} # empty dict for return data
        for i in results['artists']:
            results_dict[i['name']] = i['popularity']
        
        t = sorted(results_dict.items(), key=lambda x:-x[1])[:artist_ct]
        t = [x[0] for x in t]
        
        # empty dict to pass back artists
        sorted_dict = {}
        for i in t:
            sorted_dict[i] = ''
        
        for i in results['artists']:
            if i['name'] in sorted_dict:
                sorted_dict[i['name']] = i['uri']
        
        return sorted_dict

sp_A = sp_Artist('Celldweller')
pprint.pprint(sp_A.related_artist_list())