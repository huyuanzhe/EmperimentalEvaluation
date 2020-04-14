from storage.utils import get_request_title_description
from storage.utils import get_comments_count
from storage.utils import get_test_number, get_pull_request_total, get_reviewer, get_comment_date_max_min
from storage.utils import get_pull_request_user, get_comment_user_and_date, get_pull_request_user_for_test
from collections import Counter
from common.utils import delete_stop_words,sort_priority
from common.algorithms import TermFrequency
from common.algorithms import cosine_similarity
from collections import defaultdict
import datetime
import os
import numpy
import json
import time
import networkx as nx
from common.log import LogAdapter
from multiprocessing import Pool

from storage.sql import ONE_MONTH,HALF_YEAR,THREE_MONTH, ONE_YEAR

from common.settings import PROJECT_NAME
LOG_NAME = 'CommentNetwork'
LOG = LogAdapter().set_log(LOG_NAME)

EMPIRICAL_VALUE = 1.0
DECAY_FACTOR = 0.6

parent_dir = os.path.abspath(os.pardir)
save_path = os.path.join(parent_dir, 'result', 'comment_network')
print(save_path)
if not os.path.exists(save_path):
    os.mkdir(save_path)


class CosineSimilarity(object):
    def __init__(self,project_name):
        self.project_name = project_name
        self.comments = get_comments_count(self.project_name)

    @staticmethod
    def cos_score(new_word, past_word):
        return cosine_similarity(new_word, past_word)

    def score(self, new_word, past_word, number):
        return self.cos_score(new_word, past_word) * number


class CommentNetwork(object):
    def __init__(self, project_name,train_time):
        self.project_name = project_name
        self.comment_info = get_comment_user_and_date(self.project_name)
        self.default_corpus = self.corpus_prepare(train_time)
        self.max_date, self.min_date = get_comment_date_max_min(self.project_name)
        self.nx = nx.DiGraph()

    def corpus_prepare(self,train_time):
        LOG.info('Start to corpus prepare for Comment Network')
        corpus_dict = defaultdict(dict)
        try:
            request_info = get_pull_request_user(self.project_name,train_time)
            for request_user, value in request_info.items():
                for request_number in value:
                    comment_user_info = self.comment_info.get(request_number, None)

                    # delete pull request user own comment
                    comment_user_info.pop(request_user, None) if comment_user_info else None
                    # if pull request not comment continue
                    if not comment_user_info:
                        continue
                    #  TODO have fixed
                    # at here,the pull request number is unique, so can easy update.
                    corpus_dict[request_user].update({request_number: comment_user_info})
        except Exception as e:
            LOG.error('Failed in corpus prepare,cause {}'.format(e), exc_info=True)
            raise e

        return corpus_dict

    def calculate_egde_weight(self, comment_date):
        emprircal_value = EMPIRICAL_VALUE
        decay_factor = DECAY_FACTOR
        base_line = datetime.datetime.strptime(self.min_date, '%Y-%m-%d')
        deadline = datetime.datetime.strptime(self.max_date, '%Y-%m-%d')

        weight_list = []
        try:
            for item in comment_date:
                for index, date in enumerate(item):
                    # factor formula is
                    factor = pow(decay_factor, index)
                    timestamp = datetime.datetime.strptime(date, '%Y-%m-%d')
                    t = (timestamp - base_line) / (deadline - base_line)
                    # timestamp = datetime.datetime.strftime()
                    weight = factor * t
                    weight_list.append(weight)
            sum_weight = numpy.sum(weight_list) * emprircal_value
        except Exception as e:
            LOG.error('Error in Calculate_edge_weight ,Cause {}, Comment_date is {}'.format(e, comment_date), exc_info=True)
            sum_weight = 0
        return sum_weight

    def update_graph(self, reuquest_user, comment_info):
        comment_dict = defaultdict(list)
        node = reuquest_user
        # add node
        try:
            if not self.nx.has_node(node):
                self.nx.add_node(reuquest_user)

            for number, comment_user_info in comment_info.items():
                for comment_user, comment_date in comment_user_info.items():
                    comment_dict[comment_user].append(comment_date)

            for edge, comment_date in comment_dict.items():
                # comment date structure is like [[2013-02-04 17:34:02],[2014-03-07 23:55:04,2014-12-04 23:50:02]]
                weight = self.calculate_egde_weight(comment_date)
                # add edge and weight
                self.nx.add_edge(node, edge, weight=weight)
                print(reuquest_user, edge, weight)
        except Exception as e:
            LOG.error('Error update graph, Cause {}, request_user is {},comment_info is {}'.format(e, reuquest_user, comment_info), exc_info=True)

    def init_graph(self):
        graph_data = self.default_corpus
        # user is node.
        print('start init ------')
        for request_user, comment_info in graph_data.items():
            self.update_graph(request_user, comment_info)
        print('end init -----')

    def corpus_test(self):
        self.init_graph()
        test_info = get_pull_request_user_for_test(self.project_name)
        return test_info, self.comment_info

    def get_graph_edge(self, request):
        edge_list = list()
        origin = self.nx.edges()
        try:
            for item in origin:
                request_user = item[0]
                comment_user = item[1]
                if request_user == request:
                    weight = self.nx.get_edge_data(request_user,comment_user).get('weight', 0)
                    weight_list = [request_user,comment_user,weight]
                    edge_list.append(weight_list)
            sort_edge_list = sorted(edge_list, key=lambda x: x[2], reverse=True)
            if not edge_list:
                print('{} no comment network'.format(request))
        except Exception as e:
            LOG.error('Error in get_graph_edge, Cause {}, request is {}'.format(e, request),exc_info=True)
            sort_edge_list = None
        return sort_edge_list


