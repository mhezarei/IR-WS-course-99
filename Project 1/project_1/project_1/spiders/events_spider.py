import os
import json
import jdatetime
from bs4 import BeautifulSoup
import scrapy
from project_1 import items


class EventsSpider(scrapy.Spider):
	name = "events"
	allowed_domains = ["evand.com"]
	start_urls = [
		"https://evand.com/categories/%D8%AA%DA%A9%D9%86%D9%88%D9%84%D9%88%DA%98%DB%8C"]
	
	def parse(self, response, **kwargs):
		"""
		Main parser. Retrieves the 'تکنولوژی' page response and parses all of the
		events listed there via the `parse_event` function.

		:param response: Response of the page which is scrapy.http.Response().
		:param kwargs: Arbitrary keyword arguments.
		"""
		
		event_xpath = '//*[@id="root"]/div/div[2]/div[2]/div/div[2]/div/div/section[*]/a'
		# Since there are two possible xpath for next page
		# (first page and the other pages)
		next_url_xpath1 = '//*[@id="root"]/div/div[2]/div[2]/div/div[2]/div/nav/ul/li/a'
		text_next_page1 = '//*[@id="root"]/div/div[2]/div[2]/div/div[2]/div/nav/ul/li/a/span'
		
		next_url_xpath2 = '//*[@id="root"]/div/div[2]/div[2]/div/div[2]/div/nav/ul/li[2]/a'
		text_next_page2 = '//*[@id="root"]/div/div[2]/div[2]/div/div[2]/div/nav/ul/li[2]/a/span'
		
		# Get all events link in a page at first and parse them.
		events = response.xpath(event_xpath)
		for event in events:
			yield response.follow(url=event, callback=self.parse_event)
		
		# If the next page exist, it should be crawled as new link.
		next_page_url1 = response.xpath(next_url_xpath1)
		next_page_url2 = response.xpath(next_url_xpath2)
		
		next_page_text1 = response.xpath(text_next_page1).get()
		next_page_text2 = response.xpath(text_next_page2).get()
		
		if next_page_url1 is not None and next_page_text1 is not None and \
				'صفحه بعد' in next_page_text1:
			yield response.follow(url=next_page_url1[0], callback=self.parse)
		elif next_page_url2 is not None and next_page_text2 is not None and \
				'صفحه بعد' in next_page_text2:
			yield response.follow(url=next_page_url2[0], callback=self.parse)
	
	def parse_event(self, response):
		"""
		The event parser retrieves the response and extracts the seven
		required fields: The event title, holding time, status, holder,
		prices, registration dates for each price, and the description path.
		After getting all the information, a scrapy Item called Event is
		created and all the fields are assigned.
		
		The fields title, holding time, status, and holder are easily
		retrieved using a simple response.xpath().get() using the specific
		xpath of the element.
		
		The other fields are a bit harder to get since they are not put in
		the base html file. Luckily, the needed information was in a
		react code which contained all the fields that were to be updated.
		Having the react code (the heart is actually a json object),
		the location of every field is found and extracted.
		
		In the description path, for each event page, an html file is saved
		containing the description of the event without the style.
		
		Returns nothing if the page is not an event page.
		Otherwise, The Item object will be returned.
		
		:param response: Response of the page which is scrapy.http.Response().
		:returns item: The Event item which is a subclass of scrapy.Item.
		"""
		
		if "categories" in response.request.url:
			return
		
		# Define our desired XPaths to use it later
		title_xpath = '//*[@id="page"]/div/header/section/div[2]/div[1]/h1/text()'
		holding_time_xpath = '//*[@id="page"]/div/header/section/div[2]/div[1]/div/span/text()'
		holding_status_xpath = '//*[@id="page"]/div/header/section/div[2]/div[2]/ul/li[2]/div/span/text()'
		holder_xpath = '//*[@id="page"]/div/div[2]/div/div[1]/div/div/div/div[@*]/div/section/a/div/h4/text()'
		
		title = response.xpath(title_xpath).get()
		holding_time = response.xpath(holding_time_xpath).get()
		holding_status = self.indicate_holding_status(
			response.xpath(holding_status_xpath).get())
		holder = response.xpath(holder_xpath).get()
		
		item = items.Event()
		item["title"] = title
		item["holding_time"] = holding_time
		item["holding_status"] = holding_status
		item["holder"] = holder
		
		# Getting the react code which contains the last 3 fields that were
		# going to be updated.
		react_part = response.css("body > script::text").getall()[0]
		full_data = self.extract_json(react_part)
		
		# Getting the prices of all the tickets.
		prices = self.extract_prices(json.loads(full_data))
		item["prices"] = prices
		
		# Each ticket has a registration date; Getting those!
		registration_dates = self.extract_reg_dates(json.loads(full_data))
		item["registration_dates"] = registration_dates
		
		# Getting the description of the page and handling the images inside.
		description = response.css(".description-content").getall()
		html_directory = "Description Files/" + self.name + '/'
		# If there is a description, handle it.
		if description:
			self.handle_description(html_directory, title, description[0],
			                        json.loads(full_data), response)
		file_name = ""
		if os.path.isfile(html_directory + str(title) + ".html"):
			file_name = html_directory + str(title) + ".html"
		item["description_path"] = file_name
		
		yield item
	
	@staticmethod
	def indicate_holding_status(text: str) -> str:
		"""
		The persian text shows how the event will be held, either Online or
		In-place. If the persian text is 'آنلاین', then we will return 'Online'.
		Otherwise, 'In-Person' is returned.

		:param text: The persian text indicating the status of the event
		:return: The english equivalent of the persian text
		"""
		
		return 'Online' if text == 'آنلاین' else 'In-Person'
	
	@staticmethod
	def extract_json(react_part: str) -> str:
		"""
		The react code contains a large json text which is extracted in this
		function.
		
		:param react_part: The react code which was hard-coded in the html.
		:return: The json in the react code.
		"""
		
		start = react_part.index('{')
		finish = len(react_part) - react_part[::-1].index('}')
		return react_part[start: finish]
	
	@staticmethod
	def extract_prices(full_json: dict) -> list:
		"""
		Extracts the prices from the full json (which contains all the
		fields that are going to be updated in the html file).
		
		If a price is equal to 0, then it is replaced with the word 'free'.
		
		:param full_json: The full json which is actually a dictionary.
		:return: The list of all the ticket prices.
		"""
		
		tickets = full_json["event"]["data"]["tickets"]["data"]
		prices = [ticket["price"] for ticket in tickets]
		return ["free" if p == 0 else p for p in prices]
	
	def extract_reg_dates(self, full_json: dict) -> list:
		"""
		Extracts the registration dates from the full json
		(which contains all the fields that are going to be updated in
		the html file).
		
		Each ticket has its own price and registration date. The returned list
		respects the 'prices' list meaning that at each index, the 'prices'
		value corresponds to that of 'registration_dates' list.
		
		Since the dates are in Gregorian calendar, they are converted to
		Jalali calender which is used in this country.
		
		**Note**: All the registration dates that are `null` are replaced with the
		event holding time.
		
		:param full_json: The full json which is actually a dictionary.
		:return: The list of all the registration dates.
		"""
		
		tickets = full_json["event"]["data"]["tickets"]["data"]
		showtime_end_dates = [ticket["showtime"]["data"]["end_date"]
		                      for ticket in tickets]
		dates = [ticket["end_date"] for ticket in tickets]
		new_dates = [showtime_end_dates[i] if date is None else date for
		             i, date in enumerate(dates)]
		jalali_dates = [self.covert_to_jalali(date) for date in new_dates]
		return jalali_dates
	
	@staticmethod
	def covert_to_jalali(date: str) -> str:
		"""
		Converts a date in Gregorian format to a date in Jalali format!
		
		:param date: The date in Gregorian format.
		:return: The date in Jalali format.
		"""
		date = str(date).split('T')[0]
		y, m, d = [int(s) for s in date.split('-')]
		return str(jdatetime.date.fromgregorian(year=y, month=m, day=d))
	
	def handle_description(self, html_directory: str, title: str,
	                       description: str, full_json: dict,
	                       response) -> None:
		"""
		Since all the images in the description part in the base html file are
		an specific template image, we need to replace them with the images
		that they are going to be replaced with.
		
		This function the most code and indeed is a bit complicated
		compared to the other ones.
		
		First of all, we specify the sections of description which contain
		an image. For this, `header_link` dictionary is created which maps
		each section header name (which contains images) with a list of image
		links that are inside that section.
		
		Next, a mapping of image name to links are needed so that later on
		we can understand the name of each image.
		
		After these steps, the `src` attribute of every image is replaced with
		the corresponding link which was found earlier and the `alt` attribute
		is replaced with the actual name which is already there in the
		`name_link` dictionary.

		:param html_directory: Where to save the html file.
		:param title: The title of the event which is the name of the html file.!
		:param description: The full description of the page.
		:param full_json: The full json which is actually a dictionary.
		:param response: Response of the page which is scrapy.http.Response().
		"""
		
		header_link = {}
		name_link = {}
		data = full_json["eventDescription"]["response"]["data"]
		for part in data:
			header = part["title"]
			if "content" in part.keys() and self.has_image(part["content"]):
				for image in part["content"]:
					# Do we have any image in this section?
					if isinstance(image, dict) and "image" in image.keys():
						link = image["image"]
						if header in header_link:
							header_link[header].append(link)
						else:
							header_link[header] = []
							header_link[header].append(link)
						
						if "name" in image.keys():
							name_link[image["name"]] = link
						else:
							name_link[""] = link
		
		headers, ids = [], []
		for header in response.css(".description-content h2::text").getall():
			headers.append(header)
		for idx in response.css(".description-content h2::attr(id)").getall():
			ids.append(idx)
		
		# bs4 library is used for replacing the attributes.
		soup = BeautifulSoup(description, features="lxml")
		for header in header_link.keys():
			tag_id = ids[headers.index(header)]
			target = "#%s" % tag_id
			images = soup.select(target)[0].parent.find_all("img")
			for img in images:
				image_name = img["alt"] if "alt" in img.attrs.keys() else ""
				if image_name in name_link.keys():
					img["src"] = name_link[image_name]
					img["height"] = 200
					img["width"] = 200
		
		self.save_description_to_file(html_directory, title, soup)
	
	@staticmethod
	def save_description_to_file(html_directory: str, title: str,
	                             soup: BeautifulSoup) -> None:
		"""
		The extracted description lacks some attributes and tags which are
		added in this function. `dir` and `lang` attribute for `html` tag and
		`meta` and `title` tag for new `head` tag.
		
		:param html_directory: Where to save the html file.
		:param title: The title of the event which is the name of the html file.!
		:param soup: The BeautifulSoup objects which contains the html code.
		"""
		
		soup.find("html")["dir"] = "rtl"
		soup.find("html")["lang"] = "en"
		head_tag = soup.new_tag("head")
		meta = soup.new_tag("meta", charset="UTF-8")
		page_title = soup.new_tag("title")
		page_title.string = title
		head_tag.append(meta)
		head_tag.append(page_title)
		soup.html.insert(0, head_tag)
		
		# After the changes, save the file.
		os.makedirs(html_directory, exist_ok=True)
		with open(html_directory + str(title).replace('/', '&') + ".html",
		          "wb+") as file:
			file.write(soup.encode("UTF-8"))
	
	@staticmethod
	def has_image(content: list) -> bool:
		"""
		Checks whether or not we have any images in the specified section in
		the description.

		:param content: The content of that section.
		:return: A boolean indicating whether we have any images or not.
		"""
		ret = False
		if isinstance(content, list):
			for part in content:
				if isinstance(part, dict) and "image" in part.keys():
					ret = True
		return ret
