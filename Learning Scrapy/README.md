# Learning Scrapy
This is where I keep notes of scrapy document as I read through it.
## A Simple Crawler
We are going to scrape [Quotes to Scrape](http://quotes.toscrape.com/) which is a website full of quotes from famous authors.

Use `scrapy startproject <name>` to create the project structure and files.

Scrapy uses **Spider** class to scrape the given website(s). In this class, we have to define the "starting URL(s)" and "how to parse".

Ways to specify starting URLs:
* `start_requests()` which must return an iteratable of `Request` objects. Either a list or a generator function.
* define a `start_urls` class attribute.

**Note:** `Request` object sends a request to the specified URL and parses the response using the specified callback.

**Note:** You can use `scrapy shell <website>` to launch the interactive shell for scraping.

`response.css()` uses CSS selectors. For example, `response.css("div.quote")[0].css("div.tags a.tag::text").getall()` gets all the tags of the first quote.

**Note:** Using `get()` at the end is better because it avoids `IndexError` and returns `None` when there is nothing at all.

Use `scrapy crawl quotes -o quotes.json` for outputting the result in a file BUT remember that scrapy appends to a file rather than clearing it. So you can use
`> quotes.json && scrapy crawl quotes -o quotes.json` if you want to clear the file first.

**How to follow links?**
* Find the next page link && append it to the base URL and make the full absolute URL using `urljoin()` && yield a request the that page using a `Request` object.

  ```python
  next_page = response.css('li.next a::attr(href)').get()
  if next_page is not None:
      next_page = response.urljoin(next_page)
      yield scrapy.Request(next_page, callback=self.parse)
  ```
  
* Shortcuts:
  * Find the next page link text && `yield response.follow(link, callback=self.<parser name>)`. Don't need to make the full URL.
    ```python
    for href in response.css('ul.pager a::attr(href)'):
        yield response.follow(href, callback=self.parse)
    ```
  * `yield from response.follow_all(css=<css style of the link>, callback=self.<parser name>)` is the shortest way. It handles everything else automatically.
    ```python
    yield from response.follow_all(css='ul.pager a', callback=self.parse)
    ```

**Note:** When trying to parse multiple pages, scrapy automatically handles the duplicate pages which is quite good.

**Note:** You can pass data to the parse using `Request.cb_kwargs` argument.

**Note:** You can pass arguments to scrapy in the command line using the `-a` option like `scrapy crawl quotes -o quotes-humor.json -a tag=humor` and then, you can 
use `getattr()` to handle the arguments passed in the command line like `tag = getattr(self, 'tag', None)`. In the example, the provided `tag` argument is 
available in `self.tag`. One usage could be getting all the quotes with the specified tags.
