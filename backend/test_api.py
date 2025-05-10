import requests
import json
import sys

BASE_URL = 'http://localhost:8000/api'

def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print("\n" + "="*50 + "\n")

def test_auth():
    print("Testing Authentication Endpoints")
    
    # Register new user
    print("1. Register new user")
    data = {
        'username': 'testuser',
        'password': 'testpass123',
        'display_name': 'Test User',
        'email': 'test@example.com'
    }
    response = requests.post(f"{BASE_URL}/auth/register/", json=data)
    print_response(response)
    
    # Login
    print("2. Login")
    data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    response = requests.post(f"{BASE_URL}/auth/login/", json=data)
    print_response(response)
    
    # Get current user
    print("3. Get current user")
    token = response.json().get('token')
    headers = {'Authorization': f'Token {token}'}
    response = requests.get(f"{BASE_URL}/auth/me/", headers=headers)
    print_response(response)
    
    return token

def test_sessions(token):
    print("Testing Session Endpoints")
    headers = {'Authorization': f'Token {token}'}
    
    # Create session
    print("1. Create session")
    data = {
        'title': 'Test Session',
        'is_private': False,
        'max_participants': 4
    }
    response = requests.post(f"{BASE_URL}/sessions/", json=data, headers=headers)
    print_response(response)
    session_id = response.json().get('id')
    
    # Join session
    print("2. Leave session")
    response = requests.post(f"{BASE_URL}/sessions/{session_id}/leave/", headers=headers)
    print_response(response)


    # Join session
    print("3. Join session")
    response = requests.post(f"{BASE_URL}/sessions/{session_id}/join/", headers=headers)
    print_response(response)

    # Get leaderboard
    print("4. Ready player")
    response = requests.post(f"{BASE_URL}/sessions/{session_id}/ready/", headers=headers)
    print_response(response)
    

    # Get leaderboard
    print("5. Start session")
    response = requests.post(f"{BASE_URL}/sessions/{session_id}/start/", headers=headers)
    print_response(response)
    
    # Get session problems
    print("6. Get session problems")
    response = requests.get(f"{BASE_URL}/sessions/{session_id}/problems/", headers=headers)
    print_response(response)
    
    # Get leaderboard
    print("7. Get leaderboard")
    response = requests.get(f"{BASE_URL}/sessions/{session_id}/leaderboard/", headers=headers)
    print_response(response)
    
    return session_id

def test_problems(token, session_id):
    print("Testing Problem Endpoints")
    headers = {'Authorization': f'Token {token}'}
    
    # Get all problems
    print("1. Get all problems")
    response = requests.get(f"{BASE_URL}/solve/1/details/", headers=headers)
    print_response(response)
    problem_id = response.json()[0].get('id')
    
    # Get problem details
    print("2. Get problem details")
    response = requests.get(f"{BASE_URL}/problems/{problem_id}/details/", headers=headers)
    print_response(response)
    
    # Submit solution
    print("3. Submit solution")
    data = {
        'code': 'def solution(): return True',
        'language': 'python'
    }
    response = requests.post(f"{BASE_URL}/problems/{problem_id}/solve/", json=data, headers=headers)
    print_response(response)

def main():
    print("Starting API Tests...\n")
    
    try:
        # Test authentication
        token = test_auth()
        
        # Test sessions
        session_id = test_sessions(token)
        
        # Test problems
        test_problems(token, session_id)
        
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 