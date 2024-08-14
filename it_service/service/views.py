from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .models import Service, Subscription
from .forms import ServiceForm, SubscriptionForm , UserRegistrationForm
import razorpay
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt



def index(request):
    active_services = Service.objects.filter(active=True)
    return render(request,'index.html',{'active_services': active_services})


#  working fine
@login_required
def home(request):
    
    active_services = Service.objects.filter(active=True)
    inactive_services = Service.objects.filter(active=False)
    return render(request, 'home.html', {'active_services': active_services, 'inactive_services': inactive_services})

# working fine
@login_required
def create_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ServiceForm()
    return render(request, 'create_service.html', {'form': form})



@login_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'create_service.html', {'form': form, 'service': service})

# working fine
@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        service.delete()
        return redirect('home')
    return render(request, 'delete_service.html', {'service': service})

# working fine
def toggle_active(request, id):
    service = get_object_or_404(Service, id=id)
    if request.user.is_authenticated:
        service.active = not service.active
        service.save()
    return redirect('home')


# def register(request):
#     if request.method == "POST":
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password1']) # [password1] is field
#             user.save()
#             login(request,user)
#             return redirect('tweet_list')
#     else:
#         form = UserRegistrationForm()
#     return render(request,'registration/register.html',{'form':form})

# for register with otp 

def generate_otp():
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=6))

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            otp = generate_otp()
            # Save OTP and user info temporarily
            request.session['otp'] = otp
            request.session['user_info'] = {
                'username': user.username,
                'email': user.email,
                'password': form.cleaned_data['password1']
            }
            # Send OTP to user email
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return redirect('otp_verification')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def otp_verification(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        if otp == request.session.get('otp'):
            user_info = request.session.get('user_info')
            user = User.objects.create_user(
                username=user_info['username'],
                email=user_info['email'],
                password=user_info['password']
            )
            login(request, user)
            # Clear session data
            request.session.pop('otp', None)
            request.session.pop('user_info', None)
            return redirect('home')
        else:
            return render(request, 'registration/otp_verification.html', {'error': 'Invalid OTP'})
    return render(request, 'registration/otp_verification.html')


#  ###################################################

# Subscription and payment 

@login_required
def subscribe(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.service = service
            subscription.price = service.total_price  # Use the property to calculate total price
            subscription.payment_status = 'Pending'
            subscription.save()
            
            client = razorpay.Client(auth=("rzp_test_e664V0FP0zQy7N", "QdnuRxUHrPGeiJc9lDTXYPO7"))
            payment = client.order.create({
                'amount': int(subscription.price * 100),  # Amount in paise
                'currency': 'INR',
                'payment_capture': '1'
            })

            # Save Razorpay order ID in the subscription model
            subscription.transaction_details = payment['id']
            subscription.save()

            # Redirect to payment page
            return redirect('payment_page', payment_id=payment['id'])
    else:
        form = SubscriptionForm()

    return render(request, 'subscribe.html', {'form': form, 'service': service})



@login_required
def payment_page(request, payment_id):
    subscription = get_object_or_404(Subscription, transaction_details=payment_id)
    service = subscription.service

    # Pass Razorpay order details to the template
    return render(request, 'payment_page.html', {
        'payment': {
            'id': payment_id,
            'amount': int(subscription.price * 100),
        },
        'subscription': subscription,
        'service': service,
        'razorpay_key': "rzp_test_e664V0FP0zQy7N"
    })

@csrf_exempt

def payment_callback(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        subscription = get_object_or_404(Subscription, transaction_details=order_id)

        client = razorpay.Client(auth=("rzp_test_e664V0FP0zQy7N", "QdnuRxUHrPGeiJc9lDTXYPO7"))
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            subscription.payment_status = 'Success'
            subscription.transaction_details += f"\nPayment ID: {payment_id}"
            subscription.save()
            return redirect('home')  # Or any success page
        except razorpay.errors.SignatureVerificationError:
            subscription.payment_status = 'Failed'
            subscription.save()
            return render(request, 'payment_failed.html', {'subscription': subscription})
