import discord, os, mechanicalsoup, asyncio, sqlite3, json, mystbin
from discord.ext import commands, tasks, menus
from datetime import datetime

class BoxMenu(menus.Menu):
    def __init__(self, ctx, results):
        super().__init__()
        self.ctx = ctx
        self.results = results
        self.pg = 0
    
    async def myst(self, text):
        mystclient = mystbin.Client()
        paste = await mystclient.post(text, syntax="text")
        await mystclient.close()
        return paste.url

    async def cleanResults(self):
        if self.results["success"]:
            self.uname = self.results["data"]["name"]
            self.uid = self.results["data"]["id"]
            self.desc = ""
            coloreds = ["Ancient", "Cursed", "Glitter", "Golden", "Luminous", "Rainbow", "Shadow"]
            op = [i["name"] + " " + i["gender"] + " - Level: " + str(i["level"]) for i in self.results["data"]["pokemon"] if
                  i["loan"] == "0" and any(i["name"].startswith(x) for x in coloreds)]
            self.pkcount = len(op)

            def chunks(lst, n):
                for i in range(0, len(lst), n):
                    yield lst[i: i + n]
            if not op:
                self.desc = f"`{self.uname}'s box contains no colored pokemons.`"
                self.results = []
            else:
                self.results = list(chunks(op, 20))
                mytext = f"Box of {self.uname} - #{self.uid}\n"
                mytext += f"(This box contains {self.pkcount} colored pokemons)\n\n"
                pokes = [poke for lst in self.results for poke in lst]
                mytext += "\n".join(pokes)
                mytext += "\n\n>> Box organizer by TES Bot <<"
                self.pasteURL = await self.myst(mytext)

        else:
            self.desc = f"`Please provide a valid username.`"
            self.results = None

    def genEmbed(self):
        embed = discord.Embed(color = discord.Color.dark_gold())
        embed.set_author(name = "Box of " + self.uname + ' - #' + self.uid)
        return embed
    
    def getPagewiseDetails(self, pg):
        result = self.results
        if result == []:
            embed = discord.Embed()
            embed.set_author(name = "Box of " + self.uname + ' - #' + self.uid)
            embed.description = self.desc
            embed.set_footer(text=f"Box Organizer", icon_url= self.ctx.me.avatar_url)
            return embed

        if result is None:
            embed = discord.Embed()
            embed.set_author(name = "Username not found")
            embed.description = self.desc
            embed.set_footer(text=f"Box Organizer", icon_url= self.ctx.me.avatar_url)
            return embed

        embed = self.genEmbed()
        self.desc = f"**(This box contains {self.pkcount} colored pokemons)**\n[Click here to get the complete list!]({self.pasteURL})\n\n"
        embed.description = self.desc + "\n".join(result[pg])
        embed.set_footer(text=f"Box Organizer | Page {pg+1} of {len(result)}", icon_url= self.ctx.me.avatar_url)
        return embed
                    
    def check(self, payload):
        return payload.message_id == self.message.id and payload.user_id == self.ctx.author.id
                    
    async def send_initial_message(self, ctx, channel):
        await self.cleanResults()
        embed = self.getPagewiseDetails(self.pg)
        return await channel.send(embed=embed)
    
    buttonz = {"first": "<:first:800209150227120158>","back": "<:back:800215055634399232>", "stop": "<:stop:800214101791735808>", "next": "<:next:800214875669528596>", "last": "<:last:800209919734972426>", "page": "\U0001f522"}
    
    @menus.button(buttonz.get("first"))
    async def on_first_button(self, payload):
        if not self.check(payload):
            return 
        self.pg = 0
        self.pg %=  len(self.results)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
    
    @menus.button(buttonz.get("back"))
    async def on_previous_button(self, payload):
        if not self.check(payload):
            return
        self.pg -= 1
        self.pg %=  len(self.results)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
                
    @menus.button(buttonz.get("stop"))
    async def on_stop_button(self, payload):
        if not self.check(payload):
            return
        self.stop()
        await self.message.delete()
                        
    @menus.button(buttonz.get("next"))
    async def on_next_button(self, payload):
        if not self.check(payload):
            return 
        self.pg += 1
        self.pg %=  len(self.results)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
        
    @menus.button(buttonz.get("last"))
    async def on_last_button(self, payload):
        if not self.check(payload):
            return 
        self.pg = -1
        self.pg %=  len(self.results)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))

    @menus.button(buttonz.get("page"))
    async def on_page_button(self, payload):
        if not self.check(payload):
            return
        tmp = await self.message.channel.send(f"`Enter the Page Number (1 - {len(self.results)}):`")

        def check(message):
            return message.author == payload.member

        try:
            msg  = await self.bot.wait_for('message', timeout = 10, check=check)
        except asyncio.TimeoutError:
            await tmp.delete()
            await self.message.channel.send('`Too bad!! You did not enter the page number...`', delete_after=3)
        else:
            try:
                await tmp.delete()
                await msg.delete()
                x = int(msg.content) - 1
                if 0 < x <= len(self.results):
                    self.pg = x
                    await self.message.edit(embed=self.getPagewiseDetails(self.pg))
                else:
                    raise Exception
            except:
                await self.message.channel.send('`Invalid page number.`', delete_after=3)


