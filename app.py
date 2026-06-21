from flask import Flask, render_template, request, jsonify, session,redirect, url_for
from db import db,cursor
import os
import qrcode
import time
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = "vms_secret_key"
#UPLOAD_PHOTO = "uploads/photos"
#UPLOAD_ID = "uploads/idproofs"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.config['UPLOAD_PHOTO'] = os.path.join(BASE_DIR, 'static/uploads/photos')
app.config['UPLOAD_ID'] = os.path.join(BASE_DIR, 'static/uploads/idproofs')



# ---------------------------
# LOGIN PAGE
# ---------------------------
@app.route('/')
def home():
    return render_template('login.html')
@app.route('/approval')
def approval():

    cursor.execute("""
        SELECT COUNT(*) AS pending
        FROM Visitors
        WHERE Status='Pending'
    """)
    pending = cursor.fetchone()['pending']

    cursor.execute("""
        SELECT COUNT(*) AS approved
        FROM Visitors
        WHERE Status='Approved'
    """)
    approved = cursor.fetchone()['approved']

    cursor.execute("""
        SELECT COUNT(*) AS rejected
        FROM Visitors
        WHERE Status='Rejected'
    """)
    rejected = cursor.fetchone()['rejected']

    cursor.execute("""
        SELECT *
        FROM Visitors
        ORDER BY VisitorID DESC
    """)
    visitors = cursor.fetchall()

    return render_template(
        'Approval.html',
        visitors=visitors,
        pending=pending,
        approved=approved,
        rejected=rejected
    )


@app.route('/generate-pass', methods=['POST'])
@app.route('/generate-pass', methods=['POST'])
def generate_pass():

    visitor_name = request.form['visitor_name']
    employee_name = request.form['employee_name']
    visit_date = request.form['visit_date']

    cursor.execute("""
        SELECT * FROM Visitors
        WHERE Name=%s
        ORDER BY VisitorID DESC
        LIMIT 1
    """, (visitor_name,))

    visitor = cursor.fetchone()

    if not visitor:
        return redirect('/qrpass')

    qr_data = f"VMS-{visitor['VisitorID']}"

    qr = qrcode.make(qr_data)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    qr_folder = os.path.join(BASE_DIR, "static", "qr")
    os.makedirs(qr_folder, exist_ok=True)

    qr_path = os.path.join(
        qr_folder,
        f"visitor_{visitor['VisitorID']}.png"
    )

    qr.save(qr_path)

    return render_template(
        "QRPass.html",
        visitor=visitor,
        employee_name=employee_name,
        qr_image=f"qr/visitor_{visitor['VisitorID']}.png"
    )
@app.route('/checkin/<int:visitor_id>')
def checkin(visitor_id):

    cursor.execute("""
        UPDATE Visitors
        SET CheckInStatus=%s
        WHERE VisitorID=%s
    """, ("Checked In", visitor_id))

    db.commit()

    return redirect('/checkinout')
@app.route('/checkout/<int:visitor_id>')
def checkout(visitor_id):

    cursor.execute("""
        UPDATE Visitors
        SET CheckInStatus=%s
        WHERE VisitorID=%s
    """, ("Checked Out", visitor_id))

    db.commit()

    return redirect('/checkinout')
@app.route('/approve/<int:id>')
def approve_visitor(id):
    cursor.execute(
        "UPDATE Visitors SET Status='Approved' WHERE VisitorID=%s",
        (id,)
    )
    db.commit()
    return redirect('/approval')
@app.route('/checkinout')
def checkinout():

    cursor.execute("""
        SELECT *
        FROM Visitors
        WHERE Status='Approved'
    """)
    visitors = cursor.fetchall()

    # Checked In
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Visitors
        WHERE CheckInStatus='Checked In'
    """)
    checked_in = cursor.fetchone()['total']

    # Checked Out
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Visitors
        WHERE CheckInStatus='Checked Out'
    """)
    checked_out = cursor.fetchone()['total']

    # Currently Inside
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Visitors
        WHERE CheckInStatus='Checked In'
    """)
    inside = cursor.fetchone()['total']

    # Pending Check-Out
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Visitors
        WHERE CheckInStatus='Checked In'
    """)
    pending_checkout = cursor.fetchone()['total']

    return render_template(
        'CheckInOut.html',
        visitors=visitors,
        checked_in=checked_in,
        checked_out=checked_out,
        inside=inside,
        pending_checkout=pending_checkout
    )
