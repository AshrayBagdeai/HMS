from flask import Flask,render_template,redirect,url_for,request,flash,g,session
from datetime import datetime, timedelta
import sqlite3
DATABASE="hms.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory= sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

def init_db():
    db=g.db
    with open('schema.sql') as f:
        db.executescript(f.read())
    return 



app=Flask(__name__)
app.secret_key='12345'


@app.route("/",methods=['GET','POST'])
def land(): 
    get_db()
    init_db()
    return render_template('land.html')

@app.route("/login",methods=['GET','POST'])
def home():
    conn = sqlite3.connect(DATABASE)
    curr=conn.cursor()
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        mode = request.form.get("role")
        user=""
        pwd=""
        if mode == "admin":
            if username == "admin123" and password == "admin123":
                session['user']=username
                session['role']=mode
                return redirect(url_for('admin_panel'))
            flash("Invalid username or password! try again.","danger")
            return render_template('home.html')
        if mode == "patient":
            user=curr.execute('''Select * from patients where username= ?''',(username,)).fetchone()
            pwd=curr.execute('''Select password from patients where username= ?''',(username,)).fetchone()
            if user and password==pwd[0]:
                session['user']=username
                session['role']=mode
                return redirect(url_for('patient_panel'))
            elif not user:
                flash("Invalid username. Try creating a account first!", "danger") 
                return render_template('home.html')
            elif password!=pwd[0]:
                flash("Incorrect password! Try again.","danger")
                return render_template('home.html')
        if mode == "doctor":
            user=curr.execute('''Select * from doctor where username= ?''',(username,)).fetchone()
            pwd=curr.execute('''Select password from doctor where username= ?''',(username,)).fetchone()
            if user and password==pwd[0]:
                session['user']=username
                session['role']=mode
                return redirect(url_for('doctor_panel'))
            elif not user:
                flash("Invalid username. Try creating a account first!", "danger") 
                return render_template('home.html')
            elif password!=pwd[0]:
                flash("Incorrect password! Try again.","danger")
                return render_template('home.html')
        curr.close()
        conn.close()
      
    return render_template('home.html')


@app.route("/signup.html",methods=['GET','POST'])
def signup():
    conn = sqlite3.connect(DATABASE)
    curr=conn.cursor()
    if request.method=='POST':
        name = request.form.get('name')
        dob_str = request.form.get('DOB')
        gender = request.form.get('gender')
        email = request.form.get('email')
        pnumber = request.form.get('number')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        city=request.form.get('city')
        age=''
        if dob_str:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
            today = datetime.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        existing_user=""
        existing_email=""
        if (role=="patient"):
            existing_user = curr.execute('''Select * from patients where username= ? ''',(username,)).fetchone()
            existing_email = curr.execute('''Select * from patients where email= ? ''',(email,)).fetchone()
            existing_number = curr.execute('''Select * from patients where pnum= ? ''',(pnumber,)).fetchone()
            if existing_user :
               flash("Username already exists. Please choose another.", "danger")
               return redirect(url_for('signup'))
            if existing_email :
               flash("It looks like this email is already registered.\n Try logging in instead, or use a different email to create a new account.", "danger")
               return redirect(url_for('signup'))
            if existing_number:
                flash("It looks like this phone number is already registered.\n Try logging in instead, or use a different phone number to create a new account.", "danger")
                return redirect(url_for('signup'))
            curr.execute('''INSERT INTO patients (name,dob,gender,email,pnum,username,password,age,city) VALUES (?,?,?,?,?,?,?,?,?)''',(name,dob,gender,email,pnumber,username,password,age,city))
            conn.commit()
        if (role=="doctor"):
            existing_user = curr.execute('''Select * from doctor where username= ? ''',(username,)).fetchone()
            existing_email = curr.execute('''Select * from doctor where email= ? ''',(email,)).fetchone()
            existing_number = curr.execute('''Select * from doctor where pnum= ? ''',(pnumber,)).fetchone()
            if existing_user :
               flash("Username already exists. Please choose another.", "danger")
               return redirect(url_for('signup'))
            if existing_email :
               flash("It looks like this email is already registered.\n Try logging in instead, or use a different email to create a new account.", "danger")
               return redirect(url_for('signup'))
            if existing_number:
                flash("It looks like this phone number is already registered.\n Try logging in instead, or use a different phone number to create a new account.", "danger")
                return redirect(url_for('signup'))
            curr.execute('''INSERT INTO doctor (name,dob,gender,email,pnum,username,password,age,timing,Hid) VALUES (?,?,?,?,?,?,?,?,'NONE',0)''',(name,dob,gender,email,pnumber,username,password,age))
            conn.commit()
        curr.close()
        conn.close()
        return redirect(url_for('/success'))
    
    return render_template('signup.html')

