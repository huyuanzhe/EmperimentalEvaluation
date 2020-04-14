import time
import json
from common.log import LogAdapter
from common.settings import SIGMA, WRC_FLAG
from common.algorithms import FPSScore
from storage.utils import *
from common.settings import PROJECT_NAME
from storage.sql import ONE_MONTH,HALF_YEAR,THREE_MONTH, ONE_YEAR
from multiprocessing import Pool
import datetime


LOG = LogAdapter().set_log('FpsScore')


class CountFps(object):
    def __init__(self):
        self.fp = FPSScore()

    def count_score(self, Rn, Rp_file_name, m):
        if WRC_FLAG:
            score = self.fp.score2(Rn,Rp_file_name,m)
        else:
            score = self.fp.score(Rn,Rp_file_name,m)

        return score

    def main(self,Rn, Rps, Rp_viewers_all, k):
        """

        :param Rn: new review request
        :param k: the number of top candidates
        :return:
        """
        start_time = time.time()
        # print(Rps)
        m = 0
        review_dict = dict()
        # print(Rp_viewers_all)
        # print(Rp_viewers_all)
        for Rp_number, Rp_file_name in Rps.items():
            Rp_viewers = Rp_viewers_all.get(Rp_number)
            if not Rp_viewers:
                continue
            # the review count is this meaning of how many people review on this pull_request
            score = self.count_score(Rn, Rp_file_name, m)

            for rpv in Rp_viewers:
                i = 0
                if WRC_FLAG:
                    coef = m - i - 1
                    score = score * pow(SIGMA, coef)
                    if rpv not in review_dict.keys():
                        review_dict.setdefault(rpv, score)
                    else:
                        past_score = review_dict.get(rpv)
                        review_dict.update({rpv: past_score + score})
                else:
                    if rpv not in review_dict.keys():
                        review_dict.setdefault(rpv, score)
                    else:
                        past_score = review_dict.get(rpv)
                        review_dict.update({rpv: past_score + score})
                i += 1

            m += 1

        candidate_list_sort = sorted(review_dict.items(), key=lambda item: item[1], reverse=True)
        end_time = time.time()
        print('spend time is:', end_time-start_time)
        value = candidate_list_sort[0:k]
        value = [i[0] for i in value]
        predict = candidate_list_sort
        return value, predict


def run(PROJECT_NAME,train_time):

    start_time = time.time()

    cf = CountFps()
    number_list = get_test_number(PROJECT_NAME)
    print(len(number_list))
    train_start_number = get_train_start_number(PROJECT_NAME,train_time)

    judge_dict1 = {'right': 0, 'wrong': 0, 'all': 0}
    judge_dict3 = {'right': 0, 'wrong': 0, 'all': 0}
    judge_dict5 = {'right': 0, 'wrong': 0, 'all': 0}
    all_reviewer = get_reviewer(PROJECT_NAME, train_start_number)
    all_file = get_file_name(PROJECT_NAME, train_start_number)
    not_valie_id = []
    save_file_name = PROJECT_NAME.split('/')[1] + train_time.replace('-','_')
    if WRC_FLAG:
        save_file_name = save_file_name + '_WRC'
    for i in number_list:
        Rpf = {k: v for k, v in all_file.items() if k < i}
        Rp_viewers_all = {k: v for k, v in all_reviewer.items() if k < i}

        judge_dict1['all'] += 1
        judge_dict3['all'] += 1
        judge_dict5['all'] += 1

        f = all_file.get(i)
        print(f)
        r = all_reviewer.get(i)

        if not r or not f:
            not_valie_id.append(i)
            with open('{}.txt'.format(save_file_name), 'a') as f:
                f.write(json.dumps({i: 'this pull request id is not file or not comments!'}))
                f.write('\n')
            continue

        print(r)
        result, predict = cf.main(f, Rpf, Rp_viewers_all, 5)
        result1,result3,result5 = [result[0]],result[0:3], result
        print(result)

        with open('{}.txt'.format(save_file_name), 'a') as f:
            f.write(json.dumps({i: predict}))
            f.write('\n')

        # 比较两个列表元素是否有相同元素，并拿到它。

        compare_result1 = set(result1) & set(r)
        compare_result3 = set(result3) & set(r)
        compare_result5 = set(result5) & set(r)

        print('result1',compare_result1)
        print('result3',compare_result3)
        print('result5',compare_result5)

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

    end_time = time.time()

    print('Total spend time is {}'.format(end_time-start_time))
    rate1 = '{:.2%}'.format(judge_dict1['right'] / (judge_dict1['right'] + judge_dict1['wrong']))
    rate3 = '{:.2%}'.format(judge_dict3['right'] / (judge_dict3['right'] + judge_dict3['wrong']))
    rate5 = '{:.2%}'.format(judge_dict5['right'] / (judge_dict5['right'] + judge_dict5['wrong']))
    with open('{}.txt'.format(save_file_name), 'a') as f:
        f.write(json.dumps(rate1))
        f.write(json.dumps(rate3))
        f.write(json.dumps(rate5))
        f.write('\n')
        f.write('Total spend time is {}'.format(end_time-start_time))
    value_dict1 = {'project:{} rate:{}'.format(project_name, rate1): judge_dict1}
    value_dict3 = {'project:{} rate:{}'.format(project_name, rate3): judge_dict3}
    value_dict5 = {'project:{} rate:{}'.format(project_name, rate5): judge_dict5}
    with open('{}.txt'.format(save_file_name), 'a') as f:
        f.write('{}\n'.format(json.dumps(value_dict1)))
        f.write('{}\n'.format(json.dumps(value_dict3)))
        f.write('{}\n'.format(json.dumps(value_dict5)))
        f.write('Total spend time is {}'.format(end_time-start_time))

    LOG.info(json.dumps(value_dict1), json.dumps(value_dict3), json.dumps(value_dict5))


if __name__ == '__main__':
    all_list = []
    if not PROJECT_NAME:
        print('No Project Name set.....')
    else:
        pool = Pool()

        project_name_list = PROJECT_NAME
        for project_name in project_name_list:
            print(project_name)

            train_time = [ONE_YEAR,HALF_YEAR,THREE_MONTH,ONE_MONTH]
            for i in train_time:
                # pool.apply_async(run,(project_name,i))
                run(project_name,i)
        pool.close()
        pool.join()
            # all_list.append(value_dict)

