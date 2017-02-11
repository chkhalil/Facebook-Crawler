# coding=utf-8


def extract_data_from_post(post):
    """
    Extract likes_count, shares_count, comments_count from post
    :param post: facebook post
    :return: int, int, int
    """
    # The number of reactions, shares, comments of a specific post
    reactions_count = 0
    shares_count = 0
    comments_count = 0
    # If the post have reactions
    if 'reactions_count' in post:
        reactions_count = int(post['reactions_count'])
    # If the post has been shared
    if 'shares_count' in post:
        shares_count = int(post['shares_count'])
    # If the post has been commented
    if 'comments_count' in post:
        comments_count = int(post['comments_count'])
    # Return statement
    return reactions_count, shares_count, comments_count


def get_stats_from_list(list_of_numbers):
    """
    Return statistics about the data, essentially Max/Average
    :param list_of_numbers: List of numbers
    :return: int, float
    """
    # Check if the list is empty
    if len(list_of_numbers) == 0:
        # Set to 0
        maximum = average = 0
    else:
        maximum, average = list_of_numbers[-1], sum(list_of_numbers) * 1.0 / len(list_of_numbers)
    # Return statement
    return maximum, average


def get_stats_from_all_posts(posts, dic):
    """
    Get statistics about all the posts
    :param posts: All posts of a facebook page
    :param dic: dictionary where to add the key value entries
    :return: dictionary
    """
    # Create three lists respectively for reactions, shares and comments
    reactions = []
    shares = []
    comments = []
    # Add likes, shares and comments counts of every post to their respective list
    for post in posts:
        # Get the stats
        n_reactions, n_shares, n_comments = extract_data_from_post(post)
        # Add each object to it's appropriate list
        reactions.append(n_reactions)
        shares.append(n_shares)
        comments.append(n_comments)
    # Sort list to get the maximum
    reactions.sort()
    shares.sort()
    comments.sort()
    # Add to the dictionary the maximum and average of the likes, shares and comments of the posts' page
    dic['max_reactions'], dic['avg_reactions'] = get_stats_from_list(reactions)
    dic['max_shares'], dic['avg_shares'] = get_stats_from_list(shares)
    dic['max_comments'], dic['avg_comments'] = get_stats_from_list(comments)
    # Add to the dictionary the total number of posts in the page
    dic['total_posts'] = len(posts)
    # Add to the dictionary the talking_about_count (the talking_about_count out of the page's fans number)
    dic['talking_about_percent'] = dic['talking_about_count'] * 1.0 / dic['likes']
    # Return statement
    return dic
