from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'Q$AK3$@7Ewy&lvGiOx1y1HaTb'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    course = db.Column(db.String(100), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'danger')
        else:
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    students = Student.query.all()
    return render_template('dashboard.html', students=students)


@app.route('/add_student', methods=['POST'])
@login_required
def add_student():
    name = request.form['name']
    age = request.form['age']
    course = request.form['course']
    new_student = Student(name=name, age=age, course=course)
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        student.name = request.form['name']
        student.age = request.form['age']
        student.course = request.form['course']

        try:
            db.session.commit()
            flash(f"Student '{student.name}' has been successfully updated!", 'success')
            return redirect(url_for('dashboard'))
        except:
            db.session.rollback()
            flash('An error occurred while updating the student.', 'danger')

    return render_template('edit_student.html', student=student)


@app.route('/delete_student/<int:id>')
@login_required
def delete_student(id):
    student = Student.query.get(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('dashboard'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
