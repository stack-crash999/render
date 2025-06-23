from flask import Flask, render_template, request, redirect, url_for, session
import socket
import platform
from functools import wraps

app = Flask(__name__)
app.secret_key = "ghostwire_secret"

USERS = {"admin": "admin"}  # Update for your use
connected_clients = []

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if USERS.get(username) == password:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            error = "Invalid username or password"
    return render_template('login.html', error=error)

@app.route('/home')
@login_required
def home():
    try:
        name = platform.node()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()

        if not any(c["ip"] == ip and c["name"] == name for c in connected_clients):
            connected_clients.append({"name": name, "ip": ip})
    except Exception as e:
        print(f"[!] Failed to get current system info: {e}")

    return render_template('home.html', clients=connected_clients)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
