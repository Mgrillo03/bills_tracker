from . import views

from django.urls import path

app_name = 'bills'

urlpatterns = [
    #/bill/home/
    path('', views.index, name='index'),
    
    path('new/', views.new_bill, name='new_bill'),
    path('new/show-p/',views.new_bill_show_provider, name='new_bill_show_provider'),
    path('new/calc/', views.new_bill_calc, name='new_bill_calc'),
    path('created/', views.new_bill_save, name='bill_created'),

    # #/bills/id/detail
    path('<str:bill_id>/detail', views.bill_detail, name='bill_detail'),

    # #bill/bill-id/update
    path('<str:bill_id>/update/', views.update_bill, name='update_bill'),
    # #bill/bill-id/update-calc/
    path('<str:bill_id>/update-calc/', views.update_bill_calc, name='update_bill_calc'),
    # bill/bill-id/update-save/
    path('<str:bill_id>/update-save/', views.update_bill_save, name='update_bill_save'),

    # #bill/bill-id/delete
    path('<str:bill_id>/delete/', views.delete_bill, name='delete_bill'),
    # #bill/bill-id/delete
    path('<str:bill_id>/delete-success/', views.delete_bill_save, name='bill_deleted'),

]