@app.route('/reject/<int:id>')
def reject_visitor(id):
    cursor.execute(
        "UPDATE Visitors SET Status='Rejected' WHERE VisitorID=%s",
        (id,)
    )
    db.commit()
    return redirect('/approval')
@app.route('/scan', methods=['POST'])
def scan_qr():
    qr_data = request.form['qr_data']
    return qr_data
@app.route('/report')
def report():

    cursor.execute("""
        SELECT COUNT(*) AS daily
        FROM Visitors
        WHERE DATE(VisitDate)=CURDATE()
    """)
    daily = cursor.fetchone()["daily"]

    cursor.execute("""
        SELECT COUNT(*) AS weekly
        FROM Visitors
        WHERE YEARWEEK(VisitDate,1)=YEARWEEK(CURDATE(),1)
    """)
    weekly = cursor.fetchone()["weekly"]

    cursor.execute("""
        SELECT COUNT(*) AS monthly
        FROM Visitors
        WHERE MONTH(VisitDate)=MONTH(CURDATE())
        AND YEAR(VisitDate)=YEAR(CURDATE())
    """)
    monthly = cursor.fetchone()["monthly"]

    cursor.execute("""
        SELECT COUNT(*) AS pending
        FROM Visitors
        WHERE Status='Pending'
    """)
    pending = cursor.fetchone()["pending"]

    return render_template(
        'Report.html',
        daily=daily,
        weekly=weekly,
        monthly=monthly,
        pending=pending
    )


import qrcode

@app.route('/qrpass')
def qrpass():
    return render_template(
        "QRPass.html",
        visitor=None,
        qr_image=None,
        employee_name=""
    )

    visitor = cursor.fetchone()

    if not visitor:
        return render_template(
            "QRPass.html",
            visitor=None,
            qr_image=""
        )

    qr_data = f"""
    Visitor ID: {visitor['VisitorID']}
    Name: {visitor['Name']}
    Company: {visitor['Company']}
    Date: {visitor['VisitDate']}
    """

    qr = qrcode.make(qr_data)

    qr_folder = os.path.join("static", "qr")

    if not os.path.exists(qr_folder):
        os.makedirs(qr_folder)

    qr_path = os.path.join(qr_folder, "visitor_pass.png")

    qr.save(qr_path)

    return render_template(
        "QRPass.html",
        visitor=visitor,
        qr_image="qr/visitor_pass.png"
    )

@app.route('/admin-dashboard')
def admin_dashboard():

    cursor.execute("SELECT COUNT(*) AS total FROM Visitors")
    total_visitors = cursor.fetchone()["total"]

    cursor.execute("""
    SELECT COUNT(*) AS today
    FROM Visitors
    WHERE DATE(VisitDate)=CURDATE()
    """)
    today_visitors = cursor.fetchone()["today"]
    
    cursor.execute("""
    SELECT COUNT(*) AS pending
    FROM Visitors
    WHERE Status='Pending'
    """)
    pending_visitors = cursor.fetchone()["pending"]

    return render_template(
        "admin_dashboard.html",
        total_visitors=total_visitors,
        today_visitors=today_visitors,
        pending_visitors=pending_visitors
    )


# ---------------------------
# LOGIN API
# ---------------------------
@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    print("Login API called")
    print(data)

    email = data.get('email')
    password = data.get('password')

    cursor.execute(
        "SELECT * FROM Users WHERE Email=%s AND Password=%s",
        (email, password)
    )

    user = cursor.fetchone()

    print(user)

    if user:
        role = user["Role"]  # adjust if needed

        # 🔥 IMPORTANT FIX (SESSION SET)
        #session['role'] = role
        #session['email'] = email
        session["user_id"] = user["UserID"]
        session["role"] = role
        return jsonify({
            "message": "Login Successful",
            "role": role
            }),200


