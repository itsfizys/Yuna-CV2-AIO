"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord 
import requests 
import aiohttp 
from datetime import datetime 
import random 
import os 
from discord .ext import commands 
from random import randint 
from utils .Tools import *
from core import Cog ,LightCore ,Context 
from utils .config import *
from pathlib import Path 
import json 
from PIL import Image ,ImageDraw ,ImageOps 
import io 
from discord import ui


def RandomColor ():
  randcolor =discord .Color (random .randint (0x000000 ,0xFFFFFF ))
  return randcolor 

RAPIDAPI_HOST ="truth-dare.p.rapidapi.com"
RAPIDAPI_KEY ="1cd7c71534msh2544b357ec07ad8p18fa0bjsn1358eef1f8e9"

class Fun (commands .Cog ):

  def __init__ (self ,bot ):
    self .bot =bot 
    self .giphy_token ='y3KcqQTdiS0RYcpNJrWn8hFGglKqX4is'
    self .google_api_key ='AIzaSyA022fwm_TOQcYTg1N_ohqqIj_RUFUM9BY'
    self .search_engine_id ='2166875ec165a6c21'


  async def download_avatar (self ,url ):
      async with aiohttp .ClientSession ()as session :
          async with session .get (url )as resp :
              if resp .status !=200 :
                  return None 
              data =await resp .read ()
              return Image .open (io .BytesIO (data )).convert ("RGBA")

  def circle_avatar (self ,avatar ):
      mask =Image .new ("L",avatar .size ,0 )
      draw =ImageDraw .Draw (mask )
      draw .ellipse ((0 ,0 )+avatar .size ,fill =255 )
      avatar =ImageOps .fit (avatar ,mask .size ,centering =(0.5 ,0.5 ))
      avatar .putalpha (mask )
      return avatar 

  async def add_role (self ,*,role :int ,member :discord .Member ):
    if member .guild .me .guild_permissions .manage_roles :
      role =discord .Object (id =int (role ))
      await member .add_roles (role ,reason =f"{NAME} | Role Added ")

  async def remove_role (self ,*,role :int ,member :discord .Member ):
    if member .guild .me .guild_permissions .manage_roles :
      role =discord .Object (id =int (role ))
      await member .remove_roles (role ,reason =f"{NAME} | Role Removed")


  async def fetch_data (self ,endpoint ):
        async with aiohttp .ClientSession ()as session :
            headers ={
            "X-RapidAPI-Host":RAPIDAPI_HOST ,
            "X-RapidAPI-Key":RAPIDAPI_KEY 
            }
            async with session .get (f"https://{RAPIDAPI_HOST}{endpoint}",headers =headers )as response :
                if response .status ==200 :
                    return await response .json ()
                else :
                    return None 


  async def fetch_image (self ,ctx ,endpoint ):
    async with aiohttp .ClientSession ()as session :
        async with session .get (f"https://nekos.life/api/v2/img/{endpoint}")as response :
            if response .status ==200 :
                data =await response .json ()
                return data ["url"]
            else :
                pass 




  async def fetch_action_image (self ,action ):
        url =f"https://api.waifu.pics/sfw/{action}"
        try :
            response =requests .get (url )
            response .raise_for_status ()
            return response .json ().get ('url')
        except requests .exceptions .RequestException :
            return None 

  @commands .command ()
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def compliment (self ,ctx ,user :discord .User =None ):
      if user is None:
          user = ctx.author
      
      compliment_types = [
          "personality", "appearance", "skills", "vibes", "energy", "spirit"
      ]
      
      compliments = {
          "personality": [
              "has the kindest heart", "is absolutely hilarious", "brings joy wherever they go",
              "is incredibly thoughtful", "has the most infectious laugh", "is genuinely amazing",
              "lights up every room", "is wonderfully unique", "has such a caring soul",
              "is incredibly inspiring", "has the best sense of humor", "is absolutely delightful"
          ],
          "appearance": [
              "looks absolutely stunning today", "has the most beautiful smile", "is radiating confidence",
              "looks like they're glowing", "has amazing style", "looks fantastic as always",
              "has the most expressive eyes", "looks absolutely radiant", "has such great energy",
              "looks like they could be a model", "has the best hair", "looks absolutely gorgeous"
          ],
          "skills": [
              "is incredibly talented", "has amazing skills", "is really good at everything they do",
              "is so creative and artistic", "has such great ideas", "is incredibly smart",
              "is really good at making people laugh", "has amazing problem-solving skills",
              "is so good at bringing people together", "has incredible leadership qualities",
              "is amazingly skilled", "has such great instincts"
          ],
          "vibes": [
              "has the best vibes", "gives off such positive energy", "has main character energy",
              "has such calming presence", "radiates good vibes only", "has that special sparkle",
              "brings such good energy", "has the most positive aura", "gives off boss energy",
              "has such peaceful vibes", "radiates pure sunshine", "has that magnetic personality"
          ],
          "energy": [
              "has such amazing energy", "is full of life and passion", "brings such enthusiasm",
              "has boundless positive energy", "is incredibly energetic in the best way",
              "has such vibrant energy", "brings electric energy to everything", "is so full of life",
              "has the most contagious energy", "radiates such powerful energy", "is pure energy and light",
              "has such dynamic energy"
          ],
          "spirit": [
              "has an unbreakable spirit", "is so resilient and strong", "has such a beautiful soul",
              "has the most amazing spirit", "is incredibly brave", "has such inner strength",
              "has the most adventurous spirit", "is so determined and focused", "has a warrior spirit",
              "has such a free spirit", "is incredibly wise", "has the most generous spirit"
          ]
      }
      
      compliment_type = random.choice(compliment_types)
      compliment = random.choice(compliments[compliment_type])
      
      emojis = ["✨", "🌟", "💫", "🌈", "💖", "🔥", "⭐", "🎉", "💯", "🌸"]
      emoji = random.choice(emojis)
      
      view = ui.LayoutView()
      container = ui.Container(accent_color=None)
      container.add_item(ui.TextDisplay(f"# {emoji} Compliment Generator"))
      container.add_item(ui.Separator())
      container.add_item(ui.TextDisplay(f"**{user.display_name}** {compliment}! {emoji}"))
      container.add_item(ui.Separator())
      container.add_item(ui.TextDisplay(f"**Category:** {compliment_type.title()} Appreciation"))
      container.add_item(ui.TextDisplay("*You're absolutely amazing and don't let anyone tell you otherwise!* 💝"))
      container.add_item(ui.Separator())
      container.add_item(ui.TextDisplay(f'Spread by [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})'))
      view.add_item(container)
      
      await ctx.reply(view=view)


  @commands .command (name ="image",help ="Search for an image and display a random one.",aliases =["img"],with_app_command =True )
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def image (self ,ctx ,*,search_query :str ):
        if not ctx .channel .is_nsfw ():
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("❌ This command can only be used in NSFW (age-restricted) channels."))
            view.add_item(container)
            await ctx.reply(view=view, ephemeral=True)
            return 
            
        async with aiohttp .ClientSession ()as session :
            async with session .get (f"https://www.googleapis.com/customsearch/v1?key={self.google_api_key}&cx={self.search_engine_id}&q={search_query}&searchType=image")as response :
                data =await response .json ()
                if "items"in data :
                    view = ui.LayoutView()
                    container = ui.Container(accent_color=None)
                    container.add_item(ui.TextDisplay(f"🖼️ Random Image for '{search_query}'"))
                    gallery = ui.MediaGallery()
                    gallery.add_item(media=random.choice(data["items"])["link"])
                    container.add_item(gallery)
                    view.add_item(container)
                    await ctx.reply(view=view)
                else :
                    view = ui.LayoutView()
                    container = ui.Container(accent_color=None)
                    container.add_item(ui.TextDisplay("❌ No images found for that search query."))
                    view.add_item(container)
                    await ctx.reply(view=view)




  @commands .command (name ="howgay",
  aliases =['gay'],
  help ="check someone gay percentage",
  usage ="Howgay <person>")
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def howgay (self ,ctx ,*,person ):
    responses =random .randrange (1 ,150 )
    view = ui.LayoutView()
    container = ui.Container(accent_color=None)
    container.add_item(ui.TextDisplay("# About your gayness"))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f'**{person} is {responses}% Gay** 🏳️‍🌈'))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f'How gay are you? - [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})'))
    view.add_item(container)
    await ctx.reply(view=view)


  @commands .command (name ="lesbian",
  aliases =['lesbo'],
  help ="check someone lesbian percentage",
  usage ="lesbian <person>")
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def lesbian (self ,ctx ,*,person ):
    responses =random .randrange (1 ,150 )
    view = ui.LayoutView()
    container = ui.Container(accent_color=None)
    container.add_item(ui.TextDisplay("# Lesbian Meter"))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f'**{person} is {responses}% Lesbian** 🏳️‍🌈'))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f'How lesbian are you? - [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})'))
    view.add_item(container)
    await ctx.reply(view=view)

  @commands .command (name ="horny",
  aliases =['horniness'],
  help ="check someone horniness percentage",
  usage ="Horny <person>")
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def horny (self ,ctx ,*,person ):
    responses =random .randrange (1 ,150 )
    view = ui.LayoutView()
    container = ui.Container(accent_color=None)
    container.add_item(ui.TextDisplay("# About your horniness"))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f'**{person} is {responses}% Horny** 😳'))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f'How horny are you? - [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})'))
    view.add_item(container)
    await ctx.reply(view=view)

  @commands .command (name ="cute",
  aliases =['cuteness'],
  help ="check someone cuteness percentage",
  usage ="Cute <person>")
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def cute (self ,ctx ,*,person ):
    responses =random .randrange (1 ,150 )
    view = ui.LayoutView()
    container = ui.Container(accent_color=None)
    container.add_item(ui.TextDisplay("# About your cuteness"))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f'**{person} is {responses}% Cute** 🥰'))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f'How cute are you? - [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})'))
    view.add_item(container)
    await ctx.reply(view=view)

  @commands .command (name ="intelligence",
  aliases =['iq'],
  help ="check someone intelligence percentage",
  usage ="Intelligence <person>")
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def intelligence (self ,ctx ,*,person ):
    responses =random .randrange (1 ,150 )
    view = ui.LayoutView()
    container = ui.Container(accent_color=None)
    container.add_item(ui.TextDisplay("# About your intelligence"))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f'**{person} has an IQ of {responses}%** 🧠'))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f'How intelligent are you? - [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})'))
    view.add_item(container)
    await ctx.reply(view=view)

  @commands .command (name ="gif",help ="Search for a gif and display a random one.",with_app_command =True )
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,5 ,commands .BucketType .user )
  async def gif (self ,ctx ,*,search_query :str ):
      async with aiohttp .ClientSession ()as session :
          async with session .get (f"https://api.giphy.com/v1/gifs/search?api_key={self.giphy_token}&q={search_query}&limit=10")as response :
              data =await response .json ()
              if "data"in data :
                  view = ui.LayoutView()
                  container = ui.Container(accent_color=None)
                  container.add_item(ui.TextDisplay(f"🎬 Random GIF for '{search_query}'"))
                  gallery = ui.MediaGallery()
                  gallery.add_item(media=random.choice(data["data"])["images"]["original"]["url"])
                  container.add_item(gallery)
                  view.add_item(container)
                  await ctx.reply(view=view)
              else :
                  view = ui.LayoutView()
                  container = ui.Container(accent_color=None)
                  container.add_item(ui.TextDisplay("❌ No GIFs found for that search query."))
                  view.add_item(container)
                  await ctx.reply(view=view)




  @commands .command (name ="iplookup",
  aliases =['ip'],
  help ="Get accurate IP info",
  usage ="iplookup [ip]")
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def iplookup (self ,ctx ,*,ip ):
    async with aiohttp .ClientSession ()as session :
      try :
        async with session .get (f"http://ip-api.com/json/{ip}")as response :
          data =await response .json ()

          if data ['status']=='fail':
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("❌ Failed to retrieve data. Please check the IP address and try again."))
            view.add_item(container)
            await ctx.reply(view=view)
            return 


          query =data .get ('query','N/A')
          continent =data .get ('continent','N/A')
          continent_code =data .get ('continentCode','N/A')
          country =data .get ('country','N/A')
          country_code =data .get ('countryCode','N/A')
          region_name =data .get ('regionName','N/A')
          region =data .get ('region','N/A')
          city =data .get ('city','N/A')
          district =data .get ('district','N/A')
          zip_code =data .get ('zip','N/A')
          latitude =data .get ('lat','N/A')
          longitude =data .get ('lon','N/A')
          timezone =data .get ('timezone','N/A')
          offset =data .get ('offset','N/A')
          isp =data .get ('isp','N/A')
          organization =data .get ('org','N/A')
          asn =data .get ('as','N/A')
          asname =data .get ('asname','N/A')
          mobile =data .get ('mobile','N/A')
          proxy =data .get ('proxy','N/A')
          hosting =data .get ('hosting','N/A')

          view = ui.LayoutView()
          container = ui.Container(accent_color=None)
          container.add_item(ui.TextDisplay(f"# IP: {query}"))
          container.add_item(ui.Separator())
          container.add_item(ui.TextDisplay(
          f"🌏 **Location Info:**\n"
          f"IP: **{query}**\n"
          f"Continent: {continent} ({continent_code})\n"
          f"Country: {country} ({country_code})\n"
          f"Region: **{region_name}** ({region})\n"
          f"City: {city}\n"
          f"District: {district}\n"
          f"Zip: {zip_code}\n"
          f"Latitude: {latitude}\n"
          f"Longitude: {longitude}\n"
          f"Lat/Long: {latitude}, {longitude}"
          ))
          container.add_item(ui.Separator())
          container.add_item(ui.TextDisplay(
          f"📡 **Timezone Info:**\n"
          f"Timezone: {timezone}\n"
          f"Offset: {offset}"
          ))
          container.add_item(ui.Separator())
          container.add_item(ui.TextDisplay(
          f"🛜 **Network Info:**\n"
          f"ISP: **{isp}**\n"
          f"Organization: {organization}\n"
          f"AS: **{asn}**\n"
          f"AS Name: **{asname}**"
          ))
          container.add_item(ui.Separator())
          container.add_item(ui.TextDisplay(
          f"⚠️ **Miscellaneous Info:**\n"
          f"Mobile: {mobile}\n"
          f"Proxy: {proxy}\n"
          f"Hosting: {hosting}"
          ))
          container.add_item(ui.Separator())
          container.add_item(ui.TextDisplay(f'Made by LightCore Development - [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})'))
          view.add_item(container)
          await ctx.reply(view=view)

      except Exception as e :
        pass 



  @commands .command ()
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def weather (self ,ctx ,*,city :str ):
      api_key ="b81e2218c328686836ab6d9d31ce97d0"
      base_url ="http://api.openweathermap.org/data/2.5/weather?"
      city_name =city 
      complete_url =f"{base_url}q={city_name}&APPID={api_key}"

      async with aiohttp .ClientSession ()as session :
          async with session .get (complete_url )as response :
              data =await response .json ()
              if data ["cod"]!="404":
                  main =data ['main']
                  temperature =main ['temp']
                  temp_celsius =temperature -273.15 
                  humidity =main ['humidity']
                  pressure =main ['pressure']
                  report =data ['weather']
                  weather_desc =report [0 ]['description']

                  view = ui.LayoutView()
                  container = ui.Container(accent_color=None)
                  container.add_item(ui.TextDisplay(f"# ☁️ Weather in {city_name}"))
                  container.add_item(ui.Separator())
                  container.add_item(ui.TextDisplay(f"**Description:** {weather_desc.capitalize()}"))
                  container.add_item(ui.TextDisplay(f"**Temperature (Celsius):** {temp_celsius:.2f} °C"))
                  container.add_item(ui.TextDisplay(f"**Humidity:** {humidity}%"))
                  container.add_item(ui.TextDisplay(f"**Pressure:** {pressure} hPa"))
                  container.add_item(ui.Separator())
                  container.add_item(ui.TextDisplay(f'Requested By [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})'))
                  view.add_item(container)
                  await ctx.reply(view=view)
              else :
                  view = ui.LayoutView()
                  container = ui.Container(accent_color=None)
                  container.add_item(ui.TextDisplay("❌ City not found. Please enter a valid city name."))
                  view.add_item(container)
                  await ctx.reply(view=view)

  @commands .command (name ="fakeban",aliases =['fban'],usage ="fakeban <member>")
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def fake_ban (self ,ctx ,user :discord .Member ):
    view = ui.LayoutView()
    container = ui.Container(accent_color=None)
    container.add_item(ui.TextDisplay("# Successfully Banned!"))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f"✅ [{user.display_name}](https://discord.com/users/{user.id}) has been successfully banned"))
    container.add_item(ui.Separator())
    container.add_item(ui.TextDisplay(f'Banned By [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})'))
    view.add_item(container)
    await ctx.reply(view=view)

  @commands .command (name ="spank")
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def spank (self ,ctx ,user :discord .Member =None ):
      if not ctx .channel .is_nsfw ():
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("❌ This command can only be used in NSFW (age-restricted) channels."))
            view.add_item(container)
            await ctx.reply(view=view)
            return 
      if user is None :
          user =ctx .author 
          description =f"[{ctx.author.display_name}](https://discord.com/users/{ctx.author.id}) spanked themselves 😵‍💫"
      else :
          description =f"[{ctx.author.display_name}](https://discord.com/users/{ctx.author.id}) spanked [{user.display_name}](https://discord.com/users/{user.id}) 😹"

      image_url =await self .fetch_image (ctx ,"spank")
      if image_url :
          view = ui.LayoutView()
          container = ui.Container(accent_color=None)
          container.add_item(ui.TextDisplay(description))
          gallery = ui.MediaGallery()
          gallery.add_item(media=image_url)
          container.add_item(gallery)
          view.add_item(container)
          await ctx.reply(view=view)

  @commands .command (name ="kill")
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def kill (self ,ctx ,user :discord .Member =None ):
      if user is None :
          view = ui.LayoutView()
          container = ui.Container(accent_color=None)
          container.add_item(ui.TextDisplay(f"[{ctx.author.display_name}](https://discord.com/users/{ctx.author.id}), you can't kill the air! Find someone to kill."))
          view.add_item(container)
          await ctx.reply(view=view)
          return 

      description =f"[{ctx.author.display_name}](https://discord.com/users/{ctx.author.id}) kills [{user.display_name}](https://discord.com/users/{user.id}) ☠️"
      image_url =await self .fetch_action_image ("kill")
      if image_url :
          view = ui.LayoutView()
          container = ui.Container(accent_color=None)
          container.add_item(ui.TextDisplay(description))
          gallery = ui.MediaGallery()
          gallery.add_item(media=image_url)
          container.add_item(gallery)
          view.add_item(container)
          await ctx.reply(view=view)



  @commands .command (name ="8ball",aliases =["8b"])
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  async def eight_ball (self ,ctx ,*,question :str =None ):
      if question is None :
          view = ui.LayoutView()
          container = ui.Container(accent_color=None)
          container.add_item(ui.TextDisplay("❌ You need to ask a question!"))
          view.add_item(container)
          await ctx.reply(view=view)
          return 

      responses = [
          "It is certain", "It is decidedly so", "Without a doubt", "Yes definitely",
          "You may rely on it", "As I see it, yes", "Most likely", "Outlook good",
          "Yes", "Signs point to yes", "Reply hazy, try again", "Ask again later",
          "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
          "Don't count on it", "My reply is no", "My sources say no",
          "Outlook not so good", "Very doubtful"
      ]
      
      response = random.choice(responses)
      view = ui.LayoutView()
      container = ui.Container(accent_color=None)
      container.add_item(ui.TextDisplay("# 🎱 Magic 8-Ball"))
      container.add_item(ui.Separator())
      container.add_item(ui.TextDisplay(f"**Question:** {question}"))
      container.add_item(ui.TextDisplay(f"**Answer:** {response}"))
      container.add_item(ui.Separator())
      container.add_item(ui.TextDisplay(f'Asked by [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})'))
      view.add_item(container)
      await ctx.reply(view=view)



  @commands .command (name ="truth",aliases =["t"])
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  @commands .max_concurrency (5 ,per =commands .BucketType .default ,wait =False )
  async def truth (self ,ctx ):
      async with aiohttp .ClientSession ()as session :
          async with session .get ("https://api.truthordarebot.xyz/api/truth")as response :
              if response .status ==200 :
                  data =await response .json ()
                  question =data .get ("question")
                  if question :
                      view = ui.LayoutView()
                      container = ui.Container(accent_color=None)
                      container.add_item(ui.TextDisplay("# TRUTH"))
                      container.add_item(ui.Separator())
                      container.add_item(ui.TextDisplay(f"{question}"))
                      view.add_item(container)
                      await ctx.reply(view=view)
                  else :
                      view = ui.LayoutView()
                      container = ui.Container(accent_color=None)
                      container.add_item(ui.TextDisplay("❌ Couldn't retrieve a truth question. Please try again."))
                      view.add_item(container)
                      await ctx.reply(view=view)
              else :
                  pass 

  @commands .command (name ="dare",aliases =["d"])
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,3 ,commands .BucketType .user )
  @commands .max_concurrency (5 ,per =commands .BucketType .default ,wait =False )
  async def dare (self ,ctx ):
      async with aiohttp .ClientSession ()as session :
          async with session .get ("https://api.truthordarebot.xyz/api/dare")as response :
              if response .status ==200 :
                  data =await response .json ()
                  question =data .get ("question")
                  if question :
                      view = ui.LayoutView()
                      container = ui.Container(accent_color=None)
                      container.add_item(ui.TextDisplay("# DARE"))
                      container.add_item(ui.Separator())
                      container.add_item(ui.TextDisplay(f"{question}"))
                      view.add_item(container)
                      await ctx.reply(view=view)
                  else :
                      view = ui.LayoutView()
                      container = ui.Container(accent_color=None)
                      container.add_item(ui.TextDisplay("❌ Couldn't retrieve a dare question. Please try again."))
                      view.add_item(container)
                      await ctx.reply(view=view)
              else :
                  pass 




  @commands .command (name ="translate",aliases =["tl"])
  @blacklist_check ()
  @ignore_check ()
  @commands .cooldown (1 ,5 ,commands .BucketType .user )
  async def translate_command (self ,ctx ,*,message =None ):
    """AI-powered translation command"""


    target_language ="English"
    text_to_translate =None 

    if message is None :

      if ctx .message .reference :
        try :
          replied_msg =await ctx .fetch_message (ctx .message .reference .message_id )
          if replied_msg and replied_msg .content :
            text_to_translate =replied_msg .content 
          else :
            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("❌ No content found in the replied message."))
            view.add_item(container)
            await ctx.reply(view=view)
            return 
        except :
          view = ui.LayoutView()
          container = ui.Container(accent_color=None)
          container.add_item(ui.TextDisplay("❌ Could not fetch the replied message."))
          view.add_item(container)
          await ctx.reply(view=view)
          return 
      else :
        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        container.add_item(ui.TextDisplay("❌ Please provide text to translate or reply to a message."))
        view.add_item(container)
        await ctx.reply(view=view)
        return 
    else :

      message_lower =message .lower ()


      language_patterns ={
      'hindi':['hindi','hi'],
      'spanish':['spanish','es','español'],
      'french':['french','fr','français'],
      'german':['german','de','deutsch'],
      'italian':['italian','it'],
      'portuguese':['portuguese','pt'],
      'russian':['russian','ru'],
      'japanese':['japanese','jp'],
      'chinese':['chinese','cn','mandarin'],
      'korean':['korean','ko'],
      'arabic':['arabic','ar'],
      'dutch':['dutch','nl'],
      'polish':['polish','pl'],
      'turkish':['turkish','tr'],
      'swedish':['swedish','sv'],
      'norwegian':['norwegian','no'],
      'danish':['danish','da'],
      'finnish':['finnish','fi'],
      'greek':['greek','el'],
      'hebrew':['hebrew','he'],
      'thai':['thai','th'],
      'vietnamese':['vietnamese','vi']
      }


      detected_language =None 
      for lang ,patterns in language_patterns .items ():
        for pattern in patterns :
          if f"to {pattern}"in message_lower or f"into {pattern}"in message_lower :
            detected_language =lang 
            target_language =lang .capitalize ()


            if ctx .message .reference :
              try :
                replied_msg =await ctx .fetch_message (ctx .message .reference .message_id )
                if replied_msg and replied_msg .content :
                  text_to_translate =replied_msg .content 
                else :
                  view = ui.LayoutView()
                  container = ui.Container(accent_color=None)
                  container.add_item(ui.TextDisplay("❌ No content found in the replied message."))
                  view.add_item(container)
                  await ctx.reply(view=view)
                  return 
              except :
                view = ui.LayoutView()
                container = ui.Container(accent_color=None)
                container.add_item(ui.TextDisplay("❌ Could not fetch the replied message."))
                view.add_item(container)
                await ctx.reply(view=view)
                return 
            else :

              text_to_translate =message .replace (f"to {pattern}","").replace (f"into {pattern}","").replace (f"to {pattern.capitalize()}","").replace (f"into {pattern.capitalize()}","").strip ()
            break 
        if detected_language :
          break 


      if not detected_language :
        text_to_translate =message 

    if not text_to_translate or not text_to_translate .strip ():
      view = ui.LayoutView()
      container = ui.Container(accent_color=None)
      container.add_item(ui.TextDisplay("❌ No text provided for translation."))
      view.add_item(container)
      await ctx.reply(view=view)
      return 

    processing_view = ui.LayoutView()
    processing_container = ui.Container(accent_color=None)
    processing_container.add_item(ui.TextDisplay("🔄 Translating..."))
    processing_view.add_item(processing_container)
    processing_message = await ctx.reply(view=processing_view)

    try :

      prompt =f"Translate the following text to {target_language}. Only provide the translation without any explanations or additional text:\n\n{text_to_translate}"


      import aiohttp 
      groq_api_key =os .getenv ("GROQ_API_KEY")

      if not groq_api_key :
        await processing_message .delete ()
        view = ui.LayoutView()
        container = ui.Container(accent_color=None)
        container.add_item(ui.TextDisplay("❌ Translation service is not configured."))
        view.add_item(container)
        await ctx.reply(view=view)
        return 

      url ="https://api.groq.com/openai/v1/chat/completions"
      headers ={
      "Authorization":f"Bearer {groq_api_key}",
      "Content-Type":"application/json"
      }

      data ={
      "model":"llama-3.3-70b-versatile",
      "messages":[{"role":"user","content":prompt }],
      "temperature":0.3 
      }

      async with aiohttp .ClientSession ()as session :
        async with session .post (url ,headers =headers ,json =data )as response :
          if response .status ==200 :
            json_response =await response .json ()
            translation =json_response ['choices'][0 ]['message']['content'].strip ()

            view = ui.LayoutView()
            container = ui.Container(accent_color=None)
            container.add_item(ui.TextDisplay("# AI Translation"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(f"**📝 Original Text**\n{text_to_translate[:1024] + ('...' if len(text_to_translate) > 1024 else '')}"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(f"**🌐 Translated to {target_language}**\n{translation[:1024] + ('...' if len(translation) > 1024 else '')}"))
            container.add_item(ui.Separator())
            container.add_item(ui.TextDisplay(f'Powered by LightCore Development • Requested by [{ctx.author.display_name}](https://discord.com/users/{ctx.author.id})'))
            view.add_item(container)

            await ctx.reply(view=view)
            await processing_message.delete()
          else :
            error_message =await response .text ()
            await processing_message .delete ()
            pass 

    except Exception as e :
      await processing_message .delete ()
      pass 


"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