@app.route("/success",methods=['POST','GET'])
def success():
     flash("Account Created Successfully!","info")
     return redirect(url_for('home'))


@app.route("/admin", methods=['GET','POST'])
def admin_panel():
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))
    search_query = request.args.get('search', '').strip().lower()
    if search_query:
        like_term=f"%{search_query}%"
        patients=curr.execute('''Select * from patients where Lower(Name) like ? or Pid like ? or pnum like ? or age like ?''',(like_term,like_term,like_term,like_term)).fetchall()
        curr.close()
        conn.close()
        return render_template("admin.html",patients=patients)
    patients=curr.execute('''SELECT * FROM patients''').fetchall()
    curr.close()
    conn.close()
    return render_template("admin.html",patients=patients)

@app.route("/admin/doctors",methods=['GET','POST'])
def admin_doctor():
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))
    search_query=request.args.get('search','').strip().lower()
    if search_query:
        like_term:f"%{search_query}%"
    doctors=curr.execute('''SELECT * FROM doctor''').fetchall()
    curr.close()
    conn.close()
    return render_template("admin_doctor.html",doctors=doctors)

@app.route('/admin/patient/Profile/<int:Pid>',methods=['POST','GET'])
def view_profile(Pid):
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))
    query='''select p.Pid,p.name,p.age,p.gender,p.dob,p.city,p.pnum,p.username,p.password from patients as p where Pid like ?'''
    data=curr.execute(query,(Pid,)).fetchone()
    query='''select p.name,p.age,d.specifications,d.name,h.hname,a.time,a.date,a.status,a.Aid from appointments as a , patients as p,doctor as d,hospitals as h where a.Pid like ? and a.Pid=p.Pid and a.Did=d.Did and a.Hid=h.Hid'''
    appointments=curr.execute(query,(Pid,)).fetchall()

    if request.method=='POST':
        value1=request.form.get('button1')
        value2=request.form.get('button2')
        print(value2)
        if value1!=None:
            return render_template('delete_profile.html',data=data,role=value1)
        elif value2!=None:
            return render_template('delete_profile.html',data=[int(value2),data[1]],role='Appointment')
        elif data:  
            return render_template("Patient_Profile.html",ROLE="Patient",data=data ,appointments=appointments)
        
    return render_template("Patient_Profile.html",ROLE='Patient',data=["No Data Available"])

@app.route('/admin/doctor/Profile/<int:Did>',methods=['POST','GET'])
def doctor_profile(Did):
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))
    query='''select d.Did,d.name,d.specifications,d.age,d.email,d.pnum from doctor as d where Did like ?'''
    data=curr.execute(query,(Did,)).fetchone()
    query='''select p.name,p.age,d.specifications,d.name,h.hname,a.time,a.date,a.status,a.Aid from appointments as a , patients as p,doctor as d,hospitals as h where a.Did like ? and a.Pid=p.Pid and a.Did=d.Did and a.Hid=h.Hid'''
    appointments=curr.execute(query,(Did,)).fetchall()
    
    if request.method=='POST':
        value1=request.form.get('button1')
        value2=request.form.get('button2')
        print(value2)
        if value1!=None:
            return render_template('delete_profile.html',data=data,role='Doctor')
        elif value2!=None:
            return render_template('delete_profile.html',data=[int(value2),data[1]],role='Appointment')
        elif data:  
            return render_template("Patient_Profile.html",ROLE="Doctor",data=data ,appointments=appointments)
        
    return render_template("Patient_Profile.html",ROLE='Doctor',data=["No Data Available"])

