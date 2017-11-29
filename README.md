### sublexa
Sublexa is a repository for created for the purpose sharing, collecting and testing code for integrating Subsonic personal media streamer with Amazon Alexa.  Currently this is closer to a hack than anything else however works as a proof of concept and does allow Alexa to play music directly from a personal subsonic server.  This is not intended for production use or distribution and will require a certain level of knowledge to implement

### Notes
**This code is not made or endorsed by the Subsonic Team**  That being said, this is inspired by [geemusic](https://github.com/stevenleeg/geemusic) and based off the [audio sample](https://github.com/johnwheeler/flask-ask/tree/master/samples/audio/playlist_demo) from [flask-ask](https://github.com/johnwheeler/flask-ask/)

**There is currently no authentication between Amazon and Sublexa - use at your own risk**  Amazon uses OAuth to authenticate Alexa Skills, as of yet no attempt has been made to implement this.  an issue will be opened in this repository to discuss.  Sublexa needs your password to authenticate with your subsonic server, but there is no authentication between Alexa and Sublexa.  Meaning if someone knows your subsonic URL they could configure a skill to point at your server and there is nothing to stop them from playing your music.

### Setup
Sublexa is designed to bolt-on to an existing subsonic server using a reverse proxy to facilitate TLS.  Amazon requires HTTPS so a certificate  and external domain will be required, Letsencrypt works fine.  You may need to purchase a domain or use a dynamic DNS service if you do not have a static IP address.

**Server Config**
These instructions are for linux (specifically I use debian) but it should bassicaly apply universally.  I assume you already have your domain name and subsonic setup with defaults.  Install Nginx, Letsencrypt, Python 2.7 and Pip, you can find instruction to install these if you need.  Clone the Git repository and copy content of the nginx.conf to the sites-enabled/default file, update the domain name from subsonic.example.org to your own domain name.  Get a certifacte from letsencrypt. example: certbot --nginx -d subsonic.example.org

**Python**
cd sublexa/flaskask/
run 'pip install -r requirements.txt' to install the required packages
update the variables in the file sublexa/flaskask/sublexa/intents.py to your server URL, username, and password
run the sublexa server 'python2.7 server.py'

**Alexa Skill**
go to https://developer.amazon.com/ sign in with the Amazon account you use for Alexa and register for a devleoper account
go to Alexa > Alexa Skill Kit and Create a new custom skill
make sure to select Yes an Audio Player
copy the content from speech_assets/intentSchema.json and speech_assets/sampleUtterances.txt into the interaction model
set the Default URL to your domain now in the format https://subsonic.example.org/alexa on the configuration page
now you should be able to test the skill

### Contributing
Please feel free to fork, open issues or PRs all are welcome

### License
This project is release under the MIT License.  Feel free to use, don't expect support
