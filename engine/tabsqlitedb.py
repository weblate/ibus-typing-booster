# -*- coding: utf-8 -*-
# vim:et sts=4 sw=4
#
# ibus-typing-booster - A completion input method for IBus
#
# Copyright (c) 2011-2013 Anish Patil <apatil@redhat.com>
# Copyright (c) 2012-2018 Mike FABIAN <mfabian@redhat.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
'''
Module for ibus-typing-booster to access the sqlite3 databases
'''
import os
import os.path as path
import codecs
import unicodedata
import sqlite3
import time
import re
import logging
import itb_util
import hunspell_suggest

LOGGER = logging.getLogger('ibus-typing-booster')

DEBUG_LEVEL = int(0)

USER_DATABASE_VERSION = '0.65'

class TabSqliteDb:
    # pylint: disable=line-too-long
    '''Phrase databases for ibus-typing-booster

    The phrases table in the database has columns with the names:

    “id”, “input_phrase”, “phrase”, “p_phrase”, “pp_phrase”, “user_freq”, “timestamp”

    There are 2 databases, sysdb, userdb.

    sysdb: “Database” with the suggestions from the hunspell dictionaries
        user_freq = 0 always.

        Actually there is no Sqlite3 database called “sysdb”, these
        are the suggestions coming from hunspell_suggest, i.e. from
        grepping the hunspell dictionaries and from pyhunspell.
        (Historic note: ibus-typing-booster started as a fork of
        ibus-table, in ibus-table “sysdb” is a Sqlite3 database
        which is installed systemwide and readonly for the user)

    user_db: Database on disk where the phrases learned from the user are stored
        user_freq >= 1: The number of times the user has used this phrase
    '''
    # pylint: enable=line-too-long
    def __init__(self, user_db_file=''):
        global DEBUG_LEVEL
        try:
            DEBUG_LEVEL = int(os.getenv('IBUS_TYPING_BOOSTER_DEBUG_LEVEL'))
        except (TypeError, ValueError):
            DEBUG_LEVEL = int(0)
        if DEBUG_LEVEL > 1:
            LOGGER.debug(
                'TabSqliteDb.__init__(user_db_file = %s)', user_db_file)
        self.user_db_file = user_db_file
        if not self.user_db_file:
            self.user_db_file = path.join(
                os.getenv('HOME'), '.local/share/ibus-typing-booster/user.db')
        if (self.user_db_file != ':memory:'
                and not os.path.isdir(os.path.dirname(self.user_db_file))):
            os.makedirs(os.path.dirname(self.user_db_file))
        self._phrase_table_column_names = [
            'id',
            'input_phrase',
            'phrase',
            'p_phrase',
            'pp_phrase',
            'user_freq',
            'timestamp']

        self.old_phrases = []

        self.hunspell_obj = hunspell_suggest.Hunspell(())

        if self.user_db_file != ':memory:':
            if not os.path.exists(self.user_db_file):
                LOGGER.info(
                    'The user database %(udb)s does not exist yet.',
                    {'udb': self.user_db_file})
            else:
                try:
                    desc = self.get_database_desc(self.user_db_file)
                    if (desc is None
                            or desc["version"] != USER_DATABASE_VERSION
                            or (self.get_number_of_columns_of_phrase_table(
                                self.user_db_file)
                                != len(self._phrase_table_column_names))):
                        LOGGER.info(
                            'The user database %(udb)s seems incompatible',
                            {'udb': self.user_db_file})
                        if desc is None:
                            LOGGER.info(
                                'No version information in the database')
                        elif desc["version"] != USER_DATABASE_VERSION:
                            LOGGER.info(
                                'The version of the database does not match '
                                '(too old or too new?)')
                            LOGGER.info(
                                'ibus-typing-booster wants version=%s',
                                USER_DATABASE_VERSION)
                            LOGGER.info(
                                'But the  database actually has version=%s',
                                desc["version"])
                        elif (self.get_number_of_columns_of_phrase_table(
                                self.user_db_file)
                              != len(self._phrase_table_column_names)):
                            LOGGER.info(
                                'The number of columns of the database '
                                'does not match')
                            LOGGER.info(
                                'ibus-typing-booster expects %(col)s columns',
                                {'col': len(self._phrase_table_column_names)})
                            LOGGER.info(
                                'The database actually has %(col)s columns',
                                {'col':
                                 self.get_number_of_columns_of_phrase_table(
                                     self.user_db_file)})
                        LOGGER.info(
                            'Trying to recover the phrases from the old, '
                            'incompatible database')
                        self.old_phrases = self.extract_user_phrases()
                        timestamp = time.strftime('-%Y-%m-%d_%H:%M:%S')
                        LOGGER.info(
                            'Renaming the incompatible database to "%(name)s"',
                            {'name': self.user_db_file+timestamp})
                        if os.path.exists(self.user_db_file):
                            os.rename(self.user_db_file,
                                      self.user_db_file+timestamp)
                        if os.path.exists(self.user_db_file+'-shm'):
                            os.rename(self.user_db_file+'-shm',
                                      self.user_db_file+'-shm'+timestamp)
                        if os.path.exists(self.user_db_file+'-wal'):
                            os.rename(self.user_db_file+'-wal',
                                      self.user_db_file+'-wal'+timestamp)
                        LOGGER.info(
                            'Creating a new, empty database "%(name)s".',
                            {'name': self.user_db_file})
                        self.init_user_db()
                        LOGGER.info(
                            'If user phrases were successfully recovered '
                            'from the old, '
                            'incompatible database, they will be used to '
                            'initialize the new database.')
                    else:
                        LOGGER.info(
                            'Compatible database %(db)s found.',
                            {'db': self.user_db_file})
                except Exception:
                    LOGGER.exception(
                        'Unexpected error trying to find user database.')

        # open user phrase database
        try:
            LOGGER.info(
                'Connect to the database %(name)s.',
                {'name': self.user_db_file})
            self.database = sqlite3.connect(self.user_db_file)
            self.database.executescript('''
                PRAGMA encoding = "UTF-8";
                PRAGMA case_sensitive_like = true;
                PRAGMA page_size = 4096;
                PRAGMA cache_size = 20000;
                PRAGMA temp_store = MEMORY;
                PRAGMA journal_mode = WAL;
                PRAGMA journal_size_limit = 1000000;
                PRAGMA synchronous = NORMAL;
                ATTACH DATABASE "%s" AS user_db;
            ''' % self.user_db_file)
        except Exception:
            LOGGER.exception(
                'Could not open the database %(name)s.',
                {'name': self.user_db_file})
            timestamp = time.strftime('-%Y-%m-%d_%H:%M:%S')
            LOGGER.info(
                'Renaming the incompatible database to "%(name)s".',
                {'name': self.user_db_file+timestamp})
            if os.path.exists(self.user_db_file):
                os.rename(self.user_db_file, self.user_db_file+timestamp)
            if os.path.exists(self.user_db_file+'-shm'):
                os.rename(self.user_db_file+'-shm',
                          self.user_db_file+'-shm'+timestamp)
            if os.path.exists(self.user_db_file+'-wal'):
                os.rename(self.user_db_file+'-wal',
                          self.user_db_file+'-wal'+timestamp)
            LOGGER.info(
                'Creating a new, empty database "%(name)s".',
                {'name': self.user_db_file})
            self.init_user_db()
            self.database = sqlite3.connect(self.user_db_file)
            self.database.executescript('''
                PRAGMA encoding = "UTF-8";
                PRAGMA case_sensitive_like = true;
                PRAGMA page_size = 4096;
                PRAGMA cache_size = 20000;
                PRAGMA temp_store = MEMORY;
                PRAGMA journal_mode = WAL;
                PRAGMA journal_size_limit = 1000000;
                PRAGMA synchronous = NORMAL;
                ATTACH DATABASE "%s" AS user_db;
            ''' % self.user_db_file)
        self.create_tables()
        if self.old_phrases:
            sqlargs = []
            for ophrase in self.old_phrases:
                sqlargs.append(
                    {'input_phrase': ophrase[0],
                     'phrase': ophrase[0],
                     'p_phrase': '',
                     'pp_phrase': '',
                     'user_freq': ophrase[1],
                     'timestamp': time.time()})
            sqlstr = '''
            INSERT INTO user_db.phrases (input_phrase, phrase, p_phrase, pp_phrase, user_freq, timestamp)
            VALUES (:input_phrase, :phrase, :p_phrase, :pp_phrase, :user_freq, :timestamp)
            ;'''
            try:
                self.database.executemany(sqlstr, sqlargs)
            except Exception:
                LOGGER.exception(
                    'Unexpected error inserting old phrases '
                    'into the user database.')
            self.database.commit()
            self.database.execute('PRAGMA wal_checkpoint;')

        # do not call this always on intialization for the moment.
        # It makes the already slow “python engine/main.py --xml”
        # to list the engines even slower and may break the listing
        # of the engines completely if there is a problem with
        # optimizing the databases. Probably bring this back as an
        # option later if the code in self.optimize_database() is
        # improved to do anything useful.
        #try:
        #    self.optimize_database()
        #except:
        #    print "exception in optimize_database()"
        #    traceback.print_exc ()

        # try create all hunspell-tables in user database
        self.create_indexes(commit=False)
        self.generate_userdb_desc()

    def update_phrase(self, input_phrase='', phrase='',
                      p_phrase='', pp_phrase='',
                      user_freq=0, commit=True):
        '''
        update the user frequency of a phrase
        '''
        if not input_phrase or not phrase:
            return
        input_phrase = itb_util.remove_accents(input_phrase)
        input_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, input_phrase)
        phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, phrase)
        p_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, p_phrase)
        pp_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, pp_phrase)
        sqlstr = '''
        UPDATE user_db.phrases
        SET user_freq = :user_freq, timestamp = :timestamp
        WHERE input_phrase = :input_phrase
         AND phrase = :phrase AND p_phrase = :p_phrase AND pp_phrase = :pp_phrase
        ;'''
        sqlargs = {'user_freq': user_freq,
                   'input_phrase': input_phrase,
                   'phrase': phrase,
                   'p_phrase': p_phrase,
                   'pp_phrase': pp_phrase,
                   'timestamp': time.time()}
        if DEBUG_LEVEL > 1:
            LOGGER.debug('sqlstr=%s', sqlstr)
            LOGGER.debug('sqlargs=%s', sqlargs)
        try:
            self.database.execute(sqlstr, sqlargs)
            if commit:
                self.database.commit()
        except Exception:
            LOGGER.exception('Unexpected error updating phrase in user_db.')

    def sync_usrdb(self):
        '''
        Trigger a checkpoint operation.
        '''
        if DEBUG_LEVEL > 1:
            LOGGER.debug('commit and execute checkpoint ...')
        self.database.commit()
        self.database.execute('PRAGMA wal_checkpoint;')
        if DEBUG_LEVEL > 1:
            LOGGER.debug('commit and execute checkpoint done.')

    def create_tables(self):
        '''Create table for the phrases.'''
        sqlstr = '''CREATE TABLE IF NOT EXISTS user_db.phrases
                    (id INTEGER PRIMARY KEY,
                    input_phrase TEXT, phrase TEXT, p_phrase TEXT, pp_phrase TEXT,
                    user_freq INTEGER, timestamp REAL);'''
        self.database.execute(sqlstr)
        self.database.commit()

    def add_phrase(self, input_phrase='', phrase='',
                   p_phrase='', pp_phrase='',
                   user_freq=0, commit=True):
        '''
        Add phrase to database
        '''
        if DEBUG_LEVEL > 1:
            LOGGER.debug(
                'input_phrase=%s phrase=%s user_freq=%s ',
                input_phrase.encode('UTF-8'),
                phrase.encode('UTF-8'),
                user_freq)
        if not input_phrase or not phrase:
            return
        input_phrase = itb_util.remove_accents(input_phrase)
        input_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, input_phrase)
        phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, phrase)
        p_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, p_phrase)
        pp_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, pp_phrase)
        select_sqlstr = '''
        SELECT * FROM user_db.phrases
        WHERE input_phrase = :input_phrase
        AND phrase = :phrase AND p_phrase = :p_phrase AND pp_phrase = :pp_phrase
        ;'''
        select_sqlargs = {
            'input_phrase': input_phrase,
            'phrase': phrase,
            'p_phrase': p_phrase,
            'pp_phrase': pp_phrase}
        if self.database.execute(select_sqlstr, select_sqlargs).fetchall():
            # there is already such a phrase, i.e. add_phrase was called
            # in error, do nothing to avoid duplicate entries.
            return

        insert_sqlstr = '''
        INSERT INTO user_db.phrases
        (input_phrase, phrase, p_phrase, pp_phrase, user_freq, timestamp)
        VALUES (:input_phrase, :phrase, :p_phrase, :pp_phrase, :user_freq, :timestamp)
        ;'''
        insert_sqlargs = {'input_phrase': input_phrase,
                          'phrase': phrase,
                          'p_phrase': p_phrase,
                          'pp_phrase': pp_phrase,
                          'user_freq': user_freq,
                          'timestamp': time.time()}
        if DEBUG_LEVEL > 1:
            LOGGER.debug('insert_sqlstr=%s', insert_sqlstr)
            LOGGER.debug('insert_sqlargs=%s', insert_sqlargs)
        try:
            self.database.execute(insert_sqlstr, insert_sqlargs)
            if commit:
                self.database.commit()
        except Exception:
            LOGGER.exception('Unexpected error adding phrase to database.')

    def optimize_database(self):
        '''
        Optimize the database by copying the contents
        to temporary tables and back.
        '''
        sqlstr = '''
            CREATE TABLE tmp AS SELECT * FROM %(database)s.phrases;
            DELETE FROM user_db.phrases;
            INSERT INTO user_db.phrases SELECT * FROM tmp ORDER BY
            input_phrase, user_freq DESC, id ASC;
            DROP TABLE tmp;'''
        self.database.executescript(sqlstr)
        self.database.executescript("VACUUM;")
        self.database.commit()

    def drop_indexes(self):
        '''Drop the index in database to reduce it's size'''
        sqlstr = '''
            DROP INDEX IF EXISTS user_db.phrases_index_p;
            DROP INDEX IF EXISTS user_db.phrases_index_i;
            VACUUM;
            '''

        self.database.executescript(sqlstr)
        self.database.commit()

    def create_indexes(self, commit=True):
        '''Create indexes for the database.'''
        sqlstr = '''
        CREATE INDEX IF NOT EXISTS user_db.phrases_index_p ON phrases
        (input_phrase, id ASC);
        CREATE INDEX IF NOT EXISTS user_db.phrases_index_i ON phrases
        (phrase)
        ;'''
        self.database.executescript(sqlstr)
        if commit:
            self.database.commit()

    def best_candidates(self, phrase_frequencies):
        '''Sorts the phrase_frequencies dictionary and returns the best
        candidates.
        '''
        return sorted(phrase_frequencies.items(),
                      key=lambda x: (
                          -1*x[1],   # user_freq descending
                          len(x[0]), # len(phrase) ascending
                          x[0]       # phrase alphabetical
                      ))[:20]

    def select_words(self, input_phrase, p_phrase='', pp_phrase=''):
        '''
        Get phrases from database completing input_phrase.

        Returns a list of matches where each match is a tuple in the
        form of (phrase, user_freq), i.e. returns something like
        [(phrase, user_freq), ...]
        '''
        input_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, input_phrase)
        p_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, p_phrase)
        pp_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, pp_phrase)
        if DEBUG_LEVEL > 1:
            LOGGER.debug(
                'input_phrase=%s p_phrase=%s pp_phrase=%s',
                input_phrase.encode('UTF-8'),
                p_phrase.encode('UTF-8'),
                pp_phrase.encode('UTF-8'))
        phrase_frequencies = {}
        if not ' ' in input_phrase:
            # Get suggestions from hunspell dictionaries. But only
            # if input_phrase does not contain spaces. The hunspell
            # dictionaries contain only single words, not sentences.
            # Trying to complete an input_phrase which contains spaces
            # will never work and spell checking suggestions by hunspell
            # for input which contains spaces is almost always nonsense.
            phrase_frequencies.update([
                x for x in self.hunspell_obj.suggest(input_phrase)])
        if DEBUG_LEVEL > 1:
            LOGGER.debug(
                'hunspell: best_candidates=%s',
                self.best_candidates(phrase_frequencies))
        # Remove the accents *after* getting the hunspell candidates.
        # If the accents were removed before getting the hunspell candidates
        # an input phrase like “Glühwürmchen” would not be added as a
        # candidate because hunspell would get “Gluhwurmchen” then and would
        # not validate that as a correct word. And, because “Glühwürmchen”
        # is not in the German hunspell dictionary as a single word but
        # created by suffix and prefix rules, the accent insensitive match
        # in the German hunspell dictionary would not find it either.
        input_phrase = itb_util.remove_accents(input_phrase)
        input_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, input_phrase)
        # Now phrase_frequencies might contain something like this:
        #
        # {'code': 0, 'communicability': 0, 'cold': 0, 'colour': 0}

        # To quote a string to be used as a parameter when assembling
        # an sqlite statement with Python string operations, remove
        # all NUL characters, replace " with "" and wrap the whole
        # string in double quotes. Assembling sqlite statements using
        # parameters containing user input with python string operations
        # is not recommended because of the risk of SQL injection attacks
        # if the quoting is not done the right way. So it is better to use
        # the parameter substitution of the sqlite3 python interface.
        # But unfortunately that does not work when creating views,
        # (“OperationalError: parameters are not allowed in views”).
        quoted_input_phrase = input_phrase.replace(
            '\x00', '').replace('"', '""')
        self.database.execute('DROP VIEW IF EXISTS like_input_phrase_view;')
        sqlstr = '''
        CREATE TEMPORARY VIEW IF NOT EXISTS like_input_phrase_view AS
        SELECT * FROM user_db.phrases
        WHERE input_phrase LIKE "%(quoted_input_phrase)s%%"
        ;''' % {'quoted_input_phrase': quoted_input_phrase}
        self.database.execute(sqlstr)
        sqlargs = {'p_phrase': p_phrase, 'pp_phrase': pp_phrase}
        sqlstr = (
            'SELECT phrase, sum(user_freq) FROM like_input_phrase_view '
            + 'GROUP BY phrase;')
        try:
            # Get “unigram” data from user_db.
            #
            # Example: Let’s assume the user typed “co” and user_db contains
            #
            #     1|colou|colour|green|nice|1
            #     2|col|colour|yellow|ugly|2
            #     3|co|colour|green|awesome|1
            #     4|co|cold|||1
            #     5|conspirac|conspiracy|||5
            #     6|conspi|conspiracy|||1
            #     7|c|conspiracy|||1
            results_uni = self.database.execute(sqlstr, sqlargs).fetchall()
            # Then the result returned by .fetchall() is:
            #
            # [('colour', 4), ('cold', 1), ('conspiracy', 6)]
            #
            # (“c|conspiracy|1” is not selected because it doesn’t
            # match the user input “LIKE co%”! I.e. this is filtered
            # out by the VIEW created above already)
        except Exception:
            LOGGER.exception(
                'Unexpected error getting “unigram” data from user_db.')
        if not results_uni:
            # If no unigrams matched, bigrams and trigrams cannot
            # match either. We can stop here and return what we got
            # from hunspell.
            return self.best_candidates(phrase_frequencies)
        # Now normalize the unigram frequencies with the total count
        # (which is 11 in the above example), which gives us the
        # normalized result:
        # [('colour', 4/11), ('cold', 1/11), ('conspiracy', 6/11)]
        sqlstr = 'SELECT sum(user_freq) FROM like_input_phrase_view;'
        try:
            count = self.database.execute(sqlstr, sqlargs).fetchall()[0][0]
        except Exception:
            LOGGER.exception(
                'Unexpected error getting total unigram count from user_db')
        # Updating the phrase_frequency dictionary with the normalized
        # results gives: {'conspiracy': 6/11, 'code': 0,
        # 'communicability': 0, 'cold': 1/11, 'colour': 4/11}
        for result_uni in results_uni:
            phrase_frequencies.update(
                [(result_uni[0], result_uni[1]/float(count))])
        if DEBUG_LEVEL > 1:
            LOGGER.debug(
                'Unigram best_candidates=%s',
                self.best_candidates(phrase_frequencies))
        if not p_phrase:
            # If no context for bigram matching is available, return
            # what we have so far:
            return self.best_candidates(phrase_frequencies)
        sqlstr = (
            'SELECT phrase, sum(user_freq) FROM like_input_phrase_view '
            + 'WHERE p_phrase = :p_phrase GROUP BY phrase;')
        try:
            results_bi = self.database.execute(sqlstr, sqlargs).fetchall()
        except Exception:
            LOGGER.exception(
                'Unexpected error getting “bigram” data from user_db')
        if not results_bi:
            # If no bigram could be matched, return what we have so far:
            return self.best_candidates(phrase_frequencies)
        # get the total count of p_phrase to normalize the bigram frequencies:
        sqlstr = (
            'SELECT sum(user_freq) FROM like_input_phrase_view '
            + 'WHERE p_phrase = :p_phrase;')
        try:
            count_p_phrase = self.database.execute(
                sqlstr, sqlargs).fetchall()[0][0]
        except Exception:
            LOGGER.exception(
                'Unexpected error getting total bigram count from user_db')
        # Update the phrase frequency dictionary by using a linear
        # combination of the unigram and the bigram results, giving
        # both the weight of 0.5:
        for result_bi in results_bi:
            phrase_frequencies.update(
                [(result_bi[0],
                  0.5*result_bi[1]/float(count_p_phrase)
                  +0.5*phrase_frequencies[result_bi[0]])])
        if DEBUG_LEVEL > 1:
            LOGGER.debug(
                'Bigram best_candidates=%s',
                self.best_candidates(phrase_frequencies))
        if not pp_phrase:
            # If no context for trigram matching is available, return
            # what we have so far:
            return self.best_candidates(phrase_frequencies)
        sqlstr = ('SELECT phrase, sum(user_freq) FROM like_input_phrase_view '
                  + 'WHERE p_phrase = :p_phrase '
                  + 'AND pp_phrase = :pp_phrase GROUP BY phrase;')
        try:
            results_tri = self.database.execute(sqlstr, sqlargs).fetchall()
        except Exception:
            LOGGER.exception(
                'Unexpected error getting “trigram” data from user_db')
        if not results_tri:
            # if no trigram could be matched, return what we have so far:
            return self.best_candidates(phrase_frequencies)
        # get the total count of (p_phrase, pp_phrase) pairs to
        # normalize the bigram frequencies:
        sqlstr = (
            'SELECT sum(user_freq) FROM like_input_phrase_view '
            + 'WHERE p_phrase = :p_phrase AND pp_phrase = :pp_phrase;')
        try:
            count_pp_phrase_p_phrase = self.database.execute(
                sqlstr, sqlargs).fetchall()[0][0]
        except Exception:
            LOGGER.exception(
                'Unexpected error getting total trigram count from user_db')
        # Update the phrase frequency dictionary by using a linear
        # combination of the bigram and the trigram results, giving
        # both the weight of 0.5 (that makes the total weights: 0.25 *
        # unigram + 0.25 * bigram + 0.5 * trigram, i.e. the trigrams
        # get higher weight):
        for result_tri in results_tri:
            phrase_frequencies.update(
                [(result_tri[0],
                  0.5*result_tri[1]/float(count_pp_phrase_p_phrase)
                  +0.5*phrase_frequencies[result_tri[0]])])
        if DEBUG_LEVEL > 1:
            LOGGER.debug(
                'Trigram best_candidates=%s',
                self.best_candidates(phrase_frequencies))
        return self.best_candidates(phrase_frequencies)

    def generate_userdb_desc(self):
        '''
        Add a description table to the user database

        This adds the database version and  the create time
        '''
        try:
            sqlstring = ('CREATE TABLE IF NOT EXISTS user_db.desc '
                         + '(name PRIMARY KEY, value);')
            self.database.executescript(sqlstring)
            sqlstring = 'INSERT OR IGNORE INTO user_db.desc  VALUES (?, ?);'
            self.database.execute(
                sqlstring, ('version', USER_DATABASE_VERSION))
            sqlstring = (
                'INSERT OR IGNORE INTO user_db.desc '
                + 'VALUES (?, DATETIME("now", "localtime"));')
            self.database.execute(sqlstring, ("create-time", ))
            self.database.commit()
        except Exception:
            LOGGER.exception('Unexpected error adding description to user_db.')

    def init_user_db(self):
        '''
        Initialize the user database unless it is an in-memory database
        '''
        if self.user_db_file == ':memory:':
            return
        if not path.exists(self.user_db_file):
            database = sqlite3.connect(self.user_db_file)
            # a database containing the complete German Hunspell
            # dictionary has less then 6000 pages. 20000 pages
            # should be enough to cache the complete database
            # in most cases.
            database.executescript('''
                PRAGMA encoding = "UTF-8";
                PRAGMA case_sensitive_like = true;
                PRAGMA page_size = 4096;
                PRAGMA cache_size = 20000;
                PRAGMA temp_store = MEMORY;
                PRAGMA journal_mode = WAL;
                PRAGMA journal_size_limit = 1000000;
                PRAGMA synchronous = NORMAL;
            ''')
            database.commit()

    def get_database_desc(self, db_file):
        '''Get the description of the database'''
        if not path.exists(db_file):
            return None
        try:
            database = sqlite3.connect(db_file)
            desc = {}
            for row in database.execute("SELECT * FROM desc;").fetchall():
                desc[row[0]] = row[1]
            database.close()
            return desc
        except Exception:
            LOGGER.exception('Unexpected error getting database description.')
            return None

    def get_number_of_columns_of_phrase_table(self, db_file):
        # pylint: disable=line-too-long
        '''
        Get the number of columns in the 'phrases' table in
        the database in db_file.

        Determines the number of columns by parsing this:

        sqlite> select sql from sqlite_master where name='phrases';
CREATE TABLE phrases (id INTEGER PRIMARY KEY, input_phrase TEXT, phrase TEXT, p_phrase TEXT, pp_phrase TEXT, user_freq INTEGER, timestamp REAL)
        sqlite>

        This result could be on a single line, as above, or on multiple
        lines.
        '''
        # pylint: enable=line-too-long
        if not path.exists(db_file):
            return None
        try:
            database = sqlite3.connect(db_file)
            table_phrases_result = database.execute(
                "select sql from sqlite_master where name='phrases';"
            ).fetchall()
            # Remove possible line breaks from the string where we
            # want to match:
            string = ' '.join(table_phrases_result[0][0].splitlines())
            match = re.match(r'.*\((.*)\)', string)
            if match:
                table_phrases_columns = match.group(1).split(',')
                return len(table_phrases_columns)
            return 0
        except Exception:
            LOGGER.exception(
                'Unexpected error getting number of columns of database.')
            return 0

    def list_user_shortcuts(self):
        '''Returns a list of user defined shortcuts from the user database.

        :rtype: List of tuples of strings: [(str, str), ...]

        '''
        sqlstr = '''
        SELECT input_phrase, phrase FROM user_db.phrases WHERE user_freq >= :freq
        ;'''
        sqlargs = {'freq': itb_util.SHORTCUT_USER_FREQ}
        if DEBUG_LEVEL > 1:
            LOGGER.debug('sqlstr=%s', sqlstr)
            LOGGER.debug('sqlargs=%s', sqlargs)
        result = self.database.execute(sqlstr, sqlargs).fetchall()
        if DEBUG_LEVEL > 1:
            LOGGER.debug('result=%s', result)
        return result

    def check_phrase_and_update_frequency(
            self, input_phrase='', phrase='', p_phrase='',
            pp_phrase='', user_freq_increment=1, commit=True):
        '''
        Check whether input_phrase and phrase are already in database. If
        they are in the database, increase the frequency by 1, if not
        add them.
        '''
        if not input_phrase:
            input_phrase = phrase
        if not phrase:
            return
        phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, phrase)
        p_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, p_phrase)
        pp_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, pp_phrase)
        input_phrase = itb_util.remove_accents(input_phrase)
        input_phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, input_phrase)

        if DEBUG_LEVEL > 1:
            LOGGER.debug(
                'phrase=%(p)s, input_phrase=%(t)s',
                {'p': phrase.encode('UTF-8'),
                 't': input_phrase.encode('UTF-8')})

        # There should never be more than 1 database row for the same
        # input_phrase *and* phrase. So the following query on
        # the database should match at most one database
        # row and the length of the result array should be 0 or
        # 1. So the “GROUP BY phrase” is actually redundant. It is
        # only a safeguard for the case when duplicate rows have been
        # added to the database accidentally (But in that case there
        # is a bug somewhere else which should be fixed).
        sqlstr = '''
        SELECT max(user_freq) FROM user_db.phrases
        WHERE input_phrase = :input_phrase
        AND phrase = :phrase AND p_phrase = :p_phrase AND pp_phrase = :pp_phrase
        GROUP BY phrase
        ;'''
        sqlargs = {'input_phrase': input_phrase,
                   'phrase': phrase,
                   'p_phrase': p_phrase,
                   'pp_phrase': pp_phrase}
        if DEBUG_LEVEL > 1:
            LOGGER.debug(
                'TabSqliteDb.check_phrase_and_update_frequency() sqlstr=%s',
                sqlstr)
            LOGGER.debug(
                'TabSqliteDb.check_phrase_and_update_frequency() sqlargs=%s',
                sqlargs)
        result = self.database.execute(sqlstr, sqlargs).fetchall()
        if DEBUG_LEVEL > 1:
            LOGGER.debug(
                'check_phrase_and_update_frequency() result=%s', result)
        if result:
            # A match was found in user_db, increase user frequency by
            # user_freq_increment (1 by default)
            self.update_phrase(input_phrase=input_phrase,
                               phrase=phrase,
                               p_phrase=p_phrase,
                               pp_phrase=pp_phrase,
                               user_freq=result[0][0]+user_freq_increment,
                               commit=commit)
            return
        # The phrase was not found in user_db.
        # Add it as a new phrase, i.e. with user_freq = user_freq_increment
        # (1 by default):
        self.add_phrase(input_phrase=input_phrase,
                        phrase=phrase,
                        p_phrase=p_phrase,
                        pp_phrase=pp_phrase,
                        user_freq=user_freq_increment,
                        commit=commit)
        return

    def remove_phrase(self, input_phrase='', phrase='', commit=True):
        '''
        Remove all rows matching “input_phrase” and “phrase” from database.
        Or, if “input_phrase” is “None”, remove all rows matching “phrase”
        no matter for what input phrase from the database.
        '''
        if DEBUG_LEVEL > 1:
            LOGGER.debug(
                'TabSqliteDb.remove_phrase() phrase=%(p)s',
                {'p': phrase.encode('UTF-8')})
        if not phrase:
            return
        phrase = unicodedata.normalize(
            itb_util.NORMALIZATION_FORM_INTERNAL, phrase)
        if input_phrase:
            input_phrase = unicodedata.normalize(
                itb_util.NORMALIZATION_FORM_INTERNAL, input_phrase)
        if input_phrase:
            delete_sqlstr = '''
            DELETE FROM user_db.phrases
            WHERE input_phrase = :input_phrase AND phrase = :phrase
            ;'''
        else:
            delete_sqlstr = '''
            DELETE FROM user_db.phrases
            WHERE phrase = :phrase
            ;'''
        delete_sqlargs = {'input_phrase': input_phrase, 'phrase': phrase}
        self.database.execute(delete_sqlstr, delete_sqlargs)
        if commit:
            self.database.commit()

    def extract_user_phrases(self):
        '''extract user phrases from database'''
        try:
            database = sqlite3.connect(self.user_db_file)
            database.execute('PRAGMA wal_checkpoint;')
            phrases = database.execute(
                'SELECT phrase, sum(user_freq) FROM phrases GROUP BY phrase;'
            ).fetchall()
            database.close()
            phrases = [
                (unicodedata.normalize(
                    itb_util.NORMALIZATION_FORM_INTERNAL, x[0]), x[1])
                for x in
                phrases
            ]
            return phrases[:]
        except Exception:
            LOGGER.exception('Unexpected error extracting user phrases.')
            return []

    def read_training_data_from_file(self, filename):
        '''
        Read data to train the prediction from a text file.

        :param filename: Full path of the text file to read.
        :type filename: String
        '''
        if not os.path.isfile(filename):
            return False
        rows = self.database.execute(
            'SELECT input_phrase, phrase, p_phrase, pp_phrase, '
            + 'user_freq, timestamp FROM phrases;').fetchall()
        p_token = ''
        pp_token = ''
        database_dict = {}
        for row in rows:
            database_dict.update([((row[0], row[1], row[2], row[3]),
                                   {'input_phrase': row[0],
                                    'phrase': row[1],
                                    'p_phrase': row[2],
                                    'pp_phrase': row[3],
                                    'user_freq': row[4],
                                    'timestamp': row[5]}
                                  )])
        lines = []
        try:
            with codecs.open(filename, encoding='UTF-8') as file_handle:
                lines = [
                    unicodedata.normalize(
                        itb_util.NORMALIZATION_FORM_INTERNAL, line)
                    for line in file_handle.readlines()]
        except Exception:
            LOGGER.exception(
                'Unexpected error reading training data from file.')
            return False
        for line in lines:
            for token in itb_util.tokenize(line):
                key = (token, token, p_token, pp_token)
                if key in database_dict:
                    database_dict[key]['user_freq'] += 1
                    database_dict[key]['timestamp'] = time.time()
                else:
                    database_dict[key] = {'input_phrase': token,
                                          'phrase': token,
                                          'p_phrase': p_token,
                                          'pp_phrase': pp_token,
                                          'user_freq': 1,
                                          'timestamp': time.time()}
                pp_token = p_token
                p_token = token
        sqlargs = []
        for key in database_dict:
            sqlargs.append(database_dict[key])
        sqlstr = '''
        INSERT INTO user_db.phrases (input_phrase, phrase, p_phrase, pp_phrase, user_freq, timestamp)
        VALUES (:input_phrase, :phrase, :p_phrase, :pp_phrase, :user_freq, :timestamp)
        ;'''
        try:
            self.database.execute('DELETE FROM phrases;')
            # Without the following commit, the
            # self.database.executemany() fails with
            # “OperationalError: database is locked”.
            self.database.commit()
            self.database.executemany(sqlstr, sqlargs)
            self.database.commit()
            self.database.execute('PRAGMA wal_checkpoint;')
        except Exception:
            LOGGER.exception(
                'Unexpected error writing training data to database.')
            return False
        return True

    def remove_all_phrases(self):
        '''
        Remove all phrases from the database, i.e. delete all the
        data learned from user input or text files.
        '''
        try:
            self.database.execute('DELETE FROM phrases;')
            self.database.commit()
            self.database.execute('PRAGMA wal_checkpoint;')
        except Exception:
            LOGGER.exception(
                'Unexpected error removing all phrases from database.')

    def dump_database(self):
        '''
        Dump the contents of the database to the log

        (For debugging)
        '''
        try:
            LOGGER.debug('SELECT * FROM desc;\n')
            for row in self.database.execute("SELECT * FROM desc;").fetchall():
                LOGGER.debug('%s', repr(row))
            LOGGER.debug('SELECT * FROM phrases;\n')
            for row in self.database.execute(
                    "SELECT * FROM phrases;").fetchall():
                LOGGER.debug('%s', repr(row))
        except Exception:
            LOGGER.exception('Unexpected error dumping database.')
            return
