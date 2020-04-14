import numpy as np
from common.utils import get_file_score, split_file_length
from common.log import LogAdapter
import math

LOG = LogAdapter().set_log('Algorithms')


class FPSScore(object):

    def score(self,review_new, review_past, m, sigma=1):
        """

        :param review_new:
        :param review_past:
        :param m:
        :param sigma: time prioritization
        :return:
        """
        try:

            file_count = len(review_new) * len(review_past)
            similarity_score = self.similarity_score(review_new, review_past)
            score = similarity_score / file_count
            prioritization_score = score * pow(sigma, m)
            return prioritization_score
        except Exception as e:
            LOG.error('Failed count score cause {}'.format(e),exc_info=True)

    def similarity_score(self, review_new, review_past):
        t_s_score = []
        try:
            for new_file in review_new:
                for past_file in review_past:
                    n_length = len(split_file_length(new_file))
                    p_length = len(split_file_length(past_file))

                    max_length = max(n_length, p_length)

                    common_path = get_file_score(new_file, past_file)

                    s_score = common_path / max_length

                    t_s_score.append(s_score)

            average_score = np.mean(t_s_score)

            return average_score
        except Exception as e:
            LOG.error('Failed count similarity_score cause {}'.format(e),exc_info=True)

    def score2(self, review_new, review_past, m, sigma=1):
        """

        :param review_new:
        :param review_past:
        :param m:
        :param sigma: time prioritization
        :return:
        """
        try:
            file_count = len(review_new)
            similarity_score = self.similarity_score(review_new, review_past)
            score = similarity_score / file_count
            wdc_weight = self.weight_review_count(review_past)
            # prioritization_score = score * wdc_weight
            prioritization_score = wdc_weight
            return prioritization_score
        except Exception as e:
            LOG.error('Failed count score cause {}'.format(e),exc_info=True)

    def weight_review_count(self, review_past):
        score_list = list()
        w_score = 0
        for i,j in enumerate(review_past):
            w_score = 1/(i+1)
            score_list.append(w_score)
        # print(score_list)
        w_score = np.mean(score_list)
        return w_score


class PreProcess(object):
    def __init__(self, lib_tech_new, lib_tech_past):
        self.new = lib_tech_new
        self.past = lib_tech_past

    def get_combine_dict(self):
        result_set = set(self.new) | set(self.past)
        combine_dict = dict()
        position = 0
        for word in result_set:
            combine_dict[word] = position
            position += 1
        return combine_dict

    def get_one_hot_code(self, combine_dict):
        cut_code_new = [0] * len(combine_dict)
        cut_code_past = [0] * len(combine_dict)
        for word_new in self.new:
            cut_code_new[combine_dict[word_new]] += 1
        for word_past in self.past:
            cut_code_past[combine_dict[word_past]] += 1
        return cut_code_new, cut_code_past

    def main(self):
        # list all key word and define word position
        combine_dict = self.get_combine_dict()
        # get decode result
        cut_code_new,cut_code_past = self.get_one_hot_code(combine_dict)

        return cut_code_new, cut_code_past


def cosine_similarity(new_word, past_word):

    """
    :param lib_tech_new:
    :param lib_tech_past:
    :return:
    """

    sum_numerator = 0
    sum_denominator_1 = 0
    sum_denominator_2 = 0
    process = PreProcess(new_word, past_word)
    new_code, past_code = process.main()
    # print(new_code, past_code)

    for i in zip(new_code, past_code):
        numerator = i[0] * i[1]
        denominator_1 = pow(i[0], 2)
        denominator_2 = pow(i[1], 2)

        sum_numerator += numerator
        sum_denominator_1 += denominator_1
        sum_denominator_2 += denominator_2

    denominator = math.sqrt(sum_denominator_1) * math.sqrt(sum_denominator_2)
    try:
        result = sum_numerator / denominator
    except ZeroDivisionError:
        result = 0.0
    return result


class TermFrequency(object):
    def __init__(self):
        pass

    def tf(self, word, count):
        # count[word] 可以得到每个单词的词频， sum(count.values()) 可以得到这个pull request 的单词总数
        return count[word] / sum(count.values())

    def n_counting(self,word,count_list):
        """
        统计含有这个单词的pull request 数量
        :param word:
        :param count_list:
        :return:
        """
        return sum(1 for count in count_list if word in count)

    def idf(self,word,count_list):
        # len(count_list) 计算的是pull request 总数， n_counting 计算的是含有这个单词的request数有多少
        return math.log(len(count_list) / 1 + self.n_counting(word,count_list))

    def tf_idf(self, word, count, count_list):
        """

        :param word: elements of count ,you can think is is a term
        :param count: Count object, meaning the count object, content is the frequency of word in the sentence
        :param count_list: list,it is the count list
        :return:the score of tf-idf
        """
        return round(self.tf(word, count) * self.idf(word, count_list),5)