class Process(object):
    def __init__(self, project_name):
        self.project_name = project_name
        self.cs = CosineSimilarity(self.project_name)
        self.tf = TermFrequency()

    def get_corpus(self,train_time):
        request_infos = get_request_title_description(self.project_name,train_time)

        key_list = list()
        word_list = list()
        for request_info in request_infos:
            number = list(request_info.keys())[0]
            data = list(request_info.values())[0]
            valid_word = delete_stop_words(data)
            word = Counter(valid_word)

            key_list.append(number)
            word_list.append(word)

        return key_list, word_list

    def get_corpus_result(self,train_time):
        key_list, count_list = self.get_corpus(train_time)
        start = time.time()

        score_dict = {}
        for key, count in zip(key_list, count_list):

            word_score = {word: self.tf.tf_idf(word, count, count_list) for word in count}
            sorted_score = dict(sorted(word_score.items(), key=lambda x: x[1], reverse=True))

            sorted_list = list(sorted_score.keys())
            score_dict.update({key: sorted_list})
        end = time.time()
        print('spend time is {}'.format(end - start))
        return score_dict

    def cos_score(self, new, past, reviewer, k):
        """
        in this function will get pull request similarity.
        :param new:
        :param past:
        :param k: the number of pull request
        :return:
        """
        review_dict = {}

        for number, past_word in past.items():
            lib_tech_past = list(past_word)
            past_reviewer = reviewer.get(number)
            if not lib_tech_past or not new or not past_reviewer:
                continue

            score = self.cs.score(new, past_word, number)

            for rpv in past_reviewer:
                if rpv not in review_dict:
                    review_dict.setdefault(rpv, score)

                else:
                    past_score = review_dict.get(rpv)
                    review_dict.update({rpv: past_score + score})

        candidate_list_sort = sorted(review_dict.items(), key=lambda item: item[1], reverse=True)
        # strip zero score
        strip_zero_value = list(filter(lambda i: i[1] > 0, candidate_list_sort))

        if len(strip_zero_value) > 0:
            split_list = candidate_list_sort[0:k]
            result = [i[0] for i in split_list]
        else:
            result = []

        return result

    def cos_test_info(self,train_time):
        # get word vector
        info_dict = self.get_corpus_result(train_time)
        # get predict interval
        reviewer = get_reviewer(self.project_name)
        print(reviewer)

        # test_number = get_test_number(self.project_name)
        # for i in test_number:
        #     new_word = info_dict.get(i)
        #     past_dict = {k: v for k, v in info_dict.items() if (k < i)}
        #     score_list = self.cos_score(new_word, past_dict, reviewer, 5)
        #     print(score_list)

        return info_dict, reviewer


def graph_func(comment_info_all, number, pull_request_user, cn):
    edge_info = cn.get_graph_edge(pull_request_user)

    comment_info = comment_info_all.get(number, None)
    comment_info.pop(pull_request_user, None) if comment_info else None
    corpus_comment_info = cn.default_corpus.get(pull_request_user)

    if not comment_info:
        LOG.info('pull request {} valid comment info is empty'.format(number))
        return
    if not corpus_comment_info:
        LOG.info('corpus no request user:{} comment info'.format(pull_request_user))
        return

    cn.update_graph(pull_request_user, corpus_comment_info)
    cn.default_corpus[pull_request_user][number] = comment_info

    return edge_info


