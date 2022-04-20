from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name=''),
    path('players/<int:i_player_id>/game_exp/', views.game_exp, name=''),
    path('players/<int:player_id>/game_objectives/', views.game_objectives, name=''),
    path('matches/<int:match_id>/top_purchases/', views.game_exp2, name=''),

]