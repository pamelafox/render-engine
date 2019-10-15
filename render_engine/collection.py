import json
import logging
import urllib.parse
from pathlib import Path
from typing import Optional, Sequence, Type, Union
from dataclasses import dataclass

from render_engine.page import Page

PathString = Union[str, Type[Path]]

@dataclass
class Index:
    name: str
    pages: Sequence=list

    @property
    def slug(self):
        return urllib.parse.quote(self.name.lower())

class Collection:
    """
    Create a Collection of Similar Page Objects

    template: Optional[Union[str, Type[Path]]=None - the template file that the
        engine will use to build the page (default: None). This will be assigned
        to the iterated pages but not any associated files.

    index_template: Optional[Union[str, Type[Path]]=None the template file that
        will be used to create an index for the pages.

    no_index: bool=False

    content_path = filepath to get content and attributes from if not content.
        attributes will be saved as properties. (defined by load_page_from_file) else None.

    default_content_type: Type[Page]

    template_vars: dict={}

    index_template_vars: dict={}
    """
    _default_sort_field = 'title'
    _reverse_sort = False
    _includes = ['*.md', '*.txt', '*.html']
    _pages = set()
    content_path = None

    def __init__(
            self,
            *,
            title: str='',
            content_path: Optional[PathString]=None,
            page_content_type: Type[Page]=Page,
            pages: [Sequence]=[],
            recursive: bool=False,
            ):
        """initialize a collection object"""
        self.title = title
        self.recursive = recursive
        self.page_content_type = page_content_type

        if content_path:
            self.content_path = Path(content_path)

        self._pages = set(pages)

    @property
    def pages(self):
        if self._pages:
            return self._pages

        elif self.content_path:
            # ** is equivalent to rglob
            glob_start = '**' if self.recursive else ''
            globs = [self.content_path.glob(f'{glob_start}{x}') for x in
                    self._includes]

            pages = set()
            for glob in globs:
                for item_file in glob:
                    pages.add(self.page_content_type(content_path=item_file))

            self._pages = pages
            return pages

        else:
            return set()

    def add(self, *pages):
        pages = filter(lambda p: isinstance(p, self.page_content_type), pages)
        self._pages.add(pages)
        return self.pages

    @property
    def _iterators(self):
        return [Index(name=f'All {self.title}', pages=self.pages)]

    def __iter__(self):
        return self._pages

    def __len__(self):
        return len(self._pages)