def cos_func(info_dict, number, reviewer, proc):
    new_word = info_dict.get(number)
    past_dict = {k: v for k, v in info_dict.items() if (k < number)}
    score_list = proc.cos_score(new_word, past_dict, reviewer, 5)
    return score_list


def write_to_file(file_name, info):
    file_path = os.path.join(save_path, file_name)
    with open('{}.txt'.format(file_path), 'a') as f:
        f.write(json.dumps(info))
        f.write('\n')


def compare_result(predict, review, count_dict):
    result = set(predict) & set(review)
    count_dict['all'] += 1
    if result:
        count_dict['right'] += 1
    else:
        count_dict['wrong'] += 1

    return count_dict


def save_rate(project,name, count_dict):
    dict_value = list(count_dict.values())
    try:
        rate = dict_value[0] / (dict_value[0] + dict_value[1])
    except ZeroDivisionError:
        rate = 0
    info = {'project:{} rate:{:.2%}'.format(project, rate): count_dict}
    file_name = '{}'.format(name)
    write_to_file(file_name, info)


def main(project,train_time):
    start_time = time.time()
    proc = Process(project)
    file_name = project.split('/')[1] + train_time.replace('-', '_')
    print('Start Prepare Corpus')
    info_dict, reviewer = proc.cos_test_info(train_time)
    cn = CommentNetwork(project,train_time)
    test_info, comment_info_all = cn.corpus_test()

    end_train_time = time.time()
    spend_train_time = end_train_time - start_time
    print('start test-----')
    count_dict1 = {'right': 0, 'wrong': 0, 'all':0}
    count_dict3 = {'right': 0, 'wrong': 0, 'all':0}
    count_dict5 = {'right': 0, 'wrong': 0, 'all':0}
    predict_time = []
    update_time = []
    for number, pull_request_user in test_info.items():
        try:
            comment_info = comment_info_all.get(number, None)
            if not comment_info:
                # write_to_file(file_name, {number: 'this pull request no comment info'})
                continue

            comment_info_key = list(comment_info.keys())
            start_predict_time = time.time()

            score_list = cos_func(info_dict, number, reviewer, proc)
            print(number, pull_request_user, score_list)
            end_predict_time = time.time()

            predict_time.append(end_predict_time - start_predict_time)
            if not score_list:
                continue

            print('========== graph test ========')
            start_update_time = time.time()
            edge_info = graph_func(comment_info_all, number, pull_request_user, cn)
            end_update_time = time.time()
            update_time.append(end_update_time - start_update_time)
            if edge_info:
                network_user = [i[2] for i in edge_info]
                commented_user = sort_priority(score_list, network_user)
            else:
                commented_user = score_list

            # write_to_file(file_name, {number: commented_user})
            commented_user_1, commented_user_3, commented_user_5 = [commented_user[0]],commented_user[0:2],commented_user

            count_dict1 = compare_result(commented_user_1, comment_info_key,count_dict1)
            count_dict3 = compare_result(commented_user_3, comment_info_key,count_dict3)
            count_dict5 = compare_result(commented_user_5, comment_info_key,count_dict5)
        except Exception as e:
            LOG.error('Error in {}:{},  Cause {}'.format(number, pull_request_user, e), exc_info=True)
    save_rate(project, file_name, count_dict1)
    save_rate(project, file_name, count_dict3)
    save_rate(project, file_name, count_dict5)
    end_time = time.time()
    spend_time = end_time - start_time
    predict_time = numpy.sum(predict_time)
    update_time = numpy.sum(update_time)

    write_to_file(file_name,f'spend_train_time time is {spend_train_time}')
    write_to_file(file_name,f'predict_time time is {predict_time}')
    write_to_file(file_name,f'update_time time is {update_time}')
    write_to_file(file_name,f'spend time is {spend_time}')
    print('end test----')


if __name__ == '__main__':

    project_name_list = PROJECT_NAME
    pool = Pool()
    for project in project_name_list:
        print(project)
        train_time = [
            ONE_YEAR,
            # HALF_YEAR,
            # THREE_MONTH,
            # ONE_MONTH
        ]
        for i in train_time:
            pool.apply_async(main, (project, i))
            # main(project,i)

    # pool.close()
    # pool.join()

#
# TIME = [ONE_YEAR,HALF_YEAR,THREE_MONTH,ONE_MONTH]
# for i in TIME:
#     main(project_name,i)



