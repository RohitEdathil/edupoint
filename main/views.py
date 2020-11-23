from django.shortcuts import render
from .models import User,StudentSheet,Classroom,Review,Recovery,Notification,Feedback
import argon2 
from django.http import HttpResponseRedirect as redirect, HttpResponseForbidden as denied
import random
from .CoRE import CORE
from .forms import Classroom_form,ImageForm
from statistics import mean
from threading import Timer
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .portal import register_classroom_timing,update_classroom_timing,delete_classroom_timing,Started
import string,smtplib, ssl



a = argon2.PasswordHasher()
# Create your views here.
def autodelete(code):
    obj = Recovery.objects.get(code=code)
    obj.delete()

def randomString(stringLength):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

def my_time_clean(data):
    data = list(data)
    if data[1]==':':
        data.insert(0,'0')
    if data[-4]=='a':
        data=data[:5]
        if data[0]=="1" and data[1]=='2':
            data[0]='0'
            data[1]='0'
    elif data[-4]=='p':
        HH=int(data[0]+data[1])
        if not HH==12:
            HH+=12
        data[0]=str(HH)[0]
        data[1]=str(HH)[1]
        data=data[:5]
    info = ''.join(data)    
    return info

def random_col(sequence):
    color_pool=['#0d4e4e','#f06204','#1f5718','#4d1236','#f80000d3','#f8df00d3','#000000bd']
    bg_colors=[]
    bg_colors.extend(color_pool)
    while len(sequence)>len(bg_colors):
        bg_colors.append(random.choice(color_pool))
    random.shuffle(bg_colors)
    return bg_colors

def cur_user(data):
    return data.session.get('user')    

def home(request):
    if request.session.get('user')==None:
        username = request.POST.get("username")
        password = request.POST.get("password")
        error=""
        if ((username!=None) or (password!=None)):
            try:
                usr = User.objects.get(username = username)
                if a.verify(usr.password,password):
                    request.session['user']=usr
                    token = randomString(50)
                    usr.token=token
                    usr.save()
                    error=''
                    homepage = render(request,'home.html',
                                  {'user':request.session['user']})
                    homepage.set_cookie('portal_token',token)              
                    return homepage 
                else:
                    error="The password is wrong"
            except Exception as e:
                error="The Username or Password is Wrong"
    
        return render(request,"login.html",{
                    "error":error})
    else:
        usr=request.session['user']
        notifs = Notification.objects.filter(user = usr)
        return render(request,'home.html',{'user':usr,'notifs':notifs})
    
