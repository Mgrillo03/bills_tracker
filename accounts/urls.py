from . import views

from django.urls import path

app_name = 'accounts'

urlpatterns = [
    #/account/home/
    path('home/', views.index, name='index'),
    path('search/', views.search, name='search'),
    
    path('new/', views.new_account, name='new_account'),
    path('created/', views.new_account_save, name='account_created'),

    #/accounts/id/detail
    path('<str:account_id>/detail', views.account_detail, name='account_detail'),
    #/accounts/id/detail-search
    path('<str:account_id>/detail-search', views.detail_search, name='detail_search'),

    #account/account-id/update
    path('<str:account_id>/update/', views.update_account, name='update_account'),
    #account/account-id/update
    path('<str:account_id>/update-save/', views.update_account_save, name='account_updated'),

    #account/account-id/delete
    path('<str:account_id>/delete/', views.delete_account, name='delete_account'),
    #account/account-id/delete
    path('<str:account_id>/delete-success/', views.delete_account_save, name='account_deleted'),

]