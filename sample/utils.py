import json
from collections import Counter
from collections import defaultdict
import csv
import json


def read_info(filename):
    info_dict = dict()
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for item in reader:
            if reader.line_num == 1:
                continue
            file = item[0]
            token = item[1].split()
            info_dict.update({file: token})
    return info_dict


def read_sample(file_name, save_file_name):
    with open(file_name, 'r') as f:
        content = f.read()

    sample_list = json.loads(content)
    length = len(sample_list)

    result_dict = defaultdict(list)

    for i in sample_list:
        file = i['file']
        token = i['token']

        result_dict[token].append(file)

    print(length)
    print(dict(result_dict))
    print(len(result_dict))
    with open(save_file_name, 'w') as f:
        f.write(json.dumps(dict(result_dict)))

#
# def main(csv_file, json_file1, json_file2):
#     # 1 Read_csv and convert to json
#     result = read_info(csv_file)
#     print(result)
#     with open(json_file1,'w+') as f:
#         f.write(json.dumps(result))
#     # 2 Calcute how many files used the same token
#     read_sample(json_file1, json_file2)
#
#
# main('pytorch.csv', '1.json', '2.json')
