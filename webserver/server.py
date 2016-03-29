#!/usr/bin/env python2.7

import os
import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



DATABASEURI = "postgresql://tt2573:EDLGCH@w4111db.eastus.cloudapp.azure.com/tt2573"
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():

  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):

  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def index():
  
  cursor1 = g.conn.execute("select P.PID,P.name,P.email,P.address,P.type,S.school,S.major FROM Person P, Student S where P.type='student' and P.PID=S.PID")
  student = []
  for result in cursor1:
    student.append([str(x) for x in result])  
  cursor1.close()
  
  cursor2 = g.conn.execute("SELECT P.PID,P.name,P.email,P.address,P.type,E.job,E.rank FROM Person P, Employee E where P.type='employee' and P.PID=E.PID")
  employee= []
  for result in cursor2:
      employee.append([str(x) for x in result])
  cursor2.close()
  
  cursor3 = g.conn.execute("SELECT * FROM Company")
  company= []
  for result in cursor3:
      company.append([str(x) for x in result])
  cursor3.close() 
  
  return render_template("homepage.html", student=student, employee=employee, company=company)
  
  
@app.route('/student')
def gostudent():
  cursor= g.conn.execute("SELECT count(*) FROM Student")
  number=0
  for result in cursor:
      number=result[0]
  cursor.close()
  return render_template("student.html",number=number)

@app.route('/studentsignin', methods=['POST'])
def add():
  
  try:
    cursor = g.conn.execute("SELECT count(*) FROM Person")
    number=0
    for result in cursor:
      number=result[0]
    PID = number+1
    name = request.form['name']
    email = request.form['email']
    address = request.form['address']
    type = 'student' 
    major = request.form['major']
    school = request.form['school']
    if name != '':
      g.conn.execute("INSERT INTO Person VALUES (%s,%s,%s,%s,%s)", PID,name,email,address,type)
      g.conn.execute("insert into Student values (%s,%s,%s)",PID,major, school)  
    else:
      pass
  except:
    print("informal data format")
  return redirect('/student')

@app.route('/searchpersonbyname',methods=['GET'])
def search():
  name=request.args['name']
  if name !='':
    cursor=g.conn.execute("select * from Person where name= %s", name)
  
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
    for i in range(0,len(search_result)):  
      PID=int(search_result[i][0])
  
      if search_result[i][-1]=='student':
        cursor2=g.conn.execute("select * from Student where PID= %s", PID)
        for row in cursor2:
          search_result[i]=search_result[i]+[str(x) for x in row][1:]
      else:
        cursor2=g.conn.execute("select * from Employee where PID= %s", PID)
        for row in cursor2:
          search_result[i]=search_result[i]+[str(x) for x in row][1:]
  else:
    cursor=g.conn.execute("select * from Person")
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
  return render_template("result.html",search_result=search_result)
  

@app.route('/searchstudentbyschool',methods=['GET'])
def search2():
  school=request.args['school']
  if school !='':
    cursor=g.conn.execute("select P.PID,P.name,P.email,P.address,P.type,S.school,S.major from Person P, Student S where P.PID=S.PID and S.school= %s", school)
  
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  else:
    cursor=g.conn.execute("select P.PID,P.name,P.email,P.address,P.type,S.school,S.major from Person P, Student S where P.type='student' and P.PID = S.PID")
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
  return render_template("result.html",search_result=search_result)
  

@app.route('/searchstudentbymajor',methods=['GET'])
def search3():
  major=request.args['major']
  if major !='':
    cursor=g.conn.execute("select P.PID,P.name,P.email,P.address,P.type,S.school,S.major from Person P, Student S where P.PID=S.PID and S.major= %s", major)
  
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  else:
    cursor=g.conn.execute("select P.PID,P.name,P.email,P.address,P.type,S.school,S.major from Person P, Student S where P.type='student' and P.PID = S.PID")
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
  return render_template("result.html",search_result=search_result)
  

