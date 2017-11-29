import libsonic
from subsonic import ask
from flask import Flask, json
from flask_ask import Ask, question, statement, session, audio, current_stream, logger
from qmanager import QueueManager
from fuzzywuzzy import process
from hashlib import md5
import os
from ryclass import SonicAuth
import random
from pprint import pprint

# Enter Info Here
sshost = "https://subsonic.example.org"
ssuser = "yourname"
sspass = "Secret Password"

sauth = SonicAuth(sshost, ssuser, sspass)
ssconn = sauth._ssconn
queue = QueueManager()

@ask.launch
def start_skill():
    #print 'the amazon user id is ' + session.user['userId']
    text = 'Welcome to Subsonic. \
            Try asking me to play a song or start a playlist'
    prompt = 'For example say, play music by Ozzy Osbourne'
    return question(text).reprompt(prompt) \
        .simple_card(title='Welcome to Subsonic!',
                     content='Try asking me to play a song')

@ask.intent("AMAZON.SearchAction<object@MusicCreativeWork>", mapping={'name': 'object.name', 'type': 'object.type', 'artist': 'object.byArtist.name'})
def play_music(type, name, artist):
    songs = []
    speech_text = None
    if type == 'songs':
        if artist:
            speech_text = play_artist(artist)
        elif name:
            speech_text = play_artist(name)
    elif type == 'album':
        if name and artist:
            speech_text = play_album(artist + " " + name)
        elif name and not artist:
            speech_text = play_album(name)
        elif not name and artist:
            speech_text = play_album_byartist(artist)
    elif not type:
        if name and artist:
            speech_text = play_song(name, artist)
        elif name and not artist:
            speech_text = play_song(name)
        elif artist and not name:
            speech_text = play_artist(artist)
    if speech_text:
        if queue.up_next:
            stream_url = sauth.getStreamUrl(queue.start())
            return audio(speech_text).play(stream_url)
        else:
            return statement(speech_text)
    else:
        return statement('Herpa derpa derped a herp')

def play_song(name, artist=None):
    reslt = ssconn.search(name, None, artist, None, 1)
    song = reslt['searchResult']['match'][0]
    queue.requeue([song['id']])
    return "Playing {} by {}".format(song['title'], song['artist'])

    
def play_album(name):
    songs = []
    reslt = ssconn.search3(name, 0, 0, 1, 0, 0, 0)
    albumid = reslt['searchResult3']['album'][0]['id']
    album = ssconn.getAlbum(albumid)['album']
    for song in album['song']:
        songs.append(song['id'])
    queue.requeue(songs)
    return "Playing the album {} by {}".format(album['name'], album['artist'])

    
def play_album_byartist(artist):
    songs = []
    reslt = ssconn.search3(artist, 0, 0, 50, 0, 0, 0)
    albums = reslt['searchResult3']['album']
    random.shuffle(albums)
    albumid = albums[0]['id']
    album = ssconn.getAlbum(albumid)['album']
    for song in album['song']:
        songs.append(song['id'])
    queue.requeue(songs)
    return "Playing the album {} by {}".format(album['name'], album['artist'])

    
def play_artist(artist):
    songs = []
    reslt = ssconn.search3(artist, 1, 0, 0, 0, 0, 0)
    if reslt['searchResult3']:
        topsongs = ssconn.getTopSongs(reslt['searchResult3']['artist'][0]['name'], 20)
        for song in topsongs['topSongs']['song']:
            songs.append(song['id'])
        random.shuffle(songs)
        del songs[-5:]
        firstsong = ssconn.getSong(songs[0])['song']
        queue.requeue(songs)
        return "Playing top songs by {} , first up is {}".format(reslt['searchResult3']['artist'][0]['name'], firstsong['title'])
    else:
        return "I searched for an artist named {}, but did not find anything ... I must have misunderstood, would you please let me try again?".format(artist)

