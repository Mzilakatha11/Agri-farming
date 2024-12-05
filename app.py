from flask import Flask, render_template, request, redirect, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Thabiso@2001',
    'database': 'user_registration'
}

# Admin credentials
ADMIN_CREDENTIALS = {
    'email': 'admin@yourapp.com',
    'password': 'admin123'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Retrieve form data
            name = request.form['name']
            surname = request.form['surname']
            date_of_birth = request.form['dateofbirth']
            id_number = request.form['id']
            gender = request.form['gender']
            marital_status = request.form['maritalstatus']
            province = request.form['province']
            city = request.form['city']
            address = request.form['address']
            postal_code = request.form['postalcode']
            email = request.form['email']
            cellphone_number = request.form['cellnumber']

            # Insert into database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            query = """
                INSERT INTO users (name, surname, date_of_birth, id_number, gender, marital_status, 
                                   province, city, address, postal_code, email, cellphone_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, surname, date_of_birth, id_number, gender, marital_status,
                                   province, city, address, postal_code, email, cellphone_number))
            connection.commit()
            cursor.close()
            connection.close()

            flash('Registration successful!', 'success')
            return redirect(url_for('login'))

        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Admin login check
        if email == ADMIN_CREDENTIALS['email'] and password == ADMIN_CREDENTIALS['password']:
            session['admin_logged_in'] = True
            flash('Welcome, Admin!', 'success')
            return redirect(url_for('admin'))

        # User login check
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user and check_password_hash(user['password'], password):
                session['user_logged_in'] = True
                session['user_email'] = user['email']
                flash(f"Welcome, {user['name']}!", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password. Please try again.', 'danger')
                return redirect(url_for('login'))

        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        # Validation
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
        else:
            try:
                hashed_password = generate_password_hash(password)
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()
                query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
                cursor.execute(query, (name, email, hashed_password))
                connection.commit()
                cursor.close()
                connection.close()

                flash('Signup successful! Please login.', 'success')
                return redirect(url_for('login'))

            except mysql.connector.Error as err:
                flash(f"Error: {err}", 'danger')

    return render_template('signup.html')


@app.route('/dashboard')
def dashboard():
    if 'user_logged_in' in session:
        return render_template('register.html')
    flash('Please log in first.', 'warning')
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_logged_in' in session:
        if request.method == 'POST':
            # Handle deletion of a user
            user_id = request.form['user_id']
            try:
                connection = mysql.connector.connect(**db_config)
                cursor = connection.cursor()
                query = "DELETE FROM users WHERE id = %s"
                cursor.execute(query, (user_id,))
                connection.commit()
                cursor.close()
                connection.close()

                flash('User deleted successfully!', 'success')
                return redirect(url_for('admin'))

            except mysql.connector.Error as err:
                flash(f"Error: {err}", 'danger')
                return redirect(url_for('admin'))

        try:
            # Fetch user data
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            cursor.close()
            connection.close()

            return render_template('admin.html', users=users)

        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect(url_for('index'))

    flash('Admin access only.', 'danger')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)