@app.route('/searchemployeebyjob',methods=['GET'])
def search4():
  job=request.args['job']
  if job !='':
    cursor=g.conn.execute("select P.PID,P.name,P.email,P.address,P.type,E.job,E.rank from Person P, Employee E where P.PID=E.PID and E.job= %s", job)
  
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  else:
    cursor=g.conn.execute("select P.PID,P.name,P.email,P.address,P.type,E.job,E.rank from Person P, Employee E where P.type='employee' and P.PID = E.PID")
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
  return render_template("result.html",search_result=search_result)



@app.route('/searchcompanybyname',methods=['GET'])
def search5():
  name=request.args['name']
  if name !='':
    cursor=g.conn.execute("select * from Company where name= %s", name)
  
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  else:
    cursor=g.conn.execute("select * from Company")
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
  return render_template("result.html",search_result=search_result)
  

@app.route('/searchpositionbycompany',methods=['GET'])
def search6():
  company=request.args['company']
  if company !='':
    cursor=g.conn.execute("select C.name, P2.POS_ID, P2.title,P2.payment, P2.address, P2.start_time, P2.duration from Company C, Post P1, Position P2 where C.name= %s and C.CID=P1.CID and P1.POS_ID=P2.POS_ID order by P2.POS_ID", company)
  
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  else:
    cursor=g.conn.execute("select C.name, P2.POS_ID, P2.title,P2.payment, P2.address, P2.start_time, P2.duration from Company C, Post P1, Position P2 where C.CID=P1.CID and P1.POS_ID=P2.POS_ID order by P2.POS_ID")
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
  return render_template("result.html",search_result=search_result)


@app.route('/searchsabytime',methods=['GET'])
def search7():
  starttime=request.args['starttime']
  #starttime=datetime.datetime.strptime(starttime,'%Y/%m/%d')
  endtime=request.args['endtime']
  #endtime=datetime.datetime.strptime(endtime,'%Y/%m/%d')
  if starttime !='' and endtime != '':
    cursor=g.conn.execute("select * from Social_activity where date(time) >= date(%s) and date(time) <= date(%s)", starttime,endtime)
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  elif starttime !='' and endtime == '':
    cursor=g.conn.execute("select * from Social_activity where date(time) >= date(%s)", starttime)
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])

  elif starttime =='' and endtime != '':
    cursor=g.conn.execute("select * from Social_activity where date(time) <= date(%s)", endtime)
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row]) 
  
  else:
    cursor=g.conn.execute("select * from Social_activity")
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row]) 
         
  
  return render_template("result.html",search_result=search_result)
  
  

@app.route('/searchinterviewbycompany',methods=['GET'])
def search8():
  company=request.args['company']
  if company !='':
    cursor=g.conn.execute("select C.name, I.IID, I.location, I.time from Company C, Host H, Interview I where C.name= %s and C.CID=H.CID and I.IID=H.IID order by I.IID", company)
  
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  else:
    cursor=g.conn.execute("select C.name, I.IID, I.location, I.time from Company C, Host H, Interview I where C.CID=H.CID and H.IID=I.IID order by I.IID")
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
  return render_template("result.html",search_result=search_result)
  
  

@app.route('/searchinterviewbytime',methods=['GET'])
def search9():
  starttime=request.args['starttime']
  #starttime=datetime.datetime.strptime(starttime,'%Y/%m/%d')
  endtime=request.args['endtime']
  #endtime=datetime.datetime.strptime(endtime,'%Y/%m/%d')
  if starttime !='' and endtime != '':
    cursor=g.conn.execute("select C.name, I.IID, I.location, I.time from Interview I, Company C, Host H where date(I.time) >= date(%s) and date(I.time) <= date(%s) and C.CID=H.CID and H.IID=I.IID order by date(I.time)", starttime,endtime)
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  elif starttime !='' and endtime == '':
    cursor=g.conn.execute("select C.name, I.IID, I.location, I.time from Interview I, Company C, Host H where date(I.time) >= date(%s) and C.CID=H.CID and H.IID=I.IID order by date(I.time)", starttime)
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])

  elif starttime =='' and endtime != '':
    cursor=g.conn.execute("select C.name, I.IID, I.location, I.time from Interview I, Company C, Host H where date(I.time) <= date(%s) and C.CID=H.CID and H.IID=I.IID order by date(I.time)", endtime)
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row]) 
  
  else:
    cursor=g.conn.execute("select C.name, I.IID, I.location, I.time from Interview I, Company C, Host H where C.CID=H.CID and H.IID=I.IID order by date(I.time)")
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row]) 
         
  
  return render_template("result.html",search_result=search_result)


