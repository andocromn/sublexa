from hashlib import md5
import os
import libsonic


class SonicAuth():

    def __init__(self, host, user, passwd, port=443):
        self._host = host
        self._user = user
        self._port = port
        self._salt = md5(os.urandom(100)).hexdigest()[:12]
        self._token = md5(passwd + self._salt).hexdigest()
        self._ssconn = libsonic.Connection(host, user, passwd, port=self._port)

    def getStreamUrl(self, songid):
        return self._host + ":" + str(self._port) + "/rest/stream?id=" + str(songid) + "&u=" + self._user + "&t=" + self._token + "&s=" + self._salt + "&c=Alexa&v=1.16.0"

