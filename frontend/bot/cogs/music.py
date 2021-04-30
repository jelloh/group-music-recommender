import asyncio
import datetime as dt
import re
import random
import typing as t
from enum import Enum

import discord
import requests
import wavelink
from discord import Reaction
from discord.ext import commands

import os, sys
CURR_DIR = os.getcwd()
sys.path.append(CURR_DIR + "\\bot\\cogs\\utils")
from recommender import Recommender

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}
RATING_REACTIONS = {'👍' : 1, '👎': -1}

# I feel like there is a better way to do this, but...
rating_msgs = []

last_command = None

# set to true for songs to automatically be recommended when queue runs out
# automatic_recs = False


class AlreadyConnectedToChannel(commands.CommandError):
    pass

class NoVoiceChannel(commands.CommandError):
    pass

class QueueIsEmpty(commands.CommandError):
    pass

class NoTracksFound(commands.CommandError):
    pass

class PlayerIsAlreadyPaused(commands.CommandError):
    pass

# was commented out in video.. do we need this though
class PlayerIsAlreadyPlaying(commands.CommandError):
    pass

class NoMoreTracks(commands.CommandError):
    pass

class NoPreviousTracks(commands.CommandError):
    pass

class InvalidRepeatMode(commands.CommandError):
    pass

class KeywordsEmpty(commands.CommandError):
    pass


class RepeatMode(Enum):
    NONE = 0
    ONE = 1
    ALL = 2


