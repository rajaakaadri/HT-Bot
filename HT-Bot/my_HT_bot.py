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
from PIL import Image
from urllib.request import urlopen

client = discord.Client()
discord_to_game_id = {'raja#1779': 'Canoedo',
    'Kupopo#2456': 'Canoedle',
    'Syn#3197': 'ArkMaxim',
} 
riot_key = riot_token

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    game_type = 'lol'
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('!lol'):
        lol_user = discord_to_game_id.get(str(message.author), None)
        if lol_user:
            u_name, u_level, user_match_info, game_mode = get_user_info(lol_user, game_type)
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
            bot_lol_msg.add_field(name='Last Game Result:', value=f'{match_res} ({game_mode})', inline=True)
            bot_lol_msg.add_field(name='Champion:', value=f'{champ_name}', inline=True)
            bot_lol_msg.add_field(name='KDA:', value=f'{kda}', inline=True)
            bot_lol_msg.add_field(name='Did you carry?', value='No.')
            bot_lol_msg.set_footer(text=f'K: {kill}/D: {death}/A: {assist}')
            await message.channel.send(embed=bot_lol_msg)
            # await message.channel.send(file=discord.File(data, 'icon.png'))
        else:
            await message.channel.send('User not found in mapping variable...')

    if message.content.startswith('!tft'):
        game_type = 'tft'
        tft_user = discord_to_game_id.get(str(message.author), None)
        if tft_user:
            u_name, u_level, user_match_info, game_mode = get_user_info(tft_user, game_type)
            match_res = user_match_info.get('placement', None)
            little_legend = user_match_info.get('companion', None)
            units_info_list = user_match_info.get('units', None)
            
            units_list = []
            img_base = None
            for x in units_info_list:
                tft_unit = x.get('character_id', None)
                tft_unit_tiers = x.get('tier', '')
                if tft_unit:
                    if tft_unit.lower() != 'tft7_trainerdragon':
                        champ_icon_url = f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/characters/{tft_unit.lower()}/hud/{tft_unit.lower()}_square.tft_set7.png'
                        tft_unit_name = tft_unit[tft_unit.index('_') + 1:]
                        units_list.append(tft_unit_name + ' - ' + str(tft_unit_tiers) + ' star')
                    else:
                        champ_icon_url = 'https://raw.communitydragon.org/latest/game/assets/characters/tft_itemunknown/skins/skin0/tft7_nomsy_square.tft_set7.png' #nomsy edge case for now
                        units_list.append('Nomsy')
                    print(champ_icon_url)
                    img = Image.open(requests.get(champ_icon_url, stream=True).raw)
                    if img_base:
                        print(img_base)
                        img_base = merge(img_base, img)
                    else:
                        img_base = img  
                        continue

            print(units_list)
            units_str = '\n'.join(units_list)
            if little_legend:
                print(little_legend)
            
            # work on companion image at some point
                # companion_info = 'tooltip_aoshin_base_elder_tier3.png'
                # icon_url = f'https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/assets/loadouts/companions/{companion_info}'

            bot_tft_msg = discord.Embed(title=f'{u_name} Lvl. {u_level}')
            bot_tft_msg.add_field(name='Last Game Result:', value=f'{match_res} ({game_mode.capitalize()})', inline=True)
            bot_tft_msg.add_field(name='Units:', value = units_str, inline=False)
            with io.BytesIO() as image_binary:
                img_base.save(image_binary, 'PNG')
                image_binary.seek(0)
                final_image =discord.File(fp=image_binary, filename='image.png')
                bot_tft_msg.set_image(url='attachment://image.png')
                await message.channel.send(embed=bot_tft_msg, file=final_image)
        else:
            await message.channel.send('User not found in mapping variable...')

    # if message.content.startswith('!val'):
    #     await message.channel.send('Last VALORANT Game.')

    # if message.content.startswith('!game'):
    #     await message.channel.send('The following games are available: League, TFT, Valorant.')

# Change this to a class of lol information
# Idea # 1: Pulling game data by discord-id/username
def get_user_info(username, game_type):
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
        user_match_info, game_mode = get_matches(user_puuid, game_type)
    else:
        print('Failed.')
        exit()
    return user_name, user_level, user_match_info, game_mode

def get_matches(puuid, game_type):
    if game_type == 'lol':
        recent_match = f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=1&api_key={riot_key}'
        r = requests.get(recent_match)
        if r.status_code != 200:
            print(f'Failed at recent match list {r.status_code}')
            exit()
        match_list = r.json()
        return get_lol_match_info(match_list[0], puuid)
    elif game_type == 'tft':
        recent_match = f'https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count=1&api_key={riot_key}'    
        r = requests.get(recent_match)
        if r.status_code != 200:
            print(f'Failed at recent match list {r.status_code}')
            exit()
        match_list = r.json()
        return get_tft_match_info(match_list[0], puuid)
    else:
        print('Failed in get_matches.')
        exit()


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

def get_tft_match_info(match_id, puuid):
    match_info = f'https://americas.api.riotgames.com/tft/match/v1/matches/{match_id}?api_key={riot_key}'
    r = requests.get(match_info)
    if r.status_code != 200:
        print(f'Failed at match information {r.status_code}')
        exit()
    match_info = r.json()
    game_mode = match_info['info']['tft_game_type']
    df_match_info = pd.DataFrame(match_info['info']['participants'])
    # df_match_info.to_csv('/Users/raja/Code/HT-Bot/Files/match_info.csv')
    user_match_info = df_match_info[(df_match_info['puuid'] == puuid)].to_dict('records')[0]
    # print(user_match_info)
    return user_match_info, game_mode

def merge(im_base, im_new):
    w = im_base.size[0] + im_new.size[0]
    h = max(im_base.size[1], im_new.size[1])
    im = Image.new("RGBA", (w, h))

    im.paste(im_base)
    im.paste(im_new, (im_base.size[0], 0))

    return im

client.run(bot_token)
