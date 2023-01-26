from . import views

from django.urls import path

app_name = 'payments'

urlpatterns = [
    #/payment/home/
    path('', views.index, name='index'),
    
    #payment/new/
    path('new/', views.new_payment, name='new_payment'),
    #payment/created/
    path('created/', views.new_payment_save, name='new_payment_save'),

    ## #/payments/id/detail
    path('<str:payment_id>/detail', views.payment_detail, name='payment_detail'),

    ## #payment/payment-id/update
    path('<str:payment_id>/update/', views.update_payment, name='update_payment'),
    #payment/payment-id/update-save/
    path('<str:payment_id>/update-save/', views.update_payment_save, name='update_payment_save'),

    #payment/payment-id/delete
    path('<str:payment_id>/delete/', views.delete_payment, name='delete_payment'),
    #payment/payment-id/delete
    path('<str:payment_id>/delete-success/', views.delete_payment_save, name='payment_deleted'),

]