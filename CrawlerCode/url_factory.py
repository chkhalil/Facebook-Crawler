# coding=utf-8

import datetime
import logging

import config

# Create the logger
logger = logging.getLogger(__name__)


class Url(object):
    """
    Url class
    """

    def __init__(self):
        self.url = None
        self.param_dict = None
        self._url_objects = {'page': PageUrl, 'post': PostUrl, 'reaction': ReactionUrl, 'comment': CommentUrl}

    def create_url(self, type_of, identifier, access_token, **kwargs):
        """
        The factory method
        :param access_token: The access token used to create the request
        :param type_of: The url type
        :param identifier: If we're talking
        :param since: The date from where to begin the crawl
        :param until: The date of the latest post
        :return: the
        """
        # Create new Url object with passed parameters
        new_url_object = self._url_objects[type_of](identifier, access_token, **kwargs)
        # Return the new object
        return new_url_object


class PageUrl(Url):
    """
    The PageUrl class
    """

    def __init__(self, identifier, access_token, **kwargs):
        super(PageUrl, self).__init__()
        self.url = config.graph_url + identifier
        self.param_dict = {'fields': ','.join(config.page_fields),
                           'access_token': access_token}


class PostUrl(Url):
    """
    The PostUrl class
    """

    def __init__(self, identifier, access_token, **kwargs):
        super(PostUrl, self).__init__()
        self.url = config.graph_url + identifier + "/posts"
        self.param_dict = {'fields': ','.join(config.posts_fields),
                           'access_token': access_token}
        # Get the since and until values from kwargs
        since = kwargs.get('since', None)
        until = kwargs.get('until', None)
        # Depending on the values
        if since is not None:
            # Add the timestamp of the since date
            self.param_dict['since'] = datetime.datetime.strptime(since, '%Y-%m-%d').date().strftime('%s')
            if until is not None:
                # Add the timestamp of the until date
                self.param_dict['until'] = datetime.datetime.strptime(until, '%Y-%m-%d').date().strftime('%s')


class CommentUrl(Url):
    """
    The CommentUrl class
    """

    def __init__(self, identifier, access_token, **kwargs):
        super(CommentUrl, self).__init__()
        self.url = config.graph_url + identifier + "/comments"
        self.param_dict = {'limit': 750,
                           'access_token': access_token}


class ReactionUrl(Url):
    """
    The ReactionUrl class
    """

    def __init__(self, identifier, access_token, **kwargs):
        super(ReactionUrl, self).__init__()
        self.url = config.graph_url + identifier + "/reactions"
        self.param_dict = {'limit': 750,
                           'access_token': access_token}
