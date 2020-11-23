import asyncio
import websockets
import json
import schedule
import time
import datetime
import threading
from .models import User,StudentSheet,Classroom,Review,Recovery,Notification
global active_users
active_users = {}
active_classes = {}

class ActiveClass(object):

    def __init__(self,id,unique_id=None):
        print('User: ',id,' started a class id=> ',unique_id)
        self.classroom = Classroom.objects.get(id=str(id))
        self.id = id
        self.peer_id = unique_id
        self.owner = active_users[str(Classroom.objects.get(id=str(id)).owner.id)]
        self.active_students = {}
        self.population = 0
        active_classes[id]=self

    async def add(self,id,websocket):
        self.active_students[id]=websocket
        self.population = len(self.active_students)
    async def broadcast(self,cmd,attrib):
        await self.owner.send(json.dumps([cmd,attrib]))
        for user in self.active_students.values():
            try:
                await user.send(json.dumps([cmd,attrib]))
            except Exception as e:
                print('Error in broadcasting: ',e) 
        
    async def update_population(self):
        await self.broadcast('population',str(self.population) + "/" +str(len(list(StudentSheet.objects.filter(classroom=self.classroom)))))
    


def validate(token,id):
    obj = User.objects.get(id=id)
    if obj.token==token:
        print('WebSocket user verified',id)
        return True
    else:
        return False

def alert(id):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(active_users[str(id)].send('alert'))
        print('Notification Broadcasted')
        
    except Exception as e:
        print('Error in sending notification: ',e)   

async def main(websocket,path):
    async for message in websocket:
        data = json.loads(message)
        id=data.get('id')
        cmd=data.get('cmd')
        attrib=data.get('attrib')
        token=data.get('token')
        attrib2 = data.get('attrib2')
        print('___WebSocket recieved a message___')
        print('Sent by:',id)
        print('Command:',cmd)
        print('Unique token: ',token)
        print('Primary message:',attrib)
        print('Secondary Message:',attrib2)
        if validate(token,id):
            active_users[id]=websocket
            print('Active Users: ',active_users.keys()) 
            if cmd=='logout':
                active_users.pop(id) 
            elif cmd=='del_notif':
                id = attrib
                notif=Notification.objects.get(id=id)
                notif.delete()
            elif cmd=='start_class':
                attrib = json.loads(attrib)
                active_class = ActiveClass(attrib['id'],attrib['peer_id'])
                active_classes[attrib['id']]=active_class
                await active_class.update_population()
            elif cmd=='enter_class':
                await active_classes[attrib].add(id,websocket)
                await active_classes[attrib].owner.send(json.dumps(['peer_id',attrib2]))
                await active_classes[attrib].update_population()
            elif cmd=='asked':
                await active_classes[attrib].broadcast('question',attrib2)   
            elif cmd=='img':
                await active_classes[attrib].broadcast('img',attrib2) 
            elif attrib!= None:
                await active_classes[attrib].broadcast(cmd,'')   
            


               
        else:
            websocket.send('invalid')        
            

def start_clockwork():
    print('Timer Running')
    while 1:
        schedule.run_pending()
        time.sleep(1)  
            


def Before5min(t):
    hour = t.hour
    minute = t.minute
    opt = datetime.datetime(2002,1,1,hour,minute)
    opt -= datetime.timedelta(minutes=5)
    return str(datetime.time(hour=opt.hour,minute=opt.minute))

