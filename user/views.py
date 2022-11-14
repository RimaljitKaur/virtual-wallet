from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from datetime import date

# Create your views here.

def login_view(request):
    if(request.method=='POST'):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect(home_view)
    return render(request,'login.html')


def signup_view(request):
    if(request.method=='POST'):
        username = request.POST.get("username")
        password = request.POST.get("password")
        usertype = request.POST.get("usertype")
        if(usertype=='premium'):
            wallet_balance = 2500
        else:
            wallet_balance = 1000

        user = User.objects.create_user(username=username,password=password)
        user_type = UserType(
                user_id = user,
                user_name = username,
                user_type = usertype,
                user_balance = wallet_balance
        )
        user_type.save()
        current_user = UserType.objects.get(user_name=user)
        trasaction = Trasaction(
            user_name = current_user,
            date = date.today(),
            amount = wallet_balance,
            request_type = 'Credit',
            balance = wallet_balance,
            remarks = f'{wallet_balance} Rs. get as a {usertype} user'
        )
        trasaction.save()
    return render(request,'signup.html')

@login_required(login_url='login_view')
def home_view(request):
    return render(request,'home.html')

@login_required(login_url='login_view')
def logout_view(request):
    logout(request)
    return redirect(login_view)

@login_required(login_url='login_view')
def wallet_view(request):
    user = UserType.objects.get(user_name=request.user)
    query_set = Trasaction.objects.filter(user_name=user.user_name)
    return render(request, 'wallet.html',{'qs': query_set[::-1],'balance':user.user_balance})

@login_required(login_url='login_view')
def send_view(request):
    if(request.method=='POST'):
        user_name = request.POST.get('username')
        amount = int(request.POST.get('amount'))
        current_user = UserType.objects.get(user_name=request.user)
        requested_user = UserType.objects.get(user_name=user_name)
        if current_user:
                balance = current_user.user_balance
        if requested_user:
                requested_user_balance = requested_user.user_balance
                requested_username = requested_user.user_name

        if(balance>amount):
                new_balance = balance - amount 
                req_user_balance = requested_user_balance + amount
                UserType.objects.filter(user_name=request.user).update(user_balance=new_balance)
                UserType.objects.filter(user_name=user_name).update(user_balance=req_user_balance)
                messages.info(request,'Money Sent.')

                transaction = Trasaction(
                    user_name = current_user,
                    date = date.today(),
                    amount = amount,
                    request_type = 'Debit',
                    balance = new_balance,
                    remarks = f'{amount} Rs. send to {requested_username}'
                )
                transaction.save()
                transaction = Trasaction(
                    user_name = requested_user,
                    date = date.today(),
                    amount = amount,
                    request_type = 'Credit',
                    balance = req_user_balance,
                    remarks = f'{amount} Rs. received from {current_user.user_name}'
                )
                transaction.save()
                if(requested_user.user_type=='premium'):
                    new_amount = ((amount*1)/100)
                    transaction = Trasaction(
                        user_name = requested_user,
                        date = date.today(),
                        amount = new_amount,
                        request_type = 'Debit',
                        balance = req_user_balance-new_amount,
                        remarks = f'charges for receiveing Rs.{amount} from {current_user.user_name}'
                    )
                    transaction.save()
                    UserType.objects.filter(user_name=requested_username).update(user_balance=req_user_balance-new_amount)
                else:
                    new_amount = ((amount*3)/100)
                    transaction = Trasaction(
                        user_name = requested_user,
                        date = date.today(),
                        amount = new_amount,
                        request_type = 'Debit',
                        balance = req_user_balance-new_amount,
                        remarks = f'charges for receiveing Rs.{amount} from {current_user.user_name}'
                        )
                    transaction.save()
                    UserType.objects.filter(user_name=requested_username).update(user_balance=req_user_balance-new_amount)

                if(current_user.user_type=='premium'):
                    new_amount = ((amount*3)/100)
                    transaction = Trasaction(
                        user_name = current_user,
                        date = date.today(),
                        amount = new_amount,
                        request_type = 'Debit',
                        balance = new_balance-new_amount,
                        remarks = f'charges for sending Rs.{amount} to  {requested_username}'
                    )
                    transaction.save()
                    UserType.objects.filter(user_name=request.user).update(user_balance=new_balance-new_amount)
                else:
                    new_amount = ((amount*5)/100)
                    transaction = Trasaction(
                        user_name = current_user,
                        date = date.today(),
                        amount = new_amount,
                        request_type = 'Debit',
                        balance = new_balance-new_amount,
                        remarks = f'charges for sending Rs.{amount} to {requested_username}'
                        )
                    transaction.save()
                    UserType.objects.filter(user_name=request.user).update(user_balance=new_balance-new_amount)
        else:
            messages.info(request,'You Dont have sufficient amount.')
        
    return render(request,'send.html')

