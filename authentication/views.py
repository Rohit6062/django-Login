from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from Login import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from .tokens import generate_token
from django.core.mail import EmailMessage,send_mail

# Create your views here.
def home(request):
    return render(request,'authentication/index.html')
def signup(request):
    if request.method == 'POST':
        usrname=request.POST['usrname']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        if User.objects.filter(username=usrname):
            messages.error(request,'This username is already in use, Please select another username!')
            return redirect('signup')
            
        if User.objects.filter(email=email):
            messages.error(request,'This email is already registered')
            return redirect('signup')

        if pass1 != pass2:
            messages.error(request,'Confirmation password does not match!!')
            return redirect('signup')
            

        myuser=User.objects.create_user(usrname,email,pass1)

        myuser.first_name=fname
        myuser.last_name=lname
        myuser.is_active=False
        myuser.save()

        messages.success(request,'Your account is succesfully created. We have sent you confirmation email, Please confirm it!')

        # Welcom Email

        subject = "welcome to Django LogIn!!"
        message = ' Hellow ' + myuser.first_name + '!! \n ' + 'welcome to My Site \n Thank you for visiting our website ! \n We have also sent you a confirmation email , please confirm your email address to activate your account. \n\n  THANK YOU \n Rohit Ranaware'
        from_email=settings.EMAIL_HOST
        to_list=[myuser.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True)

        # Email address Configeration email 
        current_site=get_current_site(request)
        email_subject= 'Confirmation email for @ My site- Django Login'
        message2=render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser)

        })
        Email=EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
            
        )
        Email.fail_silently=True
        Email.send()

        return redirect('signin')


    return render(request,'authentication/signup.html')
def signin(request):

    if request.method=='POST':
        username=request.POST['usrname']
        pass1 =request.POST['pass1']
        
        user=authenticate(username=username,password=pass1)
        
        if user is not None:
            login(request,user)
            fname=user.first_name
            return render(request,'authentication/index.html',{'fname':fname})
        else:
            messages.error(request,'Bad credentials')
            return redirect('home')



    return render(request,'authentication/signin.html')
def signout(request):
    logout(request)
    messages.success(request,'Logged out successfully')
    return redirect('home')

def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser= None
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active= True 
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request,'activation_failed.html')