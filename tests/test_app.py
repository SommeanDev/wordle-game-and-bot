import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    """ Test if home route is working """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Wordle Game' in response.data

def test_invalid_guess(client):
    """ Test if invalid guess is handled correctly """
    client.get('/')

    response = client.post('/guess', data={'guess': 'invalid'})
    assert b'Invalid guess. Please enter a valid 5-letter word.' in response.data

def test_valid_guess(client):
    """ Test if valid guess is handled correctly """
    client.get('/')
    response = client.post('/guess', data={'guess': 'HELLO'})
    assert response.status_code == 200
    assert b'green' in response.data

def test_game_not_initialized(client):
    """ Test if game not initialized is handled correctly """
    response = client.post('/guess', data={'guess': 'HELLO'})
    assert b'Game not initialized. <a href=\'/\'>Start over</a>' in response.data

def test_game_over(client):
    """ Test if game over is handled correctly """
    client.get('/')
    for _ in range(6):
        response = client.post('/guess', data={'guess': 'ZZZZZ'})
        assert b"Invalid guess" in response.data

    response = client.get('/')
    assert b'Game over!' in response.data

def test_correct_guess(client):
    """Test if correct guess triggers game win"""
    client.get('/')  # Initialize the game
    
    # Assuming the target word is 'APPLE', let's test a correct guess
    response = client.post('/guess', data={'guess': 'APPLE'})
    assert b"Congratulations!" in response.data  # Check if win message appears


def test_used_remaining_letters(client):
    """Test if used and remaining letters are updated correctly"""
    client.get('/')  # Initialize the game
    
    # Assuming the target word is 'APPLE'
    client.post('/guess', data={'guess': 'APPLE'})
    response = client.get('/')
    assert b"Used Letters:" in response.data  # Ensure used letters are displayed
    assert b"A, P, L, E" in response.data  # Check if 'APPLE' letters are in used list
    
    # Test remaining letters
    assert b"Remaining Letters:" in response.data  # Ensure remaining letters are displayed
    assert b"B, C, D" in response.data  # Check if other letters are in remaining list

def test_session_persistence(client):
    """Test if session variables persist across multiple requests"""
    client.get('/')  # Initialize the game
    
    # Send a guess
    client.post('/guess', data={'guess': 'APPLE'})
    response = client.get('/')
    assert b"Attempts: 1" in response.data  # Ensure attempts count increases
    
    # Send another guess
    client.post('/guess', data={'guess': 'BANANA'})
    response = client.get('/')
    assert b"Attempts: 2" in response.data  # Ensure attempts count increases again

def test_game_reset(client):
    """Test if the game resets after a win or loss"""
    client.get('/')  # Initialize the game
    
    # Assuming the target word is 'APPLE', make a correct guess
    client.post('/guess', data={'guess': 'APPLE'})
    response = client.get('/')
    assert b"Congratulations!" in response.data  # Ensure win message appears
    
    # Ensure session is cleared and game is reset
    response = client.get('/')
    assert b"Wordle Game" in response.data  # Ensure the game title is shown again
