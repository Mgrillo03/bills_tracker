from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required


from .models import Payment
from providers.models import Provider
from bills.models import Bill
from bills.views import reset_messages, format_number, staff_member_required
from accounts.models import Account

import datetime

@login_required
def index(request):
    request = reset_messages(request)
    payments_list = Payment.objects.all().order_by('-date')
    return render(request, 'payments/index.html',{
        'payments_list':payments_list
        })

@login_required
def search(request):
    search_field = request.POST['search_field']
    provider_list = Provider.objects.filter(
        Q(name__contains=search_field) | 
        Q(nickname__contains=search_field) |
        Q(rif__contains=search_field)
        )    
    bills_list = Bill.objects.filter(
        Q(bill_number__contains=search_field) | 
        Q(note__contains=search_field) | 
        Q(provider__in=provider_list)   
    )    

    only_total = request.POST.get('only_total',False)    
    if only_total:
        payments_list = Payment.objects.filter(paid_total=True)
    else:
        payments_list = Payment.objects.all()
    only_partial = request.POST.get('only_partial',False)    
    if only_partial:
        payments_list = payments_list.filter(paid_total=False)
    
    if only_partial and only_total :
        payments_list = Payment.objects.all()

    payments_list = payments_list.filter(
        Q(account__contains=search_field) | 
        Q(description__contains=search_field) | 
        Q(transfer_id__contains=search_field) |
        Q(bill__in=bills_list)   
    ).order_by('-date')   
        

    request = reset_messages(request)    
    return render(request, 'payments/index.html',{
        'payments_list': payments_list,
        'search_field': search_field,
        'only_total': only_total,
        'only_partial': only_partial
    })

@staff_member_required
@login_required
def new_payment(request):
    request = reset_messages(request)
    bills_list = Bill.objects.filter(paid='False')
    accounts_list = Account.objects.all()
    date = datetime.date.today().isoformat() 
    return render(request, 'payments/new_payment.html',{
        'bills_list': bills_list,
        'date': date,
        'accounts_list': accounts_list,
    })

@staff_member_required
@login_required
def new_payment_show_bill(request):
    try:
        bill_id = request.POST['bill_id'].split('-',1)
        bill = Bill.objects.get(pk=bill_id[1])
    except (KeyError, Bill.DoesNotExist):
        request = reset_messages(request)
        request.session['message'] = 'Por favor seleccione una factura de la lista'
        request.session['message_shown'] = False
        return redirect('payments:new_payment')
    else:
        request = reset_messages(request)
        bills_list = Bill.objects.all()
        accounts_list = Account.objects.all()
        date = datetime.date.today().isoformat()
        return render(request,'payments/new_payment.html',{
            'bills_list':bills_list,
            'date' : date,
            'bill_selected':bill, 
            'accounts_list': accounts_list,

            })

@staff_member_required
@login_required
def new_payment_show_bill_id(request,bill_id):
    try:
        bill = Bill.objects.get(pk=bill_id)
    except (KeyError, Bill.DoesNotExist):
        request = reset_messages(request)
        request.session['message'] = 'Por favor seleccione una factura de la lista'
        request.session['message_shown'] = False
        return redirect('payments:new_payment')
    else:
        request = reset_messages(request)
        bills_list = Bill.objects.all()
        accounts_list = Account.objects.all()
        date = datetime.date.today().isoformat()
        return render(request,'payments/new_payment.html',{
            'bills_list':bills_list,
            'date' : date,
            'bill_selected':bill, 
            'accounts_list': accounts_list,
            })

@staff_member_required
@login_required
def new_payment_save(request):
    try:
        bill = Bill.objects.get(pk=request.POST['bill_selected'])
        account = Account.objects.get(name=request.POST['account_name'])
    except (KeyError, Bill.DoesNotExist):
        request = reset_messages(request)
        request.session['message'] = 'Por favor seleccione elementos de la lista'
        request.session['message_shown'] = False
        return redirect('payments:new_payment')
    else:
        date = datetime.date.fromisoformat(request.POST['date'])
        exchange_rate = format_number(request.POST['exchange_rate'])
        amount_dollar = format_number(request.POST['amount_dollar'])
        amount_bs = format_number(request.POST['amount_bs'])
        
        if exchange_rate == 0:
            exchange_rate = 1
        total_amount_dollar = amount_bs / exchange_rate
        total_amount_dollar = round(total_amount_dollar + amount_dollar,2)
        paid_total = request.POST.get('paid_total',False)
        if paid_total:
            bill.provider.dollar_debt = round(bill.provider.dollar_debt - bill.rest_to_pay_dollar,2)
            bill.provider.save()
            bill.paid = True
            bill.amount_paid_dollar = round(bill.amount_paid_dollar + total_amount_dollar,2)
            bill.rest_to_pay_dollar = 0
            bill.save()
        else:             
            bill.rest_to_pay_dollar = round(bill.rest_to_pay_dollar - total_amount_dollar,2)
            bill.amount_paid_dollar = round(bill.amount_paid_dollar + total_amount_dollar,2)
            bill.save()
            bill.provider.dollar_debt = round(bill.provider.dollar_debt - total_amount_dollar,2)
            bill.provider.save()
        Payment.objects.create(
            bill = bill,
            account = account,
            date = date,
            amount_bs = amount_bs,
            amount_dollar = amount_dollar,
            exchange_rate = exchange_rate,
            paid_total = paid_total,
            description = request.POST['description'],
            transfer_id = request.POST['transfer_id'],
            total_dollar = total_amount_dollar
        )
        request.session['message'] = 'Pago creado de manera exitosa'
        request.session['message_shown'] = False
        return redirect('payments:index')

