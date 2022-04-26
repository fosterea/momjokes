import os
import time
import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Prompt
with open('input.txt', 'r') as f:
    input = f.read()
max_context_len = 100
users = {}
max_propmpts_per_min = 15

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        context = request.form["context"]
        id = request.form["id"]

        # Limits requests per minute
        # Add new users or reset old users after a minute
        if id not in users or users[id]['time'] + 60 < time.time():
            users[id] = {'num': 0, 'time': time.time()}
        # Keep track of querys
        users[id]['num'] += 1
        # Block user if there are too many querys
        if users[id]['num'] > max_propmpts_per_min:
            return redirect(url_for("index", error="Too many prompts. Wait a minute."))
        

        error = check_input(context)
        if error != None:
            return redirect(url_for("index", error=error))

        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=generate_prompt(context),
            temperature=.2,
            max_tokens=50,
            stop=["context:"],
            user=id
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    error = request.args.get("error")
    return render_template("index.html", result=result, error=error)


@app.route("/query", methods=("POST",))
def query():
    form = request.json
    context = form["context"]
    id = form["id"]

    # Limits requests per minute
    # Add new users or reset old users after a minute
    if id not in users or users[id]['time'] + 60 < time.time():
        users[id] = {'num': 0, 'time': time.time()}
    # Keep track of querys
    users[id]['num'] += 1
    # Block user if there are too many querys
    if users[id]['num'] > max_propmpts_per_min:
        return {"error" :"Too many prompts. Wait a minute."}
        

    error = check_input(context)
    if error != None:
        return {"error":error}

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=generate_prompt(context),
        temperature=.2,
        max_tokens=50,
        stop=["context:"],
        user=id
    )
    return {"result":response.choices[0].text}



def generate_prompt(context):
    return input + context.strip() + "\njoke: "

def check_input(context):
    """Checks if the user input aligns with
    openai's policies."""
    if len(context.strip()) > max_context_len:
        return f"Context must be fewer than {max_context_len} characters."
    if len(context.strip()) == 0:
        return "Please enter more input."
    return None

if __name__ == "__main__":
    app.run()