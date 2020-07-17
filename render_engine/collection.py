from slugify import slugify
import itertools
import logging
import operator
import typing
from pathlib import Path

import more_itertools

from .feeds import RSSFeed
from .page import Page


class Collection:
    """Collection objects serve as a way to quickly process pages that have a
    LARGE portion of content that is similar or file driven.

    The most common form of collection would be a Blog, but can also be
    static pages that have their content stored in a dedicated file.

    Currently, collections must come from a content_path and all be the same
    content type.


    Example
    -------
    from render_engine import Collection

    @site.register_collection()
    class BasicCollection(Collection):
        pass


    Attributes
    ----------
    engine: str, optional
        The engine that the collection will pass to each page. Site's default
        engine
    template: str
        The template that each page will use to render
    routes: List[str]
        all routes that the file should be created at. default []
    content_path: List[PathString], optional
        the filepath to load content from.
    includes: List[str], optional
        the types of files in the content path that will be processed
        default ["*.md", "*.html"]
    has_archive: Bool
        if `True`, create an archive page with all of the processed pages saved
        as `pages`. default `False`
    template: str, optional
        template filename that will be used if `has_archive==True` default: archive.html"
    slug: str, optional
        slug for rendered page if `has_archive == True` default: all_posts
    content_type: Type[Page], optional
        content_type for the rendered archive page
    _archive_reverse: Bool, optional
        should the sorted `pages` be listed in reverse order. default: False

    """

    engine: typing.Optional[str] = None
    content_items: typing.List[Page] = []
    content_path: str = ""
    content_type: typing.Type[Page] = Page
    template: str = "page.html"
    includes: typing.List[str] = ["*.md", "*.html"]
    routes: typing.List[str] = [""]
    subcollections: typing.List[str] = []
    has_archive: bool = False
    archive_template: str = "archive.html"
    archive_reverse: bool = False
    archive_sort: typing.Tuple[str] = ('title')
    paginated: bool = False
    items_per_page: int = 10
    title: typing.Optional[str] = ''
    feeds: typing.List[typing.Optional[RSSFeed]] = []

    def __init__(self):
        if not self.title:
            self.title = self.__class__.__name__

    @property
    def _pages(self) -> typing.List[Page]:
        _pages = []

        if self.content_items:
            _pages = self.content_items

        if self.content_path:

            if Path(self.content_path).samefile("/"):
                logging.warning(
                    f"{self.content_path=}! Accessing Root Directory is Dangerous..."
                )

            for pattern in self.includes:

                for filepath in Path(self.content_path).glob(pattern):
                    page = self.content_type.from_content_path(filepath)
                    page.routes = self.routes
                    page.template = self.template
                    _pages.append(page)

        return _pages

    @property
    def archive(self):
        """Create a `Page` object for the pages in the collection"""

        sorted_pages = sorted(
            self._pages,
            key=lambda p: getattr(p, self.archive_sort),
            reverse=self.archive_reverse,
        )

        if self.paginated:
            pages = list(more_itertools.chunked(sorted_pages, self.items_per_page))

        else:
            pages = [sorted_pages]

        class Archive(Page):
            no_index = True
            template = self.archive_template
            routes = [self.routes[0]]
            title = self.title

        archive_pages = []

        for index, page in enumerate(pages):
            archive_page =  Archive()
            archive_page.routes = [self.routes[0]]
            archive_page.pages = pages[index]
            archive_page.title = self.title
            archive_page.page_index = index

            if self.paginated:
                archive_page.slug = f'{archive_page.slug}-{index}'

            archive_pages.append(archive_page)

        return archive_pages


    @classmethod
    def from_subcollection(cls, collection, attrval):
        class SubCollection(Collection):
            archive_template = collection.archive_template
            slug = slugify(attrval)
            content_type = collection.content_type
            archive_reverse = collection.archive_reverse
            content_items = []
            has_archive = True
            routes = [attrval]
            title = attrval

        return SubCollection()


    def subcollection(self, attr):
        """Returns a list of all of the values in a subcollection"""
        attrvals = []

        for page in self._pages:
            if hasattr(page, attr):
                attrvals.append(getattr(page, attr))

        return attrvals