class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0
        self.repeat_mode = RepeatMode.NONE

    @property
    def is_empty(self):
        return not self._queue

    @property
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty
        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]

    @property
    def upcoming(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[self.position + 1:]

    @property
    def history(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[:self.position]

    @property
    def length(self):
        return len(self._queue)

    def add(self, *args):
        self._queue.extend(args)

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty

        self.position += 1

        if self.position < 0:
            return None
        elif self.position > len(self._queue) - 1:
            if self.repeat_mode == RepeatMode.ALL:
                self.position = 0
            else:
                return None

        return self._queue[self.position]

    def shuffle(self):
        if not self._queue:
            raise QueueIsEmpty

        upcoming = self.upcoming
        random.shuffle(upcoming)
        self._queue = self._queue[:self.position + 1]
        self._queue.extend(upcoming)

    def set_repeat_mode(self, mode):
        if mode == "none":
            self.repeat_mode = RepeatMode.NONE
        elif mode == "1":
            self.repeat_mode = RepeatMode.ONE
        elif mode == "all":
            self.repeat_mode = RepeatMode.ALL

    def empty(self):
        self._queue.clear()


class Player(wavelink.Player):   

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlreadyConnectedToChannel

        if (channel := getattr(ctx.author.voice, "channel", channel)) is None:
            raise NoVoiceChannel

        self.text_channel = ctx.channel
        await super().connect(channel.id)
        return channel

    async def teardown(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise NoTracksFound

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)
        elif len(tracks) == 1:
            self.queue.add(tracks[0])
            await ctx.send(f"Added {tracks[0].title} to the queue.")
        else:
            if (track := await self.choose_track(ctx, tracks)) is not None:
                self.queue.add(track)
                await ctx.send(f"Added {track.title} to the queue.")
        
        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback(ctx)

    async def choose_track(self, ctx, tracks):
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )

        # TODO Would eventually be nice to have this show Hours:Minutes:Seconds 
        # instead of just Minutes:Seconds (inside the description) 
        embed = discord.Embed(
            title="Choose a song",
            description=(
                "\n".join(
                    f"**{i+1}.** {t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(text=f"Invoked by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        msg = await ctx.send(embed=embed)
        for emoji in list(OPTIONS.keys())[:min(len(tracks), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
        else:
            await msg.delete()
            return tracks[OPTIONS[reaction.emoji]]

    async def start_playback(self, ctx):
        await self.play(self.queue.current_track)
        await self.rate_song()
        
    async def advance(self):
        try:
            if (track := self.queue.get_next_track()) is not None:
                await self.play(track)
                await self.rate_song()
        except QueueIsEmpty:
            pass

    async def repeat_track(self):
        await self.play(self.queue.current_track)

    async def rate_song(self):
        
        embed = discord.Embed(
            title="Rate the current song",
            description=(
                f"{self.queue.current_track.title}"
            ),
            #colour=ctx.me.colour,
            timestamp=dt.datetime.utcnow()
        )
        #embed.set_author(name="Query Results")
        #embed.set_footer(text=f"{self.queue.current_track.ytid}")
        embed.set_footer(text=f"{self.queue.current_track.uri}")

        embed.set_thumbnail(url=self.queue.current_track.thumb)

        msg = await self.text_channel.send(embed=embed)
        #msg = await bot.say("Rate the current song")
        
        # add the message id to keep track of the songs to be rated
        # will be used when listening for reactions
        rating_msgs.append(
            {"message_id" : msg.id,
             "video_id" : self.queue.current_track.ytid}
            )

        for emoji in RATING_REACTIONS.keys():
            await msg.add_reaction(emoji)

    
class Music(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())

        self.recommender = None
        self.automatic_recs = False

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Use this to determine when to leave the voice channel.
        """
        if not member.bot and after.channel is None: # check to see if member left the channel
            if not [m for m in before.channel.members if not m.bot]: # check to see if member is bot
                await self.get_player(member.guild).teardown() # disconnect the bot from the channel (ep4)

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f" Wavelink node `{node.identifier}` ready.")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        if payload.player.queue.repeat_mode == RepeatMode.ONE:
           await payload.player.repeat_track()
        else:
            await payload.player.advance()


    async def cog_check(self, ctx):
        """
        Automatically applied to all commands. Disallow commands sent from DM.
        """
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Music commands are not available in DMs.")
            return False

        return True

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "MAIN",
                "region": "us_central", 
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)


    # --------------------------------------------------------------------
    # PLAYER COMMANDS
    # --------------------------------------------------------------------
    # TODO/Ideas
    # - command to play top (add a song to the top of the queue)

    @commands.command(name="connect", aliases=["join","hello"])
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        #await ctx.send(f"Connected to {channel.name}.")
        await ctx.send(f"(*￣3￣)╭ Hello! I've joined {channel.name}~")

        global last_command
        last_command = "connect"

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlreadyConnectedToChannel):
            #await ctx.send("Already connected to a voice channel.")
            await ctx.send("（；´д｀）ゞ I'm already connected to a voice channel.")
        elif isinstance(exc, NoVoiceChannel):
            #await ctx.send("No suitable voice channel was provided.")
            await ctx.send("(´。＿。｀) I don't know where to join!")

    @commands.command(name="disconnect", aliases=["leave", "bye"])
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.teardown()
        #await ctx.send("Disconnect.")
        await ctx.send("~(>_<。)＼ Bye!")

    @commands.command(name="play", aliases=["p"])
    async def play_command(self, ctx, *, query: t.Optional[str]):
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:

            if player.queue.is_empty:
                raise QueueIsEmpty

            await player.set_pause(False)
            #await ctx.send("Playback resumed.")
            await ctx.send("(づ￣ 3￣)づ Resuming playback~")

        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"
            
            await player.add_tracks(ctx, await self.wavelink.get_tracks(query))

        global last_command
        last_command = "play"

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPlaying):
            #await ctx.send("Already playing.")
            await ctx.send("(╬▔皿▔)╯ What are you doing? I'm already playing!")
        elif isinstance(exc, QueueIsEmpty):
            #await ctx.send("No songs to play as the queue is empty.")
            await ctx.send("╰（‵□′）╯ The queue is empty! No songs for me to play you.")

    @commands.command(name="pause")
    async def pause_command(self, ctx):
        player = self.get_player(ctx)

        if player.is_paused:
            raise PlayerIsAlreadyPaused

        if player.queue.is_empty:
            raise QueueIsEmpty

        await player.set_pause(True)
        #await ctx.send("Playback paused.")
        await ctx.send("(￣o￣) . z Z Pausing your music..")

        global last_command
        last_command = "pause"
        
    @pause_command.error
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("Already paused.")
        elif isinstance(exc, QueueIsEmpty):
            await ctx.send("No song currently playing as the queue is empty.")

    @commands.command(name="stop")
    async def stop_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.empty()
        await player.stop()
        #await ctx.send("Playback stopped.")
        await ctx.send("( •̀ ω •́ )✧ Ok! I'll stop playing songs.\nI also cleared your queue for you. ")

        global last_command
        last_command = "stop"

    @commands.command(name="next", aliases=["skip"])
    async def next_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.upcoming:
            raise NoMoreTracks
        await player.stop()
        #await ctx.send("playing next track in queue.")
        await ctx.send("╰(*°▽°*)╯ Skipping this song~ ")

        global last_command
        last_command = "next"

    @next_command.error
    async def next_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            #await ctx.send("This could not be executed as the queue is currently empty.")
            await ctx.send("(´。＿。｀)... Your queue is empty. ")
        elif isinstance(exc, NoMoreTracks):
            #await ctx.send("There are no more tracks in the queue.")
            await ctx.send("o(￣┰￣*)ゞ You have no more tracks in the queue!")

    @commands.command(name="previous")
    async def previous_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.history:
            raise NoPreviousTracks

        player.queue.position -= 2
        await player.stop()
        #await ctx.send("playing previous track in queue.")
        await ctx.send("(～￣▽￣)～ Going back one~ Playing the previous track.")

        global last_command
        last_command = "previous"

    @commands.command(name="shuffle")
    async def shuffle_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.shuffle()
        #await ctx.send("Queue shuffled.")
        await ctx.send("( •̀ ω •́ )✧ I shuffled your queue!")

        global last_command
        last_command = "shuffle"

    @shuffle_command.error
    async def  shuffle_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            #await ctx.send("The queue could not be shuffled as it is currently empty.")
            await ctx.send("/(ㄒoㄒ)/~~ Your queue is empty! There's nothing for me to shuffle.")

    @commands.command(name="repeat")
    async def repeat_command(self, ctx, mode: str):
        if mode not in ("none","1","all"):
            raise InvalidRepeatMode

        player = self.get_player(ctx)
        player.queue.set_repeat_mode(mode)
        await ctx.send("The repeat mode has been set to {mode}.")

        global last_command
        last_command = "repeat"

    @previous_command.error
    async def previous_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("This could not be executed as the queue is currently empty.")
        elif isinstance(exc, NoPreviousTracks):
            await ctx.send("There are no previous tracks in the queue.")

    @commands.command(name="queue")
    async def queue_command(self, ctx, show: t.Optional[int] = 10):
        player = self.get_player(ctx)

        if player.queue.is_empty:
            raise QueueIsEmpty

        embed = discord.Embed(
            title="Queue",
            colour=ctx.author.colour,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Currently playing",
                        value=getattr(player.queue.current_track,"title","No tracks currently playing."),
                        inline=False
                        )
        if upcoming := player.queue.upcoming:
            embed.add_field(
                name="Next up",
                value="\n".join(t.title for t in player.queue.upcoming[:show]),
                inline=False
            )

        msg = await ctx.send(embed=embed)

        global last_command
        last_command = "queue"

    @queue_command.error
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            #await ctx.send("The queue is currently empty.")
            await ctx.send("(。﹏。*) Your queue is empty..")

    # --------------------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------------------

    keyword_list = []
    @commands.command(name="keywordadd", aliases=['addkeyword','keyadd','ka','ak'])
    async def add_keyword_command(self, ctx, arg):
        await ctx.send(f"(‾◡◝) Adding your keyword: {arg}")
        self.keyword_list.append(arg)
        
        print(self.keyword_list)

        global last_command
        last_command = "keywordadd"

    @commands.command(name="keywordremove", aliases=['removekeyword','keyremove', 'kr','rk'])
    async def remove_keyword_command(self, ctx, arg):
        await ctx.send(f"(˘･_･˘) I removed your keyword: {arg}")
        self.keyword_list.remove(arg)
        
        print(self.keyword_list)

        global last_command
        last_command = "keywordremove"

    @commands.command(name="keywordclear", aliases=["clearkeywords", "clearkeys", "keyclear"])
    async def clear_keyword_command(self, ctx):
        await ctx.send("(❁´◡`❁) Clearing all keywords..")
        self.keyword_list = []

        global last_command
        last_command = "keywordclear"

    @commands.command(name="setautorecommend", aliases=["setauto", "changeauto", "changeautorecommend"])
    async def set_auto_recommender_command(self, ctx):
        if self.automatic_recs == False:
            await ctx.send("(゜▽゜*)♪ Ok! I'll automatically recommend songs when your queue is empty.")
            self.automatic_recs = True
        elif self.automatic_recs == True:
            await ctx.send("I'll stop recommending songs then~ \n(°ロ°) Play your own music!")
            self.automatic_recs = False

        global last_command
        last_command = "setautorecommend"

    @commands.command(name="recommend")
    async def recommend_command(self, ctx, arg):
        """
        args:
        1 - K. a number to specify how many songs to recommend and add to the queue. 
            Will recommend top-K songs based on the strategy
        """

        # Error handling for if no keywords exit
        if(len(self.keyword_list) == 0):
            raise KeywordsEmpty
            
        await ctx.send("This might take a little bit. \nI am learning `(*>﹏<*)′ Please be patient. ❤")

        K = int(arg[0])

        # initialize recommender 
        if(self.recommender is None):
            print("initializing recommender")
            self.recommender = Recommender(self.keyword_list)

        # Update video list only if keywords have changed
        # (so we don't have to search youtube every single time)
        print(f"keyword list: {self.keyword_list}")
        print(f"recommender's keywords: {self.recommender.get_keywords()}")
        if(set(self.keyword_list) != set(self.recommender.get_keywords())):
            print("updating keywords")
            self.recommender.set_keywords(self.keyword_list)
            self.recommender.update_video_list()
        
        # Add the tracks now
        player = self.get_player(ctx)

        for video in self.recommender.recommend(K):
            await player.add_tracks(ctx, await self.wavelink.get_tracks(video))

        global last_command
        last_command = "recommend"

    @recommend_command.error
    async def recommend_command_error(self, ctx, exc):
        if isinstance(exc, KeywordsEmpty):
            await ctx.send("（*゜ー゜*）I can't recommend without some keywords first! \nAdd some. *p l e a s e ~*")

    # --------------------------------------------------------------------
    # LISTENERS
    # --------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user):
        
        # I feel like there's definitely a better way to do this
        # get the index of the rating video this reaction is for
        # -1 if reaction is to an unrelated message
        try:
            i = [i for i, d in enumerate(rating_msgs) if rating_msgs[i]['message_id'] == reaction.message.id][0]
        except:
            i = -1

        # only do the following if the reaction is to a rating video message
        if(user.id != 828089987366256640 and i>=0):
            # get all the values we need: user id, rating, video id
            user_id = user.id
            rating = RATING_REACTIONS[reaction.emoji]
            youtube_id = rating_msgs[i]['video_id']
            #print(f"Message id: {reaction.message.id}")
            
            # get the url for the api call
            url = f"http://localhost/ratings/add_rating/{user_id}"
            
            # parameters/form data for the api call
            params = {
                "video_id" : youtube_id,
                "rating" : rating
            }

            # make the call
            r = requests.patch(url, data=params)
            print(r)

        


def setup(bot):
    bot.add_cog(Music(bot))