@app.route('/admin/hospital/Profile/<int:Hid>',methods=['POST','GET'])
def hospital_profile(Hid):
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))
    query='''select h.Hid,h.hname,h.address,h.city,h.contact_number from hospitals as h where Hid like ?'''
    data=curr.execute(query,(Hid,)).fetchone()
    query='''select p.name,p.age,d.specifications,d.name,h.hname,a.time,a.date,a.status,a.Aid from appointments as a , patients as p,doctor as d,hospitals as h where a.Hid like ? and a.Pid=p.Pid and a.Did=d.Did and a.Hid=h.Hid'''
    appointments=curr.execute(query,(Hid,)).fetchall()
    if request.method=='POST':
        value1=request.form.get('button1')
        value2=request.form.get('button2')
        print(value2)
        if value1!=None:
            return render_template('delete_profile.html',data=data,role='Hospital')
        elif value2!=None:
            return render_template('delete_profile.html',data=[int(value2),data[1]],role='Appointment')
        elif data:  
            return render_template("Patient_Profile.html",ROLE="Hospital",data=data ,appointments=appointments)
        
    return render_template("Patient_Profile.html",ROLE='Hospital',data=["No Data Available"])


@app.route('/admin/delete/<role>/<int:Pid>', methods=['GET', 'POST'])
def delete_profile(role, Pid):
    if 'user' not in session:
        return redirect(url_for('home'))

    conn = sqlite3.connect(DATABASE)
    curr = conn.cursor()
    if role.lower() == 'patient':
        query = 'DELETE FROM patients WHERE Pid = ?'
    elif role.lower() == 'doctor':
        query = 'DELETE FROM doctor WHERE Did = ?'
    elif role.lower() == 'hospital':
        query = 'DELETE FROM hospitals WHERE Hid = ?'
    elif role.lower()=='appointment':
        query='''DELETE FROM appointments WHERE Aid = ?'''
    else:
        flash("Invalid role specified.", "danger")
        return redirect(url_for('admin_panel'))

    try:
        curr.execute(query, (Pid,))
        conn.commit()
        flash(f"{role}'s profile deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting {role} profile: {str(e)}", "danger")
    finally:
        curr.close()
        conn.close()
    if session.get('role')=='admin':  
        return  redirect(url_for('admin_panel'))
    elif session.get('role')=='doctor':
        return redirect(url_for('doctor_panel'))
    else:
        return redirect(url_for('patient_panel'))



@app.route("/admin/hospitals",methods=['GET','POST'])
def admin_hopital():
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('home'))
    hospitals=curr.execute('''SELECT * FROM hospitals''').fetchall()
    curr.close()
    conn.close()
    return render_template("admin_hospital.html",hospitals=hospitals)


@app.route("/patient", methods=['GET','POST'])
def patient_panel():
    if 'user' not in session or session.get('role')!='patient':
        return redirect(url_for('home'))
    
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    
    patient_id = curr.execute("SELECT Pid FROM patients WHERE username=?", (session['user'],)).fetchone()[0]
    
    appointments = curr.execute('''
        SELECT d.name, a.date, a.time, a.status ,a.Aid
        FROM appointments as a 
        JOIN doctor as d ON a.Did = d.Did 
        WHERE a.Pid = ? AND a.status = 'pending'
    ''', (patient_id,)).fetchall()
    
    curr.close()
    conn.close()
    
    return render_template("/patient.html", appointments=appointments)

@app.route("/appointment/details/<int:Aid>", methods=['GET','POST'])
def appointment_details(Aid):
    if 'user' not in session or (session.get('role')!='patient' and session.get('role')!='doctor'):
        return redirect(url_for('home'))
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()      
    appointment=curr.execute('''select d.name, p.name, a.date, a.status, a.prescription, a.diagnosis , h.hname from appointments as a , doctor as d , patients as p , hospitals as h where p.Pid=a.Pid and d.Did=a.Did and h.Hid=a.Hid and  a.Aid=?''',(Aid,)).fetchone()
    curr.close()
    conn.close()
    return render_template("appointment_details.html", appointment=appointment)

@app.route("/patient/history", methods=['GET','POST'])
def patient_history():
    if 'user' not in session or session.get('role')!='patient':
        return redirect(url_for('home'))
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    appointments=curr.execute('''select d.name,p.name,a.date,a.status,a.Aid from appointments as a ,patients as p,doctor as d where d.Did=a.Did and a.Pid=p.Pid and a.Pid=(select Pid from patients where username=?)''',(session['user'],)).fetchall()
    curr.close()
    conn.close()
    return render_template("appointment_history.html", appointments=appointments)



