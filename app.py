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

ALLOWED_STARTS = ['yo mama\'s so']
ALLOWED_ADJ = ['fat', 'short', 'tone deaf', 'dumb', 'tall', 'literal', 'tall', 'small', 'rad', 'slow']

ALLOWED_PRE = []

for start in ALLOWED_STARTS:
    for adj in ALLOWED_ADJ:
        ALLOWED_PRE.append(f"{start} {adj}")

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

    output = response.choices[0].text.strip()
    # Check with content filter
    error = check_output(output)
    if error != None:
        return {"error": error}

    return {"result":output}



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

def check_output(output):
    """Returns any error associated with a bad output."""
    # Removes the offensive insult about yo mama
    output = " " + output.lower().strip()
    print(output)
    for allowed in ALLOWED_PRE:
        if allowed in output:
            return None

    response = openai.Completion.create(
        engine="content-filter-alpha",
        prompt = "<|endoftext|>"+output+"\n--\nLabel:",
        temperature=0,
        max_tokens=1,
        top_p=0,
        logprobs=10
    )
    output_label = response["choices"][0]["text"]

    # This is the probability at which we evaluate that a "2" is likely real
    # vs. should be discarded as a false positive
    toxic_threshold = -0.355

    if output_label == "2":
        # If the model returns "2", return its confidence in 2 or other output-labels
        logprobs = response["choices"][0]["logprobs"]["top_logprobs"][0]

        # If the model is not sufficiently confident in "2",
        # choose the most probable of "0" or "1"
        # Guaranteed to have a confidence for 2 since this was the selected token.
        if logprobs["2"] < toxic_threshold:
            logprob_0 = logprobs.get("0", None)
            logprob_1 = logprobs.get("1", None)

            # If both "0" and "1" have probabilities, set the output label
            # to whichever is most probable
            if logprob_0 is not None and logprob_1 is not None:
                if logprob_0 >= logprob_1:
                    output_label = "0"
                else:
                    output_label = "1"
            # If only one of them is found, set output label to that one
            elif logprob_0 is not None:
                output_label = "0"
            elif logprob_1 is not None:
                output_label = "1"

            # If neither "0" or "1" are available, stick with "2"
            # by leaving output_label unchanged.

    # if the most probable token is none of "0", "1", or "2"
    # this should be set as unsafe
    if output_label not in ["0", "1", "2"]:
        output_label = "2"

    if output_label == '2':
        return 'Censored'
    return None

if __name__ == "__main__":
    app.run()