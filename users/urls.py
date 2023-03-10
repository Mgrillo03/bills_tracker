from . import views

from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    #users/
    path('', views.index, name='index'),

    #users/singup/
    path('singup/', views.singup, name='singup'),
    #users/singup/next/
    path('singup/next/', views.singup_next, name='singup_next'),

    #users/login/
    path('login/', views.auth_login, name='mylogin'),
    #users/login/next
    path('login/next/', views.auth_login_next, name='login_next'),


    #users/detail/
    path('<str:user_id>/detail/', views.user_detail, name='user_detail'),
    #users/user_id/updeate
    path('<str:user_id>/update/', views.update_user, name='update_user'),
    #users/user_id/success
    path('<str:user_id>/update-saved/', views.update_user_save, name='update_user_save'),

    #users/logout
    path('logout/', views.auth_logout, name='logout'),

    #users/reset-password/
    path('<str:user_id>/reset-password/', views.auth_reset_password, name='reset_password'),
    #users/reset-password/success
    path('<str:user_id>/new-password/success/', views.auth_save_new_password, name='save_new_password'),

    #users/delete-user/
    path('<str:user_id>/delete-user/', views.delete_user, name='delete_user'),
    #users/delete-user/
    path('<str:user_id>/user-deleted/', views.delete_user_save, name='user_deleted'),
    
]