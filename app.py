from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
import smtplib
from email.message import EmailMessage
from config import EMAIL, EMAIL_PASSWORD, ADMIN_USERNAME, ADMIN_PASSWORD

app = Flask(__name__)
app.secret_key = 'your_secret_key'

complaints = []

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL, EMAIL_PASSWORD)
        smtp.send_message(msg)

# 🔥 New Intro Route
@app.route('/')
def intro():
    return render_template('intro.html')

# Complaint form moved to /home
@app.route('/home', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'gender': request.form['gender'],
            'age': int(request.form['age']),
            'category': request.form['category'],
            'description': request.form['description'],
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        complaints.append(data)

        body = f"""
        New Complaint Received:
        Name: {data['name']}
        Gender: {data['gender']}
        Age: {data['age']}
        Category: {data['category']}
        Time: {data['time']}
        Description: {data['description']}
        """
        send_email("New Complaint Registered", body)

        return render_template('index.html', message="Complaint submitted successfully!")
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if (request.form['username'] == ADMIN_USERNAME and 
            request.form['password'] == ADMIN_PASSWORD):
            session['admin'] = True
            return redirect('/dashboard')
        else:
            return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin'))

    sorted_complaints = sorted(complaints, key=lambda x: x['age'])
    return render_template('dashboard.html', complaints=sorted_complaints)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

