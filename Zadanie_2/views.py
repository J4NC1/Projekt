import psycopg2
import os
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser

# https://www.youtube.com/watch?v=rHux0gMZ3Eg&t=2038s&ab_channel=ProgrammingwithMosh
from django.http import JsonResponse
from psycopg2.extensions import JSON
from rest_framework.decorators import api_view

@api_view(['GET'])
def index(request):
    #https://www.youtube.com/watch?v=IolxqkL7cD8&ab_channel=CoreySchafer
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('AIS_LOG'),
        password=os.getenv('AIS_PASS'),
        host=os.getenv('HOST_Z2'),
        port=os.getenv('PORT_Z2')
    )


    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()

    cursor.execute("SELECT pg_database_size('dota2')/1024/1024 as dota2_db_size;")
    data = cursor.fetchone()
    return JsonResponse({'pgsql': {'version': version[0], 'dota2_db_size': data[0]}})

@api_view(['GET'])
def game_exp(request, i_player_id):
    conn2 = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('AIS_LOG'),
        password=os.getenv('AIS_PASS'),
        host=os.getenv('HOST_Z2'),
        port=os.getenv('PORT_Z2')
    )

    cursor2 = conn2.cursor()
    cursor2.execute("""select pl.id, COALESCE(pl.nick, 'unknown')as player_nick, hr.localized_name as hero_localized_name, ROUND((mch.duration::decimal)/60, 2) as match_duration_minutes, COALESCE(mpd.xp_hero,0) + COALESCE(mpd.xp_creep, 0) + COALESCE(mpd.xp_other, 0) + COALESCE(mpd.xp_roshan, 0) as experience_gained, mpd.level as level_gained, mpd.match_id,
case
    when mch.radiant_win = true and mpd.player_slot>= 0 and mpd.player_slot<=4 then true
    when mch.radiant_win = false and mpd.player_slot>=128 and mpd.player_slot<=132 then true
    else false
end as winner
from matches_players_details as mpd
join players as pl
    on mpd.player_id = pl.id
join matches as mch
    on mpd.match_id  = mch.id
join heroes as hr
    on mpd.hero_id = hr.id
    where pl.id = %s order by mch.id ASC""", [i_player_id])#moze byt aj %


    player_nick = cursor2.fetchall()
    pole = []


    for lines in player_nick:
        id = lines[0]
        pl_nick = lines[1]
        cas = float(lines[3])
        match = lines[6]
        schema ={
            "match_id": match,
            "hero_localized_name": lines[2],
            "match_duration_minutes": cas,
            "experiences_gained": lines[4],
            "level_gained": lines[5],
            "winner": lines[7]
        }
        pole.append(schema)



    return JsonResponse({"id":id, "player_nick":pl_nick,"matches":pole})


@api_view(['GET'])
def game_objectives(request, player_id):
    conn3 = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('AIS_LOG'),
        password=os.getenv('AIS_PASS'),
        host=os.getenv('HOST_Z2'),
        port=os.getenv('PORT_Z2')
    )

    cursor3 = conn3.cursor()
    cursor3.execute("""select pl.id as id, COALESCE(pl.nick, 'unknown')as player_nick, hr.localized_name as hero_localized_name,mpd.match_id,
(select distinct COALESCE(go.subtype, 'NO_ACTION')), coalesce(NULLIF(count(go.subtype),0),1)

from matches_players_details as mpd
full join game_objectives as go
    on mpd.id = go.match_player_detail_id_1
join matches as mch
    on mpd.match_id  = mch.id
join heroes as hr
    on mpd.hero_id = hr.id
join players as pl
    on mpd.player_id = pl.id
where pl.id = %s group by pl.id, mpd.match_id, hr.localized_name, go.subtype, go.match_player_detail_id_1, mpd.id
order by mpd.id ASC;""" % player_id)

    game_obj = cursor3.fetchall()
    array = []
    pole = []
    player_nick = ""
    poc = 0
    for line in game_obj:
        player_nick = line[1]
        array = []
        m_id = line[3]
        if poc == 0 or (poc != 0 and game_obj[poc - 1][3] != m_id):
            for line2 in game_obj:
                if line2[3] == m_id:
                    action = {
                        "hero_action": line2[4],
                        "count": line2[5],
                    }
                    array.append(action)
            match = {
                "match_id": line[3],
                "hero_localized_name": line[2],
                "actions": array,
            }
            pole.append(match)
        poc = poc +  1

    return JsonResponse({"id": player_id, "player_nick": player_nick, "matches": pole})





@api_view(['GET'])
def game_exp2(request, match_id):
    conn4 = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('AIS_LOG'),
        password=os.getenv('AIS_PASS'),
        host=os.getenv('HOST_Z2'),
        port=os.getenv('PORT_Z2')
    )

    cursor4 = conn4.cursor()
    cursor4.execute("""select * from(
select *, row_number() over(partition by hero_id) line_number from (
select distinct  matches.id as match_id, heroes.id as hero_id, heroes.localized_name, count(purchase_logs.item_id) as number_of_purchase, items.name as item_name,purchase_logs.item_id as item_id
from matches_players_details as mpd
join matches
on matches.id = mpd.match_id
join heroes
on heroes.id = mpd.hero_id
join purchase_logs
on mpd.id = purchase_logs.match_player_detail_id
join items
on items.id = purchase_logs.item_id
where mpd.match_id = %s and (matches.radiant_win = true and mpd.player_slot>= 0 and mpd.player_slot<=4 or matches.radiant_win = false and mpd.player_slot>=128 and mpd.player_slot<=132)
group by  heroes.localized_name,matches.id,heroes.id,mpd.player_slot,purchase_logs.item_id, items.name
order by heroes.id ASC,number_of_purchase DESC,item_name ASC) as res

group by  hero_id,match_id,item_id, item_name,res.localized_name, res.number_of_purchase
order by hero_id ASC,number_of_purchase DESC,item_name ASC) as res2

where line_number < 6
group by  hero_id,match_id,item_id, item_name,res2.localized_name, res2.number_of_purchase, res2.line_number
order by hero_id ASC,number_of_purchase DESC,item_name ASC;""", [match_id])
    data = cursor4.fetchall()
    heroes = []
    purchases = []
    check = 1
    for line in data:
        purchases_2 = {
            "id": line[2],
            "name": line[3],
            "count": line[4],
        }
        purchases.append(purchases_2)
        if check == 5:
            check = 0
            heroe_2 = {
                "id": line[0],
                "name": line[1],
                "top_purchases": purchases,
            }
            heroes.append(heroe_2)
            purchases = []
        check += 1
    return JsonResponse({"id": match_id, "heroes": heroes})
