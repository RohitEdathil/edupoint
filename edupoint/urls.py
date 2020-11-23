"""edupoint URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns,static
from .settings import MEDIA_URL,MEDIA_ROOT
from main.views import home,logout,classes,add_class,signup,my_classrooms,create_class,success,view_classroom,\
Remove,Join,Manage,confirm_delete,confirm_delete_no,confirm_delete_yes,forgot_password,check,change_password,\
Start,Enter,payments,feedback,about,report,propic

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home,name = 'home'),
    path('signup',signup,name = 'signup'),
    path('logout',logout),
    path('classes',classes),
    path('payments',payments),
    path('add_class',add_class),
    path('my_classrooms',my_classrooms),
    path('create_class',create_class),
    path('classroom/<int:id>',view_classroom),
    path('classroom/Joined/<int:id>',Remove),
    path('classroom/Join/<int:id>',Join),
    path('classroom/Manage/<int:id>',Manage),
    path('classroom/Delete/<int:id>',confirm_delete),
    path('classroom/Delete/<int:id>/no',confirm_delete_no),
    path('classroom/Delete/<int:id>/yes',confirm_delete_yes),
    path('forgot_password',forgot_password),
    path('check/<str:key>',check),
    path('change_password',change_password),
    path('Start/<int:id>',Start),
    path('Enter/<int:id>',Enter),
    path('feedback',feedback),
    path('about',about),
    path('report',report),  
    path('propic',propic)
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)