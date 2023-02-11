from django.shortcuts import render, redirect

from .models import Payment
from bills.models import Bill
from bills.views import reset_messages

import datetime

def index(request):
    request = reset_messages(request)
    payments_list = Payment.objects.all().order_by('-date')
    return render(request, 'payments/index.html',{
        'payments_list':payments_list
        })

def new_payment(request):
    request = reset_messages(request)
    bills_list = Bill.objects.filter(paid='False')
    date = datetime.date.today().isoformat() 
    return render(request, 'payments/new_payment.html',{
        'bills_list': bills_list,
        'date': date,
    })

def new_payment_save(request):
    try:
        bill = Bill.objects.get(pk=request.POST['bill_id'])
    except (KeyError, Bill.DoesNotExist):
        request = reset_messages(request)
        request.session['message'] = 'Por favor seleccione una factura de la lista'
        request.session['message_shown'] = False
        return redirect('payments:index')
    else:
        date = datetime.date.fromisoformat(request.POST['date'])
        exchange_rate = float(request.POST['exchange_rate'])
        amount_dollar = float(request.POST['amount_dollar'])
        amount_bs = float(request.POST['amount_bs'])
        total_amount_dollar = amount_bs / exchange_rate
        total_amount_dollar = round(total_amount_dollar + amount_dollar,2)
        paid_total = request.POST.get('paid_total',False)
        if paid_total:
            bill.paid = True
            bill.rest_to_pay_dollar = 0
            bill.provider.dollar_debt = round(bill.provider.dollar_debt - bill.rest_to_pay_dollar,2)
            bill.provider.save()
            bill.save()
        else:             
            bill.rest_to_pay_dollar = round(bill.rest_to_pay_dollar - total_amount_dollar,2)
            bill.save()
            bill.provider.dollar_debt = round(bill.provider.dollar_debt - total_amount_dollar,2)
            bill.provider.save()
        Payment.objects.create(
            bill = bill,
            date = date,
            amount_bs = amount_bs,
            amount_dollar = amount_dollar,
            exchange_rate = exchange_rate,
            account = request.POST['account'],
            paid_total = paid_total,
            description = request.POST['description'],
            transfer_id = request.POST['transfer_id'],
            total_dollar = total_amount_dollar
        )
        request.session['message'] = 'Pago creado de manera exitosa'
        request.session['message_shown'] = False
        return redirect('payments:index')

def payment_detail(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
    except (KeyError, Payment.DoesNotExist):
        request = reset_messages(request)
        request.session['message'] = 'No se encontro el pago'
        request.session['message_shown'] = False
        return redirect('payments:index')
    else:
        total_paid = round(payment.amount_dollar + payment.amount_bs / payment.exchange_rate,2)
        return render(request, 'payments/payment_detail.html',{
            'payment':payment,
            'total_paid': total_paid,            
            })

def update_payment(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
    except (KeyError, Payment.DoesNotExist):
        request = reset_messages(request)
        request.session['message'] = 'No se encontro el pago'
        request.session['message_shown'] = False
        return redirect('payments:index')
    else:
        date = payment.date.isoformat()        
        return render(request, 'payments/update_payment.html',{
            'payment':payment,
            'date': date,
            })

def update_payment_save(request, payment_id):
    payment = Payment.objects.get(pk=payment_id)
    date = datetime.date.fromisoformat(request.POST['date'])
    exchange_rate = float(request.POST['exchange_rate'])
    amount_dollar = float(request.POST['amount_dollar'])
    amount_bs = float(request.POST['amount_bs'])
    paid_total = request.POST.get('paid_total',False)
    new_total_amount_dollar = amount_bs / exchange_rate
    new_total_amount_dollar = new_total_amount_dollar + amount_dollar
    if paid_total:
        if not payment.paid_total:  
            update_debt = payment.bill.provider.dollar_debt + payment.total_dollar
            payment.bill.provider.dollar_debt = round(update_debt - payment.bill.amount_to_pay_dollar,2)
            payment.bill.provider.save()   

        payment.bill.paid = True
        payment.bill.rest_to_pay_dollar = 0
        payment.bill.save()
    else: 
        #Update payment, first revert the payment, then make the new one
        #revert
        payment.bill.paid = False
        update_rest_to_pay_dollar = round(float(payment.bill.rest_to_pay_dollar) + payment.total_dollar,2)
        if payment.paid_total:
            update_debt = payment.bill.provider.dollar_debt + payment.bill.amount_to_pay_dollar
            payment.bill.provider.dollar_debt = round(update_debt - new_total_amount_dollar,2)
            payment.bill.provider.save()   
        else:
            update_debt = payment.bill.provider.dollar_debt + payment.total_dollar
            payment.bill.provider.dollar_debt = round(update_debt - new_total_amount_dollar,2)
            payment.bill.provider.save()
        #new payment        
        payment.bill.rest_to_pay_dollar = round(update_rest_to_pay_dollar - new_total_amount_dollar,2)
        payment.bill.save()    
    
    payment.date = date
    payment.amount_bs = amount_bs
    payment.amount_dollar = amount_dollar
    payment.exchange_rate = exchange_rate
    payment.account = request.POST['account']
    payment.paid_total = paid_total
    payment.description = request.POST['description']
    payment.transfer_id = request.POST['transfer_id']
    payment.total_dollar = new_total_amount_dollar
    payment.save()
    
    request.session['message'] = 'Cambios guardados'
    request.session['message_shown'] = False
    return redirect('payments:payment_detail',payment_id)

def delete_payment(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
    except (KeyError, Payment.DoesNotExist):
        request = reset_messages(request)
        request.session['message'] = 'No se encontro el pago'
        request.session['message_shown'] = False
        return redirect('payments:index')
    else:
        payments_list = Payment.objects.all().order_by('-date')
        return render(request, 'payments/delete_payment.html',{
            'payment':payment,
            'payments_list':payments_list,
            })

def delete_payment_save(request, payment_id):
    request = reset_messages(request)
    payment = Payment.objects.get(pk=payment_id)
    if payment.paid_total:
        payment.bill.provider.dollar_debt = payment.bill.provider.dollar_debt + payment.bill.amount_to_pay_dollar
    else:
        payment.bill.provider.dollar_debt = payment.bill.provider.dollar_debt + payment.total_dollar
    payment.bill.provider.save()
    payment.bill.paid = False
    payment.bill.rest_to_pay_dollar = round(float(payment.bill.rest_to_pay_dollar) + payment.total_dollar,2)
    payment.bill.save()
    payment.delete()
    request.session['message'] = 'Pago eliminado'
    request.session['message_shown'] = False
    return redirect('payments:index')
