import os

from flask import Flask, redirect, render_template
import redis

app = Flask(__name__)

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

@app.route('/toggle-ocean', methods=["POST"])
def toggle_ocean():
    if redis_client.get('ocean:disabled'):
        redis_client.delete('ocean:disabled')
    else:
        redis_client.set('ocean:disabled', 'true')

    return redirect("/")

@app.route('/')
def home():
    if redis_client.get('ocean:disabled'):
        next_status = "Enable"
    else:
        next_status = "Disable"

    return render_template('toggle.html', next_status=next_status)
