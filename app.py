from flask import Flask, jsonify, render_template
from scrap import scrape_twitter_trends
from pymongo import MongoClient
import traceback

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "twitter_trends"
COLLECTION_NAME = "trends"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script', methods=['GET'])
def run_script():
    try:
        result = scrape_twitter_trends()
        return jsonify(result)
    except Exception as e:
        print("Error occurred:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/latest-record', methods=['GET'])
def latest_record():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    latest = collection.find().sort('date_time', -1).limit(1)
    return jsonify(list(latest))

if __name__ == '__main__':
    app.run(debug=True)
