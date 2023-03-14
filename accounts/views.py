from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required


from bills.views import reset_messages, staff_member_required

from .models import Account
from payments.models import Payment

import datetime

def check_name(name,list):
    """
    check if provider name is available in users account list
    """    
    for i in list:
        if name.lower() == i.name.lower():
            return False
    return True


@login_required
def index(request):
    accounts_list = Account.objects.all()
    request = reset_messages(request)
    return render(request, 'accounts/index.html',{
        'accounts_list':accounts_list,
    })


@login_required
def search(request):
    search_field = request.POST['search_field']
    accounts_list = accounts_list.filter(
    Q(name__contains=search_field) | 
    Q(description__contains=search_field)
    )
        
    request = reset_messages(request)    
    return render(request, 'accounts/index.html',{
        'accounts_list': accounts_list,
        'search_field': search_field
    })

@staff_member_required
@login_required
def new_account(request):
    request = reset_messages(request)
    return render(request, 'accounts/new_account.html',{})

@staff_member_required
@login_required
def new_account_save(request):
    accounts_list = Account.objects.all()
    name = request.POST['name']
    account_name_unique = check_name(name, accounts_list)
    request = reset_messages(request)

    if account_name_unique:
        name = request.POST['name']
        description = request.POST['description']
        account = Account.objects.create(name=name, description=description)
        request.session['success_message'] = f'Cuenta {name} creada existosamente'
        request.session['message_shown'] = False
        return redirect('accounts:index')
    else:
        request.session['error_message'] = 'Ya existe una cuenta con ese nombre'
        return redirect('accounts:new_account')



@login_required
def account_detail(request, account_id):
    request = reset_messages(request)
    try:
        account = Account.objects.get(pk=account_id)
    except (KeyError, Account.DoesNotExist):
        request.session['error_message'] = 'No se encontro el proveedor'
        request.session['message_shown'] = False
        return redirect('accounts:index')
    else:
        today = datetime.date.today().isoformat()
        date_start = today[:8] + '01'
        payments_list = Payment.objects.filter(account=account, date__gte=date_start)
        total_expent_bs = 0
        total_expent_dollar = 0
        for payment in payments_list:
            total_expent_bs += payment.amount_bs
            total_expent_dollar += payment.amount_dollar
        return render(request, 'accounts/account_detail.html',{
            'account': account,
            'total_expent_bs': total_expent_bs,
            'total_expent_dollar': total_expent_dollar,
            'payments_list': payments_list,
            'date_start': date_start,
            'date_end': today,
        })

@login_required
def detail_search(request, account_id):
    account = Account.objects.get(pk=account_id)
    payments_list = Payment.objects.filter(account=account)

    date_start = request.POST['date_start']
    date_end = request.POST['date_end']
    if date_start != '':
        date_start_iso = datetime.date.fromisoformat(date_start)
        payments_list = payments_list.filter(date__gte=date_start_iso)

    if date_end != '':
        date_end_iso = datetime.date.fromisoformat(date_end)
        payments_list = payments_list.filter(date__lte=date_end_iso)
    search_field = request.POST['search_field']
    payments_list = payments_list.filter(
    Q(transfer_id__contains=search_field) | 
    Q(description__contains=search_field)
    )        
    total_expent_bs = 0
    total_expent_dollar = 0
    for payment in payments_list:
        total_expent_bs += payment.amount_bs
        total_expent_dollar += payment.amount_dollar

    today = datetime.date.today().isoformat()
    date_start = today[:8] + '01'
    request = reset_messages(request)    
    return render(request, 'accounts/account_detail.html',{
        'account': account,
        'total_expent_bs': total_expent_bs,
        'total_expent_dollar': total_expent_dollar,
        'payments_list': payments_list,
        'search_field': search_field,
        'date_start': date_start,
        'date_end': today,
        'date_start': str(date_start_iso),
        'date_end': str(date_end_iso),
    })

@staff_member_required
@login_required
def update_account(request, account_id):
    account = Account.objects.get(pk=account_id)
    request = reset_messages(request)
    return render(request,'accounts/update_account.html',{'account':account})

@staff_member_required
@login_required
def update_account_save(request, account_id):
    accounts_list = Account.objects.all().exclude(pk=account_id)
    new_account_name = request.POST['name']
    accounts_name_unique = check_name(new_account_name, accounts_list)
    request = reset_messages(request)
   
    if accounts_name_unique :
        account = account.objects.get(pk=account_id)
        account.name = new_account_name
        account.description = request.POST['description']
        account.save()
        request.session['success_message'] = 'Cambios guardados satisfactoriamente'
        request.session['message_shown'] = False
        return redirect('accounts:update_account', account_id)
    else : 
        request.session['error_message'] = f'El Nombre {new_account_name} no esta disponible'
        request.session['message_shown'] = False
        return redirect('accounts:update_account', account_id)

@staff_member_required
@login_required
def delete_account(request,account_id):
    request = reset_messages(request)
    account = Account.objects.get(pk=account_id)
    accounts_list = Account.objects.all()
    return render(request, 'accounts/delete_account.html',{
        'account':account,
        'accounts_list':accounts_list,
        })    

@staff_member_required
@login_required
def delete_account_save(request,account_id):
    request = reset_messages(request)
    account = Account.objects.get(pk=account_id)
    account.delete()
    request.session['success_message'] = 'Cuenta eliminada satisfactoriamente'
    request.session['message_shown'] = False
    return redirect('accounts:index')    