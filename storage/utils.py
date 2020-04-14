import pymysql
from storage.sql import *
from collections import defaultdict
import numpy
mysql_connect = pymysql.connect(host=HOST,
                                port=3306, user=USER_NAME, password=PASSWD,
                                database=DATABASES, charset='utf8mb4')
cursor = mysql_connect.cursor()
# 设置返回内容为字典格式
cursor2 = mysql_connect.cursor(pymysql.cursors.DictCursor)


def get_pull_request_total(PROJECT_NAME):
    SQL = GET_PULL_REQUEST_TOTAL.format(PROJECT_NAME)
    cursor.execute(SQL)
    result = cursor.fetchall()
    result_list = []
    print(result)
    for i in result:
        result_list.append(i[0])
    return result_list


def get_test_number(PROJECT_NAME, test_number=None):
    if test_number:
        SQL = GET_TEST_PULL_NUMBER_SQL.format(PROJECT_NAME) % test_number
    else:
        SQL = GET_TEST_PULL_NUMBER_SQL2.format(START_TIME, END_TIME, PROJECT_NAME)
        print(SQL)
    cursor.execute(SQL)
    result = cursor.fetchall()
    number_list = []
    for i in result:
        number_list.append(i[0])
    return number_list


def get_file_name_by_number(PROJECT_NAME,number):
    SQL = GET_FILE_NAME_BY_PULL_NUMER_SQL.format(PROJECT_NAME) % number
    cursor.execute(SQL)
    result = cursor.fetchall()
    file_name_list = []
    for i in result:
        file_name_list.append(i[0])
    return file_name_list


def get_review_by_number(PROJECT_NAME):
    SQL = GET_REVIEWER_BY_NUMBER.format(PROJECT_NAME)
    cursor.execute(SQL)
    result = cursor.fetchall()
    reviewer_dict = {}
    for i in result:
        pull_number = i[0]
        reviewer = i[1]
        if i not in reviewer_dict.keys():
            reviewer_dict[i] = []
            reviewer_dict[i].append(i[1])
        else:
            reviewer_dict[pull_number].append(reviewer)
            reviewer_dict[pull_number] = list(set(reviewer_dict[pull_number]))
    return reviewer_dict


def get_file_name(PROJECT_NAME, limit_value=None):
    if limit_value:
        SQL = GET_FILE_NAME_SQL.format(PROJECT_NAME) % limit_value
    else:
        SQL = GET_FILE_NAME_BY_PULL_NUMER_SQL.format(PROJECT_NAME)
    cursor.execute(SQL)
    result = cursor.fetchall()
    file_dict = {}
    for i in result:
        pull_number = i[0]
        file_name = i[1]
        if pull_number not in file_dict.keys():
            file_dict[pull_number] = []
            file_dict[pull_number].append(file_name)
        else:
            file_dict[pull_number].append(file_name)
    return file_dict


def get_reviewer(PROJECT_NAME,limit_value=None):
    if limit_value:
        SQL = GET_REVIEWER_SQL.format(PROJECT_NAME) % limit_value
    else:
        SQL = GET_REVIEWER_BY_NUMBER.format(PROJECT_NAME)
    # SQL = SQL % Rp
    cursor.execute(SQL)
    result = cursor.fetchall()

    reviewer_dict = defaultdict(list)
    for item in result:
        pull_number = item[0]
        reviewer = item[1]
        reviewer_dict[pull_number].append(reviewer)

    reviewer_dict = dict(reviewer_dict)
    return reviewer_dict


def get_request_title_description(project_name,train_time):
    SQL = GET_PULL_REQUEST_INFO.format(project_name,train_time)
    cursor.execute(SQL)
    result = cursor.fetchall()
    info_list = []
    for item in result:
        number = item[0]
        title = item[1]
        description = item[2]

        content = '\n'.join(filter(None, [title, description]))
        pull_dict = {number: content}
        info_list.append(pull_dict)

    return info_list


def get_comments_count(project_name):
    SQL = GET_COMMENTS_COUNT_BY_PULL_NUMBER.format(project_name)
    cursor.execute(SQL)
    result = cursor.fetchall()
    comment_list = list()
    for item in result:
        number = item[0]
        comment_count = item[1]
        comment_dict = {number: comment_count}
        comment_list.append(comment_dict)

    return comment_list


