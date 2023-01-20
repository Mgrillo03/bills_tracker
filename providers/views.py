from django.shortcuts import render, redirect

from .models import Provider

def check_name(rif,list):
    """
    check if provider RIF is available in users account list
    """    
    for i in list:
        if rif.lower() == i.rif.lower():
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
    providers_list = Provider.objects.all()
    request = reset_messages(request)    
    return render(request, 'providers/index.html',{
        'providers_list':providers_list,
    })

def new_provider(request):
    request = reset_messages(request)
    return render(request, 'providers/new_provider.html',{})

def new_provider_save(request):
    providers_list = Provider.objects.all()
    rif = request.POST['rif']
    provider_rif_unique = check_name(rif, providers_list)
    request = reset_messages(request)

    if provider_rif_unique:
        name = request.POST['name']
        nickname = request.POST['nickname']
        taxtype = request.POST['taxtype']
        dollar_debt = float(request.POST['dollar_debt'])
        provider = Provider.objects.create(name=name, rif=rif, nickname=nickname, taxtype=taxtype, dollar_debt=dollar_debt)
        request.session['message'] = f'Usuario {name} creado existosamente'
        request.session['message_shown'] = False
    else:
        request.session['message'] = 'Ya existe un usuario con ese RIF'

    return render(request,'providers/provider_created.html',{'provider':provider})

def provider_detail(request, provider_id):
    request = reset_messages(request)
    try:
        provider = Provider.objects.get(pk=provider_id)
    except (KeyError, Provider.DoesNotExist):
        request.session['message'] = 'No se encontro el proveedor'
        request.session['message_shown'] = False
        return redirect('providers:index')
    else:
        return render(request, 'providers/provider_detail.html',{
            'provider': provider,
        })


def update_provider(request, provider_id):
    provider = Provider.objects.get(pk=provider_id)
    request = reset_messages(request)
    return render(request,'providers/update_provider.html',{'provider':provider})


def update_provider_save(request, provider_id):
    providers_list = Provider.objects.all().exclude(pk=provider_id)
    new_provider_rif = request.POST['rif']
    providers_rif_unique = check_name(new_provider_rif, providers_list)
    request = reset_messages(request)
   
    if providers_rif_unique :
        provider = Provider.objects.get(pk=provider_id)
        provider.rif = new_provider_rif
        provider.name = request.POST['name']
        provider.nickname = request.POST['nickname']
        provider.dollar_debt = float(request.POST['dollar_debt']) 
        provider.taxtype = request.POST['taxtype']
        ### crear pago cuando se modifique la deuda

        provider.save()
        request.session['message'] = 'Cambios guardados satisfactoriamente'
        request.session['message_shown'] = False
        return redirect('providers:update_provider', provider_id)
    else : 
        request.session['message'] = f'El RIF {new_provider_rif} no esta disponible'
        request.session['message_shown'] = False
        return redirect('providers:update_provider', provider_id)

def delete_provider(request,provider_id):
    request = reset_messages(request)
    provider = Provider.objects.get(pk=provider_id)
    return render(request, 'providers/delete_provider.html',{'provider':provider})    

def delete_provider_save(request,provider_id):
    request = reset_messages(request)
    provider = Provider.objects.get(pk=provider_id)
    provider.delete()
    request.session['message'] = 'Proveedor eliminado satisfactoriamente'
    request.session['message_shown'] = False
    return redirect('providers:index')    

