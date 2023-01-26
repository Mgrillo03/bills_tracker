from django.shortcuts import render, redirect

from .models import Bill
from providers.models import Provider

import datetime

def check_name(bill_number, bills_list):
    """
    check if the bill number is available in users account list
    """    
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
    bills_list = Bill.objects.all().order_by('paid','due_date')
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
    except (KeyError, Provider.DoesNotExist):
        request = reset_messages(request)
        request.session['message'] = 'Por favor seleccione un proveedor de la lista'
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
            total_amount_bs = float(request.POST['total_amount_bs'])
            sub_total_bs = round(total_amount_bs * 0.84, 2)
            tax_bs = round(total_amount_bs - sub_total_bs,2)
            taxType = provider.taxtype
            if taxType == '0':
                retained_tax_bs = 0
                amount_to_pay_bs = total_amount_bs
            elif taxType == '75':
                retained_tax_bs = round(tax_bs * 0.75, 2)
                amount_to_pay_bs = round(total_amount_bs - retained_tax_bs, 2)
            elif taxType == '100':
                retained_tax_bs = tax_bs
                amount_to_pay_bs = total_amount_bs - retained_tax_bs
            exchange_rate = float(request.POST['exchange_rate'])
            total_amount_dollar = round(total_amount_bs / exchange_rate,2)
            amount_to_pay_dollar = round(amount_to_pay_bs / exchange_rate, 2)
            note = request.POST['note']
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
            
        else:
            request.session['message'] = f'Ya existe una factura de este proveedor con el codigo: {bill_number}'
            request.session['message_shown'] = False        
            return redirect('bills:new_bill')        
    

def new_bill_save(request):
    provider = Provider.objects.get(rif=request.POST['provider_rif'])
    emission_date = datetime.date.fromisoformat(request.POST['emission_date'])
    due_date = datetime.date.fromisoformat(request.POST['due_date'])
    bill_number = request.POST['bill_number']
    amount_to_pay_dollar = float(request.POST['amount_to_pay_dollar'])
    provider.dollar_debt = round(provider.dollar_debt + amount_to_pay_dollar,2)
    provider.save()
    bill = Bill.objects.create(
        bill_number = bill_number, 
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
        rest_to_pay_dollar = request.POST['amount_to_pay_dollar'],
        note = request.POST['note'],
    )
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
        return render(request, 'bills/bill_detail_2.html',{
            'bill': bill,
        })


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

def update_bill_calc(request, bill_id):
    bill = Bill.objects.get(pk=bill_id)
    bills_list = Bill.objects.filter(provider=bill.provider).exclude(pk=bill_id)
    new_bill_number = request.POST['bill_number']
    bills_number_unique = check_name(new_bill_number, bills_list)   
    request = reset_messages(request)
   
    if bills_number_unique :
        emission_date = request.POST['emission_date']
        due_date = request.POST['due_date']

        total_amount_bs = float(request.POST['total_amount_bs'])
        sub_total_bs = round(total_amount_bs * 0.84, 2)
        tax_bs = total_amount_bs - sub_total_bs
        taxType = bill.provider.taxtype
        if taxType == '0':
            retained_tax_bs = 0
            amount_to_pay_bs = total_amount_bs
        elif taxType == '75':
            retained_tax_bs = tax_bs * 0.75
            amount_to_pay_bs = round(total_amount_bs - retained_tax_bs, 2)
        elif taxType == '100':
            retained_tax_bs = tax_bs
            amount_to_pay_bs = total_amount_bs - retained_tax_bs
        exchange_rate = float(request.POST['exchange_rate'])
        total_amount_dollar = round(total_amount_bs / exchange_rate, 2)
        amount_to_pay_dollar = round(amount_to_pay_bs / exchange_rate, 2)
        note = request.POST['note']
        return render(request,'bills/update_bill_2.html',{            
            'bill': bill, 
            'bill_number': new_bill_number,
            'emission_date': emission_date,
            'due_date': due_date,
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

    else : 
        request.session['message'] = f'Ya existe una factura de este proveedor con el codigo: {new_bill_number}'
        request.session['message_shown'] = False        
        return redirect('bills:update_bill', bill_id)

def update_bill_save(request, bill_id):
    bill = Bill.objects.get(pk=bill_id)
    #update provider debt
    update_debt = bill.provider.dollar_debt - bill.amount_to_pay_dollar
    new_amount_to_pay_dollar = float(request.POST['amount_to_pay_dollar'])
    bill.provider.dollar_debt = round(update_debt + new_amount_to_pay_dollar,2)
    bill.provider.save()

    bill.bill_number = request.POST['bill_number']
    bill.emission_date = datetime.date.fromisoformat(request.POST['emission_date'])
    bill.due_date = datetime.date.fromisoformat(request.POST['due_date'])
    bill.total_amount_bs = float(request.POST['total_amount_bs']),
    bill.sub_total_bs = float(request.POST['sub_total_bs']),
    bill.tax_bs = float(request.POST['tax_bs']),
    bill.retained_tax_bs = float(request.POST['retained_tax_bs']),
    bill.amount_to_pay_bs = float(request.POST['amount_to_pay_bs']),
    bill.exchange_rate =float( request.POST['exchange_rate']),
    bill.total_amount_dollar = float(request.POST['total_amount_dollar']),
    bill.amount_to_pay_dollar = new_amount_to_pay_dollar,
    bill.note = request.POST['note']   
    bill.save()
    
    request.session['message'] = 'Cambios guardados satisfactoriamente'
    request.session['message_shown'] = False 
    return redirect('bills:bill_detail', bill_id)

def delete_bill(request,bill_id):
    request = reset_messages(request)
    bill = Bill.objects.get(pk= bill_id)
    return render(request, 'bills/delete_bill.html',{'bill':bill})    

def delete_bill_save(request,bill_id):
    request = reset_messages(request)
    bill = Bill.objects.get(pk=bill_id)
    bill.provider.dollar_debt = bill.provider.dollar_debt - bill.rest_to_pay_dollar
    bill.provider.save()
    bill.delete()
    request.session['message'] = 'Factura eliminado satisfactoriamente'
    request.session['message_shown'] = False
    return redirect('bills:index')    
