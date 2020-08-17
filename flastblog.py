from flask import Flask, render_template, url_for, flash, redirect,session,request
from forms import RegistrationForm, LoginForm
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL


import os
from ocr_core import ocr_core


app = Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='pharmaMagic'

mysql=MySQL(app)





UPLOAD_FOLDER = '/static/uploads/'

# allow files of a specific type
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# function to check the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template('index.html', title='Home')





@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
            username=form.username.data
            email=form.email.data
            password=form.password.data
            confirm_password=form.confirm_password.data
            secure_password=sha256_crypt.encrypt(str(password))
            if password==confirm_password:
                    cur=mysql.connection.cursor()
                    cur.execute("INSERT INTO users(username,email,password)VALUES (%s, %s, %s)",(username,email,password))
                    mysql.connection.commit()
                    flash(f'Account created for {form.username.data}!', 'success')
                    return redirect(url_for('login'))
            else:
                    return render_template('register.html')

    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    session.pop('email',None)
    form = LoginForm()
    if form.validate_on_submit():
        cur=mysql.connection.cursor()
        cur.execute("Select * from users where email like '{}' and password like '{}'".format(form.email.data,form.password.data))
        users=cur.fetchall()
        if len(users)>0:
            session['email']=form.email.data
            flash('You have been logged in!', 'success')
            return redirect(url_for('pharmaMagic'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return render_template('login.html', title='Login', form=form)
#        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
 #           flash('You have been logged in!', 'success')
 #           return redirect(url_for('pharmaMagic'))
 #       else:
 #           flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/pharmaMagic",methods=['GET','POST'])
def pharmaMagic():
    if request.method == 'POST':

            if 'file' not in request.files:
                return render_template('pharmaMagic.html', msg='No file selected')
            file = request.files['file']
            # if no file is selected
            if file.filename == '':
                return render_template('pharmaMagic.html', msg='No file selected')
    
            if file and allowed_file(file.filename):
    
                # call the OCR function on it
                extracted_text = ocr_core(file)
    
                # extract the text and display it
                return render_template('pharmaMagic.html',
                                       msg='Successfully processed',
                                       extracted_text=extracted_text,
                                       img_src=UPLOAD_FOLDER + file.filename)

    return render_template('pharmaMagic.html')
@app.route('/search',methods=['GET','POST'])
def search():

        drug= request.values.get("drug")
        cur=mysql.connection.cursor()
#        cur.execute("SELECT Brand_Name FROM drug_dictionary where Generic_Name like '{}'".format(drug))
        query="SELECT Brand_Name FROM drug_dictionary WHERE Generic_Name=%s"
        cur.execute(query, (drug,))
        brand_name=cur.fetchone()
        cur.close
        query="SELECT Pharmacology FROM drug_dictionary WHERE Generic_Name=%s"
        cur.execute(query, (drug,))
        pharmacology=cur.fetchone()
        cur.close

        return render_template('search.html',brand_name=brand_name,pharmacology=pharmacology)


@app.route('/logout')
def logout():
    session.pop('email',None)
    flash('You have been logged out!', 'success')
    return redirect(url_for(login))

if __name__ == '__main__':
    app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
    app.run(debug=False)