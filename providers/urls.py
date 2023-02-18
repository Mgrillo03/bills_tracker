from . import views

from django.urls import path

app_name = 'providers'

urlpatterns = [
    #/provider/home/
    path('home/', views.index, name='index'),
    path('search/', views.search, name='search'),
    
    path('new/', views.new_provider, name='new_provider'),
    path('created/', views.new_provider_save, name='provider_created'),

    #/providers/id/detail
    path('<str:provider_id>/detail', views.provider_detail, name='provider_detail'),

    #provider/provider-id/update
    path('<str:provider_id>/update/', views.update_provider, name='update_provider'),
    #provider/provider-id/update
    path('<str:provider_id>/update-save/', views.update_provider_save, name='provider_updated'),

    #provider/provider-id/delete
    path('<str:provider_id>/delete/', views.delete_provider, name='delete_provider'),
    #provider/provider-id/delete
    path('<str:provider_id>/delete-success/', views.delete_provider_save, name='provider_deleted'),

]