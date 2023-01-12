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
    return render(request, 'providers/index.html',{
        'bills_list': bills_list,
    })

def new_bill(request):
    request = reset_messages(request)
    providers_list = Provider.objects.all()
    return render(request, 'bills/new_bill.html',{'providers_list':providers_list})

def new_bill_save(request):
    try:
        provider = Provider.objects.get(rif=request.POST['provider_rif'])
    except (KeyError, Provider.DoesNotExist):
        request = reset_messages(request)
        request.session['message'] = 'Por favor seleccione un proveedor de la lista'
        request.session['message_shown'] = False
        return redirect('accounts:new_bill')
    else:
        bill_number = request.POST['bill_number']
        bill_number_unique = check_name(bill_number)
        request = reset_messages(request)

        if bill_number_unique:
            emission_date = datetime.date.fromisoformat(request.POST['emission_date'])
            due_date = datetime.date.fromisoformat(request.POST['due_date'])
            ### los subtotales pueden tener la opcion de ser calculados o agregados directamente
            total_amount_bs = request.POST['total_amount_bs']
            sub_total_bs = request.POST['sub_total_bs']
            tax_bs = request.POST['tax_bs']
            retained_tax_bs = request.POST['retained_tax_bs']
            amount_to_pay_bs = request.POST['amount_to_pay_bs']
            exchange_fee = request.POST['exchange_fee']
            total_amount_dollar = request.POST['total_amount_dollar']
            amount_to_pay_dollar = request.POST['amount_to_pay_dollar']
            note = request.POST['note']
            Bill.objects.create(
                bill_number=bill_number, 
                emission_date=emission_date, 
                due_date=due_date, 
                provider=provider, 
                total_amount_bs=total_amount_bs,
                sub_total_bs = sub_total_bs,
                tax_bs = tax_bs,
                retained_tax_bs = retained_tax_bs,
                amount_to_pay_bs = amount_to_pay_bs,
                exchange_fee = exchange_fee,
                total_amount_dollar = total_amount_dollar,
                amount_to_pay_dollar = amount_to_pay_dollar,
                note = note
            )

            request.session['message'] = f'Factura N°{bill_number} creada existosamente'
            request.session['message_shown'] = False
        else:
            request.session['message'] = 'Ya existe una factura con el mismo numero'

        return render(request,'providers/provider_created.html',{'provider':provider})