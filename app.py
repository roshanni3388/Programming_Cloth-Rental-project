class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    area_code = db.Column(db.String(10), nullable=False)

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
