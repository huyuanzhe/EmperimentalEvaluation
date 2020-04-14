import math
import os
import time
from common.utils import read_info
from storage.utils import *
from common import algorithms
import json
from common.settings import PROJECT_NAME
from multiprocessing import Pool

from common.log import LogAdapter
LOG = LogAdapter().set_log('CrossProject')


class TokenProcess(object):
    def __init__(self, project_name):
        file_name = project_name.split('/')[1]
        self.file_name = '{}.csv'.format(file_name)
        self.project_name = project_name

    def get_request_token(self, train_start_number):
        """

        :param project_name: project name
        :return: get token dict by pull request
        """
        token = self.__get_all_token()
        token_dict = dict()
        file_name = get_file_name(self.project_name,train_start_number)
        for key, value in file_name.items():
            request_token = []
            # the key is pull request number and the value is this pull request file list
            # print(key)
            for file in value:
                # if token list not this file ,will get empty list
                file_token = token.get(file,[])
                request_token.extend(file_token)
            # delete same token
            request_token = list(set(request_token))
            token_dict.update({key: request_token})
        request_token_dict = dict(sorted(token_dict.items(),key=lambda items: items[0]))
        return request_token_dict

    def __get_all_token(self):
        path = os.getcwd()
        path = os.path.dirname(path)
        csv_path = os.path.join(path, 'sample', self.file_name)
        result = read_info(csv_path)
        return result


class Algorithms(object):
    def __init__(self,project_name):
        self.project_name = project_name

    def main(self, Rn, Rp, reviewer, k):
        time1 = time.time()
        review_dict = {}
        lib_tech_new = list(Rn.values())[0]
        for key, value in Rp.items():
            lib_tech_past = list(value)
            past_review = reviewer.get(key)
            if not lib_tech_past or not lib_tech_new or not past_review:
                continue
            score = algorithms.cosine_similarity(lib_tech_new, lib_tech_past)
            for rpv in past_review:
                if rpv not in review_dict.keys():
                    review_dict.setdefault(rpv, score)
                else:
                    past_score = review_dict.get(rpv)
                    review_dict.update({rpv: past_score + score})
        candidate_list_sort = sorted(review_dict.items(), key=lambda item: item[1], reverse=True)
        # print('---length is ',len(candidate_list_sort))
        split_list = candidate_list_sort[0:k]
        predict = candidate_list_sort[0:10]
        if not split_list:
            print('No Result')
        result = [i[0] for i in split_list]
        time2 = time.time()
        spend_time = time2 - time1
        print('spedn time is {}'.format(spend_time))
        return result,predict


def main(project_name,train_time):
    time1 = time.time()
    train_start_number = get_train_start_number(project_name,train_time)

    reviewer = get_reviewer(project_name)
    test_number = get_test_number(project_name)

    app = TokenProcess(project_name)
    all_token = app.get_request_token(train_start_number)
    alg = Algorithms(project_name)

    save_file_name = project_name.split('/')[1] + '_cross' +train_time.replace('-','_')

    invalid_id = []
    judge_dict1 = {'right': 0, 'wrong': 0,'all': 0}
    judge_dict3 = {'right': 0, 'wrong': 0,'all': 0}
    judge_dict5 = {'right': 0, 'wrong': 0,'all': 0}

    for i in test_number:

        judge_dict1['all'] += 1
        judge_dict3['all'] += 1
        judge_dict5['all'] += 1

        r = reviewer.get(i)
        if not r:
            invalid_id.append(i)
            with open('{}.txt'.format(save_file_name), 'a') as f:
                f.write(json.dumps({i: 'this pull request not comments!'}))
                f.write('\n')
            continue

        token_info = all_token.get(i)
        new_token = {i: all_token.get(i)}
        # no token meaning this request file not import info
        if not token_info:
            invalid_id.append(i)
            with open('{}.txt'.format(save_file_name), 'a') as f:
                f.write(json.dumps({i: 'this pull request files not import info!'}))
                f.write('\n')
            continue

        past_token = {k: v for k, v in all_token.items() if (k < i)}
        result, predict = alg.main(new_token, past_token, reviewer, 5)
        result1,result3,result5 = [result[0]],result[0:3], result
        with open('{}.txt'.format(save_file_name), 'a') as f:
            f.write(json.dumps({i: predict}))
            f.write('\n')

        # print(result)
        # print(r)
        # 比较两个列表元素是否有相同元素，并拿到它。
        compare_result1 = set(result1) & set(r)
        compare_result3 = set(result3) & set(r)
        compare_result5 = set(result5) & set(r)

        print('result1', compare_result1)
        print('result3', compare_result3)
        print('result5', compare_result5)

        # print(compare_result)

        if compare_result1:
            judge_dict1['right'] += 1
        else:
            judge_dict1['wrong'] += 1

        if compare_result3:
            judge_dict3['right'] += 1
        else:
            judge_dict3['wrong'] += 1

        if compare_result5:
            judge_dict5['right'] += 1
        else:
            judge_dict5['wrong'] += 1

    time2 = time.time()
    spend_time = time2 - time1

    rate1 = '{:.2%}'.format(judge_dict1['right'] / (judge_dict1['right'] + judge_dict1['wrong']))
    rate3 = '{:.2%}'.format(judge_dict3['right'] / (judge_dict3['right'] + judge_dict3['wrong']))
    rate5 = '{:.2%}'.format(judge_dict5['right'] / (judge_dict5['right'] + judge_dict5['wrong']))
    with open('{}.txt'.format(save_file_name), 'a') as f:
        f.write(json.dumps(rate1))
        f.write(json.dumps(rate3))
        f.write(json.dumps(rate5))
        f.write('\n')
        f.write('Total spend time is {}'.format(spend_time))

    value_dict1 = {'project:{} rate1:{}'.format(project_name, rate1): judge_dict1}
    value_dict3 = {'project:{} rate3:{}'.format(project_name, rate3): judge_dict3}
    value_dict5 = {'project:{} rate5:{}'.format(project_name, rate5): judge_dict5}

    with open('{}_rate.txt'.format(save_file_name), 'a') as f:
        f.write('{}\n'.format(json.dumps(value_dict1)))
        f.write('{}\n'.format(json.dumps(value_dict3)))
        f.write('{}\n'.format(json.dumps(value_dict5)))
        f.write('Spend Time is {}'.format(spend_time))

    # LOG.info(value_dict1,value_dict3,value_dict5)
    print('Spend Time is {}'.format(spend_time))


if __name__ == '__main__':
    if not PROJECT_NAME:
        print('No Project Name set.....')
    else:
        project_name_list = PROJECT_NAME
        pool = Pool()
        for project in project_name_list:
            print(project)
            train_time = [ONE_YEAR,HALF_YEAR,THREE_MONTH,ONE_MONTH]
            for i in train_time:
                print(i)
                pool.apply_async(main, (project, i))
                # main(project,i)

        pool.close()
        pool.join()
