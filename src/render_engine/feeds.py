"""
The Feeds Logic That Makes Up RSS and ATOM FeedTypes.
This is the base files and should only contain the params identified by the
standards defined.
RSS: http://www.rssboard.org/rss-specification
JSON: https://jsonfeed.org/version/1
"""

from collections import namedtuple
from datetime import datetime

import jinja2
from jinja2 import Template, select_autoescape

from .engine import render_engine_templates_loader
from .page import Page


class RSSFeed(Page):
    """The RSS Feed Component of an Archive Object"""

    template = "rss2.0.xml"
    extension: str = "rss"

    def __init__(self, pages, title: str | None = None, slug: str | None = None):
        super().__init__()
        self.pages = list(pages)
        self._title = title
        self._slug = slug
