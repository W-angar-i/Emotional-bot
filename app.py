from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import requests
import json
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key="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", base_url="https://openrouter.ai/api/v1")

user_file = 'users.json'

app = Flask(__name__)

#Load users from file
def load_users():
    if not os.path.exists(user_file):
        return[]
    with open(user_file, 'r') as f:
        return json.load(f) #json to python

#save user
def save_users(users):
    with open(user_file, 'w') as f:
        json.dump(users, f, indent=4)#to json

    
#create user
@app.route('/register', methods=['POST', 'GET'])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    #load users
    users = load_users()

    #check if user exists
    for user in users:
        if user['username'] == username and user['email'] == email:
            return jsonify({'message': 'Account already exists'}), 400
        
    #add
    new_user = {'username': username, 'password': password, 'email': email}
    users.append(new_user)
    save_users(users)

    return jsonify ({'message': 'Registration Successful'}), 201

#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    users = load_users()

    if not username or not password or not email:
        return jsonify({'Error': 'Enter the required fields!'}), 400
    
    for user in users:
       if user['username'] == username and user['email'] == email and user['password'] == password:
           return jsonify ({'message': 'Login successful'}), 200
       
    return jsonify({'error': 'Wrong username/email/password'}), 400   




#SUBMIT MOOD
@app.route('/submit_mood', methods=['POST', 'GET'])
def submit_mood():
    data = request.get_json()
    mood = data.get('mood')
    journal = data.get('journal')

    if not mood and not journal:
       return jsonify({'Error': 'You should provide a mood and and a journal entry'}), 400
    
    prompt = f"""A user feels {mood}and wrote this journal entry:\"{journal}\"
    You are a warm, emotionally intelligent mental health assistant. Respond in a supportive, kind and validating way to help the user feel heard and comforted.No need to remind you are analysing the journal and mood just speak about the feelings."""

    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages = [{"role": "user", "content": prompt}],
            temperature=0.8,
            stream = False
        )

        reply = response.choices[0].message.content
        return jsonify({"Response": reply})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    


if __name__ == "__main__":
    app.run(port=5000, debug = True)
