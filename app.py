from flask import Flask, render_template, request, session
from dotenv import load_dotenv
import pandas as pd
import os
import random

# load environment variables
load_dotenv()

# initialize flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

# valid list of 5-letter words
VALID_WORDS = pd.read_csv('./all_valid_words.csv')
SOLUTION_WORDS = pd.read_csv('./solution_words.csv')

# route for home page
@app.route('/')
def home():
    session["target_word"] = random.choice(SOLUTION_WORDS['solution_words'].tolist())
    session["guesses"] = []
    session["attempts"] = 0
    session["used_letters"] = [] # track letters used in guess
    session["remaining_letters"] = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') # track remaining letters
    return render_template('index.html', attempts=session["attempts"], guesses=session["guesses"], used_letters=session["used_letters"], remaining_letters=session["remaining_letters"])

@app.route('/guess', methods=['POST'])
def guess():
    # Ensure session variables exist
    if "target_word" not in session or "attempts" not in session or "guesses" not in session:
        return "Game not initialized. <a href='/'>Start over</a>"

    # get guess from form
    guess = request.form['guess'].upper()
    session["attempts"] += 1

    # check if guess is valid
    if len(guess) != 5 or guess not in VALID_WORDS['valid_words'].tolist():
        return render_template('index.html', error="Invalid guess. Please enter a valid 5-letter word.", 
                               attempts=session["attempts"], used_letters=session["used_letters"], 
                               remaining_letters=session["remaining_letters"])
    
    # compare guess with target word
    result = [""] * 5
    target_word_used = [False] * 5 # track letters used in target word
    guess_used = [False] * 5 # track letters used in guess

    # first pass: check for correct letters in correct positions
    for i in range(5):
        if guess[i] == session['target_word'][i]:
            result[i] = "green" # correect letter, correct position
            target_word_used[i] = True
            guess_used[i] = True
            if guess[i] not in session["used_letters"]:
                session["used_letters"].append(guess[i])
            if guess[i] in session["remaining_letters"]:
                session["remaining_letters"].remove(guess[i])
    
    # second pass: check for correct letters in incorrect positions
    for i in range(5):
        if not guess_used[i]: # if guess letter not used yet
            for j in range(5):
                if not target_word_used[j] and guess[i] == session['target_word'][j]: # if target letter not used yet but matches guess letter
                    result[i] = "yellow"
                    target_word_used[j] = True
                    guess_used[i] = True
                    if guess[i] not in session["used_letters"]:
                        session["used_letters"].append(guess[i])
                    if guess[i] in session["remaining_letters"]:
                        session["remaining_letters"].remove(guess[i])
                        break
    
    # third pass: check for incorrect letters
    for i in range(5):
        if result[i] == "": # if letter not used yet
            result[i] = "gray"
            if guess[i] not in session["used_letters"]:
                session["used_letters"].append(guess[i])
            if guess[i] in session["remaining_letters"]:
                session["remaining_letters"].remove(guess[i])

    # add guess to list of guesses
    session["guesses"].append({"guess": guess, "result": result})

    # check if player has won
    if guess == session["target_word"]:
        message = f"Congratulations! You guessed '{session['target_word']}' in {session['attempts']} attempts. <a href='/'>Play again</a>"
        session.clear()  # Reset the game
        return message
    elif session["attempts"] == 6:
        message = f"Game over! The word was '{session['target_word']}'. <a href='/'>Try again</a>"
        session.clear()  # Reset the game
        return message
    
    # return result to user
    return render_template('index.html', attempts=session["attempts"], guesses=session["guesses"], used_letters=sorted(list(session["used_letters"])), remaining_letters=sorted(list(session["remaining_letters"])))

if __name__ == '__main__':
    app.run(port=8000)