def get_comment_user_and_date(project_name):
    """

    :param project_name:
    :return: the structure is like this:
    {
        "1": {
            "wido": ["2013-02-04 13:45:02"],
            "glowell2": ["2013-02-04 17:34:02"]},
        "5": {
            "dmick": ["2014-01-18 00:44:03"]},
        "6": {
            "ghost": ["2014-02-14 02:29:03","2014-02-19 22:12:04"]}
    }

    """
    SQL = GET_COMMENT_USER_AND_DATE_GROUP_BY_NUMBER.format(project_name)
    cursor.execute(SQL)
    result = cursor.fetchall()

    info_dict = defaultdict(dict)

    for item in result:
        number = item[0]
        user = item[1].split(',')
        date = item[2].split(',')

        group = zip(user, date)

        for user, date in group:
            date_list = info_dict[number].get(user, [])
            date_list.append(date)
            info_dict[number][user] = date_list

    return info_dict


def get_pull_request_user(project_name,train_time):
    """

    :param project_name:
    :return: structure is like this:
    {'stass': [1, 2],'kylemarsh': [6, 7, 8]}
    key is the user name and value is a pull number list
    """
    user_dict = defaultdict(list)
    SQL = GET_PULL_REQUEST_USER.format(project_name,train_time, START_TIME)
    cursor.execute(SQL)
    result = cursor.fetchall()
    for item in result:
        number = item[0]
        user = item[1]
        user_dict[user].append(number)
    ret = dict(user_dict)
    return ret


def get_pull_request_user_for_test(project_name):
    """

    :param project_name:
    :return: structure is like this:
    {"1037": "guits","1038": "djgalloway","1039": "andrewschoen"}
    """
    SQL = GET_PULL_REQUEST_USER2.format(project_name, START_TIME, END_TIME)
    cursor.execute(SQL)
    result = cursor.fetchall()
    info_dict = dict()
    for item in result:
        request_number = item[0]
        request_user = item[1]
        info_dict.update({request_number: request_user})
    return info_dict


def get_comment_date_max_min(project_name):
    SQL = GET_MAX_MIN_COMMENT_DATE.format(project_name)
    cursor.execute(SQL)
    result = cursor.fetchall()[0]
    max_date = result[0]
    min_date = result[1]

    return max_date, min_date


def get_comment_user(project_name):
    """
    get comment user group by request number

    return list is like this:
    [
        {10395: ['zhouruisong']},
        {10396: ['zhouruisong', 'dang', 'zhouruisong', 'zhouruisong']}
    ]
    """
    SQL1 = SET_PROJECT_NAME.format(project_name)
    SQL2 = GET_COMMENT_USER_BY_NUMBER
    cursor.execute(SQL1)
    cursor.execute(SQL2)
    mysql_connect.commit()
    result = cursor.fetchall()
    info_list = {i[0]: i[1].split(',') for i in result}
    return info_list


def get_comment_times(project_name):
    SQL = GET_COMMENT_TIMES.format(project_name)
    cursor.execute(SQL)
    result = cursor.fetchall()
    # total = numpy.sum([item[1] for item in result if item[1] > 1])
    # print(total)
    comment_times_dict = [{item[0]:item[1]} for item in result if item[1] > 20]
    return comment_times_dict


def get_pull_request_file_count(project_name):
    """
    get pull request file count
    return is like this:
    {
        22351: 2, 22352: 2, 22353: 2,
        22354: 2, 22355: 30, 22356: 1
    }
    (key:pull request number,value:file count)
    """
    SQL1 = SET_PROJECT_NAME.format(project_name)
    SQL2 = GET_PULL_REQUEST_FILE_COUNT
    cursor.execute(SQL1)
    cursor.execute(SQL2)
    # mysql_connect.commit()
    result = cursor.fetchall()
    info_list = {i[0]: i[1] for i in result}
    return info_list


def get_request_after_open(project_name):
    SQL1 = SET_PROJECT_NAME.format(project_name)
    SQL2 = GET_TIME_AFTER_OPEN
    cursor.execute(SQL1)
    cursor.execute(SQL2)
    result = cursor.fetchall()
    info_dict = {i[0]: i[1] for i in result}
    return info_dict


def get_module_name(project_name):
    """
    return is like this:
    {
        22351: ['src/os'],
        22352: ['qa/tasks', 'src/rgw'],
        22353: ['src/osdc'],
        22354: ['src/client']
    }
    """
    SQL1 = SET_PROJECT_NAME.format(project_name)
    SQL2 = GET_REQUEST_MODULE
    cursor.execute(SQL1)
    cursor.execute(SQL2)
    result = cursor.fetchall()
    module_dict = {i[0]: i[1].split(',') for i in result}
    return module_dict