@app.route('/searchemployeebycompany',methods=['GET'])
def search10():
  company=request.args['company']
  if company !='':
    cursor=g.conn.execute("select P.PID,P.name,P.email,P.address,P.type,E.job,E.rank, C.name from Person P, Employee E, Work_in W, Company C where C.name= %s and C.CID=W.CID and W.PID=P.PID and P.PID=E.PID", company)
  
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  else:
    cursor=g.conn.execute("select P.PID,P.name,P.email,P.address,P.type,E.job,E.rank, C.name from Person P, Employee E, Work_in W, Company C where C.CID=W.CID and W.PID=P.PID and P.PID=E.PID")
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
  return render_template("result.html",search_result=search_result)
  




@app.route('/studentapplyposition', methods=['POST'])
def add1():
  personid=request.form['personid']
  positionid=request.form['positionid']
  if personid != '' and positionid != '':
    g.conn.execute("INSERT INTO Apply VALUES (%s,%s)", positionid, personid)
  else:
    pass  
  return redirect('/student')  
  
  
@app.route('/studentsignforsa', methods=['POST'])
def add2():
  personid=request.form['personid']
  said=request.form['said']
  if personid != '' and said != '':
    g.conn.execute("INSERT INTO Attend VALUES (%s,%s)", said, personid)
  else:
    pass  
  return redirect('/student')  

@app.route('/studentparticipateinterview', methods=['POST'])
def add3():
  personid=request.form['personid']
  iid=request.form['iid']
  if personid != '' and iid != '':
    g.conn.execute("INSERT INTO Participate VALUES (%s,%s)", iid, personid)
  else:
    pass  
  return redirect('/student') 

#@app.route('/searchsabylocation',methods=['GET'])
#def search8():
#  location=request.args['location']
#  if location !='':
#    cursor=g.conn.execute("select * from Social_activity where location like  '%s%' ",location )
#    #select * from Social_activity where location like '%NY%'
#  
#    search_result=[]
#    for row in cursor:
#      search_result.append([str(x) for x in row])
#    
#  else:
#    cursor=g.conn.execute('select * from Social_activity')
#  
#    search_result=[]
#    for row in cursor:
#      search_result.append([str(x) for x in row])
#  return render_template("anotherfile.html",search_result=search_result)






@app.route('/employee')
def goemployee():
  cursor= g.conn.execute("SELECT count(*) FROM Employee")
  number=0
  for result in cursor:
      number=result[0]
  cursor.close()
  return render_template("employee.html",number=number)
  
  
@app.route('/employeesignin', methods=['POST'])
def add4():
  
  try:
    cursor = g.conn.execute("SELECT count(*) FROM Person")
    number=0
    for result in cursor:
      number=result[0]
    PID = number+1
    name = request.form['name']
    email = request.form['email']
    address = request.form['address']
    type = 'employee' 
    job = request.form['job']
    rank = request.form['rank']
    if name != '':
      g.conn.execute("INSERT INTO Person VALUES (%s,%s,%s,%s,%s)", PID,name,email,address,type)
      g.conn.execute("insert into Employee values (%s,%s,%s)",PID,job, rank)  
    else:
      pass
  except:
    print("informal data format")
  return redirect('/employee')


@app.route('/employeeholdsa', methods=['POST'])
def add5():
  
  try:
    cursor = g.conn.execute("SELECT count(*) FROM Social_activity")
    number=0
    for result in cursor:
      number=result[0]
    SAID = number+1
    personid = request.form['personid']
    time = request.form['time']
    location = request.form['location']
    description = request.form['description']
    if time != '' and location != '' and personid != '':
      g.conn.execute("INSERT INTO Social_activity VALUES (%s,%s,%s,%s)", SAID,time,location,description)
      g.conn.execute("insert into Hold values (%s,%s)",SAID, personid)  
    else:
      pass
  except:
    print("informal data format")
  return redirect('/employee')


