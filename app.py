from flask import Flask, request, redirect, url_for, render_template_string, session, flash
import mysql.connector
from mysql.connector import Error
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a strong secret key

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Update with your database user
    'password': '0000',  # Update with your database password
    'database': 'diary_app'  # Ensure this database exists
}

def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS diary_entries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            entry TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        conn.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Indie+Flower&display=swap" rel="stylesheet">
    <style>
    <style>
    .currency-box {
        font-size: 3rem;/* Text color */
        padding: 10px 15px; /* Padding inside the box */
        border-radius: 5px; /* Rounded corners */
        font-weight: bold; /* Make the text bold */
        text-color:#FFFFFF
    }
    .navbar .d-flex {
        display: flex;
        align-items: center; /* Align items vertically in the center */
        text-color:#FFFFFF
    }
    body {
        background-color: #36454F; /* Gray color */
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        color: white; /* Set default text color to white */
    }
    footer {
        background-color: #5A5A5A;
        color: white;
        padding: 10px 0;
        position: relative;
        bottom: 0;
        width: 100%;
    }
    .navbar {
        background-color: #000;
    }
    .welcome-text {
        font-family: 'Georgia, serif; /* Ancient or old bold font */
        font-size: 2.5rem;
        color: aqua; /* Heading color */
        margin-top: 20px;
    }
    .content-section {
        text-align: center;
        margin-top: 30px;
    }
    .diary-image {
        max-width: 100%;
        height: auto;
        border-radius: 15px;
    }
</style>

    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>Your Diary</title>
</head>
<body>

    <nav class="navbar navbar-expand-lg navbar-dark">
    <a class="navbar-brand" href="/">Diary App</a>
    <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mr-auto"> <!-- Use mr-auto to push the right elements to the right -->
            {% if session.user_id %}
                <li class="nav-item"><a class="nav-link" href="/diary">Diary</a></li>
                <li class="nav-item"><a class="nav-link" href="/contact">Contact</a></li>
                <li class="nav-item"><a class="nav-link" href="/logout">Logout</a></li>
                <li class="nav-item"><a class="nav-link" href="/events">Events</a></li>
                <li class="nav-item"><a class="nav-link" href="/todo">TODO</a></li>
                <li class="nav-item"><a class="nav-link" href="/view_events">ViewEvents</a></li>
                {% if session.admin %}
                    <li class="nav-item"><a class="nav-link" href="/admin_dashboard">Admin</a></li>
                    <li class="nav-item"><a class="nav-link" href="/view_messages">ViewMessages</a></li>
                {% endif %}
            {% else %}
                <li class="nav-item"><a class="nav-link" href="/login">Login</a></li>
                <li class="nav-item"><a class="nav-link" href="/register">Register</a></li>
            {% endif %}
        </ul>
        <div class="currency-box" > <!-- Place the username here on the right side -->
            {% if session.user_id %}
                {{ session.username }} <!-- Display the username here -->
            {% endif %}
        </div>
    </div>
