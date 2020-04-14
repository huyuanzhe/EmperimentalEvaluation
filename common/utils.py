import csv
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from itertools import chain
from collections import defaultdict
from functools import wraps
from contextlib import ExitStack
from common.log import LogAdapter
LOG = LogAdapter().set_log('CommonUtils')


def split_file_length(file_name):
    if '\\' in file_name:
        file_length = file_name.split("\\")
        return file_length
    else:
        file_length = file_name.split("/")
        if '' in file_length:
            file_length.remove('')
        return file_length


def get_file_score(new_file, past_file):
    """
    return the number of directory/file name that
    appear from the beginning of both filepath
    :param new_file: new review file
    :param past_file: past review file
    :return: the number of directory /file the same
    """

    n_list = split_file_length(new_file)
    p_list = split_file_length(past_file)
    score = 0

    for i, j in zip(n_list, p_list):
        if i != j:
            break
        score += 1
    return score


def read_info(filename):
    info_dict = dict()
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for item in reader:
            if reader.line_num == 1:
                continue
            try:
                file = item[0]
                token = item[1].split()
                info_dict.update({file: token})
            except Exception as e:
                LOG.error('get token error cause {} and items content is {}'.format(e,item),)
    return info_dict


def delete_stop_words(data):
    """
    delete stop word by use nltk, before use you may should download nltk stopword file
    command like this:
        import nltk
        nltk.download("stopwords")
    :param data:
    :return:
    """
    lower_data = data.lower()

    tokenizer = RegexpTokenizer(r'\w+')
    raw_token = tokenizer.tokenize(lower_data)
    stop_words = set(stopwords.words('english'))

    no_stop_word = filter(lambda i: i not in stop_words, raw_token)
    filter_word = filter(lambda i: len(i) > 2 and i.isalpha, no_stop_word)
    no_stop_word_list = list(filter_word)

    return no_stop_word_list


def sort_priority(values, group):
    def helper(x):
        if x in group:
            return (0, x)
        return (1, x)
    values.sort(key=helper)
    return values


def get_map(info_dict):
    # counter = Counter(chain(*info_values))
    # print(f'counter info is {counter}')
    origin = chain(*info_dict.values())
    map_key = set(origin)
    map_key_sort = sorted(map_key)
    map_value = [str(i) for i in range(1, len(map_key) + 1)]
    # print(f'map_key {len(map_key)},map_key sorted {len(map_key_sort)},map_value {len(map_value)}')
    map_dict = dict(zip(map_key_sort, map_value))
    # print(map_dict)

    return map_dict


def convert_mapping_dict(info_dict, mapping_dict):
    convert_dict = defaultdict(list)
    for i, j in info_dict.items():
        for s in j:
            convert_dict[i].append(mapping_dict.get(s))
    convert_dict = dict(convert_dict)
    return convert_dict


def dict_decorate(func):
    @wraps(func)
    def inner(*args):
        result_dict = func(*args)
        map_dict = get_map(result_dict)
        convert_dict = convert_mapping_dict(result_dict, map_dict)
        return convert_dict, map_dict
    return inner





