from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from bills.views import  staff_member_required, reset_messages

def check_username(username,users_list):
    """
    check if username is available in user list
    """    
    for i in users_list:
        if username == i.username:
            return False
    return True

def check_email(email, users_list):
    """
    check if email is available in user list
    """
    for i in users_list:
        if email == i.email:
            return False
    return True

@staff_member_required
@login_required
def index(request):    
    request = reset_messages(request)
    users_list = User.objects.all()
    return render(request,'users/index.html',{
        'users_list' : users_list,
    })

@staff_member_required
@login_required
def singup(request):
    request = reset_messages(request)
    return render(request,'users/singup.html',{})

@staff_member_required
@login_required
def singup_next(request):
    users_list = User.objects.all()
    username = request.POST['username']
    username = username.lower()
    username_unique = check_username(username, users_list)
    email = request.POST['email']
    email_unique = check_email(email, users_list)
    password = request.POST['password']
    password_confirm = request.POST['confirm_password']
    
    if username_unique and email_unique and password == password_confirm:
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        is_staff = request.POST.get('is_staff',False)
        if is_staff == 'True':
            is_staff = True
        else:
            is_staff = False
        user = User.objects.create(username=username, 
                                   email=email, 
                                   password=password, 
                                   first_name=first_name,
                                   last_name=last_name,
                                   is_staff=is_staff,
                                   )
        user.set_password(password)
        user.save()   

        request.session['success_message'] = f'Usuario {username} creado correctamente'
        return redirect('users:index')
    elif not username_unique: 
        request.session['error_message'] = f'El username {username} no esta disponible'
        request.session['message_shown'] = False
        return redirect('users:singup')
    elif not email_unique: 
        request.session['error_message'] = f'El email {email} no esta disponible'
        request.session['message_shown'] = False
        return redirect('users:singup')
    else: 
        request.session['error_message'] = 'Las contraseñas no coinciden'
        request.session['message_shown'] = False
        return redirect('users:singup')

@login_required
def user_detail(request, user_id):
    request = reset_messages(request)
    user = User.objects.get(id=user_id)
    print(user.is_staff)
    return render(request, 'users/user_detail.html', {
        'user':user,
    })

def auth_login(request):
    if request.user.is_authenticated:
        return render(request, 'users/user_detail.html',{})
    else:            
        request = reset_messages(request)
        return render(request, 'users/login.html', {'message':'users'})

def auth_login_next(request):
    username = request.POST['username']
    username = username.lower()
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('bills:index')
    else:
        request.session['error_message'] = 'El usuario y la contraseña no coinciden'
        request.session['message_shown'] = False
        return redirect('users:mylogin')
        

def auth_logout(request):
    logout(request)
    request = reset_messages(request)
    return render(request, 'users/logout.html',{})

@staff_member_required
@login_required
def auth_reset_password(request, user_id):
    """
       Set new password 
       only admins can change a password from an admin or regular user
    """
    request = reset_messages(request)
    user = User.objects.get(id=user_id)
    return render(request, 'users/set_password.html',{'user':user})

@staff_member_required
@login_required
def auth_save_new_password(request, user_id):
    """
        Save change in new password
    """
    password = request.POST['admins_password']
    user = User.objects.get(id=user_id)

    #check admins password
    if not request.user.check_password(password):
        request.session['error_message'] = 'La contraseña no es correcta'
        request.session['message_shown'] = False
        return redirect('users:reset_password')
    else :
        new_password = request.POST['new_password']
        new_password2 = request.POST['new_password2']
        if new_password == new_password2:     
            user.set_password(new_password)
            user.save()
            request.session['success_message'] = 'Contraseña cambiada correctamente'
            request.session['message_shown'] = False
            return redirect('users:index')
        else:
            request.session['error_message'] = 'las contraseñas no coinciden'
            request.session['message_shown'] = False
            return redirect('users:reset_password')

@staff_member_required
@login_required
def update_user(request, user_id):
    request = reset_messages(request)
    user = User.objects.get(id=user_id)
    return render(request,'users/update_user.html',{'user':user})

@staff_member_required
@login_required
def update_user_save(request, user_id):
    users_list = User.objects.all().exclude(pk=user_id)
    new_username = request.POST['username']
    new_username = new_username.lower()
    username_unique = check_username(new_username, users_list)
    email = request.POST['email']
    email_unique = check_email(email, users_list)

   
    if username_unique and email_unique:
        user = User.objects.get(id=user_id)
        user.username = new_username
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.email = email
        is_staff = request.POST.get('is_staff',False)
        if is_staff == 'True':
            user.is_staff = True
        else:
            user.is_staff = False
        user.save()
        request.session['success_message'] = 'Cambios guardados satisfactoriamente'
        request.session['message_shown'] = False
        return redirect('users:update_user', user_id)
    elif not username_unique: 
        request.session['error_message'] = f'El username {new_username} no esta disponible'
        request.session['message_shown'] = False
        return redirect('users:update_user', user_id)
    elif not email_unique:
        request.session['error_message'] = f'El email {email} no esta disponible'
        request.session['message_shown'] = False
        return redirect('users:update_user', user_id)

@staff_member_required
@login_required
def delete_user(request, user_id):
    request = reset_messages(request)
    user = User.objects.get(pk=user_id)
    users_list = User.objects.all()
    
    return render(request, 'users/delete_user.html',{
        'user':user,
        'users_list': users_list
        })

@staff_member_required
@login_required
def delete_user_save(request, user_id):
    user = User.objects.get(pk=user_id)
    if user != request.user:
        user.delete()
        request.session['success_message'] = 'Usuario eliminado satisfactoriamente'
        request.session['message_shown'] = False        
        return redirect('users:index')
    else: 
        request.session['error_message'] = 'No se puede eliminar el usuario de esta sesion'
        request.session['message_shown'] = False        
        return redirect('users:index')
   

    
