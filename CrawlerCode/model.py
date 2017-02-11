# coding=utf-8

import hashlib
import threading

import config
import net_utils


class Page(object):
    """
    Facebook page class
    """

    def __init__(self, page_data=None):
        # Check if page_data is given
        if page_data is not None:
            # For each field in the page's field
            for field in config.page_fields:
                # If the field exist in the list of page_data keys
                if field in page_data:
                    # If field is fan_count : compatibility issues
                    if field == 'fan_count':
                        # Set field to likes
                        setattr(self, 'likes', page_data[field])
                    else:
                        # Create an attribute and set its value
                        setattr(self, field, page_data[field])
                # The field is not in the list of page_data keys
                else:
                    # Create an attribute and set its value to None
                    setattr(self, field, None)
        # If page_date is None
        else:
            for field in config.page_fields:
                if field == 'fan_count':
                    # Set field to likes
                    field = 'likes'
                # Create an attribute and set its value to None
                setattr(self, field, None)
        # Default values of the attributes
        self.posts = []
        self.total_posts = 0
        self.talking_about_percent = float(0)
        self.avg_comments = float(0)
        self.max_comments = 0
        self.avg_reactions = float(0)
        self.max_reactions = 0
        self.avg_shares = float(0)
        self.max_shares = 0

    def get_page_info(self, identifier, access_token):
        """
        Get the page information
        :param identifier: The actual page id
        :param access_token: The access token used to connect with to the server
        :return:
        """
        # Collect info about the page
        page_info = net_utils.data_request('page', identifier, access_token)
        # Copy the content in the attributes
        self.__init__(page_info)

    def get_posts(self, access_token, **kwargs):
        """
        Get the page posts
        :param access_token: The access token used to connect with to the server
        :param with_comments: Get the posts and their comments
        :param with_replies: Get the comments and their replies
        :param with_reactions: Get the post's reactions
        :param since: The date from where to begin the crawl
        :param until: The date of the latest post
        :param number: The number of latest posts
        :return:
        """
        # Get the value from the kwargs dict
        with_comments = kwargs.get('with_comments', False)
        with_replies = kwargs.get('with_replies', False)
        with_reactions = kwargs.get('with_reactions', False)
        since = kwargs.get('since', None)
        until = kwargs.get('until', None)
        number = kwargs.get('number', None)
        # Get the posts depending on the args
        posts = net_utils.data_request('post', getattr(self, 'id'), access_token, since=since, until=until,
                                       number=number)
        for post in posts:
            try:
                self.posts.append(Post(post))
            except:
                continue
        # Actions depending on the values of with_ args
        if with_comments is True:
            if with_reactions is True:
                # For each post
                for post in self.posts:
                    # Collect the comments of the post (replies depends on the arg)
                    post.get_comments(access_token, with_replies=with_replies)
                    # Create a new thread to collect the reactions
                    thread = threading.Thread(target=post.get_reactions, args=(access_token,))
                    thread.start()
                    thread.join()
            else:
                # For each post
                for post in self.posts:
                    # Collect the comments of the post (replies depends on the arg)
                    post.get_comments(access_token, with_replies=with_replies)
        elif with_reactions is True:
            # For each post
            for post in self.posts:
                # Collect the comments of the post (replies depends on the arg)
                post.get_reactions(access_token)
        else:
            # If with_reactions and with_comments are both False
            pass

    def get_stats(self):
        """
        Get some statistics about the page related to the comments, shares and reactions
        :return:
        """
        # Create three lists respectively for reactions, shares and comments
        reactions = []
        shares = []
        comments = []
        # Add likes, shares and comments counts of every post to their respective list
        for post in self.posts:
            # Add each object to it's appropriate list
            reactions.append(post.reactions_count['total_count'])
            shares.append(getattr(post, 'shares_count'))
            comments.append(post.comments_count)
        # Sort list to get the maximum
        reactions.sort()
        shares.sort()
        comments.sort()
        # Calculate the maximum and the average
        self.max_comments, self.avg_comments = comments[-1], sum(comments) * 1.0 / len(comments) if len(
            comments) > 0 else 0
        self.max_reactions, self.avg_reactions = reactions[-1], sum(reactions) * 1.0 / len(reactions) if len(
            reactions) > 0 else 0
        self.max_shares, self.avg_shares = shares[-1], sum(shares) * 1.0 / len(shares) if len(
            shares) > 0 else 0
        # Calculate the number of posts
        self.total_posts = len(self.posts)
        # Calculate the talking about percent
        self.talking_about_percent = float(getattr(self, 'talking_about_count')) / getattr(self, 'likes')

    def to_json(self):
        """
        Construct a dictionary containing the data of the object
        :return: dict
        """
        # Convert the posts to json data
        json_posts = [post.to_json() for post in self.posts]
        # Get the page object attributes (functions and the built-in attributes excluded)
        attributes = [attribute for attribute in dir(self)
                      if not attribute.startswith('__') and not callable(getattr(self, attribute))]
        # Create the dictionary to return
        json_dict = {}
        # For attribute in the page object attributes
        for attribute in attributes:
            # Key = attribute, and the value = self.'attributes'
            if attribute == 'posts':
                json_dict[attribute] = json_posts
            else:
                json_dict[attribute] = getattr(self, attribute)
        # Return the dictionary
        return json_dict