@app.route('/checkwhoattendsa',methods=['GET'])
def search11():
  personid=request.args['personid']
  if personid !='':
    cursor=g.conn.execute("select P.PID, P.name, S.school, A.SAID from Hold H, Attend A, Student S, Person P where H.PID = %s and H.SAID=A.SAID and A.PID=S.PID and S.PID=P.PID ", personid)
  
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  else:
    return redirect('/employee')
  return render_template("result.html",search_result=search_result)


 
@app.route('/company')
def gocompany():
  cursor= g.conn.execute("SELECT count(*) FROM Company")
  number=0
  for result in cursor:
      number=result[0]
  cursor.close()
  return render_template("company.html",number=number)


@app.route('/companysignin', methods=['POST'])
def add6():
  
  try:
    cursor = g.conn.execute("SELECT count(*) FROM Company")
    number=0
    for result in cursor:
      number=result[0]
    CID = number+1
    name = request.form['name']
    size = request.form['size']
    field = request.form['field']
    address = request.form['address']

    if name != '':
      g.conn.execute("INSERT INTO Company VALUES (%s,%s,%s,%s,%s)", CID,name,size,field,address)
       
    else:
      pass
  except:
    print("informal data format")
  return redirect('/company')

 
@app.route('/companyhostinterview', methods=['POST'])
def add7():
  
  try:
    cursor = g.conn.execute("SELECT count(*) FROM Interview")
    number=0
    for result in cursor:
      number=result[0]
    IID = number+1
    cid = request.form['cid']
    time = request.form['time']
    location = request.form['location']

    if time != '' and location != '' and cid != '':
      g.conn.execute("INSERT INTO Interview VALUES (%s,%s,%s)", IID,location,time)
      g.conn.execute("insert into Host values (%s,%s)",IID, cid)  
    else:
      pass
  except:
    print("informal data format")
  return redirect('/company')
 
 
@app.route('/companypostposition', methods=['POST'])
def add8():
  
  try:
    cursor = g.conn.execute("SELECT count(*) FROM Position")
    number=0
    for result in cursor:
      number=result[0]
    posid = number+1
    cid = request.form['cid']
    payment = request.form['payment']
    address = request.form['address']
    starttime = request.form['starttime']
    duration = request.form['duration']
    title = request.form['title']
    
    if starttime != '' and address != '' and cid != '':
      g.conn.execute("INSERT INTO Position VALUES (%s,%s,%s,%s,%s,%s)", posid,title,payment,address,starttime,duration)
      g.conn.execute("insert into Post values (%s,%s)",posid, cid)  
    else:
      pass
  except:
    print("informal data format")
  return redirect('/company')


@app.route('/checkwhoattendinterview',methods=['GET'])
def search12():
  cid=request.args['cid']
  if cid !='':
    cursor=g.conn.execute("select P.PID, P.name, S.school, PA.IID from Host H, Participate PA, Student S, Person P where H.CID = %s and H.IID=PA.IID and PA.PID=S.PID and S.PID=P.PID ", cid)
  
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  else:
    return redirect('/company')
  return render_template("result.html",search_result=search_result)


@app.route('/checkwhoappliedposition',methods=['GET'])
def search13():
  cid=request.args['cid']
  if cid !='':
    cursor=g.conn.execute("select P.PID, P.name, S.school, A.POS_ID from Post PO, Apply A, Student S, Person P where PO.CID = %s and A.POS_ID=PO.POS_ID and A.PID=S.PID and S.PID=P.PID ", cid)
  
    search_result=[]
    for row in cursor:
      search_result.append([str(x) for x in row])
    
  else:
    return redirect('/company')
  return render_template("result.html",search_result=search_result)


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):


    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
  
  
