@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, hashed_password, email))
            conn.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('login'))
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            if conn:
                cursor.close()
                conn.close()

    return render_template_string(BASE_HTML, content=""" 
        <h1>Register</h1>
        <form method="POST">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" class="form-control" name="username" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" class="form-control" name="password" required>
            </div>
            <div class="form-group">
                <label>Email:</label>
                <input type="email" class="form-control" name="email" required>
            </div>
            <button type="submit" class="btn btn-primary">Register</button>
        </form>
        <a href="/login">Already have an account? Login here.</a>
    """)