@ask.intent("AMAZON.PlaybackAction<object@MusicPlaylist>", mapping={'name': 'object.name', 'type': 'object.type', 'mode': 'mode.name', 'owner': 'object.owner.name'})
def start_playlist(type, name, mode, owner):
    plid = None
    songs = []
    playlistbasic = []
    if owner and name:
        plname = owner + " " + name
    elif owner and not name:
        plname = owner
    else:
        plname = name
    plname = plname.replace("play ","")
    plname = plname.replace("start ","")
    plname = plname.replace("Playlist ","")
    playlists = ssconn.getPlaylists()
    for playlist in playlists['playlists']['playlist']:
        playlistbasic.append({'id':playlist['id'], 'name':playlist['name'].lower()})
        if plname.lower() == playlist['name'].lower():
            plid = playlist['id']
    if not plid:
        plid = process.extractOne(plname.lower(), playlistbasic)[0]['id']
    plist = ssconn.getPlaylist(plid)
    for song in plist['playlist']['entry']:
        songs.append(song['id'])
    queue.requeue(songs)
    stream_url = sauth.getStreamUrl(queue.start())
    speech_text = "Playing the %s %s" % (plist['playlist']['name'], type)
    return audio(speech_text).play(stream_url)
#    return statement(speech_text)


# QueueManager object is not stepped forward here.
# This allows for Next Intents and on_playback_finished requests to trigger the step
@ask.on_playback_started()
def playback_started():
    ssconn.scrobble(queue.current, False)

@ask.on_playback_nearly_finished()
def nearly_finished():
    ssconn.scrobble(queue.current)
    if queue.up_next:
        _infodump('Alexa is now ready for a Next or Previous Intent')
        # dump_stream_info()
        next_stream = sauth.getStreamUrl(queue.up_next)
        _infodump('Enqueueing {}'.format(next_stream))
        return audio().enqueue(next_stream)
    else:
        _infodump('Nearly finished with last song in playlist')


@ask.on_playback_finished()
def play_back_finished():
    _infodump('Finished Audio stream for track {}'.format(queue.current_position))
    if queue.up_next:
        queue.step()
        _infodump('stepped queue forward')
        dump_stream_info()
    else:
        return statement('You have reached the end of the playlist!')


# NextIntent steps queue forward and clears enqueued streams that were already sent to Alexa
# next_stream will match queue.up_next and enqueue Alexa with the correct subsequent stream.
@ask.intent('AMAZON.NextIntent')
def next_song():
    if queue.up_next:
        songid = queue.step()
        song = ssconn.getSong(songid)['song']
        next_stream = sauth.getStreamUrl(songid)
        speech = 'playing {} by {}'.format(song['title'], song['artist'])
        _infodump('Stepped queue forward to {}'.format(next_stream))
        dump_stream_info()
        return audio(speech).play(next_stream)
    else:
        return audio('There are no more songs in the queue')


@ask.intent('AMAZON.PreviousIntent')
def previous_song():
    if queue.previous:
        speech = 'playing previously played song'
        prev_stream = sauth.getStreamUrl(queue.step_back())
        dump_stream_info()
        return audio(speech).play(prev_stream)

    else:
        return audio('There are no songs in your playlist history.')


@ask.intent('AMAZON.StartOverIntent')
def restart_track():
    if queue.current:
        speech = 'Restarting current track'
        dump_stream_info()
        return audio(speech).play(sauth.getStreamUrl(queue.current), offset=0)
    else:
        return statement('There is no current song')


@ask.on_playback_started()
def started(offset, token, url):
    _infodump('Started audio stream for track {}'.format(queue.current_position))
    dump_stream_info()


@ask.on_playback_stopped()
def stopped(offset, token):
    _infodump('Stopped audio stream for track {}'.format(queue.current_position))

@ask.intent('AMAZON.PauseIntent')
def pause():
    seconds = current_stream.offsetInMilliseconds / 1000
    msg = 'Paused the Playlist on track {}, offset at {} seconds'.format(
        queue.current_position, seconds)
    _infodump(msg)
    dump_stream_info()
    return audio('Paused').stop().simple_card(msg)


@ask.intent('AMAZON.ResumeIntent')
def resume():
    seconds = current_stream.offsetInMilliseconds / 1000
    msg = 'Resuming the Playlist on track {}, offset at {} seconds'.format(queue.current_position, seconds)
    _infodump(msg)
    dump_stream_info()
    return audio(msg).resume().simple_card(msg)


@ask.session_ended
def session_ended():
    return "{}", 200

@ask.intent('AMAZON.CancelIntent')
def stop():
    queue.reset()
    return audio('Stopping').stop()

@ask.intent('AMAZON.StopIntent')
def stop():
    queue.reset()
    return audio('Stopping').stop()

def dump_stream_info():
    status = {
        'Current Stream Status': current_stream.__dict__,
        'Queue status': queue.status
    }
    _infodump(status)


def _infodump(obj, indent=2):
    msg = json.dumps(obj, indent=indent)
    logger.info(msg)
