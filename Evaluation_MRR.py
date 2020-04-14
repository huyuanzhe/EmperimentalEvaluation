# coding = utf8
from src.utils import *
import json

if __name__ == "__main__":
    print("start")
    files = []
    #repos = ["angular/angular.js", "atom/atom", "ceph/ceph", "django/django", "facebook/react", "flutter/flutter", "laravel/laravel", "microsoft/vscode", "pytorch/pytorch", "vuejs/vue", "moment/moment", "mrdoob/three.js"]
    #repos = ["angular/angular.js"]
    #repo_name = ["angular.js", "atom", "ceph", "django", "react", "flutter", "laravel", "vscode", "pytorch", "vue", "moment", "three.js"]
    #repo_name = ["angular.js"]
    #file_post = ["2017_09_01.txt","2018_03_01.txt","2018_06_01.txt","2018_08_01.txt"]
    #approach_name = ["FPS"]

    # CORRECT
    #repos = ["ceph/ceph", "django/django", "facebook/react", "flutter/flutter", "microsoft/vscode", "pytorch/pytorch", "vuejs/vue", "moment/moment", "mrdoob/three.js"]
    #repos = ["angular/angular.js"]
    #repo_name = ["ceph", "django", "react", "flutter", "vscode", "pytorch", "vue", "moment", "three.js"]
    #file_post = ["_cross2017_09_01.txt","_cross2018_03_01.txt","_cross2018_06_01.txt","_cross2018_08_01.txt"]
    #approach_name = ["CORRECT"]

    # WRC
    #repos = ["angular/angular.js"]
    repos = ["angular/angular.js", "atom/atom", "ceph/ceph", "django/django", "facebook/react", "flutter/flutter", "laravel/laravel", "microsoft/vscode", "pytorch/pytorch", "vuejs/vue", "moment/moment", "mrdoob/three.js"]
    #repo_name = ["angular.js"]
    repo_name = ["angular.js", "atom", "ceph", "django", "react", "flutter", "laravel", "vscode", "pytorch", "vue", "moment", "three.js"]
    file_post = ["2017_09_01_WRC.txt", "2018_03_01_WRC.txt", "2018_06_01_WRC.txt", "2018_08_01_WRC.txt"]
    approach_name = ["WRC"]

    repo_dict = {}
    for i in range(0, len(repos)):
        repo_dict[repo_name[i]] = get_reviewer(repos[i])

    for i in range(0, len(approach_name)):

        for j in range(0, len(repo_name)):
            #print(repo_name[j])
            repo_data = repo_dict[repo_name[j]]
            #for item in repo_data:
             #   print(type(item))

            for k in range(0, len(file_post)):
                file_path = "result/%s/%s%s" % (approach_name[i],  repo_name[j], file_post[k])
                print(file_path)
                total_pr = 0
                total_rank = 0.0
                try:
                    with open(file_path, "r") as f:
                        records = f.readlines()
                        num = len(records) - 4
                        for n in range(0, num):
                            record = json.loads(records[n])

                            for key in record:
                                temp = int(key)
                                if temp in repo_data:
                                    #get pr
                                    trueReviewers = repo_data[temp]
                                    recReviewers = record[key]
                                    #print("-------------------------")
                                    total_pr = total_pr + 1
                                    #print(trueReviewers)
                                    #print(recReviewers)
                                    for rank in range(0, len(recReviewers)):
                                        #print(recReviewers[rank])
                                        if recReviewers[rank][0] in trueReviewers:
                                            total_rank = total_rank + (1.0/float(rank + 1))
                                            #print(recReviewers[rank])
                                            #print(total_rank)
                                            break
                                        if rank > 4:
                                            break
                                    #print("-------------------------")
                                else:
                                    #print("is not in repo_data: %d" % temp)
                                    pass
                except Exception as e:
                    print("==================================Exception: %s" % e)

                #print(total_rank)
                #print(total_pr)
                print("MRR is: %.2f" % float(total_rank/total_pr))


