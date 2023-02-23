from django.shortcuts import render, redirect
from django.db.models import Q

from bills.views import reset_messages

from .models import Account
from payments.models import Payment

def check_name(name,list):
    """
    check if provider name is available in users account list
    """    
    for i in list:
        if name.lower() == i.name.lower():
            return False
    return True

def index(request):
    accounts_list = Account.objects.all()
    request = reset_messages(request)    
    return render(request, 'accounts/index.html',{
        'accounts_list':accounts_list,
    })

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

def new_account(request):
    request = reset_messages(request)
    return render(request, 'accounts/new_account.html',{})

def new_account_save(request):
    accounts_list = Account.objects.all()
    name = request.POST['name']
    account_name_unique = check_name(name, accounts_list)
    request = reset_messages(request)

    if account_name_unique:
        name = request.POST['name']
        description = request.POST['description']
        account = Account.objects.create(name=name, description=description)
        request.session['message'] = f'Cuenta {name} creada existosamente'
        request.session['message_shown'] = False
    else:
        request.session['message'] = 'Ya existe una cuenta con ese nombre'

    return redirect('accounts:index')

def account_detail(request, account_id):
    request = reset_messages(request)
    try:
        account = Account.objects.get(pk=account_id)
    except (KeyError, Account.DoesNotExist):
        request.session['message'] = 'No se encontro el proveedor'
        request.session['message_shown'] = False
        return redirect('accounts:index')
    else:
        payments_list = Payment.objects.filter(account=account)
        total_expent_bs = 0
        total_expent_dollar = 0
        print(account.name)
        print(payments_list[0].total_dollar)
        for payment in payments_list:
            total_expent_bs += payment.amount_bs
            total_expent_dollar += payment.amount_dollar
        return render(request, 'accounts/account_detail.html',{
            'account': account,
            'total_expent_bs': total_expent_bs,
            'total_expent_dollar': total_expent_dollar,
            'payments_list': payments_list
        })

def update_account(request, account_id):
    account = Account.objects.get(pk=account_id)
    request = reset_messages(request)
    return render(request,'accounts/update_account.html',{'account':account})

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
        request.session['message'] = 'Cambios guardados satisfactoriamente'
        request.session['message_shown'] = False
        return redirect('accounts:update_account', account_id)
    else : 
        request.session['message'] = f'El Nombre {new_account_name} no esta disponible'
        request.session['message_shown'] = False
        return redirect('accounts:update_account', account_id)

def delete_account(request,account_id):
    request = reset_messages(request)
    account = Account.objects.get(pk=account_id)
    accounts_list = Account.objects.all()
    return render(request, 'accounts/delete_account.html',{
        'account':account,
        'accounts_list':accounts_list,
        })    

def delete_account_save(request,account_id):
    request = reset_messages(request)
    account = Account.objects.get(pk=account_id)
    account.delete()
    request.session['message'] = 'Cuenta eliminada satisfactoriamente'
    request.session['message_shown'] = False
    return redirect('accounts:index')    