class Post(object):
    """
    Facebook post object
    """

    def __init__(self, post_data=None):
        # Check if post_data is None
        if post_data is not None:
            # For each field in the post's field
            for field in config.posts_fields:
                # If the field exist in the list of post_data keys
                if field in post_data:
                    # If field is ... : compatibility issues
                    if field == 'from':
                        setattr(self, 'from_name', post_data['from']['name'])
                        setattr(self, 'from_id', post_data['from']['id'])
                    elif field == 'created_time':
                        setattr(self, 'published_date', post_data[field])
                    elif field == 'updated_time':
                        setattr(self, 'last_reaction', post_data[field])
                    elif field == 'message':
                        setattr(self, field, post_data[field].encode('utf-8').replace('\n', ' '))
                    elif field == 'shares':
                        setattr(self, 'shares_count', post_data[field]['count'])
                    else:
                        setattr(self, field, post_data[field])
                # The field is not in the list of post_data keys
                else:
                    # Create an attribute and set its value to None
                    if field == 'from':
                        setattr(self, 'from_name', '')
                        setattr(self, 'from_id', '')
                    elif field == 'created_time':
                        setattr(self, 'published_date', '')
                    elif field == 'updated_time':
                        setattr(self, 'last_reaction', '')
                    elif field == 'message':
                        setattr(self, field, '')
                    elif field == 'shares':
                        setattr(self, 'shares_count', 0)
                    elif field == 'name':
                        setattr(self, 'shares_count', '')
                    else:
                        setattr(self, field, None)
        # If page_date is None
        else:
            for field in config.posts_fields:
                # Create an attribute and set its value to None
                if field == 'from':
                    setattr(self, 'from_name', '')
                    setattr(self, 'from_id', '')
                elif field == 'created_time':
                    setattr(self, 'published_date', '')
                elif field == 'updated_time':
                    setattr(self, 'last_reaction', '')
                elif field == 'message':
                    setattr(self, field, '')
                elif field == 'shares':
                    setattr(self, 'shares_count', 0)
                else:
                    setattr(self, field, None)
        # Default values of the attributes
        self.reactions = []
        self.comments = []
        self.reactions_count = 0
        self.comments_count = 0

    def get_comments(self, access_token, **kwargs):
        """
        Get the posts' comments
        :return: List(Dict)
        """
        # Get the args value from kwargs
        with_replies = kwargs.get('with_replies', False)
        # Get the list of comments (list of dictionaries)
        comments = net_utils.data_request('comment', getattr(self, 'id'), access_token)
        # Actions depending on with_replies value
        if with_replies is False:
            # Convert the list of comments to a list of objects
            for comment in comments:
                try:
                    self.comments.append(Comment(comment))
                except:
                    continue
        else:
            for comment in comments:
                _comment = Comment(comment)
                _comment.get_replies(access_token)
                self.comments.append(_comment)
        # Calculate the number of comments
        self.comments_count = len(comments)

    def get_reactions(self, access_token):
        """
        Get the posts' comments
        :return: List(Dict)
        """
        # Get the list of reactions (list of dictionaries)
        reactions = net_utils.data_request('reaction', getattr(self, 'id'), access_token)
        # Convert the list of reactions to a list of objects
        for reaction in reactions:
            try:
                self.reactions.append(Reaction(reaction))
            except:
                continue
        # Calculate each occurrences of each reaction
        summary = {'LIKE': 0, 'LOVE': 0, 'WOW': 0, 'HAHA': 0, 'SAD': 0, 'ANGRY': 0, 'THANKFUL': 0}
        # Looping through the reactions
        for reaction in self.reactions:
            summary[reaction.type] += 1
        # Calculate the number of all reactions
        summary['total_count'] = len(self.reactions)
        # Adding the result to the post object
        self.reactions_count = summary

    def to_json(self):
        """
        Construct a dictionary containing the data of the object
        :return: Dict
        """
        # Convert the reactions and comments to json data
        json_reactions = [reaction.to_json() for reaction in self.reactions]
        json_comments = [comment.to_json() for comment in self.comments]
        # Get the page object attributes (functions and the built-in attributes excluded)
        attributes = [attribute for attribute in dir(self)
                      if not attribute.startswith('__') and not callable(getattr(self, attribute))]
        # Create the dictionary to return
        json_dict = {}
        # For attribute in the page object attributes
        for attribute in attributes:
            # Key = attribute, and the value = self.'attributes'
            if attribute == 'comments':
                json_dict[attribute] = json_comments
            elif attribute == 'reactions':
                json_dict[attribute] = json_reactions
            else:
                json_dict[attribute] = getattr(self, attribute)
        # Return the dictionary
        return json_dict


