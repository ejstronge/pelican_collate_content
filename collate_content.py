"""
Collate Content
===============

(c) 2014 - Edward Stronge

Connects to the content generator finalized signal to combine
content sharing a category into a single list that will be
available in the template context.

Thanks to #pelican member @kura for suggestions on creating this
plugin.
"""
from collections import defaultdict
import functools
import re

from pelican import signals


def group_content(generator, content_type):
    """
    Assembles articles and pages into lists which are available
    through the global context passed to the template engine.

    For each category, substitutes '_' for all whitespace and '-'
    characters, then creates a list named `SUBSTITUTED_CATEGORY_NAME`_articles
    or `SUBSTITUTED_CATEGORY_NAME`_pages for Articles or Pages,
    respectively.

    Note that the *original* category name must appear in the
    `CATEGORIES_TO_COLLATE` when using this plugin with category
    filtering enabled.
    """
    category_filter = generator.settings.get('CATEGORIES_TO_COLLATE', None)
    filtering_active = type(category_filter) in (list, tuple, set)

    collations = generator.context.get('collations', defaultdict(list))
    for content in generator.context[content_type]:
        category = content.category.name
        if filtering_active and category not in category_filter:
            continue
        category = re.sub(r'\s', '_', category).replace('-', '_')
        collations['%s_%s' % (category, content_type)].append(content)
    print(collations)
    generator.context['collations'] = collations


ARTICLE_GROUPER = functools.partial(group_content, content_type='articles')
PAGE_GROUPER = functools.partial(group_content, content_type='pages')


def register():
    """Register the new plugin"""
    signals.article_generator_finalized.connect(ARTICLE_GROUPER)
    signals.page_generator_finalized.connect(PAGE_GROUPER)
