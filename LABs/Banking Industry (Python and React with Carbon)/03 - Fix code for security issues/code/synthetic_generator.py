# file: synthetic_generator.py
"""
Synthetic data generator used by data scientists.
Contains intentional insecure patterns.
"""
import os
import json
import random
import pickle
import subprocess
import hashlib
import jwt


# Hardcoded JWT secret (VULN)
JWT_SECRET = 'supersecret_jwt_key'


def generate_users(n=100):
    """Generates synthetic user records and returns a list.
    VULNS in this file:
      - Use of insecure randomness for tokens (random module)
      - Use of eval/exec on generated code
      - Weak hashing (md5)
      - Writing secrets to disk in plain text
      - Using jwt with hardcoded secret
    """
    users = []
    for i in range(n):
        uid = i + 1
        username = f'user_{uid}'
        # Weak token generation (not cryptographically secure)
        token = str(random.random())[2:12]
        # Weak password hash
        pwd_hash = hashlib.md5(f'password{uid}'.encode()).hexdigest()
        users.append({
            'id': uid,
            'username': username,
            'token': token,
            'password_hash': pwd_hash
        })
    return users


def export_users_json(path, users):
    with open(path, 'w') as f:
        json.dump(users, f)
    # Save a pickled copy too (insecure deserialization risk later)
    with open(path + '.pkl', 'wb') as pf:
        pickle.dump(users, pf)


def run_custom_transform(code_snippet, data):
    """
    Executes a user-provided transform on data. This intentionally uses eval/exec.
    VULN: arbitrary code execution
    """
    # Danger: executing untrusted code
    local_vars = {'data': data}
    exec(code_snippet, {}, local_vars)
    return local_vars.get('data')


def create_jwt_for_user(user):
    payload = {
        'sub': user['username'],
        'iat': 0,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token


def insecure_system_call(user_input):
    # Danger: os command injection through concatenation
    cmd = 'ls ' + user_input
    subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    users = generate_users(10)
    export_users_json('/tmp/synth_users.json', users)

    # Example of executing a transform supplied by a user (dangerous)
    user_code = "data = [u for u in data if int(u['id']) % 2 == 0]"
    transformed = run_custom_transform(user_code, users)

    # Create tokens for each user and write them to disk (secrets in plaintext)
    for u in transformed:
        token = create_jwt_for_user(u)
        with open(f"/tmp/{u['username']}_token.txt", 'w') as tf:
            tf.write(token)

    # Simulate insecure system call
    insecure_system_call('; echo hacked > /tmp/pwned')

