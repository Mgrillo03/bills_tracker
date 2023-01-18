from django.shortcuts import render, redirect

from .models import Bill
from providers.models import Provider

import datetime

def check_name(bill_number):
    """
    check if the bill number is available in users account list
    """    
    bills_list = Bill.objects.all()
    for i in bills_list:
        if bill_number.lower() == i.bill_number.lower():
            return False
    return True

def reset_messages(request):
    try : 
        aux = request.session['message_shown']
    except KeyError:
        request.session['message_shown'] = False
        request.session['message'] = ''
    else:
        if not request.session['message_shown'] :
            request.session['message_shown'] = True
        else:
            request.session['message'] = ''
        return request

def index(request):
    bills_list = Bill.objects.all()
    request = reset_messages(request)    
    return render(request, 'bills/index.html',{
        'bills_list': bills_list,
    })

def new_bill(request):
    request = reset_messages(request)
    providers_list = Provider.objects.all()
    date = datetime.date.today().isoformat()   

    return render(request, 'bills/new_bill.html',{
        'providers_list':providers_list,
        'date' : date,        
        })

def new_bill_calc(request):
    try:
        provider = Provider.objects.get(rif=request.POST['provider_rif'])
        print(provider.name)
    except (KeyError, Provider.DoesNotExist):
        print('error')
        request = reset_messages(request)
        request.session['message'] = 'Por favor seleccione un proveedor de la lista'
        request.session['message_shown'] = False
        return redirect('bills:new_bill')
    else:
        bill_number = request.POST['bill_number']
        bill_number_unique = check_name(bill_number)
        request = reset_messages(request)

        if bill_number_unique:
            emission_date = request.POST['emission_date']
            due_date = request.POST['due_date']
            total_amount_bs = float(request.POST['total_amount_bs'])
            sub_total_bs = total_amount_bs * 0.84
            sub_total_bs = int(sub_total_bs * 100) / 100
            tax_bs = total_amount_bs - sub_total_bs
            taxType = provider.taxtype
            if taxType == '0':
                retained_tax_bs = 0
                amount_to_pay_bs = total_amount_bs
            elif taxType == '75':
                retained_tax_bs = tax_bs * 0.75
                amount_to_pay_bs = total_amount_bs - retained_tax_bs
                amount_to_pay_bs = int(amount_to_pay_bs * 100) / 100
            elif taxType == '100':
                retained_tax_bs = tax_bs
                amount_to_pay_bs = total_amount_bs - retained_tax_bs
            exchange_rate = float(request.POST['exchange_rate'])
            total_amount_dollar = total_amount_bs / exchange_rate
            total_amount_dollar = int(total_amount_dollar * 100) / 100
            amount_to_pay_dollar = amount_to_pay_bs / exchange_rate
            amount_to_pay_dollar = int(amount_to_pay_dollar * 100) / 100
            note = request.POST['note']
            
        else:
            request.session['message'] = 'Ya existe una factura con el mismo numero'

        
        return render(request,'bills/new_bill_2.html',{            
            'bill_number':bill_number, 
            'emission_date':emission_date,
            'due_date':due_date ,
            'provider':provider, 
            'total_amount_bs':total_amount_bs,
            'sub_total_bs':sub_total_bs,
            'tax_bs' : tax_bs,
            'retained_tax_bs': retained_tax_bs,
            'amount_to_pay_bs': amount_to_pay_bs,
            'exchange_rate': exchange_rate,
            'total_amount_dollar': total_amount_dollar,
            'amount_to_pay_dollar': amount_to_pay_dollar,
            'note': note,
            })

def new_bill_save(request):
    provider = Provider.objects.get(rif=request.POST['provider_rif'])
    emission_date = datetime.date.fromisoformat(request.POST['emission_date'])
    due_date = datetime.date.fromisoformat(request.POST['due_date'])
    bill = Bill.objects.create(
        bill_number = request.POST['bill_number'], 
        emission_date = emission_date,
        due_date = due_date,
        provider = provider,
        total_amount_bs = request.POST['total_amount_bs'],
        sub_total_bs = request.POST['sub_total_bs'],
        tax_bs = request.POST['tax_bs'],
        retained_tax_bs = request.POST['retained_tax_bs'],
        amount_to_pay_bs = request.POST['amount_to_pay_bs'],
        exchange_rate = request.POST['exchange_rate'],
        total_amount_dollar = request.POST['total_amount_dollar'],
        amount_to_pay_dollar = request.POST['amount_to_pay_dollar'],
        note = request.POST['note']    
    )
    bill_number = request.POST['bill_number']
    request.session['message'] = f'Factura N°{bill_number} creada existosamente'
    request.session['message_shown'] = False
    return render(request,'bills/bill_created.html',{'bill':bill})
    

def bill_detail(request, bill_id):
    request = reset_messages(request)
    try:
        bill = Bill.objects.get(pk=bill_id)
    except (KeyError, Bill.DoesNotExist):
        request.session['message'] = 'No se encontro la factura'
        request.session['message_shown'] = False
        return redirect('bills:index')
    else:
        return render(request, 'bills/bill_detail.html',{
            'bill': bill,
        })


def update_bill(request):
    pass

def delete_bill(request):
    pass