</nav>

    <div class="container mt-4 flex-grow-1">
        {% with messages = get_flashed_messages(with_categories=True) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        {{ content|safe }}
    </div>
    <footer class="text-center mt-4">
        <p>&copy;All right reserved to Ritesh Ardale Diary App 2024 </p>
    </footer>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
"""

@app.route('/todo', methods=['GET', 'POST'])
def todo_list():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("Please log in to view your To-Do List.", "danger")
        return redirect(url_for('login'))

    tasks = []
    if request.method == 'POST':
        # Adding a new task
        task = request.form.get('task')
        if task:
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO todo_list (user_id, task) VALUES (%s, %s)",
                    (session['user_id'], task)
                )
                conn.commit()
                flash("Task added successfully!", "success")
            except Error as e:
                flash(f"Error: {e}", "danger")
            finally:
                if conn:
                    cursor.close()
                    conn.close()

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Fetch all tasks for the logged-in user
        cursor.execute(
            "SELECT id, task, is_completed FROM todo_list WHERE user_id = %s ORDER BY created_at",
            (session['user_id'],)
        )
        tasks = cursor.fetchall()

    except Error as e:
        flash(f"Error: {e}", "danger")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return render_template_string("""
        <html>
            <head>
                <title>To-Do List</title>
                <style>
                  body {
                      font-family: Arial, sans-serif;
                      margin: 0;
                      padding: 0;
                      background-color: #00FFFF; /* Dark background */
                  }

                  h1 {
                      text-align: center;
                      color: #00c4cc; /* Aqua color */
                      margin-top: 50px;
                  }

                  /* Navbar Style */
                  .navbar {
                      position: fixed;
                      top: 0;
                      left: 50%;
                      transform: translateX(-50%);
                       /* Decrease width for a more compact look */
                      background-color: #000; /* Black background */
                      padding: 10px 0;
                       /* Curved edges */
                      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
                      display: flex;
                      justify-content: center; /* Center the links */
                      align-items: center;
                      z-index: 9999;
                  }

                  .navbar a {
                      color: #fff; /* White text */
                      padding: 10px 20px;
                      text-decoration: none;
                      font-size: 18px;
                      text-align: center;
                      /* Rounded edges */
                      margin: 0 10px; /* Space between links */
                  }

                  .navbar a:hover {
                      
                  }

                  .navbar a:first-child {
                      
                  }

                  .navbar a:last-child {
                    
                  }

                  .container {
                      max-width: 1000px;
                      margin: 0 auto;
                      padding: 40px;
                      background-color: #212529; /* Dark grey background */
                      
                      box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
                      margin-top: 70px; /* Adjust for navbar */
                  }

                  ul {
                      list-style-type: none;
                      padding-left: 0;
                  }

                  li {
                      background-color: #eaeaea;
                      padding: 15px;
                      margin: 10px 0;
                      border-radius: 5px;
                  }

                  li.completed {
                      text-decoration: line-through;
                      color: #888;
                  }

                  li strong {
                      font-size: 18px;
                      color: #333;
                  }

                  form {
                      text-align: center;
                      margin-bottom: 30px;
                  }

                  input[type="text"] {
                      padding: 12px;
                      font-size: 18px;
                      width: 70%;
                      margin-bottom: 15px;
                      border-radius: 5px;
                      border: 1px solid #ccc;
                      background-color: #f5f5f5;
                  }

                  input[type="submit"] {
                      padding: 12px;
                      font-size: 18px;
                      border: none;
                      background-color: #28a745;
                      color: white;
                      border-radius: 5px;
                      cursor: pointer;
                  }

                  button {
                      padding: 8px 15px;
                      border-radius: 5px;
                      cursor: pointer;
                      color: white;
                      border: none;
                  }

                  .delete-btn {
                      background-color: #dc3545;
                  }

                  .complete-btn {
                      background-color: #007bff;
                  }

                  @media (max-width: 768px) {
                      .container {
                          padding: 20px;
                          max-width: 90%;
                      }

                      input[type="text"] {
                          width: 90%;
                      }
                  }
                </style>
            </head>
            <body>
                <!-- Navbar with a Logout button -->
                <div class="navbar">
                    <a href="{{ url_for('home') }}">Home</a>
                    <a href="{{ url_for('diary') }}">diary</a>
                    
                    <a href="{{ url_for('view_events') }}">events</a>
                    
                    <a href="{{ url_for('contact') }}">contact</a>
                    
                    <a href="{{ url_for('logout') }}">Logout</a>
                </div>

                <div class="container">
                    <h1>Your To-Do List</h1>

                    <!-- Form to add a new task -->
                    <form method="POST">
                        <input type="text" name="task" placeholder="Add a new task" required />
                        <input type="submit" value="Add Task" />
                    </form>

                    <ul>
                        {% for task in tasks %}
                            <li class="{{ 'completed' if task[2] else '' }}">
                                <strong>{{ task[1] }}</strong>
                                {% if not task[2] %}
                                    <a href="{{ url_for('mark_completed', task_id=task[0]) }}">
                                        <button class="complete-btn">Mark as Completed</button>
                                    </a>
                                {% else %}
                                    <span>Completed</span>
                                {% endif %}
                                <a href="{{ url_for('delete_task', task_id=task[0]) }}">
                                    <button class="delete-btn">Delete</button>
                                </a>
                            </li>
                        {% else %}
                            <li>No tasks found.</li>
                        {% endfor %}
                    </ul>
                </div>
            </body>
        </html>
    """, tasks=tasks)

@app.route('/mark_completed/<int:task_id>', methods=['GET'])
def mark_completed(task_id):
    if 'user_id' not in session:
        flash("Please log in to mark tasks as completed.", "danger")
        return redirect(url_for('login'))

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Update the task as completed
        cursor.execute(
            "UPDATE todo_list SET is_completed = TRUE WHERE id = %s AND user_id = %s",
            (task_id, session['user_id'])
        )
        conn.commit()
        flash("Task marked as completed!", "success")
    except Error as e:
        flash(f"Error: {e}", "danger")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return redirect(url_for('todo_list'))

@app.route('/delete_task/<int:task_id>', methods=['GET'])
def delete_task(task_id):
    if 'user_id' not in session:
        flash("Please log in to delete tasks.", "danger")
        return redirect(url_for('login'))

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Delete the task
        cursor.execute(
            "DELETE FROM todo_list WHERE id = %s AND user_id = %s",
            (task_id, session['user_id'])
        )
        conn.commit()
        flash("Task deleted successfully!", "success")
    except Error as e:
        flash(f"Error: {e}", "danger")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return redirect(url_for('todo_list'))



@app.route('/events', methods=['GET', 'POST'])
def add_event():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("Please log in to add events.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        location = request.form['location']
        description = request.form['description']

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Insert the new event into the database
            cursor.execute("INSERT INTO events (event_name, event_date, event_time, location, description, user_id) VALUES (%s, %s, %s, %s, %s, %s)", 
               (event_name, event_date, event_time, location, description, session['user_id']))
            conn.commit()
            flash("Event added successfully.", "success")
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            if conn:
                cursor.close()
                conn.close()

    return render_template_string("""
        <html>
            <head>
                <title>Add Event</title>
                <style>
                    /* Curvy Navbar styling */
                    .navbar {
                        background-color: #000;
                        padding: 10px 40px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        border-radius: 25px;
                        width: 80%;
                        max-width: 600px;
                        margin: 20px auto;
                    }
                    .navbar a {
                        color: #FFFFFF;
                        text-decoration: none;
                        padding: 10px 20px;
                        font-size: 1.1em;
                        border-radius: 20px;
                    }
                    .navbar a:hover {
                        color: #00FFFF;
                        background-color: rgba(255, 255, 255, 0.2);
                    }

                    /* Body and jumbotron styling */
                    body {
                        font-family: 'Arial', sans-serif;
                        background-color: #2a2a2a; /* Charcoal background color */
                        margin: 0;
                        height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        flex-direction: column;
                        padding-bottom: 30px;
                    }
                    .jumbotron {
                        background-color: rgba(0, 0, 0, 0.7); /* Black background with transparency */
                        border-radius: 15px;
                        padding: 40px;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
                        text-align: center;
                        color: #00FFFF; /* Aqua color for text */
                    }
                    h1 {
                        color: #00FFFF;
                    }
                    label {
                        color: #56cfe1; /* Aqua label color */
                    }
                    button {
                        background-color: #56cfe1; /* Aqua button */
                        color: black;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 5px;
                        font-size: 1em;
                        cursor: pointer;
                    }
                    button:hover {
                        background-color: #48b8d1; /* Darker aqua on hover */
                    }
                    input, textarea {
                        width: 100%;
                        padding: 10px;
                        margin-top: 5px;
                        margin-bottom: 15px;
                        border-radius: 5px;
                        border: 1px solid #56cfe1; /* Aqua border */
                        background-color: #333; /* Dark input field background */
                        color: #fff; /* White text in inputs */
                    }
                    input:focus, textarea:focus {
                        border-color: #00FFFF; /* Focused input border in Aqua */
                        background-color: #444; /* Slightly lighter background when focused */
                    }
                </style>
            </head>
            <body>
                <!-- Curvy Navbar -->
                <div class="navbar">
                    <a href="{{ url_for('home') }}">Home</a>
                    <a href="{{ url_for('add_event') }}">Add Event</a>
                    <a href="{{ url_for('view_events') }}">View Events</a>
                    <a href="{{ url_for('logout') }}">Logout</a>
                </div>
                
                <!-- Event Form -->
                <div class="jumbotron">
                    <h1>Add Event</h1>
                    <form method="POST">
                        <label for="event_name">Event Name:</label>
                        <input type="text" id="event_name" name="event_name" required>
                        
                        <label for="event_date">Event Date:</label>
                        <input type="date" id="event_date" name="event_date" required>
                        
                        <label for="event_time">Event Time:</label>
                        <input type="time" id="event_time" name="event_time" required>
                        
                        <label for="location">Location:</label>
                        <input type="text" id="location" name="location" required>
                        
                        <label for="description">Description:</label>
                        <textarea id="description" name="description" required></textarea>
                        
                        <button type="submit">Add Event</button>
                    </form>
                    <br>
                    <a href="{{ url_for('view_events') }}" style="color: #56cfe1;">View Events</a>
                </div>
            </body>
        </html>
    """)

# Route to view the events page with past and future buttons
@app.route('/view_events', methods=['GET', 'POST'])
def view_events():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("Please log in to view events.", "danger")
        return redirect(url_for('login'))

    events = []
    date_filter = None  # Default to None (no filter)

    if request.method == 'POST':
        date_filter = request.form.get('event_date')  # Get the date from the form
        # Ensure the date format is correct (e.g., 'YYYY-MM-DD')
        if date_filter:
            try:
                # You can use datetime to ensure the date is in the correct format
                from datetime import datetime
                datetime.strptime(date_filter, '%Y-%m-%d')  # Validate the date format
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
                return redirect(url_for('view_events'))

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Adjust the SQL query to include date filtering if a date is provided
        if date_filter:
            cursor.execute(
                "SELECT event_name, event_date, event_time, location, description "
                "FROM events WHERE user_id = %s AND event_date = %s",
                (session['user_id'], date_filter)
            )
        else:
            cursor.execute(
                "SELECT event_name, event_date, event_time, location, description "
                "FROM events WHERE user_id = %s",
                (session['user_id'],)
            )

        events = cursor.fetchall()

    except Error as e:
        flash(f"Error: {e}", "danger")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return render_template_string("""
        <html>
            <head>
                <title>View Events</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #333; /* Dark grey background */
                    }

                    h1 {
                        text-align: center;
                        color: #fff; /* White text for heading */
                        margin-top: 50px;
                    }

                    .container {
                        max-width: 900px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #222; /* Slightly darker background for content */
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }

                    .navbar {
                        background-color: #000; /* Black navbar */
                        padding: 10px;
                        display: flex;
                        justify-content: space-around;
                        align-items: center;
                        border-radius: 10px;
                        margin: 20px auto;
                        width: 70%;
                    }

                    .navbar a {
                        color: white;
                        text-decoration: none;
                        font-size: 16px;
                        padding: 10px;
                    }

                    .navbar a:hover {
                        color: #00ffff; /* Cyan hover effect */
                    }

                    ul {
                        list-style-type: none;
                        padding-left: 0;
                    }

                    li {
                        background-color: #000; /* Black background for events */
                        color: #fff; /* White text for event details */
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    }

                    li strong {
                        font-size: 18px;
                        color: #00ffff; /* Cyan for event names */
                    }

                    li br {
                        margin-bottom: 10px;
                    }

                    form {
                        text-align: center;
                        margin-bottom: 20px;
                    }

                    input[type="date"] {
                        padding: 5px;
                        font-size: 16px;
                    }
                </style>
            </head>
            <body>
                <!-- Navbar -->
                <div class="navbar">
                    <a href="{{ url_for('home') }}">Home</a>
                    <a href="{{ url_for('add_event') }}">Add Event</a>
                    <a href="{{ url_for('view_events') }}">View Events</a>
                    <a href="{{ url_for('logout') }}">Logout</a>
                </div>

                <div class="container">
                    <h1>Your Events</h1>

                    <!-- Form to filter events by date -->
                    <form method="POST">
                        <input type="date" name="event_date" value="{{ date_filter }}" />
                        <input type="submit" value="Filter Events" />
                    </form>

                    <ul>
                        {% for event in events %}
                            <li>
                                <strong>{{ event[0] }}</strong><br>
                                {{ event[1] }} at {{ event[2] }} - {{ event[3] }}<br>
                                {{ event[4] }}
                            </li>
                        {% else %}
                            <li>No events found for this date.</li>
                        {% endfor %}
                    </ul>
                </div>
            </body>
        </html>
    """, events=events, date_filter=date_filter)


@app.route('/')
def home():
    return render_template_string(BASE_HTML, content=""" 
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(to right, #ffafbd, #ffc3a0); /* Colorful gradient background */
                margin: 0;
                height: 100vh; /* Full height */
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .jumbotron {
                background-color: rgba(255, 255, 255, 0.9); /* Semi-transparent white background */
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2); /* Shadow for depth */
                text-align: center;
                overflow: hidden;
                position: relative;
            }
            .welcome-text {
                font-size: 3em;
                color: #ff6f61; /* Coral color */
                animation: fadeInUp 1s forwards 0.5s;
            }
            .lead {
                font-size: 1.5em;
                color: #6a0572; /* Deep purple */
                animation: fadeInUp 1s forwards 1s;
            }
            .btn {
                background-color: #56cfe1; /* Teal color */
                color: #ffffff; /* White text */
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                font-size: 1.2em;
                text-decoration: none;
                display: inline-block;
                animation: fadeInUp 1s forwards 1.5s;
                cursor: pointer;
            }
            .btn:hover {
                background-color: #48b8d1; /* Darker teal on hover */
            }
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            .writing-animation {
                font-size: 2em;
                color: #ff6f61; /* Coral color for the writing */
                margin-top: 20px;
                white-space: nowrap;
                overflow: hidden; 
                border-right: 0.15em solid #ff6f61; /* Cursor effect */
                animation: typing 3s steps(10, end) infinite, blink-caret 0.75s step-end infinite;
            }
            @keyframes typing {
                0% { width: 0; }
                30% { width: 15ch; }
                60% { width: 30ch; }
                100% { width: 0; }
            }
            @keyframes blink-caret {
                from, to { border-color: transparent; }
                50% { border-color: #ff6f61; }
            }
        </style>
        
        <div class="container text-center">
            <div class="jumbotron">
                <h1 class="welcome-text">Welcome to Your Diary</h1>
                <p class="lead">A safe space to write down your thoughts and memories.</p>
                <div class="writing-animation">✏️ Writing in progress...</div>
                <a href="/diary" class="btn">Start Writing</a>
            </div>
        </div>
    """)

@app.route('/my-events', methods=['GET'])
def my_events():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("Please log in to view your events.", "danger")
        return redirect(url_for('login'))

    events_by_date = {}
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT event_name, event_date, event_time, location, description FROM events WHERE user_id = %s ORDER BY event_date", (session['user_id'],))
        events = cursor.fetchall()

        # Organize events by date
        for event in events:
            date = event[1]  # event_date
            if date not in events_by_date:
                events_by_date[date] = []
            events_by_date[date].append(event)

    except Error as e:
        flash(f"Error: {e}", "danger")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return render_template_string(BASE_HTML, content=f"""
        <style>
            /* Your CSS styles */
        </style>

        <h1>My Events</h1>
        <p>Here are your events, organized by date:</p>
        <a href="/create-event" class="btn-primary">Add New Event</a>
        <br><br>
        {''.join(f"<h3>{date}</h3><ul>" + ''.join(f"<li><strong>{event[0]}</strong> - {event[2]} at {event[3]}<br>{event[4]}</li>" for event in events_by_date[date]) + "</ul>" for date in sorted(events_by_date.keys()))}
    """)


@app.route('/create-event', methods=['GET', 'POST'])
def create_event():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("Please log in to create an event.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        location = request.form['location']
        description = request.form['description']

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO events (user_id, event_name, event_date, event_time, location, description) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (session['user_id'], event_name, event_date, event_time, location, description)
            )
            conn.commit()
            flash("Event created successfully!", "success")
            return redirect(url_for('calendar'))  # Redirect to calendar view
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            if conn:
                cursor.close()
                conn.close()

    return render_template_string(BASE_HTML, content=f"""
        <style>
        </style>

        <h1>Create Event</h1>
        <form method="POST">
            <div class="form-group">
                <label for="event_name">Event Name:</label>
                <input type="text" class="form-control" id="event_name" name="event_name" required>
            </div>
            <div class="form-group">
                <label for="event_date">Event Date:</label>
                <input type="date" class="form-control" id="event_date" name="event_date" required>
            </div>
            <div class="form-group">
                <label for="event_time">Event Time:</label>
                <input type="time" class="form-control" id="event_time" name="event_time" required>
            </div>
            <div class="form-group">
                <label for="location">Location:</label>
                <input type="text" class="form-control" id="location" name="location" required>
            </div>
            <div class="form-group">
                <label for="description">Description:</label>
                <textarea class="form-control" id="description" name="description"></textarea>
            </div>
            <button type="submit" class="btn-primary">Create Event</button>
        </form>
    """)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_FOLDER, filename)

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
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(to right, #ffafbd, #ffc3a0); /* Colorful gradient background */
                margin: 0;
                height: 100vh; /* Full height */
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden; /* Hide overflow */
            }
            .form-container {
                background-color: rgba(255, 255, 255, 0.9); /* Semi-transparent white background */
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2); /* Shadow for depth */
                width: 300px; /* Fixed width for form */
                text-align: center;
                position: relative;
            }
            h1 {
                color: #6a0572; /* Deep purple */
                margin-bottom: 20px;
                animation: fadeIn 1s forwards;
            }
            .form-group {
                margin-bottom: 15px;
                text-align: left;
            }
            label {
                display: block;
                margin-bottom: 5px;
                color: #333;
            }
            input[type="text"],
            input[type="password"],
            input[type="email"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                transition: border 0.3s;
            }
            input[type="text"]:focus,
            input[type="password"]:focus,
            input[type="email"]:focus {
                border: 1px solid #6a0572; /* Focus border color */
                outline: none;
            }
            .btn {
                background-color: #ff6f61; /* Coral color */
                color: #ffffff; /* White text */
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 1.2em;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .btn:hover {
                background-color: #ff4c47; /* Darker coral on hover */
            }
            a {
                display: block;
                margin-top: 15px;
                color: #6a0572; /* Deep purple */
                text-decoration: none;
                transition: color 0.3s;
            }
            a:hover {
                color: #ff6f61; /* Coral on hover */
            }
            .writing-animation {
                position: absolute;
                right: -150px; /* Further off-screen initially */
                top: 50%;
                transform: translateY(-50%);
                font-size: 2em;
                color: #000; /* Deep purple */
                white-space: nowrap;
                overflow: hidden; /* Hide overflow */
                animation: slideIn 5s forwards;
            }
            @keyframes slideIn {
                0% {
                    left: 200pxpx; /* Start off-screen */
                }
                50% {
                    left: 280%; /* Adjust to fit your layout */
                }
                80% {
                    left: 300px; /* Move back off-screen */
                }
                100%{
                    left:200px
                }
            }
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            /* Pencil writing effect */
            .writing-animation span {
                display: inline-block;
                opacity: 0;
                animation: writingEffect 0.5s forwards;
            }
            @keyframes writingEffect {
                0% { opacity: 0; }
                100% { opacity: 1; }
            }
        </style>
        
        <div class="form-container">
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
                <button type="submit" class="btn">Register</button>
            </form>
            <a href="/login">Already have an account? Login here.</a>
            <div class="writing-animation" id="writingEffect"></div>
        </div>

        <script>
            const text = "Writing...";
            let index = 0;
            const writingEffect = document.getElementById('writingEffect');
            
            function type() {
                if (index < text.length) {
                    // Create a span for each character to apply pencil effect
                    const span = document.createElement('span');
                    span.textContent = text.charAt(index);
                    writingEffect.appendChild(span);
                    index++;
                    setTimeout(type, 150); // Adjust typing speed here
                } else {
                    // Clear the text after it's fully typed
                    setTimeout(() => {
                        writingEffect.innerHTML = '';
                        index = 0; // Reset index for next typing effect
                        setTimeout(type, 500); // Delay before restarting typing
                    }, 2000); // Delay before clearing
                }
            }
            type(); // Start the typing effect
        </script>
    """)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT id, is_admin FROM users WHERE username = %s AND password = %s", (username, hashed_password))
            user = cursor.fetchone()

            if user:
                session['user_id'] = user[0]
                session['admin'] = user[1]
                session['username'] = username
                flash("Login successful!", "success")
                return redirect(url_for('diary'))
            else:
                flash("Invalid username or password", "danger")
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            if conn:
                cursor.close()
                conn.close()

    return render_template_string(BASE_HTML, content="""
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(to right, #00c6ff, #0072ff); /* Aqua gradient background */
                margin: 0;
                height: 100vh; /* Full height */
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden; /* Prevent scrollbars from appearing */
            }
            .form-container {
                background-color: #1a1a1a; /* Darkest black for the form background */
                color: #ffffff; /* White text color */
                border-radius: 15px;
                padding: 40px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5); /* Shadow for depth */
                width: 300px; /* Fixed width for form */
                text-align: center;
                position: relative; /* For absolute positioning of the animated text */
            }
            h1 {
                color: #00c6ff; /* Aqua color for the heading */
                margin-bottom: 20px;
            }
            .animated-text {
                position: absolute;
                top: 50%;
                left: 140%; /* Adjust position as needed */
                transform: translateY(-200%);
                font-size: 1.5rem;
                color:#000;
                color:#000; /* Semi-transparent white for a subtle effect */
                white-space: nowrap; /* Prevent text wrapping */
                overflow: hidden; /* Hide overflow */
                animation: typing 2s steps(50, end) forwards, blink-caret .75s step-end infinite; /* Typing animation */
            }
            @keyframes typing {
                from { width: 0; }
                to { width: 100%; }
            }
            @keyframes blink-caret {
                from, to { border-color: transparent; }
                50% { border-color: rgba(255, 255, 255, 0.6); }
            }
            .form-group {
                margin-bottom: 15px;
                text-align: left;
            }
            label {
                display: block;
                margin-bottom: 5px;
                color: #ffffff; /* White color for labels */
            }
            input[type="text"],
            input[type="password"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #333; /* Charcoal border */
                border-radius: 5px;
                transition: border 0.3s;
                background-color: #333; /* Charcoal background for inputs */
                color: #ffffff; /* White text for inputs */
            }
            input[type="text"]:focus,
            input[type="password"]:focus {
                border: 1px solid #00c6ff; /* Focus border color */
                outline: none;
            }
            .btn {
                background-color: #0072ff; /* Blue button color */
                color: #ffffff; /* White text for button */
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 1.2em;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .btn:hover {
                background-color: #005bb5; /* Darker blue on hover */
            }
            a {
                display: block;
                margin-top: 15px;
                color: #00c6ff; /* Aqua color for links */
                text-decoration: none;
                transition: color 0.3s;
            }
            a:hover {
                color: #0072ff; /* Darker blue on hover */
            }
        </style>
        
        <div class="form-container">
            <h1>Login</h1>
            <form method="POST">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" class="form-control" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" class="form-control" name="password" required>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
            <a href="/register">Don't have an account? Register here.</a>
            <div class="animated-text">Welcome to Your Diary</div> <!-- Animated text -->
        </div>
    """)

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for('home'))

