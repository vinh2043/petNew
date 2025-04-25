from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'tuvavinh'  # 👈 Bạn có thể đặt gì cũng được, miễn là không rỗng

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model đặt ở đây
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(10), default='user')

# 👉 Tạo bảng ở đây:
with app.app_context():
    db.create_all()

# ======== Routes =========

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            flash('Mật khẩu xác nhận không khớp.', 'error')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email đã tồn tại.', 'error')
            return redirect(url_for('register'))

        new_user = User(fullname=fullname, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Đăng ký thành công. Hãy đăng nhập!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('index'))
        else:
            flash('Sai tài khoản hoặc mật khẩu!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')  # đảm bảo file login.html tồn tại


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Bạn cần đăng nhập để tiếp tục.', 'error')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất.', 'info')
    return redirect(url_for('home'))

# Model Pet
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    owner = db.relationship('User', backref=db.backref('pets', lazy=True))


# Xem , thêm thú cưng
@app.route('/pets', methods=['GET', 'POST'])
def pets():
    if 'user_id' not in session:
        flash('Bạn cần đăng nhập.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        pet_type = request.form['type']
        age = int(request.form['age'])

        new_pet = Pet(name=name, type=pet_type, age=age, user_id=session['user_id'])
        db.session.add(new_pet)
        db.session.commit()
        flash('Thêm thú cưng thành công!', 'success')
        return redirect(url_for('pets'))

    pet_list = Pet.query.filter_by(user_id=session['user_id']).all()
    return render_template('pets.html', pets=pet_list)


# Sửa thú cưng
@app.route('/pets/edit/<int:pet_id>', methods=['GET', 'POST'])
@app.route('/pets/edit/<int:pet_id>', methods=['GET', 'POST'])
def edit_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)

    if request.method == 'POST':
        pet.name = request.form['name']
        pet.type = request.form['type']
        pet.age = int(request.form['age'])

        db.session.commit()
        flash('Cập nhật thành công!', 'success')
        return redirect(url_for('pets'))

    return render_template('edit_pet.html', pet=pet)



# Xóa thú cưng
@app.route('/pets/delete/<int:pet_id>', methods=['POST'])
@app.route('/pets/delete/<int:pet_id>', methods=['POST'])
def delete_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)

    db.session.delete(pet)
    db.session.commit()
    flash('Đã xóa thú cưng.', 'info')
    return redirect(url_for('pets'))



# ======== Main =========

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
