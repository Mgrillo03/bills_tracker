from django.shortcuts import render, redirect

from .models import Payment
from bills.models import Bill
from bills.views import reset_messages

import datetime

def index(request):
    request = reset_messages(request)
    payments_list = Payment.objects.all()
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
        paid_total = request.POST.get('paid_total',False)
        if paid_total:
            bill.paid = True
            bill.rest_to_pay_dollar = 0
            bill.save()
        else: 
            total_amount_dollar = amount_bs / exchange_rate
            total_amount_dollar = total_amount_dollar + amount_dollar
            bill.rest_to_pay_dollar = round(float(bill.rest_to_pay_dollar) - total_amount_dollar,2)
            bill.save()
        Payment.objects.create(
            bill = bill,
            date = date,
            amount_bs = amount_bs,
            amount_dollar = amount_dollar,
            exchange_rate = exchange_rate,
            account = request.POST['account'],
            paid_total = paid_total,
            description = request.POST['description'],
            transfer_id = request.POST['transfer_id']
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
            'total_paid': total_paid
            
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
        date = datetime.date.today().isoformat()        
        return render(request, 'payments/update_payment.html',{
            'payment':payment,
            'date': date,
            })

def update_payment_save(request, payment_id):
    print('actualizar')
    payment = Payment.objects.get(pk=payment_id)
    date = datetime.date.fromisoformat(request.POST['date'])
    exchange_rate = float(request.POST['exchange_rate'])
    amount_dollar = float(request.POST['amount_dollar'])
    amount_bs = float(request.POST['amount_bs'])
    paid_total = request.POST.get('paid_total',False)
    if paid_total:
        print('pago total')
        payment.bill.paid = True
        payment.bill.rest_to_pay_dollar = 0
        payment.bill.save()
    else: 
        print('pago parcial')
        #Update payment, first revert the payment, then make the new one
        #revert
        payment.bill.paid = False
        prev_total_amount_dollar = payment.amount_bs / payment.exchange_rate
        prev_total_amount_dollar = prev_total_amount_dollar + payment.amount_dollar
        payment.bill.rest_to_pay_dollar = round(float(payment.bill.rest_to_pay_dollar) + prev_total_amount_dollar,2)
        payment.bill.save()

        #new payment
        new_total_amount_dollar = amount_bs / exchange_rate
        new_total_amount_dollar = new_total_amount_dollar + amount_dollar
        payment.bill.rest_to_pay_dollar = round(float(payment.bill.rest_to_pay_dollar) - new_total_amount_dollar,2)
        payment.bill.save()    
    
    payment.date = date
    payment.amount_bs = amount_bs
    payment.amount_dollar = amount_dollar
    payment.exchange_rate = exchange_rate
    payment.account = request.POST['account']
    payment.paid_total = paid_total
    payment.description = request.POST['description']
    payment.transfer_id = request.POST['transfer_id']
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
        return render(request, 'payments/delete_payment.html',{'payment':payment})

def delete_payment_save(request, payment_id):
    request = reset_messages(request)
    payment = Payment.objects.get(pk=payment_id)
    payment.bill.paid = False
    total_amount_dollar = payment.amount_bs / payment.exchange_rate
    total_amount_dollar = total_amount_dollar + payment.amount_dollar
    payment.bill.rest_to_pay_dollar = round(float(payment.bill.rest_to_pay_dollar) + total_amount_dollar,2)
    payment.bill.save()
    payment.delete()
    request.session['message'] = 'Pago eliminado'
    request.session['message_shown'] = False
    return redirect('payments:index')
