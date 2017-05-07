# coding: utf-8
import MySQLdb
import logging
from buildings.models import Building
from buildings.utils import add_a_new_address
from django.db.models import F
from search.utils import query_to_dicts
from django.dispatch import Signal

empty_result = Signal(providing_args=["query"])

logger = logging.getLogger(__name__)


class Search(object):
    def __init__(self, host='127.0.0.1', port=9306, user='root', password=''):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def query(self, q, limit=0, offset=0, zipcode=None, show_additional=True, index_name='skyline_idx'):
        automatically_added = False
        address_is_not_exist = False
        logger.debug(u'===================== QUERY =====================')
        logger.debug(u'q: %s' % q.encode('utf-8'))
        logger.debug(u'limit: %s' % limit)
        logger.debug(u'offset: %s' % offset)
        logger.debug(u'zipcode: %s' % zipcode)
        logger.debug(u'show additional: %s' % show_additional)
        logger.debug(u'index name: %s' % index_name)

        # connect
        db = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port,
                             cursorclass=MySQLdb.cursors.DictCursor)
        cursor = db.cursor()

        sphinx_base = '@(building_name,address,city,state,zipcode) '
        sphinx_base_zip_only = '@(city,zipcode,state) '
        sphinx_options = "OPTION ranker=expr('sum(lcs*user_weight)*1000+bm25+total_marketplace*1000')"
        sphinx_query = sphinx_base + q.encode('utf-8')

        logger.debug('Sphinx query: %s' % sphinx_query)

        sphinx_full_query = "select * from %s where match('%s')" % (index_name, sphinx_query)
        sphinx_full_query += ' LIMIT %s,%s %s' % (offset, limit, sphinx_options)

        logger.debug('Sphinx full query: %s' % sphinx_full_query)

        sphinx_result = cursor.execute(sphinx_full_query)

        # commit your changes
        db.commit()

        ids = []

        zipcode_of_first_result = None
        diff = 0

        if zipcode:
            zipcode_of_first_result = zipcode

        logger.debug('Zip code of first result from zipcode: %s' % zipcode_of_first_result)

        # get the number of rows in the resultset
        numrows = int(cursor.rowcount)



        if numrows > 0:
            logger.debug('############# FOUND: %s ###############' % numrows)
            for x in range(0, numrows):
                row = cursor.fetchone()
                ids.append(row['id'])

                if not zipcode_of_first_result:
                    zipcode_of_first_result = row['zipcode_attr']
                    logger.debug('Zip code of first result from result: %s' % zipcode_of_first_result)
        else:
            logger.debug('############# NOT FOUND ###############')
            logger.debug('Try to query smartystreets...')
            automatically_added, address_is_not_exist = add_a_new_address(q.encode('utf-8'))


        logger.debug(u'Automatically added: %s' % automatically_added)
        logger.debug(u'Address is not exist: %s' % address_is_not_exist)

        if not zipcode_of_first_result or zipcode_of_first_result == '':
            if zipcode and zipcode != '':
                zipcode_of_first_result = zipcode
            else:
                zipcode_of_first_result = '90017'  # downtown

        logger.debug(u'Zip code of first result: %s' % zipcode_of_first_result)

        if show_additional:
            logger.debug(u'Show additional')

            if not ids or len(ids) < 100:
                logger.debug(u'Trying to add a set of building by zipcode')

                diff = 100 - len(ids)
                sphinx_additional_query = "select * from %s where match('%s%s')" % (
                    index_name, sphinx_base_zip_only, zipcode_of_first_result)
                sphinx_additional_query += ' LIMIT %s %s' % (diff, sphinx_options)
                sphinx_additional_result = cursor.execute(sphinx_additional_query)

                logger.debug(u'Additional query: %s' % sphinx_additional_query)

                # commit your changes
                db.commit()

                numrows = int(cursor.rowcount)

                logger.debug(u'Num rows (additional): %s' % numrows)

                if numrows > 0:
                    for x in range(0, numrows):
                        row = cursor.fetchone()
                        ids.append(row['id'])
                else:
                    logger.debug(u'Not found by zipcode too, trying to use 90017')
                    # show 90017
                    sphinx_additional_query = "select * from %s where match('%s%s')" % (
                        index_name, sphinx_base_zip_only, 90017)
                    sphinx_additional_query += ' LIMIT %s %s' % (diff, sphinx_options)
                    sphinx_additional_result = cursor.execute(sphinx_additional_query)
                    logger.debug(u'Additional query: %s' % sphinx_additional_query)

                    # commit your changes
                    db.commit()

                    numrows = int(cursor.rowcount)

                    for x in range(0, numrows):
                        row = cursor.fetchone()
                        ids.append(row['id'])

        sphinx_cnt_query = "select count(*) as cnt from %s where match('%s') %s" % (
            index_name, sphinx_query, sphinx_options)

        logger.debug(u'Matching queries cnt: %s' % sphinx_cnt_query)
        sphinx_cnt_result = cursor.execute(sphinx_cnt_query)

        # commit your changes
        db.commit()

        numrows = int(cursor.rowcount)

        if (numrows > 0):
            total_cnt = cursor.fetchone()['cnt']
        else:
            total_cnt = 0

        logger.debug(u'Total fully matched count: %s' % total_cnt)

        logger.debug(u'IDS for results: %s' % ids)
        logger.debug(u'Len IDS for results: %s' % len(ids))

        if ids:
            res = Building.objects.filter(property_id__in=ids).distinct().extra(
                select={'manual': 'FIELD(property_id,%s)' % ','.join(map(str, ids))},
                order_by=['manual']
            ).distinct()

            if len(res) > 0:
                logger.debug(u'Result count: %s' % len(res))
                return [len(res), res, automatically_added, address_is_not_exist]

        logger.debug(u'Result count: %s' % 0)

        return [0, [], automatically_added, address_is_not_exist]
