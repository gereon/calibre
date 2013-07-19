#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Kovid Goyal <kovid@kovidgoyal.net>'
__docformat__ = 'restructuredtext en'

import datetime
from io import BytesIO

from calibre.utils.date import utc_tz
from calibre.db.tests.base import BaseTest

class ReadingTest(BaseTest):

    def test_read(self):  # {{{
        'Test the reading of data from the database'
        cache = self.init_cache(self.library_path)
        tests = {
                3  : {
                    'title': 'Unknown',
                    'sort': 'Unknown',
                    'authors': ('Unknown',),
                    'author_sort': 'Unknown',
                    'series' : None,
                    'series_index': 1.0,
                    'rating': None,
                    'tags': (),
                    'formats':(),
                    'identifiers': {},
                    'timestamp': datetime.datetime(2011, 9, 7, 19, 54, 41,
                        tzinfo=utc_tz),
                    'pubdate': datetime.datetime(2011, 9, 7, 19, 54, 41,
                        tzinfo=utc_tz),
                    'last_modified': datetime.datetime(2011, 9, 7, 19, 54, 41,
                        tzinfo=utc_tz),
                    'publisher': None,
                    'languages': (),
                    'comments': None,
                    '#enum': None,
                    '#authors':(),
                    '#date':None,
                    '#rating':None,
                    '#series':None,
                    '#series_index': None,
                    '#tags':(),
                    '#yesno':None,
                    '#comments': None,
                    'size':None,
                },

                2 : {
                    'title': 'Title One',
                    'sort': 'One',
                    'authors': ('Author One',),
                    'author_sort': 'One, Author',
                    'series' : 'A Series One',
                    'series_index': 1.0,
                    'tags':('Tag One', 'Tag Two'),
                    'formats': ('FMT1',),
                    'rating': 4.0,
                    'identifiers': {'test':'one'},
                    'timestamp': datetime.datetime(2011, 9, 5, 21, 6,
                        tzinfo=utc_tz),
                    'pubdate': datetime.datetime(2011, 9, 5, 21, 6,
                        tzinfo=utc_tz),
                    'publisher': 'Publisher One',
                    'languages': ('eng',),
                    'comments': '<p>Comments One</p>',
                    '#enum':'One',
                    '#authors':('Custom One', 'Custom Two'),
                    '#date':datetime.datetime(2011, 9, 5, 6, 0,
                        tzinfo=utc_tz),
                    '#rating':2.0,
                    '#series':'My Series One',
                    '#series_index': 1.0,
                    '#tags':('My Tag One', 'My Tag Two'),
                    '#yesno':True,
                    '#comments': '<div>My Comments One<p></p></div>',
                    'size':9,
                },
                1  : {
                    'title': 'Title Two',
                    'sort': 'Title Two',
                    'authors': ('Author Two', 'Author One'),
                    'author_sort': 'Two, Author & One, Author',
                    'series' : 'A Series One',
                    'series_index': 2.0,
                    'rating': 6.0,
                    'tags': ('Tag One', 'News'),
                    'formats':('FMT1', 'FMT2'),
                    'identifiers': {'test':'two'},
                    'timestamp': datetime.datetime(2011, 9, 6, 6, 0,
                        tzinfo=utc_tz),
                    'pubdate': datetime.datetime(2011, 8, 5, 6, 0,
                        tzinfo=utc_tz),
                    'publisher': 'Publisher Two',
                    'languages': ('deu',),
                    'comments': '<p>Comments Two</p>',
                    '#enum':'Two',
                    '#authors':('My Author Two',),
                    '#date':datetime.datetime(2011, 9, 1, 6, 0,
                        tzinfo=utc_tz),
                    '#rating':4.0,
                    '#series':'My Series Two',
                    '#series_index': 3.0,
                    '#tags':('My Tag Two',),
                    '#yesno':False,
                    '#comments': '<div>My Comments Two<p></p></div>',
                    'size':9,

                },
        }
        for book_id, test in tests.iteritems():
            for field, expected_val in test.iteritems():
                val = cache.field_for(field, book_id)
                if isinstance(val, tuple) and 'authors' not in field and 'languages' not in field:
                    val, expected_val = set(val), set(expected_val)
                self.assertEqual(expected_val, val,
                        'Book id: %d Field: %s failed: %r != %r'%(
                            book_id, field, expected_val, val))
        # }}}

    def test_sorting(self):  # {{{
        'Test sorting'
        cache = self.init_cache(self.library_path)
        for field, order in {
            'title'  : [2, 1, 3],
            'authors': [2, 1, 3],
            'series' : [3, 1, 2],
            'tags'   : [3, 1, 2],
            'rating' : [3, 2, 1],
            # 'identifiers': [3, 2, 1], There is no stable sort since 1 and
            # 2 have the same identifier keys
            # 'last_modified': [3, 2, 1], There is no stable sort as two
            # records have the exact same value
            'timestamp': [2, 1, 3],
            'pubdate'  : [1, 2, 3],
            'publisher': [3, 2, 1],
            'languages': [3, 2, 1],
            'comments': [3, 2, 1],
            '#enum' : [3, 2, 1],
            '#authors' : [3, 2, 1],
            '#date': [3, 1, 2],
            '#rating':[3, 2, 1],
            '#series':[3, 2, 1],
            '#tags':[3, 2, 1],
            '#yesno':[3, 1, 2],
            '#comments':[3, 2, 1],
        }.iteritems():
            x = list(reversed(order))
            self.assertEqual(order, cache.multisort([(field, True)],
                ids_to_sort=x),
                    'Ascending sort of %s failed'%field)
            self.assertEqual(x, cache.multisort([(field, False)],
                ids_to_sort=order),
                    'Descending sort of %s failed'%field)

        # Test subsorting
        self.assertEqual([3, 2, 1], cache.multisort([('identifiers', True),
            ('title', True)]), 'Subsort failed')
    # }}}

    def test_get_metadata(self):  # {{{
        'Test get_metadata() returns the same data for both backends'
        from calibre.library.database2 import LibraryDatabase2
        old = LibraryDatabase2(self.library_path)
        old_metadata = {i:old.get_metadata(
            i, index_is_id=True, get_cover=True, cover_as_data=True) for i in
                xrange(1, 4)}
        for mi in old_metadata.itervalues():
            mi.format_metadata = dict(mi.format_metadata)
            if mi.formats:
                mi.formats = tuple(mi.formats)
        old.conn.close()
        old = None

        cache = self.init_cache(self.library_path)

        new_metadata = {i:cache.get_metadata(
            i, get_cover=True, cover_as_data=True) for i in xrange(1, 4)}
        cache = None
        for mi2, mi1 in zip(new_metadata.values(), old_metadata.values()):
            self.compare_metadata(mi1, mi2)
    # }}}

    def test_get_cover(self):  # {{{
        'Test cover() returns the same data for both backends'
        from calibre.library.database2 import LibraryDatabase2
        old = LibraryDatabase2(self.library_path)
        covers = {i: old.cover(i, index_is_id=True) for i in old.all_ids()}
        old.conn.close()
        old = None
        cache = self.init_cache(self.library_path)
        for book_id, cdata in covers.iteritems():
            self.assertEqual(cdata, cache.cover(book_id), 'Reading of cover failed')
            f = cache.cover(book_id, as_file=True)
            self.assertEqual(cdata, f.read() if f else f, 'Reading of cover as file failed')
            if cdata:
                with open(cache.cover(book_id, as_path=True), 'rb') as f:
                    self.assertEqual(cdata, f.read(), 'Reading of cover as path failed')
            else:
                self.assertEqual(cdata, cache.cover(book_id, as_path=True),
                                 'Reading of null cover as path failed')
        buf = BytesIO()
        self.assertFalse(cache.copy_cover_to(99999, buf), 'copy_cover_to() did not return False for non-existent book_id')
        self.assertFalse(cache.copy_cover_to(3, buf), 'copy_cover_to() did not return False for non-existent cover')

    # }}}

    def test_searching(self):  # {{{
        'Test searching returns the same data for both backends'
        from calibre.library.database2 import LibraryDatabase2
        old = LibraryDatabase2(self.library_path)
        oldvals = {query:set(old.search_getting_ids(query, '')) for query in (
            # Date tests
            'date:9/6/2011', 'date:true', 'date:false', 'pubdate:9/2011',
            '#date:true', 'date:<100daysago', 'date:>9/6/2011',
            '#date:>9/1/2011', '#date:=2011',

            # Number tests
            'rating:3', 'rating:>2', 'rating:=2', 'rating:true',
            'rating:false', 'rating:>4', 'tags:#<2', 'tags:#>7',
            'cover:false', 'cover:true', '#float:>11', '#float:<1k',
            '#float:10.01', 'series_index:1', 'series_index:<3', 'id:1',
            'id:>2',

            # Bool tests
            '#yesno:true', '#yesno:false', '#yesno:yes', '#yesno:no',
            '#yesno:empty',

            # Keypair tests
            'identifiers:true', 'identifiers:false', 'identifiers:test',
            'identifiers:test:false', 'identifiers:test:one',
            'identifiers:t:n', 'identifiers:=test:=two', 'identifiers:x:y',
            'identifiers:z',

            # Text tests
            'title:="Title One"', 'title:~title', '#enum:=one', '#enum:tw',
            '#enum:false', '#enum:true', 'series:one', 'tags:one', 'tags:true',
            'tags:false', '2', 'one', '20.02', '"publisher one"',
            '"my comments one"',

            # User categories
            '@Good Authors:One', '@Good Series.good tags:two',

            # Cover/Formats
            'cover:true', 'cover:false', 'formats:true', 'formats:false',
            'formats:#>1', 'formats:#=1', 'formats:=fmt1', 'formats:=fmt2',
            'formats:=fmt1 or formats:fmt2', '#formats:true', '#formats:false',
            '#formats:fmt1', '#formats:fmt2', '#formats:fmt1 and #formats:fmt2',

        )}
        old.conn.close()
        old = None

        cache = self.init_cache(self.library_path)
        for query, ans in oldvals.iteritems():
            nr = cache.search(query, '')
            self.assertEqual(ans, nr,
                'Old result: %r != New result: %r for search: %s'%(
                    ans, nr, query))

    # }}}

    def test_get_categories(self):  # {{{
        'Check that get_categories() returns the same data for both backends'
        from calibre.library.database2 import LibraryDatabase2
        old = LibraryDatabase2(self.library_path)
        old_categories = old.get_categories()
        old.conn.close()
        cache = self.init_cache(self.library_path)
        new_categories = cache.get_categories()
        self.assertEqual(set(old_categories), set(new_categories),
            'The set of old categories is not the same as the set of new categories')

        def compare_category(category, old, new):
            for attr in ('name', 'original_name', 'id', 'count',
                         'is_hierarchical', 'is_editable', 'is_searchable',
                         'id_set', 'avg_rating', 'sort', 'use_sort_as_name',
                         'tooltip', 'icon', 'category'):
                oval, nval = getattr(old, attr), getattr(new, attr)
                if (
                    (category in {'rating', '#rating'} and attr in {'id_set', 'sort'}) or
                    (category == 'series' and attr == 'sort') or  # Sorting is wrong in old
                    (category == 'identifiers' and attr == 'id_set') or
                    (category == '@Good Series') or  # Sorting is wrong in old
                    (category == 'news' and attr in {'count', 'id_set'}) or
                    (category == 'formats' and attr == 'id_set')
                ):
                    continue
                self.assertEqual(oval, nval,
                    'The attribute %s for %s in category %s does not match. Old is %r, New is %r'
                                %(attr, old.name, category, oval, nval))

        for category in old_categories:
            old, new = old_categories[category], new_categories[category]
            self.assertEqual(len(old), len(new),
                'The number of items in the category %s is not the same'%category)
            for o, n in zip(old, new):
                compare_category(category, o, n)

    # }}}

    def test_get_formats(self):  # {{{
        'Test reading ebook formats using the format() method'
        from calibre.library.database2 import LibraryDatabase2
        from calibre.db.cache import NoSuchFormat
        old = LibraryDatabase2(self.library_path)
        ids = old.all_ids()
        lf = {i:set(old.formats(i, index_is_id=True).split(',')) if old.formats(
            i, index_is_id=True) else set() for i in ids}
        formats = {i:{f:old.format(i, f, index_is_id=True) for f in fmts} for
                   i, fmts in lf.iteritems()}
        old.conn.close()
        old = None
        cache = self.init_cache(self.library_path)
        for book_id, fmts in lf.iteritems():
            self.assertEqual(fmts, set(cache.formats(book_id)),
                             'Set of formats is not the same')
            for fmt in fmts:
                old = formats[book_id][fmt]
                self.assertEqual(old, cache.format(book_id, fmt),
                                 'Old and new format disagree')
                f = cache.format(book_id, fmt, as_file=True)
                self.assertEqual(old, f.read(),
                                 'Failed to read format as file')
                with open(cache.format(book_id, fmt, as_path=True,
                                       preserve_filename=True), 'rb') as f:
                    self.assertEqual(old, f.read(),
                                 'Failed to read format as path')
                with open(cache.format(book_id, fmt, as_path=True), 'rb') as f:
                    self.assertEqual(old, f.read(),
                                 'Failed to read format as path')

        buf = BytesIO()
        self.assertRaises(NoSuchFormat, cache.copy_format_to, 99999, 'X', buf, 'copy_format_to() failed to raise an exception for non-existent book')
        self.assertRaises(NoSuchFormat, cache.copy_format_to, 1, 'X', buf, 'copy_format_to() failed to raise an exception for non-existent format')

    # }}}

    def test_author_sort_for_authors(self):  # {{{
        'Test getting the author sort for authors from the db'
        cache = self.init_cache()
        table = cache.fields['authors'].table
        table.set_sort_names({next(table.id_map.iterkeys()): 'Fake Sort'}, cache.backend)

        authors = tuple(table.id_map.itervalues())
        nval = cache.author_sort_from_authors(authors)
        self.assertIn('Fake Sort', nval)

        db = self.init_old()
        self.assertEqual(db.author_sort_from_authors(authors), nval)
        db.close()
        del db

    # }}}

    def test_get_next_series_num(self):  # {{{
        'Test getting the next series number for a series'
        cache = self.init_cache()
        cache.set_field('series', {3:'test series'})
        cache.set_field('series_index', {3:13})
        table = cache.fields['series'].table
        series = tuple(table.id_map.itervalues())
        nvals = {s:cache.get_next_series_num_for(s) for s in series}
        db = self.init_old()
        self.assertEqual({s:db.get_next_series_num_for(s) for s in series}, nvals)
        db.close()

    # }}}

    def test_has_book(self):  # {{{
        'Test detecting duplicates'
        from calibre.ebooks.metadata.book.base import Metadata
        cache = self.init_cache()
        db = self.init_old()
        for title in cache.fields['title'].table.book_col_map.itervalues():
            for x in (db, cache):
                self.assertTrue(x.has_book(Metadata(title)))
                self.assertTrue(x.has_book(Metadata(title.upper())))
                self.assertFalse(x.has_book(Metadata(title + 'XXX')))
                self.assertFalse(x.has_book(Metadata(title[:1])))
        db.close()
    # }}}