def signup(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    email = request.POST.get("email")
    confirm_pass = request.POST.get("confirm_pass")
    if password==None:
        return signup_rend('',request)
   
    else:   
        
        try:
            User.objects.get(username = username)
            return signup_rend("Username already taken",request)
        except:
            if password!=confirm_pass:
                return signup_rend('Passwords are not mutually matching',request)
            elif len(password)<8:
                return signup_rend('The password must contain atleast 8 chatacters ',request)
            elif password.isalpha():
                return signup_rend('Password must contain atleast one number,one letter and \
                            one special character',request)
            elif password.isalnum():
                return signup_rend('Password must contain atleast one number,one letter and \
                            one special character',request) 
            elif ("@" not in email) or ("." not in email):
                return signup_rend('Please enter a valid email-id',request)
            else:    
                User.objects.create(username=username,password= a.hash(password),email=email)
                usr=User.objects.get(username=username)
                request.session['user']=usr
                response = render(request,'home.html',{'user':request.session['user']})
                token = randomString(50)
                response.set_cookie('portal_token',token)
                return response
    
def signup_rend(error,request):
    return render(request,'signup.html',{"error":error})

def logout(request):
    try:
        usr = cur_user(request)
        usr.token = ''
        usr.save()
        request.session.pop('user') 
    except Exception as e:
        print('Error in logout Mechanism:' + e)
        
    response = redirect('/')
    response.set_cookie('portal_token','')
    return response

def classes(request):
    classes = StudentSheet.objects.filter(student=request.session.get('user'))
    output=zip(classes,random_col(classes))
    return render(request,'classes.html',{'user':cur_user(request),'output':output})

def add_class(request):
    keywords = request.GET.get('keyword')
    if keywords!=None:
        data_pool=[]
        all_classrooms=Classroom.objects.all()
        for a_class in all_classrooms:
            class_data=[]
            class_data.extend(a_class.title.lower().split())
            class_data.extend(a_class.description.lower().split())
            class_data.extend(a_class.owner.username.lower().split())
            class_data.append(str(a_class.fee))
            class_data.append(str(a_class.start_time))
            class_data.append(str(a_class.end_time))
            data_pool.append(class_data)
        search_engine = CORE(list(all_classrooms),data_pool)
        error=''
        results=search_engine.match(keywords.lower().split(),sort=True)
        if len(results)==0:
           error='No results found'
        output=zip(results,random_col(results))
        return render(request,'add_class.html',
                                     {'user':request.session['user'],
                                        'output':output,'error':error})                                
    else:
        return render(request,'add_class.html',
                                     {'user':request.session['user']})     

def my_classrooms(request):
    classes = Classroom.objects.filter(owner=request.session.get('user'))
    output=zip(classes,random_col(classes))
    return render(request,'my_classrooms.html',{'user':cur_user(request),'output':output})   

def payments(request):
    return render(request,'payments.html',{'user':cur_user(request)})    

def create_class(request):
    form = Classroom_form(request.POST or None)
    if form.is_valid():
        form.save()
        obj = Classroom.objects.all().order_by('-id')[0]
        register_classroom_timing(obj)
        return success(request)        

    else:    
        return render(request,'create_class.html',{'user':cur_user(request),'form':form})  

def success(request):
    return render(request,'success.html',{'user':cur_user(request)})                                           

def view_classroom(request,id):
    classroom = Classroom.objects.get(id=id)
    reviews = Review.objects.filter(reviewed=classroom)
    students = []
    post = request.POST.copy()
    rating_list=[]
    for review in reviews:
        rating_list.append(review.rating)
    for record in StudentSheet.objects.filter(classroom=classroom):
        students.append(record.student)
    nos = len(students)
    days=[]
    classroom.start_time=str(classroom.start_time)
    classroom.end_time=str(classroom.end_time)
    status = str(classroom.running)
    
    if status=='1' and cur_user(request)==classroom.owner:
        status = 'Start'
    elif status=='2' and cur_user(request) in students:
        status='Enter'    
    else:
        status=''
    if cur_user(request)==classroom.owner:
        action='Manage'
    elif cur_user(request) in students:
        action='Joined'   
    else:
        action='Join'     
    if classroom.sunday:
        days.append('Sunday')
    if classroom.monday:
        days.append('Monday')
    if classroom.tuesday:
       days.append('Tuesday')
    if classroom.wednesday:
       days.append('Wednesday')
    if classroom.thursday:
       days.append('Thursday')
    if classroom.friday:
       days.append('Friday')
    if classroom.saturday:
       days.append('Saturday')
    if post.get('review')!='' and post.get('review')!=None:
        try:
            Review.objects.get(review=post.get('review'))
        except:
            Review.objects.create(review=post.get('review'),
            rating=int(post.get('rating')),
            reviewed=classroom,
            reviewer=cur_user(request))
    if post.get('comment_id',None):
        try:
            r = Review.objects.get(id=post.get('comment_id'))   
            r.delete()
        except:
            pass 
    try:
        mean_rating=round(mean(rating_list),1)
    except:
        mean_rating=0
    reviews = Review.objects.filter(reviewed=classroom)                
    return render(request,'view_classroom.html',{
        'class':classroom,'reviews':reviews,'days':days,'user':cur_user(request),
        'nos':nos,'action':action,'avg_rating':mean_rating,'status':status
    })

def Remove(request,id):
    record=StudentSheet.objects.filter(classroom=Classroom.objects.get(id=id))
    record = record.get(student=cur_user(request))
    record.delete()
    return redirect('/classroom/'+str(id)) 

def Join(request,id):
    user = cur_user(request)
    classroom = Classroom.objects.get(id=id)
    StudentSheet.objects.create(student=user,classroom=classroom)
    return redirect('/classroom/'+str(id))

def Manage(request,id):
    classroom = Classroom.objects.get(id=id)  
    if classroom.owner == cur_user(request):
        post = request.POST.copy()
        try:
            post['start_time']=my_time_clean(post['start_time'])
            post['end_time']=my_time_clean(post['end_time'])
        except:
            pass    
        form = Classroom_form(post or None)
        if not form.is_valid():
            sunday=''
            monday=''
            tuesday=''
            wednesday=''
            thursday=''
            friday=''
            saturday=''
            if classroom.sunday:
                sunday ="checked"
            if classroom.monday:
                monday="checked"
            if classroom.tuesday:
                tuesday="checked"
            if classroom.wednesday:
                wednesday="checked"
            if classroom.thursday:
                thursday="checked"
            if classroom.friday:
                friday="checked"
            if classroom.saturday:
                saturday="checked"    
            return render(request,'edit_class.html',{
                'user':cur_user(request),'class':classroom,
                'sunday':sunday,
            'monday':monday,
            'tuesday':tuesday,
            'wednesday':wednesday,
            'thursday':thursday,
            'friday':friday,
            'saturday':saturday,
            'form':form
            })
        else:
            days=['sunday','monday','tuesday','wednesday','thursday','friday','saturday']
            for day in days:
                if post.get(day)=='on':
                    post[day]=True
                else:
                    post[day]=False    
            classroom.title=post.get('title')
            classroom.description=post.get('description')
            classroom.start_time=post.get('start_time')
            classroom.end_time=post.get('end_time')
            classroom.fee=post.get('fee')
            classroom.sunday=post['sunday']        
            classroom.monday=post['monday']
            classroom.tuesday=post['tuesday']
            classroom.wednesnday=post['wednesday']
            classroom.thurssunday=post['thursday']
            classroom.friday=post['friday']
            classroom.saturday=post['saturday']
            classroom.save()
            update_classroom_timing(classroom)
            return redirect('/classroom/'+str(id))    
    else:
        return denied("<h1 style='color:red'>Access Denied, You can't edit a class that isn't yours :(</h1>") 

def confirm_delete(request,id):
    return render(request,'confirm_delete.html',{'user':cur_user(request),'id':id})

def confirm_delete_no(request,id):
    return redirect('/classroom/'+str(id))

def confirm_delete_yes(request,id):
    classroom=Classroom.objects.get(id=id)
    classroom.delete()
    delete_classroom_timing(classroom)
    return redirect('/my_classrooms')

def forgot_password(request):
    username=request.POST.get('username')
    if username==None:
        return render(request,'forgot_password.html',{})    
    else:
        try:
            user=User.objects.get(username=username)
            key = randomString(50)
            Recovery.objects.create(code=key,key=user.username)
            global auto_delete_timer
            auto_delete_timer=Timer(450.0,autodelete,args=(key,))
            auto_delete_timer.start()
            sender_email = "edupointceo@gmail.com"
            receiver_email = user.email
            password = 'access@123'
            message = MIMEMultipart("alternative")
            message["Subject"] = "Recovery mail for your EduPoint account."
            message["From"] = sender_email
            message["To"] = receiver_email
            html = '''\
            <html>
            <body>
                <p>Hi,<br>
                <a href="http://localhost:8000/check/'''+ key +'''">Click me</a> 
                to reset your password.(Link expires in 15 mins.)
                </p>
            </body>
            </html>
            '''
            part2 = MIMEText(html, "html")
            message.attach(part2)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )
            return render(request,'forgot_password.html',{'verified':'true'})
        except Exception as e:
            print("Error in Email Mechanism:" + e)
            return render(request,'forgot_password.html',{'error':'Invalid Username'}) 

