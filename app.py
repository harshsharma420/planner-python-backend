from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'planner'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql = MySQL()
mysql.init_app(app)

@app.route('/admins', methods=['GET'])
def get_admins():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Admin')
    admins = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(admins)


@app.route('/admins/register', methods=['POST'])
def create_admin():
    conn = mysql.connect()
    cursor = conn.cursor()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Assuming your users table has `name` and `password` columns
    query = "INSERT INTO Admin (username, password) VALUES (%s, %s)"
    cursor.execute(query, (username, password))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(message='Admin created successfully')

@app.route('/admins/login', methods=['POST'])
def adminlogin():
    conn = mysql.connect()
    cursor = conn.cursor()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Assuming your users table has `username` and `password` columns
    query = "SELECT * FROM Admin WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    admin = cursor.fetchone()
    cursor.close()
    conn.close()
    if admin:
        admin_id,username, password = admin
        return jsonify(message='Login successful', admin_id=admin_id, username=username, password=password)
    else:
        return jsonify(error='Invalid credentials', message='Invalid username or password'), 401



@app.route('/users', methods=['GET'])
def get_users():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@app.route('/users/register', methods=['POST'])
def create_user():
    conn = mysql.connect()
    cursor = conn.cursor()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Assuming your users table has `name` and `password` columns
    query = "INSERT INTO Users (username, password) VALUES (%s, %s)"
    cursor.execute(query, (username, password))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(message='User created successfully')

@app.route('/users/login', methods=['POST'])
def login():
    conn = mysql.connect()
    cursor = conn.cursor()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Assuming your users table has `username` and `password` columns
    query = "SELECT * FROM Users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        user_id,username, password = user
        return jsonify(message='Login successful', user_id=user_id, username=username, password=password)
    else:
        return jsonify(error='Invalid credentials', message='Invalid username or password'), 401


@app.route('/tasks/<int:user_id>', methods=['GET'])
def get_tasks_by_user(user_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    # Assuming your Task and Progress tables have relevant columns
    query = """
    SELECT t.task_id, t.title, t.description, t.priority, t.deadline, p.task_completion_rate, p.timeline, p.resource_usage
    FROM Task t
    JOIN Progress p ON t.task_id = p.task_id
    WHERE t.assigned_user_id = %s
    ORDER BY t.priority DESC
    """
    cursor.execute(query, (user_id,))
    tasks = []
    for row in cursor.fetchall():
        task_id, title, description, priority, deadline, completion_rate, timeline, resource_usage = row
        task = {
            'task_id': task_id,
            'title': title,
            'description': description,
            'priority': priority,
            'deadline': deadline,
            'completion_rate': completion_rate,
            'timeline': timeline,
            'resource_usage': resource_usage
        }
        tasks.append(task)
    cursor.close()
    conn.close()
    return jsonify(tasks)

@app.route('/tasks/create', methods=['POST'])
def create_task():
    conn = mysql.connect()
    cursor = conn.cursor()
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority')
    deadline = data.get('deadline')
    project_id = data.get('project_id')
    assigned_user_id = data.get('assigned_user_id')
    
    query = "INSERT INTO Task (title, description, priority, deadline, project_id, assigned_user_id) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (title, description, priority, deadline, project_id, assigned_user_id))
    
    # Get the last inserted task_id
    task_id = cursor.lastrowid
    
    # Insert a new entry in the progress table
    progress_query = "INSERT INTO Progress (task_id, task_completion_rate, timeline, resource_usage) VALUES (%s, %s, %s, %s)"
    cursor.execute(progress_query, (task_id, 0, '0% complete', 'none'))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify(message='Task created successfully')








@app.route('/projects', methods=['POST'])
def create_project():
    conn = mysql.connect()
    cursor = conn.cursor()
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    admin_id = data.get('admin_id')
    
    # Assuming your Project table has `title`, `description`, `start_date`, `end_date`, and `admin_id` columns
    query = "INSERT INTO Project (title, description, start_date, end_date, admin_id) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (title, description, start_date, end_date, admin_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify(message='Project created successfully')

@app.route('/projects/<int:admin_id>', methods=['GET'])
def get_projects_by_admin(admin_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    # Assuming your Project table has `admin_id` column
    query = "SELECT * FROM Project WHERE admin_id = %s ORDER BY project_id DESC"
    cursor.execute(query, (admin_id,))
    projects = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(projects)

# In your progress.py file

@app.route('/progress/fetch/<int:task_id>', methods=['GET'])
def get_progress(task_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "SELECT * FROM Progress WHERE task_id = %s"
    cursor.execute(query, (task_id,))
    progress = cursor.fetchone()
    cursor.close()
    conn.close()
    if progress:
        progress_id, completion_rate, timeline, resource_usage, additional_column = progress
        progress_details = {
            'progress_id': progress_id,
            'completion_rate': completion_rate,
            'timeline': timeline,
            'resource_usage': resource_usage,
            'additional_column': additional_column
        }
        return jsonify(progress_details)
    else:
        return jsonify(error="There is an error", message='Progress not found'), 404



@app.route('/progress/<int:task_id>', methods=['PUT'])
def update_progress(task_id):
    conn = mysql.connect()
    cursor = conn.cursor()

    # Get the updated data from the request
    data = request.get_json()
    completion_rate = data.get('completion_rate')
    timeline = data.get('timeline')
    resource_usage = data.get('resource_usage')

    # Update the progress entry in the database based on task ID
    query = """
    UPDATE Progress
    SET task_completion_rate = %s, timeline = %s, resource_usage = %s
    WHERE task_id = %s
    """
    cursor.execute(query, (completion_rate, timeline, resource_usage, task_id))

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return jsonify(message='Progress updated successfully')


if __name__ == '__main__':
    app.run(debug=True)



