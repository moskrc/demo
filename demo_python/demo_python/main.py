#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import logging
import sqlite3
import re
from grab.spider import Spider, Task

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('scraper')

additional_headers = {
    'Accept-Charset': 'utf-8',
    'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'
}


class DBWrapper():
    def __init__(self, *args, **kwargs):
        self.conn = sqlite3.connect("data.sqlite")
        #self.conn = sqlite3.connect(":memory:")

    def create_category(self, name, parent_id):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO categories(title, parent_id) VALUES (?, ?)", (name, parent_id))
        self.conn.commit()
        return cur.lastrowid

    def create_post(self, category_id, post):
        cur = self.conn.cursor()

        post['category_id'] = category_id

        columns = ', '.join(post.keys())
        placeholders = ', '.join('?' * len(post))

        sql = 'INSERT INTO posts ({}) VALUES ({})'.format(columns, placeholders)

        cur.execute(sql, post.values())
        self.conn.commit()
        return cur.lastrowid

    def create_address(self, post_id, adr):
        cur = self.conn.cursor()
        cur.execute("""INSERT INTO addresses(address, is_main,
        tel1, tel1_owner,
        tel2, tel2_owner,
        tel3, tel3_owner,
        post_id)
        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (adr['address'], adr['is_main'], adr['tel1'], adr['tel1_owner'], adr['tel2'], adr['tel2_owner'], adr['tel3'], adr['tel3_owner'], post_id))
        self.conn.commit()
        return cur.lastrowid

    def create_tables(self):
        cur = self.conn.cursor()
        cur.executescript("""
        DROP TABLE IF EXISTS categories;
        DROP TABLE IF EXISTS posts;
        DROP TABLE IF EXISTS addresses;

        CREATE TABLE categories(id INTEGER PRIMARY KEY, title TEXT, parent_id INTEGER);

        CREATE TABLE posts(
            id INTEGER PRIMARY KEY,
            title TEXT,
            director TEXT,
            d_type TEXT,
            d_view TEXT,
            funding TEXT,
            legal_form TEXT,
            submission TEXT,
            district TEXT,
            region TEXT,
            founder TEXT,
            forms_of_study TEXT,
            max_people TEXT,
            license TEXT,
            accreditation TEXT,
            email TEXT,
            inn TEXT,
            kpp TEXT,
            ogrn TEXT,
            okato TEXT,
            category_id INTEGER);

        CREATE TABLE addresses(
            id INTEGER PRIMARY KEY,
            post_id INTEGER,
            address TEXT,
            is_main INTEGER,
            tel1 TEXT, tel1_owner TEXT,
            tel2 TEXT, tel2_owner TEXT,
            tel3 TEXT, tel3_owner TEXT);
        """)
        self.conn.commit()
        return cur.lastrowid


class Educom(Spider):
    initial_urls = [
        'http://www.educom.ru/_ekis/eduoffices/gateways/portal_eo_catalog.php',
        #'http://www.educom.ru/_ekis/eduoffices/gateways/portal_eo_catalog.php?path=1:7'
    ]

    def __init__(self, *args, **kwargs):
        super(Educom, self).__init__(*args, **kwargs)
        self.setup_grab(headers=additional_headers)
        self.db = DBWrapper()
        self.db.create_tables()

    def prepare(self):
        self.parsed_urls = []
        self.parsed_items = []
        self.parsed_categories = []
        self.failed_items = []

    def shutdown(self):
        print u"Parsed categories: %s" % len(self.parsed_categories)
        print u"Parsed items: %s" % len(self.parsed_items)
        print u"Parsed URLs: %s" % len(self.parsed_urls)

    def task_initial(self, grab, task):
        for item in grab.css_list("ul li a"):
            cat_name = item.text_content().strip()
            cat_url = item.attrib['href']

            yield Task('category',
                       url=grab.make_url_absolute(cat_url, resolve_base=True),
                       title=cat_name,
                       parent=None,
                       cat_id=None)

    def task_category(self, grab, task):
        log.info('Category URL %s, id %s, title %s, parent %s' % (task.url, task.cat_id, task.title, task.parent))

        if not task.cat_id:
            cat_id = self.db.create_category(task.title, task.parent)
        else:
            log.info('founded')
            cat_id = task.cat_id

        # Подразделы
        for item in grab.css_list("ul li a"):
            cat_name = item.text_content().strip()
            cat_url = item.attrib['href']

            yield Task('category',
                       url=grab.make_url_absolute(cat_url, resolve_base=True),
                       title=cat_name,
                       parent=cat_id,
                       cat_id=None)

        # Есть товары
        if grab.css_list('table.tahoma'):
            for i in grab.css_list('table td a'):
                yield Task('post',
                           url=grab.make_url_absolute(i.attrib['href'], resolve_base=True),
                           title=i.text_content(),
                           category=cat_id, )

        # Ищем сл. страницу если страниц у категории много
        for a in grab.css_list('p a'):
            if u'вперед' in a.text_content():
                next_page_url = a.attrib['href']
                if next_page_url not in self.parsed_urls:
                    self.parsed_urls.append(next_page_url)
                    yield Task('category',
                               url=grab.make_url_absolute(next_page_url, resolve_base=True),
                               title=task.title,
                               parent=task.parent,
                               cat_id=cat_id)

    def task_post(self, grab, task):
        log.info('Post URL %s, title %s, category %s' % (task.url, task.title, task.category))

        db_fields = {
            u'Директор': 'director',
            u'Тип': 'd_type',
            u'Вид': 'd_view',
            u'Финансирование': 'funding',
            u'Организационно-правовая форма': 'legal_form',
            u'Подчинение': 'submission',
            u'Округ': 'district',
            u'Район': 'region',
            u'Учредитель': 'founder',
            u'Формы обучения': 'forms_of_study',
            u'Максимальное число учащихся': 'max_people'
        }

        post = {}

        keys = []
        vals = []

        for item in grab.tree.xpath("//p[1]"):
            for j, x in enumerate(item.itertext()):
                text = x.replace(u'—', '').strip()
                if len(text) > 1:
                    if j % 2 == 0:
                        vals.append(text)
                    else:
                        keys.append(text)

        for x in zip(keys, vals):
            post[db_fields[x[0]]] = x[1]

        body = grab.response.unicode_body()


        # license

        post['license'] = None

        if body.find(u'Лицензия') > 0:
            try:
                for item in grab.tree.xpath("//p[2]"):
                    text = item.text_content().split(u'—')[1].strip()
                    license = re.sub(' +', ' ', text).replace('\n', '')
                    post['license'] = license
            except:
                pass


        # accreditation

        post['accreditation'] = None

        if body.find(u'Аккредитация') > 0:
            try:
                for item in grab.tree.xpath("//p[3]"):
                    text = item.text_content().split(u'—')[1].strip()
                    accreditation = re.sub(' +', ' ', text).replace('\n', '')
                    post['accreditation'] = accreditation
            except:
                pass


        # email

        post['email'] = None

        if body.find(u'Контактный e-mail') > 0:
            try:
                for item in grab.tree.xpath("//p[5]"):
                    text = item.text_content().split(u'—')[1].strip()
                    email = re.sub(' +', ' ', text).replace('\n', '')
                    post['email'] = email
            except:
                pass


        # bank

        bank_found = False
        bank_data = [u'Огрн', u'Инн', u'Кпп', u'ОКАТО']
        for x in bank_data:
            if body.find(x) > 0:
                bank_found = True

        if bank_found:

            binfo = re.compile(u'<strong>Инн(.*?)<!--', re.DOTALL | re.IGNORECASE).findall(body)[0]
            binfo = binfo.replace('</strong>', '')
            binfo = binfo.replace('<strong>', '')
            binfo = binfo.replace('<br/>', '')
            binfo = binfo.replace('&nbsp;', '')
            binfo = binfo.replace('&#8212;', '')
            binfo = u'Инн' + binfo


            post['inn'] = post['kpp'] = post['ogrn'] = post['okato'] = None

            bank_info_lines = re.findall('([\D]+\d+)', binfo)
            for l in bank_info_lines:
                if u'Инн' in l:
                    post['inn'] = l.split(' ')[1]
                if u'Кпп' in l:
                    post['kpp'] = l.split(' ')[1]
                if u'Огрн' in l:
                    post['ogrn'] = l.split(' ')[1]
                if u'ОКАТО' in l:
                    post['okato'] = l.split(' ')[1]


        for m in db_fields:
            if db_fields[m] not in post:
                post[db_fields[m]] = None

        post['title'] = task.title

        new_post_id = self.db.create_post(task.category, post)

        # address

        tds = ['address', 'is_main', 'tel1', 'tel1_owner', 'tel2', 'tel2_owner', 'tel3', 'tel3_owner']

        for r in grab.tree.xpath("//ul/table/tr"):
            adr = {}
            for z, td in enumerate(r.cssselect('td')):
                adr[tds[z]] = td.text_content().strip()

            if 'address' in adr:
                self.db.create_address(new_post_id, adr)


if __name__ == '__main__':
    bot = Educom(thread_number=1, request_pause=0.3)

    try:
        bot.run()
    except KeyboardInterrupt:
        pass

    print bot.render_stats()

