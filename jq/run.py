# -*- coding: utf-8 -*-
import os
import sys

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding='utf-8')
        self.start_log = True
        self.record_code()

    def record_code(self):
        input_file = 'Strategy.py'

        with open(input_file, 'r', encoding='utf-8') as f_in:
            code = f_in.read()
            self.log.write(code)
        self.log.write('\n'+ '#'*40 + '\n')

    def write(self, message):
        self.terminal.write(message)
        if self.start_log:
            self.log.write(message)

    def flush(self):
        pass

current_folder_path = os.path.dirname(__file__) + '/'
sys.stdout = Logger(current_folder_path + "log.log")

import jqdata as jq


def run():
    file_path = "./userStrategy.py"
    jq.run_file(file_path)

if __name__ == '__main__':
    run()
