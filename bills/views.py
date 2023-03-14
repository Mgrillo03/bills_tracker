from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required



from .models import Bill
from providers.models import Provider
from payments.models import Payment

import datetime

def staff_member_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff :
            return view_func(request, *args, **kwargs)
        else:
            request.session['error_message'] = f'No tienes permisos para usar esta funcion'
            request.session['message_shown'] = False
            referer = request.META.get('HTTP_REFERER')
            return redirect(referer or 'bills:index')
    return wrapper

def format_number(string):
    string = string.replace('.','')
    return float(string.replace(',','.'))

def check_name(bill_number, bills_list):
    """
    check if the bill number is available in users account list
    """    
    for i in bills_list:
        if bill_number.lower() == i.bill_number.lower():
            return False
    return True

def check_overdue_bill(bills_list):
    """
    check and update the overdue status
    """
    today = datetime.date.today()
    for i in bills_list:
        if today > i.due_date and i.paid == False: 
            i.overdue = True
            i.save()
        elif i.paid == True:
            i.overdue = False
            i.save()

def reset_messages(request):
    try : 
        aux = request.session['message_shown']
    except KeyError:
        request.session['message_shown'] = False
        request.session['message'] = ''
        request.session['success_message'] = ''
        request.session['error_message'] = ''

    else:
        if not request.session['message_shown'] :
            request.session['message_shown'] = True
        else:
            request.session['message'] = ''
            request.session['success_message'] = ''
            request.session['error_message'] = ''
        return request

@login_required
def index(request):
    bills_list = Bill.objects.all().order_by('-overdue','paid','due_date')
    check_overdue_bill(bills_list)
    request = reset_messages(request)    
    return render(request, 'bills/index.html',{
        'bills_list': bills_list,
    })

@login_required
def search(request):
    date_start = request.POST['date_start']
    date_end = request.POST['date_end']
    if date_start != '':
        date_start_iso = datetime.date.fromisoformat(date_start)
        bills_list = Bill.objects.filter(emission_date__gte=date_start_iso)
    else: 
        bills_list = Bill.objects.all()

    if date_end != '':
        date_end_iso = datetime.date.fromisoformat(date_end)
        bills_list = bills_list.filter(emission_date__lte=date_end_iso)

    search_field = request.POST['search_field']
    provider_list = Provider.objects.filter(
        Q(name__contains=search_field) | 
        Q(nickname__contains=search_field) |
        Q(rif__contains=search_field)
        )
    only_overdue = request.POST.get('only_overdue',False)    
    if only_overdue:
        bills_list = bills_list.filter(overdue=True)
    # else:
    #     bills_list = Bill.objects.all()
    only_unpaid = request.POST.get('only_unpaid',False)    
    if only_unpaid:
        bills_list = bills_list.filter(paid=False)   
        
    bills_list = bills_list.filter(
        Q(bill_number__contains=search_field) | 
        Q(note__contains=search_field) | 
        Q(provider__in=provider_list)   
    ).order_by('-overdue','paid','due_date')
    request = reset_messages(request)    
    return render(request, 'bills/index.html',{
        'bills_list': bills_list,
        'search_field': search_field,
        'only_overdue': only_overdue,
        'only_unpaid': only_unpaid,
        'date_start': date_start,
        'date_end': date_end
    })

@staff_member_required
@login_required
def new_bill(request):
    request = reset_messages(request)
    providers_list = Provider.objects.all()
    date = datetime.date.today().isoformat()
    return render(request, 'bills/new_bill.html',{
        'providers_list':providers_list,
        'date' : date,        
        })

@staff_member_required
@login_required
def new_bill_show_provider(request):
    try:
        provider = Provider.objects.get(rif=request.POST['provider_rif'])
    except (KeyError, Provider.DoesNotExist):
        print('error')

        request = reset_messages(request)
        request.session['error_message'] = 'Por favor seleccione un proveedor de la lista'
        request.session['message_shown'] = False
        return redirect('bills:new_bill')
    else:
        request = reset_messages(request)
        providers_list = Provider.objects.all()
        date = datetime.date.today().isoformat()
        return render(request,'bills/new_bill.html',{
            'providers_list':providers_list,
            'date' : date,
            'provider_selected':provider, 
            })