class PokemonCreed(commands.Cog):
    """Pokemon Creed related commands"""
    def __init__(self, client):
        #uncomment the below line before uploading to github
        self.hitdownBGTask.start()
        self.promoBGTask.start()
        self.client = client

    def convertNumber(self, x):
        op = 0
        num_map = {'K': 1000, 'M': 1000000, 'B': 1000000000, 'T': 1000000000000, 'Q': 1000000000000000}
        if x.isdigit():
            op = int(x)
        else:
            if len(x) > 1:
                op = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
        return int(op)

    #set HitdownNotif as True for notification
    HitdownNotif = True
    Promo = ""

    @property
    def get_hd_channel(self):
        return self.client.get_channel(530734189633601536)
    @property
    def get_promo_channel(self):
        return self.client.get_channel(781395831353638942)

    async def scrape_hd(self):
        cred = os.environ.get('CREED_LOGIN').split(',')
        time_dict = {}
        browser = mechanicalsoup.StatefulBrowser()
        browser.open('https://pokemoncreed.net/login.php')
        browser.get_current_page()
        browser.select_form()
        browser["username"] = cred[0]
        browser["password"] = cred[1]
        response = browser.submit_selected()
        await asyncio.sleep(1)
        browser.open('https://pokemoncreed.net/hitdown.php')
        data = browser.get_current_page().text
        data = data[data.index('Time till next round:'):]
        data = data[22:data.index('.')]
        tmp = ''
        for i in range(len(data) - 1):
            if data[i].isnumeric():
                tmp += data[i]
            elif data[i + 1].isnumeric():
                tmp += ':'
            else:
                continue

        if all(i in data for i in ['hour', 'minutes']):
            t = tmp.split(':')
            time_dict['h'] = int(t[0])
            time_dict['m'] = int(t[1])
            time_dict['s'] = int(t[2])

        elif 'hour' not in data and 'minutes' in data:
            t = tmp.split(':')
            time_dict['h'] = 0
            time_dict['m'] = int(t[0])
            time_dict['s'] = int(t[1])

        elif 'hour' in data and 'minutes' not in data:
            t = tmp.split(':')
            time_dict['h'] = int(t[0])
            time_dict['m'] = 0
            time_dict['s'] = int(t[1])
        else:
            t = tmp.split(':')
            time_dict['h'] = 0
            time_dict['m'] = 0
            time_dict['s'] = int(tmp)

        browser.open('https://pokemoncreed.net/logout.php')
        return time_dict

    # <# BG Task: Hitdown - Start #>

    @tasks.loop(seconds = 120)
    async def hitdownBGTask(self):
        hd_channel = self.get_hd_channel
        if self.HitdownNotif != True:
            return

        try:
            t = await self.scrape_hd()
            sec = (t['h'] * 60 * 60) + (t['m'] * 60) + t['s'] - 100
            await asyncio.sleep(sec)
            await self.client.change_presence(activity = discord.Game('Hitdown'))
            await hd_channel.send('@everyone, It\'s Hitdown time!')
            await asyncio.sleep(300)
            await self.client.change_presence(activity = discord.Game('Pokemon Creed'))
        except:
            print(f'Restarting Hitdown Nootification!')
            await asyncio.sleep(120)
            self.hitdownBGTask.restart()

    @hitdownBGTask.before_loop
    async def before_hitdownBGTask(self):
        await self.client.wait_until_ready()

    # <# BG Task: Hitdown - End #>

    # <# BG Task: Promo - Start #>

    @tasks.loop(seconds = 10)
    async def promoBGTask(self):
        promo_channel = self.get_promo_channel
        url = 'https://pokemoncreed.net/ajax/pokedex.php?pokemon=promo'
        browser = mechanicalsoup.StatefulBrowser()
        browser.open(url)
        data = browser.get_current_page().text
        result = json.loads(data)
        current_promo = result["name"]
        if self.Promo == "":
            self.Promo = current_promo
        elif self.Promo != current_promo:
            self.Promo = current_promo
            embed = discord.Embed(title = f"New Promo: {self.Promo}")
            embed.description = f"** Promo Center - [Claim Promo](https://www.pokemoncreed.net/promo.php)**"
            embed.color = discord.Color.blue()
            embed.set_image(url = f"https://pokemoncreed.net/sprites/{self.Promo}.png")
            embed.set_footer(text = f"{self.Promo} | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", icon_url = f"https://pokemoncreed.net/img/icon/{self.Promo}.gif")
            await promo_channel.send("@everyone", embed = embed)

    @promoBGTask.before_loop
    async def before_promoBGTask(self):
        await self.client.wait_until_ready()

    # <# BG Task: Promo - End #>

    @commands.command(hidden = True, aliases = ['HitdownNotif','HitdownNotification'])
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.is_owner()
    async def hdnotif(self, ctx):
        """Toggles hitdown notification."""
        if self.HitdownNotif == True:
            self.HitdownNotif = False
            self.hitdownBGTask.cancel()
            x = await ctx.send('Hitdown notification disabled!', delete_after = 10)
        else:
            self.HitdownNotif = True
            try:
                self.hitdownBGTask.cancel()
                self.hitdownBGTask.start()
            except:
                self.hitdownBGTask.start()
            x = await ctx.send('Hitdown notification enabled!', delete_after = 10)

    @commands.group()
    async def exp(self, ctx):
        """Calculates Xp related stuffs."""
        scmds = [c.qualified_name + f" - {c.help}" +"\n" for c in self.exp.commands]
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="Exp Sub Commands:")
            embed.description = f'```{"".join(scmds)}```'
            embed.set_footer(text="do !help exp <subcommand> for more info")
            await ctx.send(embed=embed)
       
    @exp.command(name = "for")
    async def exp_for(self, ctx, level:str):
        """Calculates Xp required for given Level."""
        level = level.replace(",","")
        try:
            level = self.convertNumber(level)
        except Exception as e:
            await ctx.send(f"```Invalid inputs provided!```", delete_after=3)
            return
        embed = discord.Embed()
        embed.description = f"```Level: {level:,} pokemon will have {(level ** 3) + 1:,} xp!```"
        await ctx.send(embed=embed)
        
    @exp.command(name = "gain")
    async def exp_gain(self, ctx, level:str, *, bonus = ''):
        """Calculates Xp gained against Mew for given Level."""
        multiplier = 1
        boosts = []
        level = level.replace(",","")
        if 'egg' in bonus:
            multiplier *= 1.6
            boosts.append('Lucky Egg')
        if 'vip' in bonus:
            multiplier *= 1.25
            boosts.append('VIP')
        try:
            level = self.convertNumber(level)
        except Exception as e:
            await ctx.send(f"`Invalid inputs provided!`", delete_after=3)
            return
        exp = round(multiplier * (level * 10) ** 1.7)
        embed = discord.Embed()
        
        if multiplier > 1:
            embed.description = f"```With {' & '.join(boosts)}, You will receive {exp:,} xp against Mysterious Trainer's Mew for level {level:,}.```"
        else:
            embed.description = f"```You will receive {exp:,} xp against Mysterious Trainer's Mew for level {level:,}.```"
        await ctx.send(embed=embed)
        
    @exp.command(name = "diff")
    async def exp_diff(self, ctx, level1:str, level2:str):
        """Calculates Xp difference between given two levels."""
        level1 = level1.replace(",","")
        level2 = level2.replace(",","")
        try:
            levels = sorted([self.convertNumber(lvl) for lvl in [level1, level2]])
        except Exception as e:
            await ctx.send(f"```Invalid inputs provided!```", delete_after=3)
            return
        exp = round((levels[1] ** 3 - levels[0] ** 3))
        embed = discord.Embed()
        embed.description = f'```The xp difference between level: {levels[0]:,} and level: {levels[1]:,} is {exp:,} xp!```'
        await ctx.send(embed=embed)
        
    @exp.command(name = "level")
    async def exp_level(self, ctx, experience:str):
        """Calculates Level corresponding to given Xp."""
        experience = experience.replace(",","")
        try:
            exp = self.convertNumber(experience)
        except Exception as e:
            await ctx.send(f"```Invalid inputs provided!```", delete_after=3)
            return
        level = int((exp ** (1/3)))
        embed = discord.Embed()
        embed.description = f'```Level: {level:,} pokemon will have {exp:,} xp!```'
        await ctx.send(embed=embed)
        
    @exp.command(name = "train")
    async def exp_train(self, ctx, *, levelTOexp):
        """Calculates New Level after training the given Level by given Xp."""
        levelTOexp = levelTOexp.replace(",","")
        try:
            level, exp = levelTOexp.replace(" ","").split("to")
        except:
            await ctx.send("Invalid inputs! Use `exp train <level> to <exp>`", delete_after=5)
            return
        
        try:
            level = self.convertNumber(level)
            exp = self.convertNumber(exp)
        except Exception as e:
            await ctx.send(f"```Invalid inputs provided!```", delete_after=3)
            return
        
        flevel = ((level ** 3 + 1) + exp) ** (1/3)
        embed = discord.Embed()
        embed.description = f'```Training level {level:,} to {exp:,} xp will be level {int(flevel):,}!```'
        await ctx.send(embed=embed)

    @commands.command(aliases = ['dex'])
    async def pokedex(self, ctx, *, value):
        """Displays pokedex details of the given #ID/Pokemon."""
        botdb = sqlite3.connect('botdb.db')
        cursor = botdb.cursor()

        if all(ch.isnumeric() for ch in value):
            if int(value) <= 890:
                fetch = cursor.execute('select * from Pokedex where id = ?', (str(value).zfill(3),)).fetchone()
            else:
                raise ValueError
        else:
            fetch = cursor.execute('select * from Pokedex where lower(name) = ?', (value.lower(),)).fetchone()

        try:
            if len(fetch[3]) == 0:
                t = fetch[2]
            else:
                t = fetch[2] + ' | ' + fetch[3]

            desc = f"**Type: {t}**\n**HP:** {fetch[4]}\n**Attack:** {fetch[5]}\n**Defense:** {fetch[6]}\n**Sp.Attack:** {fetch[7]}\n**Sp.Defense:** {fetch[8]}\n**Speed:** {fetch[9]}\n**Total:** {fetch[10]}\n"
            embed = discord.Embed(title = f'Pokedex #{fetch[0][:3]} : {fetch[1]}',
                                  description = desc,
                                  color = discord.Color.teal())
            embed.set_image(url = 'https://www.serebii.net/pokemon/art/' + fetch[11])
            await ctx.send(embed = embed)

        except:
            embed = discord.Embed(title = 'Pokedex Error',
                                  description = 'The #ID/Pokemon doesn\'t exist!',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)

        finally:
            botdb.close()

    @commands.command(aliases = ['mv'])
    async def move(self, ctx, *, value):
        """Displays move details of the given pokemon move."""
        db = sqlite3.connect('botdb.db')
        cursor = db.cursor()
        try:
            output = cursor.execute('select * from Moves where lower(name) = ?', (value.lower(),)).fetchall()
            if len(output) == 0:
                suggestions = cursor.execute('select * from Moves where lower(name) like ?',
                                             ('%' + value.lower() + '%',)).fetchall()
                if len(suggestions) == 0:
                    suggestion = 'Try searching a part of the move name?'
                else:
                    suggestion = 'Looking for any of the below moves?\n'
                    for mv in suggestions:
                        suggestion += '`' + mv[1] + '`\n'
                embed = discord.Embed(title = 'Move not found',
                                      description = suggestion,
                                      color = discord.Color.teal())
            else:
                desc = '**Type:** {0[2]}\n**Category:** {0[3]}\n**Base Power:** {0[4]}\n**Accuracy:** {0[5]}\n'.format(
                    output[0])
                embed = discord.Embed(title = f'Move: {output[0][1]}',
                                      description = desc,
                                      color = discord.Color.teal())
                type_url = 'https://raw.githubusercontent.com/EliteB0Y/TestBot/master/Images/' + output[0][2] + '.png'
                embed.set_thumbnail(url = type_url)
            await ctx.send(embed = embed)

        except Exception as e:
            raise e
        finally:
            db.close()

    @commands.command(aliases = ['rate', 'rarity'])
    async def p(self, ctx, *, pokemon):
        """Displays rate, rarity and sprite of the Creed Pokemon."""
        url = 'https://pokemoncreed.net/ajax/pokedex.php?pokemon=' + pokemon
        browser = mechanicalsoup.StatefulBrowser()
        browser.open(url)
        data = browser.get_current_page().text
        result = json.loads(data)
        if result["success"]:
            embed = discord.Embed(title = result["name"],
                                  url = "https://pokemoncreed.net/search_pokemon.php?pokemon=" + result[
                                      "name"].replace(".","").replace(" ","%20") + "&trainer=&og=&ntrainer=&gender=&search=Search",
                                  color = result["color"])
            embed.set_thumbnail(url = 'https://pokemoncreed.net/sprites/' + result["name"].replace(".","").replace(" ","%20") + '.png')
            embed.set_footer(text = result["name"] + " | Requested by " + ctx.author.name,
                             icon_url = 'https://pokemoncreed.net/img/icon/' + result["name"].replace(".","").replace(" ","%20") + '.gif')
            embed.add_field(name = "**Rarity:**",
                            value = str(result["rarity"]["total"]) + " (" + str(result["rarity"]["male"]) + "M/" +
                                    str(result["rarity"]["female"]) + "F/" + str(result["rarity"]["ungendered"]) + "G)", inline = False)
            embed.add_field(name = "**Rate:**", value = result["rating"])
            await ctx.send(embed = embed)
        else:
            embed = discord.Embed(title = "Pokemon Not Found!",
                                  description = "Try searching for a different Pokemon...",
                                  color = discord.Color.dark_gold())
            await ctx.send(embed = embed)

    @commands.command(aliases = [])
    async def box(self, ctx, *, uname):
        """Displays colored pokemons of a Creed user."""
        url = 'https://pokemoncreed.net/ajax/box.php?user=' + uname
        browser = mechanicalsoup.StatefulBrowser()
        browser.open(url)
        data = browser.get_current_page().text
        result = json.loads(data)
        bm = BoxMenu(ctx, result)
        await bm.start(ctx)

    @commands.command(aliases = ['hd'], hidden = True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.has_any_role('Hitdown', 'hitdown')
    async def hitdown(self, ctx):
        """Displays time remaining for the next hitdown."""
        try:
            hdtime = await self.scrape_hd()
            msg = "`Next Hitdown in " + str(hdtime['h']) + "h : " + str(hdtime['m']) + "m : " + str(hdtime['s']) + "s.`"
            embed = discord.Embed(title = 'Hitdown',
                                  description = msg,
                                  color = discord.Color.teal())
            await ctx.send(embed = embed)
        except:
            embed = discord.Embed(title = 'Command Error',
                                  description = 'Some error occurred, Please try again later.',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)

    @commands.command(aliases = ['pkrate'])
    async def pokerate(self, ctx, *, pkmn):
        """Computes the total rate of given pokemon(s)."""
        browser = mechanicalsoup.StatefulBrowser()
        pkmn = pkmn.split(',')
        considered = []
        not_considered = []
        rates = []
        desc = f"{self.client.emotes.get('loading','')} Computing rates...\n(This might take some time!)"
        embed = discord.Embed(description = desc)
        embed.set_author(name = "TES Bot (Pokemon Rater)", icon_url = ctx.me.avatar_url)
        m = await ctx.send(embed = embed)
        for pk in pkmn:
            tmp = pk.split('*')
            pk = tmp[0].strip()
            try:
                c = int(tmp[1])
            except Exception as e:
                c = 1

            url = 'https://pokemoncreed.net/ajax/pokedex.php?pokemon=' + pk
            browser.open(url)
            data = browser.get_current_page().text
            result = json.loads(data)

            if result["success"]:
                pk = result["name"].strip()
                try:
                    rate = self.convertNumber(result["rating"])
                    considered.append(f"{pk} - ({result['rating']}) [x{c}]")
                    rates.append(rate * c)
                except Exception as e:
                    not_considered.append(pk)
            else:
                not_considered.append(pk)
        desc = "\n"
        if considered:
            desc += "\n".join(considered)
            desc += f"\n\n**Total Rating: {sum(rates):,}**\n"

        embed = discord.Embed(description = desc)

        if not_considered:
            embed.add_field(name = "Below pokemon(s) are not considered:", value = "\n".join(not_considered))
        embed.set_author(name = "TES Bot (Pokemon Rater)", icon_url = ctx.me.avatar_url)
        embed.set_footer(text = f'Requested by {ctx.author.name}', icon_url = ctx.author.avatar_url)
        await m.edit(embed = embed)

    # <# Pokemon Creed Error Handler - Start #>

    @hitdown.error
    @box.error
    @p.error
    @move.error
    @pokedex.error
    @pokerate.error
    @exp.error
    async def creed_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description = f'`Hi {ctx.author.name}, Please provide required arguments for {ctx.command.name} command!`',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(description = f'`Hi {ctx.author.name}, You are on cooldown. Please retry after {round(error.retry_after)}s.`',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(description = f'`You cannot use this command because: {str(error)}`',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(description = f'`Hi {ctx.author.name}, I do not have the following permissions: {error.missing_perms}`',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        else:
            embed = discord.Embed(description = f'Command Error: {str(error)}', color = discord.Color.red())
            await ctx.send(embed = embed)

    # <# Pokemon Creed Error Handler - End #>

def setup(client):
    client.add_cog(PokemonCreed(client))