@app.route("/patient/book", methods=['GET'])
def book_appointment():
    
    if 'user' not in session or session.get('role')!='patient':
        return redirect(url_for('home'))
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    doctors=curr.execute('''SELECT Did, name, specifications,available FROM doctor''').fetchall()
    curr.close()
    conn.close()
    return render_template("patient_doctors.html", doctors=doctors)



@app.route("/patient/book/<int:Did>", methods=['GET', 'POST'])
def book_appointment_alt(Did):
    if 'user' not in session or session.get('role')!='patient':
        return redirect(url_for('home'))
    
    conn = sqlite3.connect(DATABASE)
    curr = conn.cursor()
    doctor = curr.execute('''SELECT Did, name, specifications, timing FROM doctor where Did=?''', (Did,)).fetchone()
    
    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')

        if time:
            patient_id = curr.execute("SELECT Pid FROM patients WHERE username=?", (session['user'],)).fetchone()[0]
            hospital_id = curr.execute("SELECT Hid FROM doctor WHERE Did=?", (Did,)).fetchone()[0]
            curr.execute("INSERT INTO appointments (Pid, Did, date, time, status,Hid) VALUES (?, ?, ?, ?, 'pending', ?)",
                         (patient_id, Did, date, time, hospital_id))
            conn.commit()
            flash("Appointment booked successfully!", "success")
            return redirect(url_for('patient_panel'))
        
        elif date:
            timing = doctor[3]
            if timing == 'NONE':
                available_slots = []
                flash("Doctor has not set their availability timing yet.", "warning")
            else:
                start_time_str, end_time_str = timing.split(' - ')
                start_time = datetime.strptime(start_time_str, '%H:%M')
                end_time = datetime.strptime(end_time_str, '%H:%M')

                time_slots = []
                current_time = start_time
                while current_time < end_time:
                    time_slots.append(current_time.strftime('%H:%M'))
                    current_time = current_time + timedelta(hours=1)
                
                booked_appointments = curr.execute("SELECT time FROM appointments WHERE Did=? AND date=?", (Did, date)).fetchall()
                booked_times = [appointment[0] for appointment in booked_appointments]

                available_slots = [slot for slot in time_slots if slot not in booked_times]
            
            conn.close()
            return render_template("book_appointment_alt.html", doctor=doctor, date=date, time_slots=available_slots)

    conn.close()
    return render_template("book_appointment_alt.html", doctor=doctor, date=None, time_slots=None)

@app.route("/patient/profile/view", methods=['GET'])
def patient_profile_view():
    if 'user' not in session or session.get('role')!='patient':
        return redirect(url_for('home'))
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    patient=curr.execute('''select * from patients where username=?''',(session['user'],)).fetchone()
    curr.close()
    conn.close()
    return render_template("patient_profile_view.html", patient=patient)

@app.route("/patient/profile/edit", methods=['GET', 'POST'])
def patient_profile_edit():
    if 'user' not in session or session.get('role')!='patient':
        return redirect(url_for('home'))
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    patient=curr.execute('''select * from patients where username=?''',(session['user'],)).fetchone()
    if request.method == 'POST':
        name = request.form.get('name')
        dob_str = request.form.get('DOB')
        gender = request.form.get('gender')
        email = request.form.get('email')
        pnumber = request.form.get('number')
        username = request.form.get('username')
        password = request.form.get('password')
        city=request.form.get('city')
        age=''
        if dob_str:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
            today = datetime.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        curr.execute('''UPDATE patients SET name=?, dob=?, gender=?, email=?, pnum=?, username=?, password=?, age=?, city=? WHERE username=?''', (name, dob, gender, email, pnumber, username, password, age, city, session['user']))
        conn.commit()
        session['user'] = username
        flash("Profile updated successfully!", "success")
        return redirect(url_for('patient_profile'))
    curr.close()
    conn.close()
    return render_template("patient_profile_edit.html", patient=patient)



