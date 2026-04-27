import requests
import time
import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

# CONFIGURATION DU CHEMIN
DB_PATH = '/home/damien/mysite/quality.db'

def run_frankfurter_tests():
    url = "https://api.frankfurter.app/latest"
    latencies = []
    success_count = 0
    total_tests = 6 
    
    for i in range(total_tests):
        try:
            start = time.time()
            response = requests.get(url, timeout=3)
            latency = (time.time() - start) * 1000
            if response.status_code == 200:
                success_count += 1
                latencies.append(latency)
        except:
            pass
            
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    success_rate = (success_count / total_tests) * 100
    
    # SAUVEGARDE DANS LA BASE
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO runs (avg_latency, success_rate) VALUES (?, ?)", 
                 (round(avg_latency, 2), round(success_rate, 2)))
    conn.commit()
    conn.close()
    return avg_latency, success_rate

@app.route('/run')
def run_route():
    run_frankfurter_tests()
    # On redirige vers l'accueil après le test pour voir le tableau mis à jour
    return "Test fini ! <a href='/'>Cliquez ici pour voir le tableau</a>"

@app.route('/')
def home():
    try:
        conn = sqlite3.connect(DB_PATH)
        # On récupère les 10 derniers tests
        runs = conn.execute("SELECT timestamp, avg_latency, success_rate FROM runs ORDER BY id DESC LIMIT 10").fetchall()
        conn.close()
    except:
        runs = []

    # --- PARTIE ESTHÉTIQUE (HTML/CSS) ---
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>QA Dashboard - Frankfurter</title>
        <style>
            body { font-family: 'Segoe UI', Arial; background-color: #0b1020; color: #e9edff; display: flex; justify-content: center; padding-top: 50px; }
            .dashboard { background: #121a33; padding: 30px; border-radius: 15px; border: 1px solid #23305c; box-shadow: 0 10px 30px rgba(0,0,0,0.5); width: 80%; max-width: 800px; }
            h1 { color: #77baff; margin-bottom: 20px; font-size: 24px; border-bottom: 2px solid #23305c; padding-bottom: 10px; }
            .btn { background: #77baff; color: #0b1020; padding: 12px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; margin-bottom: 25px; transition: 0.3s; }
            .btn:hover { background: #d6dcff; transform: translateY(-2px); }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th { text-align: left; color: #aab4d4; font-size: 13px; text-transform: uppercase; padding: 10px; border-bottom: 2px solid #23305c; }
            td { padding: 12px 10px; border-bottom: 1px solid #1e294d; font-size: 15px; }
            .status-ok { color: #62d6a0; font-weight: bold; }
            .latency { color: #ffcc66; }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <h1>📊 Indicateurs de Qualité API</h1>
            <a href="/run" class="btn">🚀 Lancer une batterie de tests</a>
            <table>
                <thead>
                    <tr>
                        <th>Date & Heure</th>
                        <th>Latence Moyenne</th>
                        <th>Taux de Succès</th>
                    </tr>
                </thead>
                <tbody>
    """
    for run in runs:
        html += f"""
            <tr>
                <td>{run[0]}</td>
                <td class="latency">{run[1]} ms</td>
                <td class="status-ok">{run[2]} %</td>
            </tr>
        """
    
    if not runs:
        html += "<tr><td colspan='3' style='text-align:center;'>Aucun historique disponible.</td></tr>"

    html += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html
