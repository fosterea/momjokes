# Mom Jokes Generator

This flask web app uses OpenAI’s [GPT-3](https://beta.openai.com) to generate yo mama jokes. The standard prompt is stored in [input.txt](input.txt). The users input is appended to this file.

```
The following is a list of yo mama jokes and their context.

context: stocks
joke: Yo mama's so fat, when she skips a meal, the stock market crashes.

context: 
```

[app.py](app.py) implements the flask web app. The / route returns the web page and /query is the internal api. The query function inplements:
* Stopping the user from providing input 15 times per minute
* Checks if the input is longer than 100 characters or has no characters
* Sends the request to OpenAI
* Uses a jery rigged content filter to censor content. Because almost all jokes are flaged as harmful, it only checks jokes not begining with the allowed prefixes (generated in app.py).

[user.js](static/user.js) implements the client side. user.js creates a random id based on the time and a random number, which is stored as cookie on the user's browser (not secure I know). user.js also gets the result or error from the server.

The link to the working website is [momjokes.herokuapp.com](http://momjokes.herokuapp.com). **Note it may take a second to boot up**