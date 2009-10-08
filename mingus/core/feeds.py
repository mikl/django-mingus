from django.core.urlresolvers import reverse
from django.utils.feedgenerator import Atom1Feed
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.syndication.feeds import Feed
from django.contrib.sites.models import Site

from basic.blog.models import Post, Category, Settings
from django_proxy.models import Proxy


class BlogPostsFeed(Feed):
    _settings = Settings.get_current()
    title = '%s feed' % _settings.site_name
    subtitle = '%s posts feed.' % _settings.site_name
    author_name = _settings.author_name
    copyright = _settings.copyright
    feed_type = Atom1Feed

    def link(self):
        return reverse('blog_index')

    def items(self):
        return Post.objects.published()[:10]

    def item_pubdate(self, obj):
        return obj.publish


class BlogPostsByCategory(Feed):
    _settings = Settings.get_current()
    title = '%s posts category feed' % _settings.site_name
    author_name = _settings.author_name
    copyright = _settings.copyright
    feed_type = Atom1Feed

    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Category.objects.get(slug__exact=bits[0])

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return "Posts recently categorized as %s" % obj.title

    def items(self, obj):
        return obj.post_set.published()[:10]


class CommentsFeed(Feed):
    _site = Site.objects.get_current()
    title = '%s comment feed' % _site.name
    subtitle = '%s comments feed.' % _site.name
    feed_type = Atom1Feed

    def link(self):
        return reverse('blog_index')

    def items(self):
        ctype = ContentType.objects.get_for_model(Post)
        return Comment.objects.filter(content_type=ctype)[:10]

    def item_pubdate(self, obj):
        return obj.submit_date


class AllEntries(Feed):
    _settings = Settings.get_current()
    title = '%s all entries feed' % _settings.site_name
    subtitle = 'All entries published and updated on %s' % _settings.site_name
    author_name = _settings.author_name
    copyright = _settings.copyright
    feed_type = Atom1Feed

    def link(self):
        return 'http://%s' % self._settings.site.domain

    def items(self):
        return Proxy.objects.published().order_by('-pub_date')[:10]

    def item_link(self, item):
        return item.content_object.get_absolute_url()

    def item_categories(self, item):
        return item.tags.replace(',', '').split()