def check(request,key):
    try:
        record=Recovery.objects.get(code=key)
        user=User.objects.get(username=record.key)
        global auto_delete_timer
        auto_delete_timer.cancel()
        record.delete()
        request.session['user']=user
        return redirect('/change_password')  
    except:
        return denied('Access Denied')    

def change_password(request):
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')
    if password!=None:
        if password!=confirm_password:
                return render(request,'change_password.html',{'error':'Passwords are not mutually matching','user':cur_user(request)})
        elif len(password)<8:
            return render(request,'change_password.html',{'error':'The password must contain atleast 8 chatacters ','user':cur_user(request)})
        elif password.isalpha():
            return render(request,'change_password.html',{'error':'Password must contain atleast one number,one letter and \
                        one special character','user':cur_user(request)})
        elif password.isalnum():
            return render(request,'change_password.html',{'error':'Password must contain atleast one number,one letter and \
                        one special character','user':cur_user(request)}) 
        else:
            user=cur_user(request)
            user.password=a.hash(password)
            user.save()
            return success(request)                

    else:    
        return render(request,'change_password.html',{'user':cur_user(request)})   

def Start(request,id):
    classroom = Classroom.objects.get(id=id)
    usr=cur_user(request)
    if usr==classroom.owner and not classroom.running==0:
        Started(classroom)
        classroom.running = 2
        classroom.save()
        return render(request,'Streamer.html',{'user':usr,
        'class':classroom})
    else:
        return denied("<h1 style='color:red'>Access Denied :(</h1>")    

def Enter(request,id):
    classroom = Classroom.objects.get(id=id)
    usr=cur_user(request)
    students=[]
    if usr.balance < classroom.fee:
        return denied("<h1 style='color:red'>Insufficient Balance In your account :( </h1> <a href='/payments'>Click here to go to payment page</a>")
    else:    
        for record in StudentSheet.objects.filter(classroom=classroom):
            students.append(record.student)
        if usr in students and classroom.running==2:
            return render(request,'Viewer.html',{'user':usr,
            'class':classroom})
        else:
            return denied("<h1 style='color:red'>Access Denied :( </h1>")   

def feedback(request):
    feedback = request.POST.get('feedback')
    if feedback!=None and feedback!='':
        Feedback.objects.create(feedback=feedback,user=cur_user(request))
        return success(request)
    else:
        print('New feedback recieved!!!')    
        return render(request,'feedback.html',{'user':cur_user(request)})

def report(request):
    report = request.POST.get('feedback')
    if report!=None and report!='':
        Feedback.objects.create(feedback=report,user=cur_user(request))
        return success(request)
    else:
        print('New Complaint recieved!!!')    
        return render(request,'report.html',{'user':cur_user(request)})


def about(request):
    return render(request,'about.html',{'user':cur_user(request)})
    
def propic(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            m = User.objects.get(id=cur_user(request).id)
            m.propic = form.cleaned_data['image']
            m.save()
            return home(request)
    return render(request,'propic.html',{'user':cur_user(request)})