from flask import Flask, request, jsonify
import csv
import hashlib

app = Flask(__name__)
occupied_by = None
users_file = 'users.csv'

# Function to check if a user exists
def user_exists(email):
    with open(users_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['email'] == email:
                return True
    return False

# Function to register a new user
def register_user(name, email, password):
    with open(users_file, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, email, hashlib.sha256(password.encode()).hexdigest()])

# Function to authenticate user login
def authenticate_user(email, password):
    with open(users_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['email'] == email and row['encrypted_password'] == hashlib.sha256(password.encode()).hexdigest():
                return True
    return False

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not user_exists(email):
        register_user(name, email, password)
        return jsonify({'success': True, 'message': 'Registration successful'}), 201
    else:
        return jsonify({'success': False, 'message': 'User already exists'}), 400

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    global occupied_by
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if authenticate_user(email, password):
        if occupied_by is None:
            occupied_by = email
            return jsonify({'success': True, 'message': 'Login successful. Server occupied.'}), 200
        elif occupied_by == email:
            return jsonify({'success': False, 'message': 'You already have occupied the server'}), 200
        else:
            return jsonify({'success': False, 'message': 'Server is already occupied by another user.'}), 403
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# Route to check server occupancy status and who has occupied it (if occupied)
@app.route('/status', methods=['GET'])
def get_status():
    global occupied_by
    if occupied_by:
        return jsonify({'success': True, 'occupied': True, 'occupied_by': occupied_by}), 200
    else:
        return jsonify({'success': True, 'occupied': False}), 200

# Route to occupy the server
@app.route('/occupy', methods=['POST'])
def occupy_server():
    global occupied_by
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if authenticate_user(email, password):
        if occupied_by is None:
            occupied_by = email
            return jsonify({'success': True, 'message': 'Server occupied by {}'.format(email)}), 200
        elif occupied_by == email:
            return jsonify({'success': False, 'message': 'You already have occupied the server'}), 200
        else:
            return jsonify({'success': False, 'message': 'Server is already occupied by another user.'}), 403
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# Route to release the server
@app.route('/release', methods=['POST'])
def release_server():
    global occupied_by
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if authenticate_user(email, password):
        if occupied_by == email:
            occupied_by = None
            return jsonify({'success': True, 'message': 'Server released successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'You do not have permission to release the server'}), 403
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True)
