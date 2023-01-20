from . import views

from django.urls import path

app_name = 'payments'

urlpatterns = [
    #/payments/home/
    path('', views.index, name='index'),
    
    #path('new/', views.new_payments, name='new_payments'),
    #path('new/calc', views.new_payments_calc, name='new_payments_calc'),
    #path('created/', views.new_payments_save, name='payments_created'),

    ## #/paymentss/id/detail
    #path('<str:payments_id>/detail', views.payments_detail, name='payments_detail'),

    ## #payments/payments-id/update
    #path('<str:payments_id>/update/', views.update_payments, name='update_payments'),
    ## #payments/payments-id/update-calc/
    #path('<str:payments_id>/update-calc/', views.update_payments_calc, name='update_payments_calc'),
    ## payments/payments-id/update-save/
    #path('<str:payments_id>/update-save/', views.update_payments_save, name='update_payments_save'),

    ## #payments/payments-id/delete
    #path('<str:payments_id>/delete/', views.delete_payments, name='delete_payments'),
    ## #payments/payments-id/delete
    #path('<str:payments_id>/delete-success/', views.delete_payments_save, name='payments_deleted'),

]