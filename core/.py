import os
from storage.utils import get_pull_request_user

parents_path = os.path.abspath(os.path.pardir)
save_path = os.path.join(parents_path, 'result', 'implicit_relation')
if not os.path.exists(save_path):
    os.makedirs(save_path)

DECAY_FACTOR = 1.0


class ReviewerRecommendation(object):
    def __init__(self, project):
        self.project = project

    def transform_function(self):
        pass

    def get_reviewer(self):
        pass

    def get_request(self):
        pass

    def calculate_request_marix(self):
        pass

    def catch_implicit_relations(self):
        pass

    def main(self, r, k):

        project = self.project

        score = list()
        return project


def main():
    pass








