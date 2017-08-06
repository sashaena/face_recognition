from flask import Flask, session, render_template, request, redirect, url_for, escape, flash
import requests, os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'images'
ALLOWED_EXTENTIONS = set(['jpg', 'jpeg'])

# APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = os.urandom(24)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username             

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == "POST":
		payload = {'email':request.form['email'], 'password':request.form['password'], 'serial_number':'12345678910'}
		headers ={'X-ASORIBA-APP-SOURCE':'biometric'}
		url = "https://devapi.asoriba.com/api/v1.2/mobile/attendance/login/"
		r = requests.post(url, json=payload, headers=headers)
		response = r.json()
		print(r.status_code)
		print(response)
		# print(response['user']['username'])
		if (r.status_code == 200):
			username, auth_key = response['user']['username'], response['auth_key']
			session['username'] = username
			session['auth_key'] = auth_key
			return redirect(url_for('attendance'))
	return render_template('index.html')

@app.route('/attendance')
def attendance():
	if 'username' in session:
		if 'auth_key' in session:
			return render_template('attendance.html')
	return redirect(url_for('index'))

@app.route('/learnfaces')
def learnfaces():
	if 'username' in session:
		if 'auth_key' in session:
			if 'name' in request.args:
				if 'email_address' in request.args:
					if 'id' in request.args:
						if 'phone_number' in request.args:
							print(request.args)
							return render_template('learnfaces.html', user=request.args)
			else:
				flash("Uncompleted Credentials")
			return render_template('learnfaces.html')
	else:
		return render_template('index.html')
	
	
@app.route('/search')
def search():
	if 'username' in session:
		if 'auth_key' in session:
			print("You tried to search " + request.args.get('query'))

			headers ={'X-ASORIBA-APP-SOURCE':'biometric', 'Content-Type': 'application/json', 'Authorization': 'Token ' + session['auth_key']}
			url = "https://devapi.asoriba.com/api/v1.2/mobile/attendance/search/"
			value = request.args.get('query')
			payload = {'value':value}
			# do request
			r = requests.get(url, params=payload, headers=headers)

			print ('R is ', r)
			print('R url is', r.url)
			print('Status Code is', r.status_code)
			response=r.json()
			# print ('Json is ', response)
			# print(response['results'])

			return render_template('search.html',response=response['results'])

@app.route('/addnew')
def addnew():
	if 'username' in session:
			if request.method =='POST':
				if not request.form['firstname'] or not request.form['password'] or not request['lastname'] or not request.form['phonenumber']:
					flash("Please enter all fields")
				else:
					member= members(request.form['email'], request.form['firstname'], request.form['lastname'], request.form['password'], request.form['phonenumber'])
					db.session.add(member)
					db.session.commit()
					flash('Record was successfully added')
					return redirect(url_for('learnfaces'))
	return render_template('addnew.html')

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENTIONS
@app.route('/face_encoding', methods=['GET', 'POST'])
def face_encoding():
	if 'username' in session:
		if 'auth_key' in session:
			# file = request.files['file']
			if request.method == 'POST':
				if 'file' not in request.files:
					flash('File ZERO!!!')
					return redirect(request.url)
				else:
					file = request.files['file']
					if file.filename == '':
						flash('No selected ZERO!!!!')
						return redirect (request.url)
					if file and allowed_file(filename):
						filename = secure_filename(file.filename)
						file.save(os.path.join(app.config['UPLOADED_FOLDER'], filename))
						return redirect(url_for('uploaded_file', filename=filename))
			return render_template('face_encoding.html')
	return render_template('face_encoding.html')

	# target = os.path.join(APP_ROOT, 'Images/')
	# print(target)

	# if not os.path.isdir(target):
	# 	os.mkdir(target)
	# return redirect(url_for('leanrfaces'))

# # @app.route('/', methods=['GET', 'POST'])
# # def upload_file():






			
if __name__ == "__main__":
	db.create_all()
	app.run(debug=True)
