import psycopg2
import os
from django.shortcuts import render

# https://www.youtube.com/watch?v=rHux0gMZ3Eg&t=2038s&ab_channel=ProgrammingwithMosh
from django.http import JsonResponse
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