def register_classroom_timing(obj):
    start_time = str(obj.start_time)
    end_time = str(obj.end_time)
    if obj.sunday:
        schedule.every().sunday.at(Before5min(obj.start_time)).do(notif5min,obj).tag(str(obj.id))
        schedule.every().sunday.at(start_time).do(class_start,obj).tag(str(obj.id))
        schedule.every().sunday.at(end_time).do(end_class,obj).tag(str(obj.id))
    if obj.monday:
        schedule.every().monday.at(Before5min(obj.start_time)).do(notif5min,obj).tag(str(obj.id))
        schedule.every().monday.at(start_time).do(class_start,obj).tag(str(obj.id))
        schedule.every().monday.at(end_time).do(end_class,obj).tag(str(obj.id))
    if obj.tuesday:
        schedule.every().tuesday.at(Before5min(obj.start_time)).do(notif5min,obj).tag(str(obj.id))
        schedule.every().tuesday.at(start_time).do(class_start,obj).tag(str(obj.id))
        schedule.every().tuesday.at(end_time).do(end_class,obj).tag(str(obj.id))
    if obj.wednesday:
        schedule.every().wednesday.at(Before5min(obj.start_time)).do(notif5min,obj).tag(str(obj.id))
        schedule.every().wednesday.at(start_time).do(class_start,obj).tag(str(obj.id))
        schedule.every().wednesday.at(end_time).do(end_class,obj).tag(str(obj.id))
    if obj.thursday:
        schedule.every().thursday.at(Before5min(obj.start_time)).do(notif5min,obj).tag(str(obj.id))
        schedule.every().thursday.at(start_time).do(class_start,obj).tag(str(obj.id))
        schedule.every().thursday.at(end_time).do(end_class,obj).tag(str(obj.id))
    if obj.friday:
        schedule.every().friday.at(Before5min(obj.start_time)).do(notif5min,obj).tag(str(obj.id))
        schedule.every().friday.at(start_time).do(class_start,obj).tag(str(obj.id))
        schedule.every().friday.at(end_time).do(end_class,obj).tag(str(obj.id))
    if obj.saturday:
        schedule.every().saturday.at(Before5min(obj.start_time)).do(notif5min,obj).tag(str(obj.id))
        schedule.every().saturday.at(start_time).do(class_start,obj).tag(str(obj.id))
        schedule.every().saturday.at(end_time).do(end_class,obj).tag(str(obj.id))
    

def update_classroom_timing(obj):
    delete_classroom_timing(obj)
    obj = Classroom.objects.get(id=obj.id)
    register_classroom_timing(obj)    

def delete_classroom_timing(obj):
    schedule.clear(str(obj.id))
    

def class_start(obj):
    print('Classroom ',obj.id,' is starting')
    alert(obj.owner.id)
    obj.running = 1
    obj.save() 
    Notification.objects.create(user = obj.owner,classroom=obj,\
    note='It is time for the Class '+ obj.title +' to be started.')

def Started(obj): 
    records = StudentSheet.objects.filter(classroom = obj)   
    for record in records:
        alert(record.student.id)
        Notification.objects.create(user = record.student,classroom=obj, \
        note='The Class '+ obj.title +' has started.')

def notif5min(obj):
    records = StudentSheet.objects.filter(classroom = obj)
    alert(obj.owner.id)
    Notification.objects.create(user = obj.owner,classroom=obj,\
    note='Your Class '+ obj.title +' will start in 5.')
    for record in records:
        alert(record.student.id)
        Notification.objects.create(user = record.student,classroom=obj,\
        note='The Class "'+ obj.title +'" will start in 5 minutes.')

def end_class(obj):
    classroom = active_classes[str(obj.id)]
    fee = obj.fee
    print('Class ',classroom,' Ended')
    owner_db = obj.owner
    total_fee = 0
    for key in classroom.active_students.keys():
        student = User.objects.get(id=int(key))
        Notification.objects.create(user = student,classroom=obj,\
        note='₹'+ str(fee) +' have been paid for the class '+ obj.title)
        student.balance-=fee
        student.save()
        total_fee+=fee
    owner_db.balance+=total_fee 
    Notification.objects.create(user = owner_db,classroom=obj,\
    note='₹'+ str(total_fee) +' have been credited to your account ')   
    owner_db.save()
    del active_classes[str(obj.id)]
    obj.running = 0
    obj.save()

server = websockets.server.Serve(main,host='localhost',port=8512)
asyncio.get_event_loop().run_until_complete(server)
print('WebSocket is live')
for classroom in Classroom.objects.all():
    register_classroom_timing(classroom)
threading.Thread(target=asyncio.get_event_loop().run_forever).start()    
threading.Thread(target=start_clockwork).start()


     
