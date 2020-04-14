# coding = utf8
import copy
import datetime
import json

from src.utils import *


def calculate_pr_score(comment_dict, prScore):
    # print(comment_dict)

    wrc_dict = {}
    for user in comment_dict:

        if user in wrc_dict:
            #pass
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        else:
            wrc_dict[user] = prScore

    #print(wrc_dict)
    return wrc_dict


def sum_wrc(base_dict, new_dict):
    #print(base_dict)
    #print(new_dict)

    for user in new_dict:
        if user in base_dict:
            base_wrc = base_dict[user]
            new_wrc = new_dict[user]
            base_dict[user] = base_wrc + new_wrc
        else:
            base_dict[user] = copy.deepcopy(new_dict[user])

    #print(base_dict)
    return base_dict


def train(pr_ids, files, comments):
    sum_dict = {}
    total_file = 0
    #print("*************************************************")
    for pr_id_train in pr_ids:
        # print(type(pr_id_train))
        if pr_id_train in files:
            #print(len(files[pr_id_train]))
            prScore = 1.0/float(len(files[pr_id_train]))
            wrc_dict = calculate_pr_score(comments[pr_id_train], prScore)
            # sum pr score to each file
            for file in files[pr_id_train]:
                if file in sum_dict:
                    temp_dict = sum_dict[file]
                    sum_dict[file] = sum_wrc(temp_dict, wrc_dict)
                else:
                    sum_dict[file] = copy.deepcopy(wrc_dict)
                    total_file = total_file + 1
        else:
            pass
            #print("=======================================%s" % pr_id_train)
    # print(total_file)
    # print(len(sum_dict))

    #print("*************************************************")
    return sum_dict


def rank(prepare_to_rank):

    ranked_dict = sorted(prepare_to_rank.items(), key=lambda x: x[1], reverse=True)
    return ranked_dict


def recommend(data, files):
    new_file_count = 0
    user_wrc = {}
    for file in files:
        if file in data:
            file_wrc = data[file]
            for user in file_wrc:
                if user in user_wrc:
                    temp = user_wrc[user]
                    temp = temp + file_wrc[user]
                    user_wrc[user] = temp
                else:
                    user_wrc[user] = file_wrc[user]
        else:
            new_file_count = new_file_count + 1

    if new_file_count == len(files):
        #print("there is no reviewer to recomend, because of change files are all new file!")
        return {}

    ranked_dict = rank(user_wrc)
    #print(ranked_dict)
    return ranked_dict


def recommend_reviewer(repo, start_train, start_rec, end_rec):

    #sum_dict = {}

    # get comments by pull request
    train_comments = get_comment_user_and_date_between(start_train, start_rec, repo)
    #print(len(train_comments))

    # record pull request id
    pr_ids_train = []
    for key in train_comments:
        pr_ids_train.append(key)

    # get files for training set
    train_files = get_file_name_between(repo, pr_ids_train[0], pr_ids_train[len(pr_ids_train) - 1])
    #print(len(train_files))
    #print(train_files)
    # get comments for test set
    test_comments = get_comment_user_and_date_between(start_rec, end_rec, repo)
    #print(len(test_comments))
    pr_ids_test = []
    for key in test_comments:
        pr_ids_test.append(key)
    # get files for test set
    test_files = get_file_name_between(repo, pr_ids_test[0], pr_ids_test[len(pr_ids_test) - 1])

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

            prScore = 1.0/float(len(test_files[pr_id_test]))
            wrc_dict_test = calculate_pr_score(test_comments[pr_id_test], prScore)

            # sum wrc to each file
            for file in test_files[pr_id_test]:
                if file in sum_dict:
                    temp_dict = sum_dict[file]
                    sum_dict[file] = sum_wrc(temp_dict, wrc_dict_test)
                    # print("%s-----------------------%s" % (pr_id_train, file))
                else:
                    sum_dict[file] = copy.deepcopy(wrc_dict_test)
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
    start_train = '2018-08-01'
    start_rec = '2018-09-01'
    end_rec = '2019-09-01'
    for i in range(0, len(repos)):
        #print("------------%s" % repos[i])

        results, time_span = recommend_reviewer(repos[i], start_train, start_rec, end_rec)

        print(time_span)

        file_path = 'result/WRC/%s%s.txt' % (repo_name[i], start_train)
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