# ---------------------------
# LOGOUT
# ---------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ---------------------------
# ADMIN DASHBOARD
# ---------------------------
@app.route('/admin')
def admin():
    if session.get('role') != "Admin":
        return "Unauthorized Access", 403

    cursor.execute("SELECT COUNT(*) AS total FROM Visitors")
    total_visitors = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS today
        FROM Visitors
        WHERE DATE(VisitDate) = CURDATE()
    """)
    today_visitors = cursor.fetchone()["today"]

    cursor.execute("""
        SELECT COUNT(*) AS pending
        FROM Visitors
        WHERE Status = 'Pending'
    """)
    pending_visitors = cursor.fetchone()["pending"]

    return render_template(
        'admin.html',
        total_visitors=total_visitors,
        today_visitors=today_visitors,
        pending_visitors=pending_visitors
    )

# ---------------------------
# RECEPTION DASHBOARD
# ---------------------------
@app.route('/reception')
def reception():
    cursor.execute("SELECT COUNT(*) AS total FROM Visitors")
    total_visitors = cursor.fetchone()["total"]

    cursor.execute("""
    SELECT COUNT(*) AS today
    FROM Visitors
    WHERE DATE(VisitDate) = CURDATE()
    """)
    today_visitors = cursor.fetchone()["today"]
    cursor.execute("""
    SELECT COUNT(*) AS pending
    FROM Visitors
    WHERE Status='Pending'
    """)
    pending_visitors = cursor.fetchone()["pending"]

    # Temporary values until Check-In/Check-Out module is built
    checkedin_visitors = 0
    checkedout_visitors = 0

    return render_template(
        'reception.html',
        total_visitors=today_visitors,   # because card says "Total Visitors Today"
        checkedin_visitors=checkedin_visitors,
        checkedout_visitors=checkedout_visitors,
        pending_visitors=pending_visitors
    )


# ---------------------------
# EMPLOYEE DASHBOARD
# ---------------------------
@app.route('/employee')
def employee():
    if session.get('role') != "Employee":
        return "Unauthorized Access", 403

    return render_template('employee.html')


# ---------------------------
# VISITOR REGISTRATION
# ---------------------------
@app.route('/register-visitor', methods=['POST'])
def register_visitor():
    
    print(request.form)
    print("REQUEST RECEIVED")
    name = request.form.get('name')
    mobile = request.form.get('mobile')
    email = request.form.get('email')
    company = request.form.get('company')
    print("FORM:", request.form)
    print("FILES:", request.files)

    # Uploaded files
    photo = request.files.get('photo')
    id_proof = request.files.get('id_proof')
    query = """
    INSERT INTO Visitors (Name, Mobile, Email, Company)
    VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (name, mobile, email, company))
        db.commit()
        print("DATA INSERTED SUCCESSFULLY")
    except Exception as e:
        print("DATABASE ERROR:", e)

    photo_name = ""
    id_name = ""

    if photo:
        photo_name = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_PHOTO'], photo_name))

    if id_proof:
        id_name = secure_filename(id_proof.filename)
        id_proof.save(os.path.join(app.config['UPLOAD_ID'], id_name))
    print("PHOTO:", photo)
    print("ID:", id_proof)
    return jsonify({
        "message": "Visitor Registered Successfully",
        "photo": photo_name,
        "id_proof": id_name
    })
@app.route('/register')
def register():
    return render_template('Registration.html')


@app.route('/dashboard')
def dashboard():

    cursor.execute("SELECT COUNT(*) AS total FROM Visitors")
    total_visitors = cursor.fetchone()["total"]
    cursor.execute("""
    SELECT COUNT(*) AS today
    FROM Visitors
    WHERE DATE(VisitDate)=CURDATE()
    """)
    today_visitors = cursor.fetchone()["today"]
    cursor.execute("""
    SELECT COUNT(*) AS pending
    FROM Visitors
    WHERE Status='Pending'
    """)
    pending_visitors = cursor.fetchone()["pending"]

    checkedin_visitors = 0
    checkedout_visitors = 0

    return render_template(
        'reception.html',
        total_visitors=today_visitors,
        checkedin_visitors=checkedin_visitors,
        checkedout_visitors=checkedout_visitors,
        pending_visitors=pending_visitors
    )
# ---------------------------
# RUN APP
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)