@staff_member_required
@login_required
def new_bill_calc(request):
    try:
        provider = Provider.objects.get(rif=request.POST['provider_rif'])
    except (KeyError, Provider.DoesNotExist):
        request = reset_messages(request)
        request.session['error_message'] = 'Por favor seleccione un proveedor de la lista'
        request.session['message_shown'] = False
        return redirect('bills:new_bill')
    else:

        bill_number = request.POST['bill_number']
        bills_list = Bill.objects.filter(provider=provider)
        bill_number_unique = check_name(bill_number, bills_list)
        request = reset_messages(request)        

        if bill_number_unique:
            emission_date = request.POST['emission_date']
            due_date = request.POST['due_date']

            amount_bs = round(format_number(request.POST['amount_bs']),2)
            sub_total_bs = round(amount_bs / 1.16 , 2)
            tax_bs = round(amount_bs - sub_total_bs,2)

            amount_dollar = round(format_number(request.POST['amount_dollar']),2)
            sub_total_dollar = round(amount_dollar / 1.16 , 2)
            tax_dollar = round(amount_dollar - sub_total_dollar,2)
            
            taxType = provider.taxtype
            if taxType == '0':
                retained_tax_bs = 0
                amount_to_pay_bs = amount_bs
                retained_tax_dollar = 0
                amount_to_pay_dollar = amount_dollar

            elif taxType == '75':
                retained_tax_bs = round(tax_bs * 0.75, 2)
                amount_to_pay_bs = round(amount_bs - retained_tax_bs, 2)
                retained_tax_dollar = round(tax_dollar * 0.75, 2)
                amount_to_pay_dollar = round(amount_dollar - retained_tax_dollar, 2)

            elif taxType == '100':
                retained_tax_bs = tax_bs
                amount_to_pay_bs = round(amount_bs - retained_tax_bs,2)
                retained_tax_dollar = tax_dollar
                amount_to_pay_dollar = round(amount_dollar - retained_tax_dollar,2)


            exchange_rate = format_number(request.POST['exchange_rate'])
            if exchange_rate == 0 : 
                exchange_rate = 1

            bill_total_dollar = amount_bs / exchange_rate
            bill_total_dollar = round(bill_total_dollar + amount_dollar,2)
            total_to_pay_dollar = round(amount_to_pay_bs / exchange_rate + amount_to_pay_dollar, 2)

            note = request.POST['note']
            return render(request,'bills/new_bill_2.html',{            
            'bill_number':bill_number, 
            'emission_date':emission_date,
            'due_date':due_date ,
            'provider':provider,

            'amount_bs':amount_bs,
            'sub_total_bs':sub_total_bs,
            'tax_bs' : tax_bs,
            'retained_tax_bs': retained_tax_bs,
            'amount_to_pay_bs': amount_to_pay_bs,

            'exchange_rate': exchange_rate,

            'amount_dollar':amount_dollar,
            'sub_total_dollar':sub_total_dollar,
            'tax_dollar' : tax_dollar,
            'retained_tax_dollar': retained_tax_dollar,
            'amount_to_pay_dollar': amount_to_pay_dollar,

            'bill_total_dollar': bill_total_dollar,
            'total_to_pay_dollar': total_to_pay_dollar,
            'note': note,
            })
            
        else:
            request.session['error_message'] = f'Ya existe una factura de este proveedor con el codigo: {bill_number}'
            request.session['message_shown'] = False        
            return redirect('bills:new_bill')            

