import discord
from discord import app_commands
from discord.ext import commands
from pydexcom import Dexcom
import requests
from datetime import datetime,timedelta
import os
from dotenv import load_dotenv, find_dotenv, dotenv_values

my_uuid = "61258482c6044e8fbf7640804ff786a3"
mcsr_endpoint = "https://api.mcsrranked.com/"
match_amount = 25

bloodsugar_levels = {
     "good_bs":{"upper":120, "lower":90, "msg":"within range"},
     "mid_bs": {"upper":160, "lower":70, "msg":"not good bloodsugar"},
     "bad_bs": {"upper":250, "lower":40, "msg":"bad blood sugar"}
}
        
special_values = {
     "HIGH": {"value":401,"msg":"current: QUITE LITERALLY SAYS \"HIGH\", VERY BAD. ABOVE 400. UNABLE TO BE DISPLAYED ON APP, IF NOT FIXED SOON THERE IS A NON ZERO CHANCE I GET HOSPITALIZED"},
     "LOW": {"value":39,"msg": "current: QUITE LITERALLY SAYS \"LOW\", VERY BAD. BELOW 40. UNABLE TO BE DISPLAYED ON APP, IF NOT FIXED SOON THERE IS A ZERO CHANCE I GET HOSPITALIZED"},
     }

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()
load_dotenv()
dex_email = os.getenv("DEXCOM_EMAIL")
dex_password = os.getenv("DEXCOM_PASSWORD")
discord_bot_secret = os.getenv("DISCORD_BOT_SECRET")

dexcom = Dexcom(username=dex_email, password=dex_password)

@bot.tree.command(name="texttest", description="say what you wanna say")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def texttest(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(f"{text}", ephemeral=False)


@bot.tree.command(name="bloodsugar", description="michael's current blood sugar")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def bloodsugar(interaction: discord.Interaction, hide: bool):
     try:
             if dexcom.get_current_glucose_reading() is not None:
               print(dexcom.get_current_glucose_reading())
               current = dexcom.get_current_glucose_reading().value
               previous = dexcom.get_glucose_readings(10, 2)[1]
               trend = dexcom.get_current_glucose_reading().trend_arrow
               bs_level = {}
               base_msg = f"current bloodsugar: {current}\ncurrent trend: {trend}\nprevious bs: {previous.value}"
               
               is_special = any(special.get("value") == current for special in special_values.values())
                    
     
               if not is_special:
                    for level in bloodsugar_levels:
                         if bloodsugar_levels[level]["upper"] <= current >= bloodsugar_levels[level]["lower"]:
                              bs_level = bloodsugar_levels[level]
                              print(bs_level)
                    await interaction.response.send_message(f"{base_msg}\n{bs_level["msg"]}", ephemeral=hide)
               else:
                    for special in special_values:
                         if current == special_values[special]["value"]:
                              bs_level = special_values[special]
                              await interaction.response.send_message(f"{base_msg}\n{bs_level["msg"]}", ephemeral=hide)
                              break
             else:
                 await interaction.response.send_message(f"sensor not detected", ephemeral=hide)
     except Exception as e:
                 print(e)
                 await interaction.response.send_message(f"something went wrong", ephemeral=True)
@bot.tree.command(name="bs", description="michael's current blood sugar")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def bs(interaction: discord.Interaction, hide: bool):
     try:
        if dexcom.get_current_glucose_reading() is not None:
          print(dexcom.get_current_glucose_reading())
          current = dexcom.get_current_glucose_reading().value
          previous = dexcom.get_glucose_readings(10, 2)[1]
          trend = dexcom.get_current_glucose_reading().trend_arrow
          bs_level = {}
          base_msg = f"current bloodsugar: {current}\ncurrent trend: {trend}\nprevious bs: {previous.value}"
          
          is_special = any(special.get("value") == current for special in special_values.values())
               

          if not is_special:
               for level in bloodsugar_levels:
                    if bloodsugar_levels[f"{level}"]["upper"] <= current >= bloodsugar_levels[f"{level}"]["lower"]:
                         bs_level = bloodsugar_levels[f"{level}"]
                         print(bs_level)
               await interaction.response.send_message(f"{base_msg}\n{bs_level["msg"]}", ephemeral=hide)
          else:
               for special in special_values:
                    if current == special_values[special]["value"]:
                         bs_level = special_values[special]
                         await interaction.response.send_message(f"{base_msg}\n{bs_level["msg"]}", ephemeral=hide)
                         break
        else:
            await interaction.response.send_message(f"sensor is either off or like broken sorry guppy", ephemeral=hide)
     except Exception as e:
            print(e)
            await interaction.response.send_message(f"something went wrong lol.", ephemeral=True)

@bot.tree.command(name="mcsr", description="minecraft speedrunning ranked stats for me today")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def mcsr(interaction: discord.Interaction):
     def getTodayMatchesData():
          recent_matches = requests.get(f"{mcsr_endpoint}users/{my_uuid}/matches/?count={match_amount}").json()["data"]
          todays_matches = []
          for i in range(match_amount):
               match_datetime = datetime.fromtimestamp(recent_matches[i]["date"]).date()
               todays_date = datetime.today().date()
               if match_datetime == todays_date:
                    todays_matches.append(recent_matches[i])
          return todays_matches
     try:
          mcsr_data = requests.get(f"{mcsr_endpoint}users/{my_uuid}").json()["data"]
          todays_matches = getTodayMatchesData()
          todays_stats = {"total": 0, "wins": 0, "losses": 0, "draws": 0,  "elo_change": 0}
          for match in todays_matches:
            match_result = match["result"]
            match_change = match["changes"]
            if len(match_change) != 0:
               if match_change[0]["uuid"] == my_uuid:
                    todays_stats["elo_change"] += match_change[0]["change"]
               else:
                    todays_stats["elo_change"] += match_change[1]["change"]

            if match_result["uuid"] == my_uuid:
                 todays_stats["wins"] += 1
            elif match_result["uuid"] == None:
                 todays_stats["draws"] += 1
            else:
                 todays_stats["losses"] += 1
          await interaction.response.send_message(f"Current ELO: {mcsr_data["eloRate"]}, 24H Change: {todays_stats["elo_change"]:+}\nToday's Stats: (win-draw-loss-total): {todays_stats["wins"]} - {todays_stats["draws"]} - {todays_stats["losses"]} - {len(todays_matches)}")
     except Exception as e:
       print(e)
       await interaction.response.send_message(f"something went wrong", ephemeral=True)

bot.run(token=discord_bot_secret)