@app.route('/diary', methods=['GET', 'POST'])
def diary():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        entry = request.form['entry']
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO diary_entries (user_id, entry) VALUES (%s, %s)", (session['user_id'], entry))
            conn.commit()
            flash("Diary entry added!", "success")
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            if conn:
                cursor.close()
                conn.close()

    entries = []
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT entry, created_at FROM diary_entries WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
        entries = cursor.fetchall()
    except Error as e:
        flash(f"Error: {e}", "danger")
    finally:
        if conn:
            cursor.close()
            conn.close()

    entries_html = "".join([
        f"""
        <div class="entry-box">
            <p>{entry[0]}</p>
            <small>{entry[1]}</small>
        </div>
        """ for entry in entries
    ])

    return render_template_string(BASE_HTML, content=f"""
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background: linear-gradient(to right, #ffafbd, #ffc3a0);
                margin: 0;
                padding: 20px;
            }}
            .navbar {{
                background: #000;
                border-radius: 10px;
                padding: 10px 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                display: flex;
                justify-content: center;
                position: fixed;
                top: 0;
                left: 50%;
                transform: translateX(-50%);
                width: auto;
                margin: 0;
                z-index: 1000;
                color:#FFFFFF;
            }}
            .navbar a {{
                color: #ff6f61;
                text-decoration: none;
                font-weight: bold;
                transition: color 0.3s;
            }}
            .navbar a:hover {{
                color: #ff3e3e;
            }}
            h1, h2 {{
                color: #6a0572;
            }}
            .form-group {{
                margin-bottom: 15px;
                text-align: left;
            }}
            .entry-box {{
                background-color: #1a1a1a;
                border-radius: 15px;
                padding: 15px;
                margin: 10px 0;
                color: #ffffff;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
            }}
            textarea {{
                width: 100%;
                padding: 10px;
                border: 1px solid #333;
                border-radius: 5px;
                background-color: #333;
                color: #ffffff;
            }}
            .btn {{
                background-color: #56cfe1;
                color: #ffffff;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 1.2em;
                cursor: pointer;
                transition: background-color 0.3s;
            }}
            .btn:hover {{
                background-color: #48b8d1;
            }}
        </style>
        <br>
        <br>
        <br>
        <br>
        <h1>Your Diary Entries</h1>
        <form method="POST">
            <div class="form-group">
                <label>New Entry:</label>
                <textarea class="form-control" name="entry" required></textarea>
            </div>
            <button type="submit" class="btn">Add Entry</button>
        </form>
        <h2>Your Entries:</h2>
        <div class="entries-container">
            {entries_html}
        </div>
    """)

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or not session['admin']:
        flash("Access denied!", "danger")
        return redirect(url_for('home'))

    users = []
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
    except Error as e:
        flash(f"Error: {e}", "danger")
    finally:
        if conn:
            cursor.close()
            conn.close()

    users_html = "".join([f"""
        <div class="user-box">
            <p><strong>Username:</strong> {user[1]}</p>
            <p><strong>Email:</strong> {user[2]}</p>
            <div class="user-actions">
                <a href='/admin/edit_user/{user[0]}' class="btn btn-edit">Edit</a>
                <a href='/admin/delete_user/{user[0]}' class="btn btn-delete">Delete</a>
            </div>
        </div>
    """ for user in users])

    return render_template_string(BASE_HTML, content=f"""
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background: linear-gradient(to right, #e2e2e2, #ffffff); /* Light background */
                margin: 0;
                padding: 20px;
            }}
            .navbar {{
                background: #000; /* Navbar background */
                border-radius: 10px;
                padding: 10px 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                display: flex;
                justify-content: center;
                position: fixed;
                top: 0;
                left: 50%;
                transform: translateX(-50%);
                width: auto;
                margin: 0;
                z-index: 1000;
            }}
            .navbar a {{
                color: #ff6f61; /* Coral color for navbar links */
                text-decoration: none;
                font-weight: bold;
                transition: color 0.3s;
            }}
            .navbar a:hover {{
                color: #ff3e3e; /* Darker coral on hover */
            }}
            h1 {{
                color: #6a0572; /* Deep purple for headings */
                text-align: center; /* Center heading */
            }}
            h2 {{
                color: #6a0572;
                margin-top: 40px; /* Space above h2 */
            }}
            .user-box {{
                background-color: #f5f5f5; /* Light grey background for user boxes */
                border-radius: 15px; /* Curvy box */
                padding: 15px;
                margin: 10px 0; /* Space between user entries */
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2); /* Shadow for depth */
            }}
            .user-actions {{
                margin-top: 10px; /* Space above actions */
            }}
            .btn {{
                background-color: #56cfe1; /* Teal color */
                color: #ffffff; /* White text */
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 1em;
                cursor: pointer;
                transition: background-color 0.3s;
                text-decoration: none; /* Remove underline from links */
                display: inline-block; /* Display as block for padding */
                margin-right: 5px; /* Space between buttons */
            }}
            .btn-edit {{
                background-color: #ffa500; /* Orange color for edit button */
            }}
            .btn-edit:hover {{
                background-color: #ff8c00; /* Darker orange on hover */
            }}
            .btn-delete {{
                background-color: #ff4d4d; /* Red color for delete button */
            }}
            .btn-delete:hover {{
                background-color: #ff1a1a; /* Darker red on hover */
            }}
        </style>
        <br>
        <br>
        <br>
        <br>
        <h1>Admin Dashboard</h1>
        <h2>Users</h2>
        <div class="users-container">
            {users_html}
        </div>
    """)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session or not session['admin']:
        flash("Access denied!", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET username = %s, email = %s WHERE id = %s", (username, email, user_id))
            conn.commit()
            flash("User updated successfully!", "success")
            return redirect(url_for('admin_dashboard'))
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            if conn:
                cursor.close()
                conn.close()

    user = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT username, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
    except Error as e:
        flash(f"Error: {e}", "danger")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return render_template_string(BASE_HTML, content=f"""
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #ffffff; /* White background */
                color: #333; /* Dark text */
                margin: 0;
                padding: 20px;
            }}
            .navbar {{
                background: #000; /* Navbar background */
                border-radius: 10px;
                padding: 10px 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                display: flex;
                justify-content: center;
                position: fixed;
                top: 0;
                left: 50%;
                transform: translateX(-50%);
                width: auto;
                margin: 0;
                z-index: 1000;
            }}
            .navbar a {{
                color: #00bcd4; /* Aqua color for navbar links */
                text-decoration: none;
                font-weight: bold;
                transition: color 0.3s;
            }}
            .navbar a:hover {{
                color: #0097a7; /* Darker aqua on hover */
            }}
            h1 {{
                color: #000; /* Black for headings */
                text-align: center; /* Center heading */
            }}
            .form-group {{
                margin-bottom: 15px; /* Space between form groups */
            }}
            .form-control {{
                border-radius: 10px; /* Curvy input */
                border: 1px solid #ddd; /* Light border */
                padding: 10px;
                width: 100%; /* Full width */
                transition: border 0.3s; /* Smooth border transition */
            }}
            .form-control:focus {{
                border-color: #ff4081; /* Pink border on focus */
                box-shadow: 0 0 5px rgba(255, 64, 129, 0.5); /* Pink glow */
            }}  
            .btn-primary {{
                background-color: #00bcd4; /* Aqua button */
                border: none;
                border-radius: 10px; /* Curvy button */
                padding: 10px 15px;
                color: white;
                font-weight: bold;
                transition: background-color 0.3s; /* Smooth background transition */
            }}
            .btn-primary:hover {{
                background-color: #0097a7; /* Darker aqua on hover */
            }}
        </style>
        <br>
        <br>
        <br>
        <br>
        <h1>Edit User</h1>
        <form method="POST">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" class="form-control" name="username" value="{user[0]}" required>
            </div>
            <div class="form-group">
                <label>Email:</label>
                <input type="email" class="form-control" name="email" value="{user[1]}" required>
            </div>
            <button type="submit" class="btn btn-primary">Update User</button>
        </form>
    """)




# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

@app.route('/admin/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    if 'user_id' not in session or not session['admin']:
        flash("Access denied!", "danger")
        return redirect(url_for('home'))

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        flash("User deleted successfully!", "success")
    except Error as e:
        flash(f"Error: {e}", "danger")
    finally:
        if conn:
            cursor.close()
            conn.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        message = request.form['message']
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (user_id, message) VALUES (%s, %s)", (session['user_id'], message))
            conn.commit()
            flash("Message sent!", "success")
        except Error as e:
            flash(f"Error: {e}", "danger")
        finally:
            if conn:
                cursor.close()
                conn.close()

    return render_template_string(BASE_HTML, content=f"""
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background: linear-gradient(to right, #e2e2e2, #ffffff); /* Light background */
                margin: 0;
                padding: 20px;
            }}
            .navbar {{
                background: #000; /* Navbar background */
                border-radius: 10px;
               
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                display: flex;
                justify-content: center;
                position: fixed;
                top: 0;
                left: 50%;
                transform: translateX(-50%);
                width: auto;
                margin: 0;
                z-index: 1000;
            }}
            .navbar a {{
                color: #ff6f61; /* Coral color for navbar links */
                text-decoration: none;
                
                transition: color 0.3s;
            }}
            .navbar a:hover {{
                color: #ff3e3e; /* Darker coral on hover */
            }}
            h1 {{
                color: #6a0572; /* Deep purple for headings */
                text-align: center; /* Center heading */
            }}
            .chat-container {{
                border-radius: 10px;
                background-color: #f5f5f5; /* Light grey background for chat */
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                margin-top: 80px; /* Space for fixed navbar */
            }}
            .form-group {{
                margin-bottom: 15px;
                text-align: left;
            }}
            .message-box {{
                background-color: #1a1a1a; /* Dark background for messages */
                border-radius: 15px; /* Curvy box */
                padding: 15px;
                margin: 10px 0; /* Space between messages */
                color: #ffffff; /* White text color */
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5); /* Shadow for depth */
            }}
            textarea {{
                width: 100%;
                padding: 10px;
                border: 1px solid #333; /* Charcoal border */
                border-radius: 5px;
                background-color: #333; /* Charcoal background for inputs */
                color: #ffffff; /* White text for inputs */
            }}
            .btn {{
                background-color: #56cfe1; /* Teal color */
                color: #ffffff; /* White text */
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                font-size: 1.2em;
                cursor: pointer;
                transition: background-color 0.3s;
                width: 100%; /* Full width for button */
            }}
            .btn:hover {{
                background-color: #48b8d1; /* Darker teal on hover */
            }}
        </style>

        <div class="chat-container">
            <h1>Contact Us</h1>
            <div class="message-box">
                <strong>Admin:</strong> How can I assist you today?
            </div>
            <form method="POST">
                <div class="form-group">
                    <label>Your Message:</label>
                    <textarea class="form-control" name="message" required></textarea>
                </div>
                <button type="submit" class="btn">Send Message</button>
            </form>
        </div>
    """)

@app.route('/view_messages', methods=['GET'])
def view_messages():
    if 'user_id' not in session or not session['admin']:
        flash("Access denied!", "danger")
        return redirect(url_for('home'))

    messages = []
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT m.message, u.username FROM messages m JOIN users u ON m.user_id = u.id")
        messages = cursor.fetchall()
    except Error as e:
        flash(f"Error: {e}", "danger")
    finally:
        if conn:
            cursor.close()
            conn.close()

    messages_html = "".join([f"""
        <div class="message-box">
            <strong>{msg[1]}:</strong> {msg[0]}
        </div>
    """ for msg in messages])

    return render_template_string(BASE_HTML, content=f"""
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #ffffff; /* White background */
                color: #333; /* Dark text */
                margin: 0;
                padding: 20px;
            }}
            .navbar {{
                background: #000; /* Navbar background */
                border-radius: 10px; 
                padding: 10px 20px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                display: flex;
                justify-content: center;
                position: fixed;
                top: 0;
                left: 50%;
                transform: translateX(-50%);
                width: auto;
                margin: 0;
                z-index: 1000;
            }}
            .navbar a {{
                color: #00bcd4; /* Aqua color for navbar links */
                text-decoration: none;
                font-weight: bold;
                transition: color 0.3s;
            }}
            .navbar a:hover {{
                color: #0097a7; /* Darker aqua on hover */
            }}
            h1 {{
                color: #000; /* Black for headings */
                text-align: center; /* Center heading */
            }}
            .message-box {{
                background-color: #f0f0f0; /* Light grey for message box */
                border-radius: 10px; /* Curvy box */
                padding: 15px;
                margin: 10px 0; /* Space between messages */
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); /* Shadow for depth */
                transition: background-color 0.3s; /* Smooth background transition */
            }}
            .message-box:hover {{
                background-color: #e0e0e0; /* Darker grey on hover */
            }}
        </style>
        <br>
        <br>
        <br>
        <br>
        <h1>Messages</h1>
        <div class="messages-container">
            {messages_html}
        </div>
    """)



if __name__ == '__main__':
    init_db()  # Initialize the database and create tables
    app.run(debug=False)