@login_required
def payment_detail(request, payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
    except (KeyError, Payment.DoesNotExist):
        request = reset_messages(request)
        request.session['message'] = 'No se encontro el pago'
        request.session['message_shown'] = False
        return redirect('payments:index')
    else:
        if payment.exchange_rate == 0:
            payment.exchange_rate = 1 
            payment.save()
        total_paid = round(payment.amount_dollar + payment.amount_bs / payment.exchange_rate,2)
        return render(request, 'payments/payment_detail.html',{
            'payment':payment,
            'total_paid': total_paid,            
            })

@staff_member_required
@login_required
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
        accounts_list = Account.objects.all()
        return render(request, 'payments/update_payment.html',{
            'payment':payment,
            'date': date,
            'accounts_list': accounts_list,
        })

@staff_member_required
@login_required
def update_payment_save(request, payment_id):
    try:
        account = Account.objects.get(name=request.POST['account_name'])
    except (KeyError, Payment.DoesNotExist):
        request = reset_messages(request)
        request.session['message'] = 'Por favor seleccione una cuenta de la lista'
        request.session['message_shown'] = False
        return redirect('payments:update_payment')
    else:
        payment = Payment.objects.get(pk=payment_id)
        date = datetime.date.fromisoformat(request.POST['date'])
        exchange_rate = format_number(request.POST['exchange_rate'])
        amount_dollar = format_number(request.POST['amount_dollar'])
        amount_bs = format_number(request.POST['amount_bs'])
        paid_total = request.POST.get('paid_total',False)
        if exchange_rate == 0 :
            exchange_rate = 1
        new_total_amount_dollar = amount_bs / exchange_rate
        new_total_amount_dollar = new_total_amount_dollar + amount_dollar
        if paid_total:
            if not payment.paid_total:  
                update_debt = payment.bill.provider.dollar_debt + payment.total_dollar
                payment.bill.provider.dollar_debt = round(update_debt - payment.bill.amount_to_pay_dollar,2)
                payment.bill.provider.save()   

            payment.bill.paid = True
            payment.bill.amount_paid_dollar = payment.bill.total_to_pay_dollar
            payment.bill.rest_to_pay_dollar = 0
            payment.bill.save()
        else: 
            #Update payment, first revert the payment, then make the new one
            
            payment.bill.paid = False
            #update_rest_to_pay_dollar = round(payment.bill.rest_to_pay_dollar + payment.total_dollar,2)
            if payment.paid_total:
                update_debt = payment.bill.provider.dollar_debt + payment.bill.total_to_pay_dollar
                payment.bill.provider.dollar_debt = round(update_debt - new_total_amount_dollar,2)
                payment.bill.provider.save()   
            else:
                update_debt = payment.bill.provider.dollar_debt + payment.total_dollar
                payment.bill.provider.dollar_debt = round(update_debt - new_total_amount_dollar,2)
                payment.bill.provider.save()
            #revert amount paid
            new_amount_paid_dollar = payment.bill.amount_paid_dollar - payment.total_dollar + new_total_amount_dollar        
            #new amount paid
            payment.bill.amount_paid_dollar = round(new_amount_paid_dollar,2)
            payment.bill.rest_to_pay_dollar = round(payment.bill.total_to_pay_dollar - new_amount_paid_dollar,2)
            payment.bill.save()    
        
        payment.account = account
        payment.date = date
        payment.amount_bs = amount_bs
        payment.amount_dollar = amount_dollar
        payment.exchange_rate = exchange_rate
        payment.paid_total = paid_total
        payment.description = request.POST['description']
        payment.transfer_id = request.POST['transfer_id']
        payment.total_dollar = new_total_amount_dollar
        payment.save()
        
        request.session['message'] = 'Cambios guardados'
        request.session['message_shown'] = False
        return redirect('payments:payment_detail',payment_id)

@staff_member_required
@login_required
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

@staff_member_required
@login_required
def delete_payment_save(request, payment_id):
    request = reset_messages(request)
    payment = Payment.objects.get(pk=payment_id)
    payment.bill.paid = False
    amount_paid = payment.bill.amount_paid_dollar - payment.total_dollar
    payment.bill.amount_paid_dollar = round(amount_paid,2)
    old_rest_to_pay = payment.bill.rest_to_pay_dollar
    payment.bill.rest_to_pay_dollar = round(payment.bill.total_to_pay_dollar - amount_paid,2)
    payment.bill.save()
    payment.bill.provider.dollar_debt = round(payment.bill.provider.dollar_debt - old_rest_to_pay + payment.bill.rest_to_pay_dollar ,2)
    payment.bill.provider.save()

    payment.delete()
    request.session['message'] = 'Pago eliminado'
    request.session['message_shown'] = False
    return redirect('payments:index')
