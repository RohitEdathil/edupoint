from django.contrib import admin
from .models import Classroom,Review,User,StudentSheet,Recovery,Notification,Feedback
# Register your models here.
admin.site.register(Notification)
admin.site.register(Classroom)
admin.site.register(Review)
admin.site.register(User)
admin.site.register(StudentSheet)
admin.site.register(Recovery)
admin.site.register(Feedback)