from dbus.mainloop.glib import DBusGMainLoop
import mpris2
import lyricsgenius
from os import path

import gi.repository.GLib

def get_player():
    uris = list(mpris2.get_players_uri())

    if len(uris) == 0:
        raise Exception("No Mpris2 player detected. Are you sure you're running Spotify?")

    if len(uris) == 1:
        match = uris[0]
    else:
        match = None
        for u in uris:
            if u.split('.')[-1] == "spotify":
                match = u
                break
        if match is None:
            print("Mpris2 players were found be not spotify. Please select a player:")
            for i, u in enumerate(uris):
                print("[%d] %s" % (i, u))

            while match is None:
                inp = input("Enter number: ")
                try:
                    inp = int(inp)
                except Exception as e:
                    print("%s is not a integer." % inp)
                if inp < 0 or inp >= len(uris):
                    print("%d is not a valid option." % inp)
                else:
                    match = uris[inp]

    return mpris2.Player(dbus_interface_info={'dbus_uri': match}), match


def getLyrics(genius, title, artist):
    song = genius.search_song(title, artist)
    if song:
        return song.lyrics
    else:
        return None


def start_loop():
    DBusGMainLoop(set_as_default=True)

    player, uri = get_player()

    with open(path.join("genius_token.txt"), "r") as f:
        genius = lyricsgenius.Genius(f.readline()[:-1])


    current_title = player.Metadata["xesam:title"]
    current_artist = player.Metadata["xesam:artist"][0]
    print(getLyrics(genius, player.Metadata["xesam:title"], player.Metadata["xesam:artist"][0]))


    def handler(self, *args, **kargs):
        nonlocal current_title
        nonlocal current_artist
        title = args[0]["Metadata"]["xesam:title"]
        artist = args[0]["Metadata"]["xesam:artist"][0]
        if title != current_title or artist != current_artist:
            print()
            print("=" * 40)
            lyrics = getLyrics(genius, title, artist)
            current_title = title
            current_artist = artist
            print()
            print(lyrics)

    player.PropertiesChanged = handler

    mloop = gi.repository.GLib.MainLoop()
    mloop.run()


start_loop()
