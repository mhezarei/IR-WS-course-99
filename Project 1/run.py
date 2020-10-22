import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler


def some_job():
	# The timestamp is built and passed to the crawler.
	name = datetime.datetime.now(datetime.timezone.utc).strftime(
		"%Y-%m-%d %H:%M:%S")
	os.system(
		'cd project_1 && scrapy crawl -a name="%s" events -L WARNING' % name)


scheduler = BlockingScheduler()
# Every 4 hours starting from now.
scheduler.add_job(some_job, 'interval', hours=4,
                  next_run_time=datetime.datetime.now())
scheduler.start()
