from threading import Lock, Condition
from time import sleep


class MailBox:
    def __init__(self):
        self.lock = Lock()
        self.topics = {}

    def check_requests(self, agent):
        """ Returns the first message for the agent given in param"""
        for topic in self.topics.values():
            for conv in topic['messages']:
                if conv['agent_asked'] == agent and 'response' not in conv.keys():
                    return conv
        return None

    def request(self, agent_asking, agent_asked, path_to_free):
        """ Makes a requests to free the path passed in param to the agent"""
        conv = {
                'agent_asking': agent_asking,
                'agent_asked': agent_asked,
                'path_to_free': path_to_free,
                'confirm': False
            }
        if agent_asking.id in self.topics.keys():
            if self.topics[agent_asking.id]['lock'].acquire(timeout=1):
                self.topics[agent_asking.id]['messages'].append(conv)
        else:
            self.topics[agent_asking.id] = dict()
            self.topics[agent_asking.id]['messages'] = [conv]
            self.topics[agent_asking.id]['lock'] = Condition()

    def check_responses(self, agent_asking):
        """ Returns a list of all the responses ij the topic"""
        res = []
        with self.topics[agent_asking.id]['lock']:
            for conv in self.topics[agent_asking.id]['messages']:
                if 'response' in conv.keys():
                    res.append(conv)
        return res

    def wait_for_confirm(self, conv, timeout=0.5):
        if self.topics[conv['agent_asking'].id]['lock'].acquire(timeout=timeout):
            self.topics[conv['agent_asking'].id]['lock'].wait(timeout=timeout)
            self.topics[conv['agent_asking'].id]['lock'].release()
        return conv['confirm']

    def confirm_choice(self, agent_asking, conv):
        conv['confirm'] = True
        self.topics[agent_asking.id]['lock'].acquire()
        self.topics[agent_asking.id]['lock'].notify_all()
        self.topics[agent_asking.id]['lock'].wait()
        self.topics[agent_asking.id]['lock'].release()

    def done(self, conv, wait=False, remove_topic=False):
        self.topics[conv['agent_asking'].id]['lock'].acquire()
        self.topics[conv['agent_asking'].id]['lock'].notify_all()
        if wait:
            self.topics[conv['agent_asking'].id]['lock'].wait()
        self.topics[conv['agent_asking'].id]['lock'].release()
        if remove_topic:
            sleep(0.05)
            del self.topics[conv['agent_asking'].id]
