import discord
import sys
sys.path.append('/Users/raja/Code')
try:
    from my_token import bot_token, riot_token
except:
    print('Failed...')
import requests
import pandas as pd
import json
import openpyxl
import io 
import aiohttp

client = discord.Client()
discord_to_game_id = {'raja#1779': 'Canoedo',
    'Kupopo#2456': 'Canoedle'
} 
riot_key = riot_token

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('Hello Queen Cutie ;^)))!')

    if message.content.startswith('!lol'):
        lol_user = discord_to_game_id.get(str(message.author), None)
        if lol_user:
            u_name, u_level, user_match_info, game_mode = get_lol_info(lol_user)
            match_res = user_match_info.get('win', None)
            if match_res == True:
                match_res = 'Victory'
            elif match_res == False:
                match_res = 'Defeat'
            else:
                match_res = '???'
            kill = user_match_info.get('kills', None)
            death = user_match_info.get('deaths', None)
            assist = user_match_info.get('assists', None)
            if kill and death and assist:
                kda = round((kill + assist)/death, 2)
            else:
                kda = None
            champ_name = user_match_info.get('championName', None)
            champ_id = user_match_info.get('championId', None)
            icon_url = 'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/' + str(champ_id) + '.png'

            bot_lol_msg = discord.Embed(title=f'{u_name} Lvl. {u_level}')
            bot_lol_msg.set_thumbnail(url=icon_url)
            bot_lol_msg.add_field(name='Last Game Result:', value=f'{match_res} ({game_mode})', inline=False)
            bot_lol_msg.add_field(name='Champion:', value=f'{champ_name}', inline=True)
            bot_lol_msg.add_field(name='KDA:', value=f'{kda}', inline=True)
            bot_lol_msg.set_footer(text=f'K: {kill}/D: {death}/A: {assist}')
            await message.channel.send(embed=bot_lol_msg)
            # await message.channel.send(file=discord.File(data, 'icon.png'))
        else:
            await message.channel.send('User not found in mapping variable...')

    if message.content.startswith('!tft'):
        await message.channel.send('Last TFT Game.')

    if message.content.startswith('!val'):
        await message.channel.send('Last VALORANT Game.')

    if message.content.startswith('!game'):
        await message.channel.send('The following games are available: League, TFT, Valorant.')

# Change this to a class of lol information
# Idea # 1: Pulling game data by discord-id/username
def get_lol_info(username):
    user_info = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{username}?api_key={riot_key}'
    r = requests.get(user_info)
    if r.status_code != 200:
        print(f'Failed at user information: {r.status_code}')
        exit()
    user_dict = r.json()
    user_puuid = user_dict.get('puuid', None)
    user_name = user_dict.get('name', None)
    user_level = user_dict.get('summonerLevel', None)
    if user_puuid:
        print(user_puuid)
        user_match_info, game_mode = get_lol_matches(user_puuid)
    else:
        print('Failed.')
        exit()
    return user_name, user_level, user_match_info, game_mode

def get_lol_matches(puuid):
    recent_match = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=1&api_key={riot_key}'
    r = requests.get(recent_match)
    if r.status_code != 200:
        print(f'Failed at recent match list {r.status_code}')
        exit()
    match_list = r.json()
    return get_lol_match_info(match_list[0], puuid)

# def flatten_dict(nested_dict):
#     res = {}
#     if isinstance(nested_dict, dict):
#         for k in nested_dict:
#             flattened_dict = flatten_dict(nested_dict[k])
#             for key, val in flattened_dict.items():
#                 key = list(key)
#                 key.insert(0, k)
#                 res[tuple(key)] = val
#     else:
#         res[()] = nested_dict
#     return res

# def nested_dict_to_df(values_dict):
#     flat_dict = flatten_dict(values_dict)
#     df = pd.DataFrame.from_dict(flat_dict, orient="index")
#     df.index = pd.MultiIndex.from_tuples(df.index)
#     df = df.unstack(level=-1)
#     df.columns = df.columns.map("{0[1]}".format)
#     return df

def get_lol_match_info(match_id, puuid):
    match_info = f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={riot_key}'
    r = requests.get(match_info)
    if r.status_code != 200:
        print(f'Failed at match information {r.status_code}')
        exit()
    match_info = r.json()
    game_mode = match_info['info']['gameMode']
    df_match_info = pd.DataFrame(match_info['info']['participants'])
    # df_match_info.to_csv('/Users/raja/Code/HT-Bot/Files/match_info.csv')
    user_match_info = df_match_info[(df_match_info['puuid'] == puuid)].to_dict('records')[0]
    return user_match_info, game_mode

client.run(bot_token)
