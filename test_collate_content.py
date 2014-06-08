"""
test_collate_content
====================

Edward J. Stronge
(c) 2014

Tests for the collate_content module
"""
from collections import namedtuple
import os
import random
import tempfile
import shutil
import string
import unittest

from pelican import Pelican
from pelican import ArticlesGenerator, PagesGenerator
from pelican.settings import read_settings

import collate_content as cc

TEMP_PAGE_TEMPLATE = """Title: {title}
Date: 2014-03-06
Category: {category}
Author: Rumpelstiltskin
Tags: just, a, test

some interesting writing!

"""

Content = namedtuple('Content', ['title', 'path', 'category'])
# Characters likely to appear in blog titles/categories. Could eventually
# extend support to more characters that can't appear in a Python identifier
BLOG_CHARACTERS = string.letters + ' -:'


def make_content(directory, categories, count=5, categories_per_content=1):
    """
    make_content --> {(processed_category, original_category): articles, ...}

    Writes random titles and categories into `count` temporary
    files in `directory`. If desired, specify `categories_per_content`
    to assign multiple categories to each written file.

    Returns a dictionary whose keys are in `categories` with values
    that are (title, path, category) tuples for the generated
    content files.
    """
    new_content = {}
    for _ in range(count):
        title = get_random_text_and_whitespace()
        category_choice = random.sample(categories, categories_per_content)
        categories_string = ', '.join(category_choice)
        output = TEMP_PAGE_TEMPLATE.format(
            title=title, category=categories_string)

        content_file = tempfile.NamedTemporaryFile(
            dir=directory, mode='w', suffix='.md', delete=False)
        with content_file as tmp:
            tmp.write(output)
        path = os.path.join(directory, content_file.name)
        new_content[
            (cc.substitute_category_name(category_choice), category_choice)] =\
            Content(title, path, categories_string)
    return new_content


def get_random_text_and_whitespace(length=10):
    """
    Returns at most `length` randomly-generated letters and/or
    whitespace. The returned string will not begin or end in whitespace.
    """
    return "".join(random.sample(BLOG_CHARACTERS, length)).strip()


def modified_pelican_run(self):
    """Runs the generators and returns the context object

    Modified from the Pelican object's run methods.
    """

    context = self.settings.copy()
    context['filenames'] = {}  # share the dict between all the generators
    context['localsiteurl'] = self.settings['SITEURL']  # share
    generators = [
        cls(
            context=context,
            settings=self.settings,
            path=self.path,
            theme=self.theme,
            output_path=self.output_path,
        ) for cls in self.get_generator_classes()
    ]

    for p in generators:
        if hasattr(p, 'generate_context'):
            p.generate_context()

    writer = self.get_writer()

    for p in generators:
        if hasattr(p, 'generate_output'):
            p.generate_output(writer)

    next(g for g in generators if isinstance(g, ArticlesGenerator))
    next(g for g in generators if isinstance(g, PagesGenerator))
    return context


class TestContentCollation(unittest.TestCase):
    """Test generation of lists of content based on their Category metadata"""

    def setUp(self, settings_overrides=None, articles=5, pages=5,
              categories_per_content=1):
        self.temp_input_dir = tempfile.mkdtemp(prefix="cc-input-")
        page_directory = os.path.join(self.temp_input_dir, 'pages')
        os.mkdir(page_directory)
        self.temp_output_dir = tempfile.mkdtemp(prefix="cc-output-")
        categories = [get_random_text_and_whitespace() for _ in range(5)]
        self.articles = make_content(
            self.temp_input_dir, categories, count=5,
            categories_per_content=categories_per_content)
        self.pages = make_content(
            page_directory, categories, count=5,
            categories_per_content=categories_per_content)
        settings = {
            'PATH': self.temp_input_dir,
            'PAGE_DIR': 'pages',
            'OUTPUT_PATH': self.temp_output_dir,
            'PLUGINS': [cc],
            }
        if settings_overrides is not None:
            settings.update(settings_overrides)
        settings = read_settings(override=settings)
        pelican = Pelican(settings=settings)
        pelican.modified_run = modified_pelican_run
        self.collations = pelican.modified_run(pelican)['collations']

    def tearDown(self):
        shutil.rmtree(self.temp_input_dir)
        shutil.rmtree(self.temp_output_dir)

    def test_articles_with_one_category(self):

        for categories, articles in self.articles.items():
            substituted_category, original_category = categories
            self.assertIn(
                '%s_articles' % substituted_category, self.collations)


class TestContentCollationWithFilteredCategories(unittest.TestCase):
    """Test generation of lists of content based on their Category metadata"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_articles_with_one_category(self):
        pass

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromNames(['test_collate_content'])
    unittest.TextTestRunner(verbosity=1).run(suite)
