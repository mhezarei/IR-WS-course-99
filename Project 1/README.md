# First Project
In this project, we are going to crawl a webpage to some information which we are going to use later for creating a simple search engine.

The crawled information have to gathered in a `.json` file.

## Project Description
The webpage assigned to our team is [`https://evand.com/categories/تکنولوژی`](https://evand.com/categories/%D8%AA%DA%A9%D9%86%D9%88%D9%84%D9%88%DA%98%DB%8C) which shows all the technology-related events held in the [`evand.com`](https://evand.com/) website.

These are the information we have to crawl **every 4 hours**:
- Event Title
- Event holding time
- Online/In person?
- Name of the organizers
- Highest ticket price
- Lowest ticket price
- Registration due date
- Event Description

The first four are done by Peyman and the others by me.

## Implementation Notes
1. If the crawler sends too many requests in a short amount of time, the server will blacklist the computer ip and will send `403` responses. 
To fix that, we could `sleep()` the main thread each time we crawl a webpage.

2. Be careful of when the website sends you unicode characters (mainly occurs when dealing with persian websites). For the sake of readability,
convert the characters to `utf-8` and then save them in the database.

3. We need to add a `requirements.txt`, a report in `.pdf` (which contains some information about the code plus some screenshots), and a good document.

---

All the Information about how this works are given in the docstrings of most of the function.

## Running the program
To run the program, run the `run.py` file. Remember to install the `requirements.txt` beforehand.

Since the output will be saved in mongoDB, make sure that your `mongod` service is active (running).

__TODO:__ Add the command-line arguemnt to control saving into database.