@app.route("/doctor", methods=['GET','POST'])
def doctor_panel():
    if 'user' not in session or session.get('role')!='doctor':
        return redirect(url_for('home'))
    
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    data=curr.execute('''select p.name,p.age,a.status,a.date,a.time,a.Aid,d.specifications from appointments as a ,doctor as d ,patients as p where d.username = ? and d.Did=a.Did and a.Pid=p.Pid''',(session['user'],)).fetchall()
    temp=curr.execute('''select d.specifications from doctor as d where d.username = ?''',(session['user'],)).fetchone()
    availability=curr.execute('''select d.available from doctor as d where d.username = ?''',(session['user'],)).fetchone()
    conn.commit()
    curr.close()
    conn.close()
    count=0
    for x in data:
        if x[2]=='pending':
            count=1
    
    if temp[0]==None:
            return redirect(url_for('profile'))
    return render_template("/doctor.html",appointments=data,availability=availability[0],count=count)

@app.route('/toggle_availability', methods=['POST'])
def toggle_availability():
    status = request.form['status']
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    if status=='no':
        curr.execute('''update doctor set available='no' where username=?''',(session['user'],))
    else:
        curr.execute('''update doctor set available='yes' where username=?''',(session['user'],))
         
    conn.commit()
    curr.close()    
    conn.close()
    
    return redirect(url_for('doctor_panel'))

@app.route("/doctor/history", methods=['GET','POST'])
def doctor_history():
    if 'user' not in session or session.get('role')!='doctor':
        return redirect(url_for('home'))
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    data=curr.execute('''select p.name,p.age,a.status,a.date,a.time,a.Aid from appointments as a ,doctor as d ,patients as p where d.username = ? and d.Did=a.Did and a.Pid=p.Pid''',(session['user'],)).fetchall()
    curr.close()
    conn.close()
    return render_template("/doctor_history.html",appointments=data)

@app.route("/profile", methods=['GET','POST'])
def profile():
    if 'user' not in session or session.get('role')!='doctor':
        return redirect(url_for('home'))
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    query='''select hname from hospitals'''
    data=curr.execute(query).fetchall()
    curr.close()
    conn.close()
    print(data)
    specifications=request.form.get('specifications')
    hospital =request.form.get('hospital')
    timing1=request.form.get('timing')
    timing2=request.form.get('timing2')
    timing=str(timing1)+" - "+str(timing2)
    if request.method=='POST':
        conn=sqlite3.connect(DATABASE)
        curr=conn.cursor()
        curr.execute('''update doctor set specifications=?, timing=?,Hid=(select Hid from hospitals where hname=?) where username=?''',(specifications,timing,hospital,session['user'],))
        conn.commit()
        curr.close()
        conn.close()
        flash("Profile Updated Successfully!","info")
        return redirect(url_for('doctor_panel'))
    return render_template("/profile.html", data=data)

@app.route("/cancel/appointment/<Aid>", methods=['GET','POST'])
def cancel_appointment(Aid):
    if 'user' not in session:
        return redirect(url_for('home'))
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    curr.execute('''update appointments set status='cancelled' where Aid=?''',(Aid,))
    conn.commit()
    curr.close()
    conn.close()
    flash("Appointment Cancelled Successfully!","info")
    if session.get('role')=='patient':
        return redirect(url_for('patient_panel'))
    else:
        return redirect(url_for('doctor_panel'))

@app.route("/doctor/ongoing/<Aid>", methods=['GET','POST'])
def ongoing_appointments(Aid):
    if 'user' not in session or session.get('role')!='doctor':
        return redirect(url_for('home'))
    conn=sqlite3.connect(DATABASE)
    curr=conn.cursor()
    data=curr.execute('''select p.name,p.age,p.gender,a.time from appointments as a ,doctor as d ,patients as p where d.username = ? and d.Did=a.Did and a.Pid=p.Pid and a.Aid=?''',(session['user'],Aid,)).fetchone()
    curr.close()
    conn.close()
    if request.method=='POST':
        prescription=request.form.get('prescription')
        diagnosis=request.form.get('diagnosis')
        conn=sqlite3.connect(DATABASE)
        curr=conn.cursor()
        curr.execute('''update appointments set status='completed', prescription=?, diagnosis=? where Aid=?''',(prescription, diagnosis, Aid,))
        conn.commit()
        curr.close()
        conn.close()
        flash("Appointment Confirmed!","info")
        return redirect(url_for('doctor_panel'))
    
    return render_template("/doctor_ongoing.html", data=data)


@app.route("/logout")
def logout():
    session.clear()  
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('home'))
if __name__ =='__main__':
    app.run(host='0.0.0.0',debug=True)
    