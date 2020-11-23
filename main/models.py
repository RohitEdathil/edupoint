from django.db import models
# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    token = models.CharField(max_length=50,default='')
    balance = models.DecimalField(decimal_places=2,max_digits=20,default=0)
    propic = models.ImageField(upload_to = 'propics/', default = 'media/propics/propic.png')
    

class Classroom(models.Model):
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(max_length = 1000)
    start_time = models.TimeField()
    end_time = models.TimeField()
    fee = models.DecimalField(decimal_places=2,max_digits=20)
    sunday = models.BooleanField()
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    running = models.IntegerField(default=0)

    
class StudentSheet(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    classroom = models.ForeignKey("Classroom",on_delete=models.CASCADE)
    
class Review(models.Model):
    reviewer = models.ForeignKey(User,on_delete=models.CASCADE)
    reviewed = models.ForeignKey(Classroom,on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.IntegerField()

class Recovery(models.Model):
    code = models.CharField(max_length=50)
    key = models.CharField(max_length=50)    

class Notification(models.Model):
    note = models.CharField(max_length=100)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom,on_delete=models.CASCADE)    

class Feedback(models.Model):
    feedback = models.TextField()
    user = models.ForeignKey(User,on_delete=models.CASCADE)   


