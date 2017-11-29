# sublexa
Sublexa is a repository for created for the purpose sharing, collecting and testing code for integrating Subsonic personal media streamer with Amazon Alexa.  Currently this is closer to a hack than anything else however works as a proof of concept and does allow Alexa to play music directly from a personal subsonic server.  This is not intended for production use or distribution and will require a certain level of knowledge to implement

### Notes
**This code is not made or endorsed by the Subsonic Team**  That being said, this is inspired by [geemusic] (https://github.com/stevenleeg/geemusic) and based off the [audio sample] (https://github.com/johnwheeler/flask-ask/tree/master/samples/audio/playlist_demo) from [flask-ask] (https://github.com/johnwheeler/flask-ask/)

**There is currently no authentication between Amazon and Sublexa - use at your own risk**  Amazon uses OAuth to authenticate Alexa Skills, as of yet no attempt has been made to implement this.  an issue will be opened in this repository to discuss.  Sublexa needs your password to authenticate with your subsonic server, but there is no authentication between Alexa and Sublexa.  Meaning if someone knows your subsonic URL they could configure a skill to point at your server and there is nothing to stop them from playing your music.

### Setup
Sublexa is designed to bolt-on to an existing subsonic server using a reverse proxy to facilitate TLS.  Amazon requires HTTPS so a certificate  and external domain will be required, Letsencrypt works fine.  You may need to purchase a domain or use a dynamic DNS service if you do not have a static IP address.

More details to come, if you are reading this now...  please come back later because I have not finished the readme