@staff_member_required
@login_required
def new_bill_save(request):
    provider = Provider.objects.get(rif=request.POST['provider_rif'])
    emission_date = datetime.date.fromisoformat(request.POST['emission_date'])
    due_date = datetime.date.fromisoformat(request.POST['due_date'])
    bill_number = request.POST['bill_number']
    total_to_pay_dollar = format_number(request.POST['total_to_pay_dollar'])
    provider.dollar_debt = round(provider.dollar_debt + total_to_pay_dollar,2)
    provider.save()
    bill = Bill.objects.create(
        bill_number = bill_number, 
        emission_date = emission_date,
        due_date = due_date,
        provider = provider,

        amount_bs = format_number(request.POST['amount_bs']),
        sub_total_bs = format_number(request.POST['sub_total_bs']),
        tax_bs = format_number(request.POST['tax_bs']),
        retained_tax_bs = format_number(request.POST['retained_tax_bs']),
        amount_to_pay_bs = format_number(request.POST['amount_to_pay_bs']),

        exchange_rate = format_number(request.POST['exchange_rate']),

        amount_dollar = format_number(request.POST['amount_dollar']),
        sub_total_dollar = format_number(request.POST['sub_total_dollar']),
        tax_dollar = format_number(request.POST['tax_dollar']),
        retained_tax_dollar = format_number(request.POST['retained_tax_dollar']),
        amount_to_pay_dollar = format_number(request.POST['amount_to_pay_dollar']),

        bill_total_dollar = format_number(request.POST['bill_total_dollar']),
        total_to_pay_dollar = format_number(request.POST['total_to_pay_dollar']),
        rest_to_pay_dollar = format_number(request.POST['total_to_pay_dollar']),
        note = request.POST['note'],
    )
    request.session['success_message'] = f'Factura N°{bill_number} creada existosamente'
    request.session['message_shown'] = False
    return redirect('bills:index')

@login_required
def bill_detail(request, bill_id):
    request = reset_messages(request)
    try:
        bill = Bill.objects.get(pk=bill_id)
    except (KeyError, Bill.DoesNotExist):
        request.session['error_message'] = 'No se encontro la factura'
        request.session['message_shown'] = False
        return redirect('bills:index')
    else:
        payments_list = Payment.objects.filter(bill=bill)
        return render(request, 'bills/bill_detail.html',{
            'bill': bill,
            'payments_list': payments_list,
        })

@staff_member_required
@login_required
def update_bill(request, bill_id):
    bill = Bill.objects.get(pk=bill_id)
    emission_date = bill.emission_date.isoformat()
    due_date = bill.due_date.isoformat()
    request = reset_messages(request)
    return render(request,'bills/update_bill.html',{
        'bill':bill,
        'emission_date':emission_date,
        'due_date':due_date,
        })

@staff_member_required
@login_required
def update_bill_calc(request, bill_id):
    bill = Bill.objects.get(pk=bill_id)
    bills_list = Bill.objects.filter(provider=bill.provider).exclude(pk=bill_id)
    new_bill_number = request.POST['bill_number']
    new_bill_number_unique = check_name(new_bill_number, bills_list)   
    request = reset_messages(request)
   
    if new_bill_number_unique :
        emission_date = request.POST['emission_date']
        due_date = request.POST['due_date']

        amount_bs = round(format_number(request.POST['amount_bs']),2)
        sub_total_bs = round(amount_bs / 1.16 , 2)
        tax_bs = round(amount_bs - sub_total_bs,2)

        amount_dollar = round(format_number(request.POST['amount_dollar']),2)
        sub_total_dollar = round(amount_dollar / 1.16 , 2)
        tax_dollar = round(amount_dollar - sub_total_dollar,2)
        
        taxType = bill.provider.taxtype
        if taxType == '0':
            retained_tax_bs = 0
            amount_to_pay_bs = amount_bs
            retained_tax_dollar = 0
            amount_to_pay_dollar = amount_dollar

        elif taxType == '75':
            retained_tax_bs = round(tax_bs * 0.75, 2)
            amount_to_pay_bs = round(amount_bs - retained_tax_bs, 2)
            retained_tax_dollar = round(tax_dollar * 0.75, 2)
            amount_to_pay_dollar = round(amount_dollar - retained_tax_dollar, 2)

        elif taxType == '100':
            retained_tax_bs = tax_bs
            amount_to_pay_bs = round(amount_bs - retained_tax_bs,2)
            retained_tax_dollar = tax_dollar
            amount_to_pay_dollar = round(amount_dollar - retained_tax_dollar,2)

        exchange_rate = format_number(request.POST['exchange_rate'])
        if exchange_rate == 0 : 
            exchange_rate = 1

        bill_total_dollar = amount_bs / exchange_rate
        bill_total_dollar = round(bill_total_dollar + amount_dollar,2)
        total_to_pay_dollar = round(amount_to_pay_bs / exchange_rate + amount_to_pay_dollar, 2)

        note = request.POST['note']

        return render(request,'bills/update_bill_2.html',{            
            'bill': bill, 
            'bill_number':new_bill_number, 
            'emission_date':emission_date,
            'due_date':due_date ,

            'amount_bs':amount_bs,
            'sub_total_bs':sub_total_bs,
            'tax_bs' : tax_bs,
            'retained_tax_bs': retained_tax_bs,
            'amount_to_pay_bs': amount_to_pay_bs,

            'exchange_rate': exchange_rate,

            'amount_dollar':amount_dollar,
            'sub_total_dollar':sub_total_dollar,
            'tax_dollar' : tax_dollar,
            'retained_tax_dollar': retained_tax_dollar,
            'amount_to_pay_dollar': amount_to_pay_dollar,

            'bill_total_dollar': bill_total_dollar,
            'total_to_pay_dollar': total_to_pay_dollar,
            'note': note,
            })                  

    else : 
        request.session['error_message'] = f'Ya existe una factura de este proveedor con el codigo: {new_bill_number}'
        request.session['message_shown'] = False        
        return redirect('bills:update_bill', bill_id)

