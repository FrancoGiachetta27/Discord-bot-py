import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import utils


class BotSpotify:
    def __init__(self, id, secret):

        self.spotify = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=id,
                client_secret=secret,
            )
        )

    async def get_playlist(self, ctx, name):
        playlist = self.spotify.search(q=name, limit=1, type="playlist", market=None)
        url = playlist["playlists"]["items"][0]["external_urls"]["spotify"]
        tracks = self.spotify.playlist_tracks(playlist["playlists"]["items"][0]["id"])

        await ctx.send(url)

        return tracks
