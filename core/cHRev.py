# coding = utf8
import copy
import datetime
import json

from src.utils import *


def calculate_xFactor(comment_dict):
    # print(comment_dict)

    xFactor_dict = {}
    for user in comment_dict:
        user_comments = comment_dict[user]
        # print(user_comments)
        comment_count = len(user_comments)
        workdays = list(set(user_comments))
        workdays.sort()
        workday_count = len(workdays)
        recency = workdays[workday_count - 1]
        if user in xFactor_dict:
            pass
            #print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        else:
            xFactor_dict[user] = [comment_count, workday_count, recency]

    # print(xFactor_dict)
    return xFactor_dict


def sum_xFactor(base_dict, new_dict):
    # print(base_dict)
    # print(new_dict)

    for user in new_dict:
        if user in base_dict:
            base_comment_cout = base_dict[user][0]
            base_workday_cout = base_dict[user][1]
            base_recency = base_dict[user][2]

            new_comment_cout = new_dict[user][0]
            new_workday_cout = new_dict[user][1]
            new_recency = new_dict[user][2]

            base_dict[user][0] = base_comment_cout + new_comment_cout
            base_dict[user][1] = base_workday_cout + new_workday_cout
            temp_list = [base_recency, new_recency]
            temp_list.sort()
            base_dict[user][2] = temp_list[1]
        else:
            base_dict[user] = copy.deepcopy(new_dict[user])

    # print(base_dict)
    return base_dict


def train(pr_ids, files, comments):
    sum_dict = {}
    total_file = 0
    for pr_id_train in pr_ids:
        # print(type(pr_id_train))
        xFactor_dict = calculate_xFactor(comments[pr_id_train])

        if pr_id_train in files:
            # sum xFactor to each file
            for file in files[pr_id_train]:
                if file in sum_dict:
                    temp_dict = sum_dict[file]
                    sum_dict[file] = sum_xFactor(temp_dict, xFactor_dict)
                else:
                    sum_dict[file] = copy.deepcopy(xFactor_dict)
                    total_file = total_file + 1
        else:
            pass
            #print("=======================================%s" % pr_id_train)
    # print(total_file)
    # print(len(sum_dict))
    return sum_dict


def rank(prepare_to_rank):
    score_dict = {}
    for score in prepare_to_rank:
        if score[0] in score_dict:
            temp = score_dict[score[0]]
            temp = temp + score[1]
            score_dict[score[0]] = temp
        else:
            score_dict[score[0]] = score[1]
    ranked_dict = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
    return ranked_dict


def recommend(data, files):
    new_file_count = 0
    user_xFactors = []
    for file in files:
        if file in data:
            file_xFactor = data[file]
            comments = []
            workdays = []
            recencys = []
            for user in file_xFactor:
                comments.append(file_xFactor[user][0])
                workdays.append(file_xFactor[user][1])
                recencys.append(file_xFactor[user][2])
            total_comment = sum(comments)
            total_workday = sum(workdays)
            recencys.sort()
            recency = recencys[len(recencys) - 1]

            user_recency = 0.0
            user_comments = 0.0
            user_workdays = 0.0
            for user in file_xFactor:
                if file_xFactor[user][2] == recency:
                    user_recency = 1.0
                else:
                    user_recency = 0.0
                user_comments = float(file_xFactor[user][0]) / float(total_comment)
                user_workdays = float(file_xFactor[user][1]) / float(total_workday)
                user_xFactor = user_comments + user_workdays + user_recency
                user_xFactors.append([user, user_xFactor])
        else:
            new_file_count = new_file_count + 1

    if new_file_count == len(files):
        #print("there is no reviewer to recomend, because of change files are all new file!")
        return {}

    ranked_dict = rank(user_xFactors)
    return ranked_dict


def recommend_reviewer(repo, start_train, start_rec, end_rec):

    #sum_dict = {}

    # get comments by pull request
    train_comments = get_comment_user_and_date_between(start_tain, start_rec, repo)
    #print(len(train_comments))

    # record pull request id
    pr_ids_train = []
    for key in train_comments:
        pr_ids_train.append(key)

    # get files for training set
    train_files = get_file_name_between(repo, pr_ids_train[0], pr_ids_train[len(pr_ids_train) - 1])
    #print(len(train_files))
    # get comments for test set
    test_comments = get_comment_user_and_date_between(start_rec, end_rec, repo)
    #print(len(test_comments))
    pr_ids_test = []
    for key in test_comments:
        pr_ids_test.append(key)

    # get files for test set
    test_files = get_file_name_between(repo, pr_ids_test[0], pr_ids_test[len(pr_ids_test) - 1])
    #print(len(test_files))

    #start to recommend, record time
    start_time = datetime.datetime.now()
    sum_dict = train(pr_ids_train, train_files, train_comments)

    results = defaultdict(dict)


    for pr_id_test in pr_ids_test:
        if pr_id_test in test_files:
            result = recommend(sum_dict, test_files[pr_id_test])
            temp = results[pr_id_test].get(pr_id_test, [])
            temp.extend(result)
            results[pr_id_test][pr_id_test] = temp

            xFactor_dict_test = calculate_xFactor(test_comments[pr_id_test])

            # sum xFactor to each file
            for file in test_files[pr_id_test]:
                if file in sum_dict:
                    temp_dict = sum_dict[file]
                    sum_dict[file] = sum_xFactor(temp_dict, xFactor_dict_test)
                    # print("%s-----------------------%s" % (pr_id_train, file))
                else:
                    sum_dict[file] = copy.deepcopy(xFactor_dict_test)
        else:
            pass
            #print("=======================================%s" % pr_id_test)
    # print(len(rec_comments))
    #print(results)
    #print(len(results))
    end_time = datetime.datetime.now()
    span = end_time - start_time

    return results, span.total_seconds()


if __name__ == '__main__':
    print('start')
    repos = ["angular/angular.js", "atom/atom", "ceph/ceph", "django/django", "facebook/react", "flutter/flutter", "laravel/laravel", "microsoft/vscode", "pytorch/pytorch", "vuejs/vue", "moment/moment", "mrdoob/three.js"]
    #repos = ["angular/angular.js"]
    repo_name = ["angular.js", "atom", "ceph", "django", "react", "flutter", "laravel", "vscode", "pytorch", "vue", "moment", "three.js"]
    start_tain = '2017-09-01'
    start_rec = '2018-09-01'
    end_rec = '2019-09-01'
    for i in range(0, len(repos)):
        #print("------------%s" % repos[i])
        #t1 = datetime.datetime.now()
        results, time_span = recommend_reviewer(repos[i], start_tain, start_rec, end_rec)
        #t2 = datetime.datetime.now()
        #span = t2 - t1
        print(time_span)

        file_path = 'result/cHRev/%s%s.txt' % (repo_name[i], start_tain)
        try:
            with open(file_path, 'w') as f:
                for result in results:
                    line = json.dumps(results[result]) + '\n'
                    f.write(line)
                time_span_str = str(time_span) + '\n'
                f.write(time_span_str)
                f.close()
        except Exception as e:
            print("Exception: %s" % e)