@staff_member_required
@login_required
def update_bill_save(request, bill_id):
    bill = Bill.objects.get(pk=bill_id)
    #update provider debt
    new_total_to_pay_dollar = format_number(request.POST['total_to_pay_dollar'])
    update_debt = bill.provider.dollar_debt - bill.total_to_pay_dollar
    bill.provider.dollar_debt = round(update_debt + new_total_to_pay_dollar,2)
    bill.provider.save()

    bill.bill_number = request.POST['bill_number']
    bill.emission_date = datetime.date.fromisoformat(request.POST['emission_date'])
    bill.due_date = datetime.date.fromisoformat(request.POST['due_date'])
    
    bill.amount_bs = format_number(request.POST['amount_bs'])
    bill.sub_total_bs = format_number(request.POST['sub_total_bs'])
    bill.tax_bs = format_number(request.POST['tax_bs'])
    bill.retained_tax_bs = format_number(request.POST['retained_tax_bs'])
    bill.amount_to_pay_bs = format_number(request.POST['amount_to_pay_bs']) 
      
    bill.exchange_rate =format_number( request.POST['exchange_rate'])

    bill.amount_dollar = format_number(request.POST['amount_dollar'])
    bill.sub_total_dollar = format_number(request.POST['sub_total_dollar'])
    bill.tax_dollar = format_number(request.POST['tax_dollar'])
    bill.retained_tax_dollar = format_number(request.POST['retained_tax_dollar'])
    bill.amount_to_pay_dollar = format_number(request.POST['amount_to_pay_dollar'])

    bill.bill_total_dollar = format_number(request.POST['bill_total_dollar'])
    total_to_pay_dollar = format_number(request.POST['total_to_pay_dollar'])
    bill.total_to_pay_dollar = total_to_pay_dollar
    bill.rest_to_pay_dollar = round(total_to_pay_dollar - bill.amount_paid_dollar,2)

    bill.note = request.POST['note']   
    bill.save()
    
    request.session['success_message'] = 'Cambios guardados satisfactoriamente'
    request.session['message_shown'] = False 
    return redirect('bills:bill_detail', bill_id)

@staff_member_required
@login_required
def delete_bill(request,bill_id):
    request = reset_messages(request)
    bills_list = Bill.objects.all().order_by('paid','due_date')
    bill = Bill.objects.get(pk= bill_id)
    return render(request, 'bills/delete_bill.html',{
        'bill':bill,
        'bills_list':bills_list
        })    

@staff_member_required
@login_required
def delete_bill_save(request,bill_id):
    request = reset_messages(request)
    bill = Bill.objects.get(pk=bill_id)
    bill.provider.dollar_debt = round(bill.provider.dollar_debt - bill.rest_to_pay_dollar,2)
    bill.provider.save()
    bill.delete()
    request.session['success_message'] = 'Factura eliminada satisfactoriamente'
    request.session['message_shown'] = False
    return redirect('bills:index')    