def get_request_user_for_bayes(project_name):
    start_time = '2010-09-01 00:00:00'
    end_time = '2019-09-01 00:00:00'
    SQL = GET_PULL_REQUEST_USER2.format(project_name, start_time, end_time)
    cursor.execute(SQL)
    result = cursor.fetchall()
    info_dict = {i[0]: [i[1]] for i in result}
    return info_dict


def get_project_name():
    SQL = GET_PROJECT_NAME
    cursor.execute(SQL)
    result = cursor.fetchall()
    project_list = [i[0] for i in result]
    return project_list

# utils func for Request Matrix


def get_pull_request_user_and_date(project_name):
    """
    return is like
    [
        {'number': 1, 'requester': 'stass', 'request_date': '2011-09-22 04:03:04'},
        {'number': 2, 'requester': 'stass', 'request_date': '2011-10-04 23:32:05'},
        {'number': 5, 'requester': 'homac', 'request_date': '2011-12-15 21:43:03'}
    ]

    """
    SQL = GET_PULL_REQUEST_USER_AND_DATE.format(project_name)
    cursor2.execute(SQL)
    result = cursor2.fetchall()
    return result


# only for statistics
def get_comment_user_and_date2(project_name):
    """

    :param project_name:
    :return: the structure is like this:
    {
        "1": {
            "wido": ["2013-02-04 13:45:02"],
            "glowell2": ["2013-02-04 17:34:02"]},
        "5": {
            "dmick": ["2014-01-18 00:44:03"]},
        "6": {
            "ghost": ["2014-02-14 02:29:03","2014-02-19 22:12:04"]}
    }

    """
    SQL = GET_COMMENT_USER_AND_DATE_GROUP_BY_NUMBER2.format(project_name)
    cursor.execute(SQL)
    result = cursor.fetchall()

    info_dict = defaultdict(dict)

    for item in result:
        number = item[0]
        user = item[1].split(',')
        date = item[2].split(',')

        group = zip(user, date)

        for user, date in group:
            date_list = info_dict[number].get(user, [])
            date_list.append(date)
            info_dict[number][user] = date_list

    return info_dict


def build_review_and_request_diff(project_name,exclude_list):
    import datetime
    import time
    request_info = get_pull_request_user_and_date(project_name)
    comment_info = get_comment_user_and_date2(project_name)
    result_dict = defaultdict(list)
    print(comment_info)
    print(request_info)
    project = project_name.split('/')[1]
    for pr in request_info:
        pull_number = pr.get('number')
        pull_date = pr.get('request_date')
        requester = pr.get('requester')
        print(pull_number, pull_date, requester)
        comments = comment_info.get(pull_number)
        print(f'---comments--\n')
        if not comments:
            continue
        for commenter, comment_date in comments.items():
            if requester == commenter:
                continue
            if commenter in exclude_list:
                continue
            # comment_date = datetime.datetime.strptime(comment_date[0],'%Y-%m-%d %H:%M:%S')
            # pull_date2 = datetime.datetime.strptime(pull_date, '%Y-%m-%d %H:%M:%S')
            comment_date = time.mktime(time.strptime(comment_date[0], "%Y-%m-%d %H:%M:%S"))
            pull_date2 = time.mktime(time.strptime(pull_date, "%Y-%m-%d %H:%M:%S"))
            time_diff = int(round((comment_date-pull_date2)/60, 0))
            # print(commenter,time_diff)
            print(f'{commenter},{pull_number},{requester},{time_diff}')
            result_dict[commenter].append({'{}:{}'.format(pull_number,requester):time_diff})
            with open('{}.csv'.format(project),'a') as f:
                f.write(f'{commenter},{pull_number},{requester},{time_diff}')
                f.write('\n')
    return dict(result_dict)


def get_train_start_number(project_name,start_time):
    SQL = GET_START_TRAIN_PULL_NUMBER.format(project_name,start_time)
    print(SQL)
    cursor.execute(SQL)
    result = cursor.fetchall()[0]
    return result




def get_pull_request_count(project_name, start_time, end_time):
    SQL = GET_PULL_REQUEST_COUNT.format(project_name,start_time,end_time)
    cursor.execute(SQL)
    result = cursor.fetchall()[0]
    return result