@login_required(login_url='login_view')
def receive_view(request):
    if(request.method=='POST'):
        user_name = request.POST.get('username')
        amount = int(request.POST.get('amount'))

        to_user = UserType.objects.get(user_name=user_name)

        user_request = Request(
            user_name = to_user,
            date = date.today(),
            amount = amount,
            requested_by = request.user,
            status = 'N.A.'
        )
        user_request.save()
        messages.info(request,'Request Sent.')
    return render(request,'receive.html')

@login_required(login_url='login_view')
def requests_view(request):
    if(request.method=='POST'):
        action = request.POST.get('action')
        req_id = request.POST.get('reqid')
        if action=='accepted':
            Request.objects.filter(req_id=req_id).update(action='N.A.',status='accepted')
            user_id = Request.objects.get(req_id=req_id)
            user_name = user_id.user_name
            amount = int(user_id.amount)
            current_user = UserType.objects.get(user_name=user_name)
            requested_user = UserType.objects.get(user_name=user_id.requested_by)
            if current_user:
                    balance = current_user.user_balance
            if requested_user:
                    requested_user_balance = requested_user.user_balance
                    requested_username = requested_user.user_name

            if(balance>amount):
                    new_balance = balance - amount 
                    req_user_balance = requested_user_balance + amount
                    UserType.objects.filter(user_name=request.user).update(user_balance=new_balance)
                    UserType.objects.filter(user_name=user_name).update(user_balance=req_user_balance)
                    messages.info(request,'Money Sent.')

                    transaction = Trasaction(
                        user_name = current_user,
                        date = date.today(),
                        amount = amount,
                        request_type = 'Debit',
                        balance = new_balance,
                        remarks = f'{amount} Rs. send to {requested_username}'
                    )
                    transaction.save()
                    transaction = Trasaction(
                        user_name = requested_user,
                        date = date.today(),
                        amount = amount,
                        request_type = 'Credit',
                        balance = req_user_balance,
                        remarks = f'{amount} Rs. received from {current_user.user_name}'
                    )
                    transaction.save()
                    if(requested_user.user_type=='premium'):
                        new_amount = ((amount*1)/100)
                        transaction = Trasaction(
                            user_name = requested_user,
                            date = date.today(),
                            amount = new_amount,
                            request_type = 'Debit',
                            balance = req_user_balance-new_amount,
                            remarks = f'charges for receiveing Rs.{amount} from {current_user.user_name}'
                        )
                        transaction.save()
                        UserType.objects.filter(user_name=requested_username).update(user_balance=req_user_balance-new_amount)
                    else:
                        new_amount = ((amount*3)/100)
                        transaction = Trasaction(
                            user_name = requested_user,
                            date = date.today(),
                            amount = new_amount,
                            request_type = 'Debit',
                            balance = req_user_balance-new_amount,
                            remarks = f'charges for receiveing Rs.{amount} from {current_user.user_name}'
                            )
                        transaction.save()
                        UserType.objects.filter(user_name=requested_username).update(user_balance=req_user_balance-new_amount)

                    if(current_user.user_type=='premium'):
                        new_amount = ((amount*3)/100)
                        transaction = Trasaction(
                            user_name = current_user,
                            date = date.today(),
                            amount = new_amount,
                            request_type = 'Debit',
                            balance = new_balance-new_amount,
                            remarks = f'charges for sending Rs.{amount} to  {requested_username}'
                        )
                        transaction.save()
                        UserType.objects.filter(user_name=request.user).update(user_balance=new_balance-new_amount)
                    else:
                        new_amount = ((amount*5)/100)
                        transaction = Trasaction(
                            user_name = current_user,
                            date = date.today(),
                            amount = new_amount,
                            request_type = 'Debit',
                            balance = new_balance-new_amount,
                            remarks = f'charges for sending Rs.{amount} to {requested_username}'
                            )
                        transaction.save()
                        UserType.objects.filter(user_name=request.user).update(user_balance=new_balance-new_amount)
            else:
                messages.info(request,'You Dont have sufficient amount.')
            return redirect(home_view)
        elif action=='denied':
            Request.objects.filter(req_id=req_id).update(action='N.A.',status='denied')
            return redirect(home_view)
        else:
            user = UserType.objects.get(user_name=request.user)
            query_set = Request.objects.filter(user_name=user.user_name)
            return render(request, 'requests.html',{'qs': query_set[::-1]})
    user = UserType.objects.get(user_name=request.user)
    query_set = Request.objects.filter(user_name=user.user_name)
    return render(request, 'requests.html',{'qs': query_set[::-1]})
