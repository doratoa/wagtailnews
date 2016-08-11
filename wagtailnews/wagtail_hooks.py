from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core import urlresolvers
from django.core.urlresolvers import reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from wagtail.wagtailadmin.menu import MenuItem
from wagtail.wagtailadmin.search import SearchArea
from wagtail.wagtailcore import hooks

from . import urls
from .models import NEWSINDEX_MODEL_CLASSES
from .permissions import user_can_edit_news


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^news/', include(urls)),
    ]


@hooks.register('construct_main_menu')
def construct_main_menu(request, menu_items):
    if user_can_edit_news(request.user):
        menu_items.append(
            MenuItem(_('News'), urlresolvers.reverse('wagtailnews_choose'),
                     classnames='icon icon-grip', order=250)
        )


@hooks.register('register_admin_search_area')
def register_news_search():
    """Register news search."""

    return SearchArea(_('News'),
                      urlresolvers.reverse('wagtailnews_search'),
                      classnames='icon icon-grip',
                      order=250)


@hooks.register('register_permissions')
def newsitem_permissions():
    newsitem_models = [model.get_newsitem_model()
                       for model in NEWSINDEX_MODEL_CLASSES]
    newsitem_cts = ContentType.objects.get_for_models(*newsitem_models).values()
    return Permission.objects.filter(content_type__in=newsitem_cts)


@hooks.register('insert_editor_js')
def editor_js():
    js_files = [
        static('js/news_chooser.js'),
    ]
    js_includes = format_html_join(
        '\n', '<script src="{0}"></script>\n',
        ((filename, ) for filename in js_files)
    )
    urls = format_html(
        '<script>window.chooserUrls.newsChooser = "{}";</script>',
        reverse('wagtailnews_chooser'))
    return js_includes + urls
