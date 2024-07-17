from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    area_code = db.Column(db.String(10), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    area_code = db.Column(db.String(10), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    subcategory = db.Column(db.String(50), nullable=False)
    age_group = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean, default=True)
    image = db.Column(db.String(120), nullable=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Ongoing')
    product = db.relationship('Product', backref=db.backref('orders', lazy=True))
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        area_code = request.form['area_code']
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password=hashed_password, area_code=area_code)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username already exists. Please choose a different username.', 'danger')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            if user.is_admin:
                session['admin_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('admin_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = Admin.query.filter_by(username=username).first()

        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin username or password. Please try again.', 'danger')

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    products = Product.query.all()
    return render_template('admin_dashboard.html', products=products)

@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        subcategory = request.form['subcategory']
        age_group = request.form['age_group']
        description = request.form['description']
        price = float(request.form['price'])
        available = True if request.form.get('available') else False
        image = request.files['image']
        
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = filename  # Save just the filename
        else:
            image_url = None
        
        new_product = Product(
            name=name,
            category=category,
            subcategory=subcategory,
            age_group=age_group,
            description=description,
            price=price,
            available=available,
            image=image_url
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_product.html')


@app.route('/admin/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.category = request.form['category']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.available = True if request.form.get('available') else False
        image = request.files['image']
        
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image = filename  # Save just the filename
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_product.html', product=product)

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        area_code = request.form['area_code']

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create new admin user
        new_admin = Admin(username=username, password=hashed_password, area_code=area_code)
        
        try:
            db.session.add(new_admin)
            db.session.commit()
            flash('Admin registration successful! Please log in.', 'success')
            return redirect(url_for('admin_login'))
        except:
            flash('Username already exists. Please choose a different username.', 'danger')

    return render_template('admin_register.html')

@app.route('/admin/delete_product/<int:id>',methods=['POST'])
def delete_product(id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    product = Product.query.get_or_404(id)
    
    # Delete the image file if it exists
    if product.image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/products')
def products():
    event_category = request.args.get('event_category')
    subcategory = request.args.get('subcategory')
    age_group = request.args.get('age_group')
    
    query = Product.query
    
    if event_category:
        query = query.filter_by(category=event_category)
    if subcategory:
        query = query.filter(Product.subcategory.ilike(f'%{subcategory}%'))
    if age_group:
        query = query.filter_by(age_group=age_group)
        
    products = query.all()
    return render_template('products.html', products=products)

@app.route('/rent_product/<int:product_id>', methods=['GET', 'POST'])
def rent_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        total_cost = float(request.form['total_cost'])  
        new_order = Order(
            user_id=session['user_id'],
            product_id=product.id,
            start_date=datetime.strptime(start_date, '%Y-%m-%d'),
            end_date=datetime.strptime(end_date, '%Y-%m-%d'),
            total_cost=total_cost
        )
        db.session.add(new_order)
        db.session.commit()
        
        flash(f'Product {product.name} rented successfully!', 'success')
        return redirect(url_for('products'))
    
    return render_template('rent_product.html', product=product)

@app.route('/rentals')
def rentals():
    if 'user_id' not in session:
        flash('You need to log in to view your rentals.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_rentals = Order.query.filter_by(user_id=user_id).all()
    
    return render_template('rentals.html', rentals=user_rentals)

@app.route('/return_rental/<int:rental_id>', methods=['POST'])
def return_rental(rental_id):
    rental = Order.query.get_or_404(rental_id)
    
    if rental.user_id != session['user_id']:
        flash('You are not authorized to return this rental.', 'danger')
        return redirect(url_for('rentals'))

    # Implement the return logic here : update or remove the rental
    rental.status = 'Returned'
    db.session.commit()

    flash(f'Rental {rental.product.name} returned successfully!', 'success')
    return redirect(url_for('rentals'))

@app.route('/buy_product/<int:product_id>', methods=['GET', 'POST'])
def buy_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            end_date_str = request.form['end_date']
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_date = datetime.now().date()
            
            if end_date < start_date:
                flash('End date cannot be in the past.', 'danger')
                return redirect(url_for('buy_product', product_id=product.id))
            
            total_cost = float(request.form['total_cost'])
            
            new_order = Order(
                user_id=session['user_id'],
                product_id=product.id,
                start_date=start_date,
                end_date=end_date,
                total_cost=total_cost,
                status='Ongoing'
            )


            db.session.add(new_order)
            db.session.commit()

            flash(f'Product{product.name} bought successfully!','success')
            return redirect(url_for('products'))
        except KeyError:
            flash('Form Submission error:missing fields.', 'danger')
        except ValueError:
            flash('Invalid input for date or cost.','danger')
    return render_template('buy_product.html',product=product)

if __name__=='__main__':
    app.run(debug=True,host="0.0.0.0",port=8080)

    




