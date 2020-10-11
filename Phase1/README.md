# First Project
In this project, we are going to crawl a webpage to some information which we are going to use later for creating a simple search engine.

The crawled information have to gathered in a `.json` file.

## Project Description
The webpage assigned to our team is `https://evand.com/categories/تکنولوژی` which shows all the technology-related events held in their website.

These are the information we have to crawl **every 4 hours**:
- Event Title
- Event holding time
- Online/In person?
- Name of the organizers
- Highest ticket price
- Lowest ticket price
- Registration due date
- Event Description

## Implementation Notes
1. If the crawler sends too many requests in a short amount of time, the server will blacklist the computer ip and will send `403` responses. 
To fix that, we could `sleep()` the main thread each time we crawl a webpage.

2. Be careful of when the website sends you unicode characters (mainly occurs when dealing with persian websites). For the sake of readability,
convert the characters to `utf-8` and then save them in the database.

3. We need to add a `requirements.txt`, a report in `.pdf` (which contains some information about the code plus some screenshots), and a good document.