class Reply(object):
    """
    Facebook comment class
    """

    def __init__(self, reply_data=None):
        # Check if comment_date is None
        if reply_data is not None:
            # Copy the values from the dictionary to the object attributes
            self.id = reply_data['id']
            self.from_id = hashlib.md5(reply_data['from']['id']).hexdigest()
            self.message = reply_data['message'].encode('utf-8').replace('\n', ' ')
            self.created_time = reply_data['created_time']
        # If comment_data is None
        else:
            # Set all attributes to None
            self.id = ''
            self.from_id = ''
            self.message = ''
            self.created_time = ''

    def to_json(self):
        """
        Construct a dictionary containing the data of the object
        :return: Dict
        """
        return {'id': self.id, 'from_id': self.from_id, 'created_time': self.created_time, 'message': self.message}


class Comment(Reply):
    """
    Facebook comment class
    """

    def __init__(self, comment_data=None):
        # Call the Reply's object constructor
        super(Comment, self).__init__(comment_data)
        # Default values of the attributes
        self.replies = []

    def get_replies(self, access_token):
        """
        Get the replies of the comment
        :param access_token: The access token used to autheticate with to the server
        :return:
        """
        # Get the list of replies (list of dictionaries)
        replies = net_utils.data_request('comment', self.id, access_token)
        # Convert the list of replies to a list of objects (Replies are considered as comments)
        for reply in replies:
            try:
                self.replies.append(Reply(reply))
            except:
                continue

    def to_json(self):
        """
        Construct a dictionary containing the data of the object
        :return: Dict
        """
        # Call the same method from the Reply class
        json_data = super(Comment, self).to_json()
        # Add the list of replies to the dictionary
        json_data['replies'] = [reply.to_json() for reply in self.replies]
        # Return the dictionary
        return json_data


class Reaction(object):
    """
    Facebook reaction object
    """

    def __init__(self, reaction_data=None):
        # Check if reaction_data is None
        if reaction_data is not None:
            # Copy the values from the dictionary to the object attributes
            self.profile_id = hashlib.md5(reaction_data['id']).hexdigest()
            self.type = reaction_data['type']
        # If comment_data is None
        else:
            # Set all the attributes to None
            self.profile_id = ''
            self.type = ''

    def to_json(self):
        """
        Construct a dictionary containing the data of the object
        :return: dict
        """
        return {'profile_id': self.profile_id, 'type': self.type}
