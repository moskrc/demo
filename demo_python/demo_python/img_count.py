#!/usr/bin/env python

from __future__ import division
from Queue import Queue
from threading import Thread
import json
import math
import re
import logging

from lxml.html import fromstring
import requests


# ----------------------------------------------------------------------------
# SETTINGS
# ----------------------------------------------------------------------------

API_KEY = 'hz54u92dhdukkcmxpmyr6rbk'
PER_PAGE = 50

# ----------------------------------------------------------------------------
# LOGGER
# ----------------------------------------------------------------------------

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

# create a file handler and set level to debug
ch = logging.FileHandler('img_count.log')
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


# ----------------------------------------------------------------------------


class CommonThread(Thread):
    def __init__(self, queue, instance):
        Thread.__init__(self)
        self.queue = queue
        self.instance = instance


class RottenTomatoesWorker(CommonThread):
    def run(self):
        while True:
            page = self.queue.get()
            # collect movies
            self.instance.updateMovies(self.instance.getInTheaterMovies(page)[0])
            self.queue.task_done()


class ImdbWorker(CommonThread):
    def run(self):
        while True:
            m = self.queue.get()
            # get imdb_id and images_count for a movie
            imdb, images_count = self.instance.processMovie(m)
            logger.debug('Movie: %s is done! [imdb: %s, images: %s]' % (m['title'], imdb, images_count))
            # append this result to results
            self.instance.updateResults(
                {'url': 'http://www.imdb.com/title/tt%s' % imdb, 'count': int(images_count), 'imdb_id': imdb});
            self.queue.task_done()


class ImageCounter(object):
    """
    Todo:
    - Use the rottentomatoes.com API to get the list all of movies currently in theaters
    - For-each movie in the list, download it's matching IMDB page and get a count of the number of images in the page.
    """
    def __init__(self, api_key, per_page=10, rotten_tomatoes_threads=8, imdb_threads=50):
        logger.debug('api_key: %s, per_page: %s, rotten_tomatoes_threads: %s, imdb_threads: %s' % (
            api_key, per_page, rotten_tomatoes_threads, imdb_threads
        ))

        self.api_key = api_key
        self.per_page = per_page
        self.rotten_tomatoes_threads_count = rotten_tomatoes_threads
        self.imdb_threads_count = imdb_threads
        self.results = []
        self.movies = []

    def getPageContent(self, url, params=None):
        """
        Get HTML
        :param url: URI
        :param params: params for GET request
        :return:
        """
        try:
            r = requests.get(url, params=params, timeout=1)
            logger.debug('Get: %s' % r.url)
        except requests.exceptions.RequestException as e:
            logger.error(e)
            raise e

        return r.content

    def updateMovies(self, data):
        """
        For RottenTomatoesWorker thread
        :param data: a dict
        :return:
        """
        self.movies.extend(data)

    def updateResults(self, data):
        """
        For ImdbWorker thread
        :param data: a list
        :return:
        """
        self.results.append(data);

    def getInTheaterMovies(self, page):
        """
        Get list of movies
        :param page: page num
        :return: list of movies for current page and total movies
        """
        url = "http://api.rottentomatoes.com/api/public/v1.0/lists/movies/in_theaters.json"
        params = {'apikey': API_KEY, 'page_limit': PER_PAGE, 'page': page, 'country': 'us'}

        data = self.getPageContent(url, params)

        js = json.loads(data)
        return js["movies"], js['total']

    def getImdbIdByTitle(self, title):
        """
        Find a movie's imdb id by title
        :param title: movie title
        :return: imdb_id
        """
        data = self.getPageContent("http://www.imdb.com/find", {'q': title, 's': 'all'})

        root = fromstring(data)
        href = root.xpath("//table[contains(@class,'findList')]/tr/td/a/@href")[0]

        imdb_id = re.search(r'tt(\d+)', href).group(1)
        return imdb_id

    def getImagesCount(self, imdb_id):
        """
        Read total images count for a movie by imdb_id
        :param imdb_id: id of a movie on IMDB
        :return: images count
        """
        url = 'http://www.imdb.com/title/tt%s/mediaindex'
        data = self.getPageContent(url % imdb_id)

        root = fromstring(data)
        link = root.xpath("//div[@id='left']/text()")[0]

        images_count = re.search(r'(\d+) photo', link)

        if images_count is not None:
            try:
                return images_count.group(1)
            except IndexError:
                return 0
        else:
            return 0

    def processMovie(self, m):
        """
        Get images count for a movie
        :param m: movie
        :return: imdb_id, images_count
        """
        try:
            if 'alternate_ids' in m:
                imdb = m['alternate_ids']['imdb']
            else:
                imdb = self.getImdbIdByTitle(m['title'])

            return imdb, self.getImagesCount(imdb)

        except Exception as e:
            logger.debug(e)
            return 0, 0

    def grab(self):
        # get first page of movies and count of all movies
        self.movies, total = self.getInTheaterMovies(1)

        logger.debug('Total movies: %d' % total)

        # calculate pages
        total_pages = max(int(math.ceil(total / self.per_page)), 1)

        logger.debug('Total pages: %d' % total_pages)

        if total_pages > 1:

            logger.debug('More than one page, let\'s grab them all...')

            # queue for rottenTomatoes
            rt_queue = Queue()

            # threads
            for x in range(self.rotten_tomatoes_threads_count):
                worker = RottenTomatoesWorker(rt_queue, self)
                worker.setDaemon(True)
                worker.start()


            # start
            for page in xrange(1, total_pages):
                logger.debug('Starting grabbing page %d ...' % page)
                rt_queue.put(page + 1)

            rt_queue.join()

            logger.debug('Done')


        # queue for IMDB
        imdb_queue = Queue()

        logger.debug('Starting a set of thread for grabbing data for the movies')

        for x in range(self.imdb_threads_count):
            worker = ImdbWorker(imdb_queue, self)
            worker.setDaemon(True)
            worker.start()

        for m in self.movies:
            logger.debug('Movie: %s...' % m['title'])
            imdb_queue.put(m)

        imdb_queue.join()

        return self.results


if __name__ == "__main__":
    logger.debug('#' * 79)

    img_counter = ImageCounter(API_KEY, PER_PAGE)
    results = img_counter.grab()
    json_data = json.dumps(results)

    logger.debug('Total Movies for JSON: %s' % len(results))
    logger.debug('Done')

    # dump to json
    print json_data
