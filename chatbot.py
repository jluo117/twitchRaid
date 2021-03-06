'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
'''

import sys
import irc.bot
import requests
from threading import Thread
from Game import Game
class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channelID, callback,token):
        self.client_id = 'null'
        self.token = token
        self.channel = '#' + channelID
        self.onMessage = callback
        self.c = None
        self.e = None
        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channelID
        headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print ('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+self.token)], channelID, channelID)


    def on_welcome(self, c, e):
        print ('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        c.privmsg(self.channel, "your streamer has started an epic fight")
        c.privmsg(self.channel, "!attack/atk to attack !interupt/int to interupt !heal to heal and don't forget to use your cheers")
        self.c = c
        self.e = e

    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print ('Received command: ' + cmd + self.channel)
            self.onMessage(self.channel, cmd)
        return
    def post_round(self,message,game):
        self.c.privmsg(self.channel,message)

def main():
    game = Game("null","null")
    bots = []
    def UserMessage(channelID , message):
        game.stream1Chat.append(message)
        print(game.stream1Chat,game.stream2Chat)
        if game.validSize():
            outPut = game.turn()
            for bot in bots:
                bot.post_round(outPut,game)
    bots.append(TwitchBot("null", UserMessage,'id'))
    def UserMessage2(channelID, message):
            game.stream2Chat.append(message)
            print(game.stream1Chat,game.stream2Chat)
            if game.validSize() :
                outPut = game.turn()
                for bot in bots:
                    bot.post_round(outPut,game)
    bots.append(TwitchBot("null", UserMessage2,'id'))
    for bot in bots:
        t = Thread(target=bot.start, args=())
        t.start()

if __name__ == "__main__":
    main()
