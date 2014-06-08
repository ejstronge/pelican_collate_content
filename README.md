# Collate Content #
*Author: Edward Stronge <ejstronge.net>*

Makes categories of content available to the template as lists.

## Installation ##

Add this module to your Pelican configuration as follows:

    PLUGIN_PATH = '/path/to/pelican-plugins'
    PLUGINS = ['collate_content', ]

## Usage ##

To display the title of all content in the category `Software Development`, 
you could use the following block in a template:

    ```jinja
    <h1>Development blog</h1>
    <ul> 
    {% for a in articles %}
        {% if a in software_development_list %}
            <li>a.date - a.title</li> 
        {% endif %}
    {% endfor %}
    </ul>
    
    <h1> Open source projects </h1>
    I maintain the following projects:
    
    <ul>
    {% for p in pages %}
        {% if p in software_development_list %}
            <li>p.date - p.title</li> 
        {% endif %}
    {% endfor %}
    ```

## Settings ##

To limit which categories and subcategories are collated, set the
`CATEGORIES_TO_COLLATE` option in your Pelican configuration file.

If this option is present and is a list, only categories present
in `CATEGORIES_TO_COLLATE` will be collated:

    CATEGORIES_TO_COLLATE = ['category-of-interest', 'another-cool-category']
