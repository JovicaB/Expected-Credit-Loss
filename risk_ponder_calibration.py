import ast
import itertools
import os
import random
import threading


class PonderCalibration:
    def __init__(self, data):
        self.data = data
        self.ponder_index = self.data[0]
        self.ponder_value = self.data[1]
        self.ponder_status = self.data[2:]

    def replace_false(self):
        # self.ponder_status = self.ponder_status[0]

        total = sum([0 if x is False else x for x in self.ponder_status])

        value = 100 - total

        for i in range(len(self.ponder_status)):
            if self.ponder_status[i] is False:
                self.ponder_status[i] = value

        return self.ponder_status

    def set_iterator(self):
        """
        define randomised iterator list without element that is changed
        example: if ponder 1 is changed method randomises remaining ponder indexes, because moving ponder slider without
        randomise tends to only change next ponder
        """
        raw_seq = [0, 1, 2, 3, 4]
        raw_seq.remove(self.ponder_index - 1)
        random.shuffle(raw_seq)

        return raw_seq

    def change_ponder_data(self):
        """
        method that calibrates ponders based on changes in chosen ponder value
        """
        self.replace_false()

        iterator = self.set_iterator()
        seq = itertools.cycle(iterator)
        seq = itertools.islice(seq, 0, None)

        # changing slider number to list index
        ponder_index = self.ponder_index - 1
        new_value = int(self.ponder_value)

        # # defining difference in value to be distributed among other ponders
        value_to_distribute = new_value - self.ponder_status[ponder_index]

        # # # changing value that we know for ponder_index
        self.ponder_status[ponder_index] = new_value

        while abs(value_to_distribute) > 0:
            # if value that should be distributed among ponders is positive
            if value_to_distribute > 0:
                for i in seq:
                    if abs(value_to_distribute) == 0:
                        break
                    else:
                        if i != ponder_index:
                            if self.ponder_status[i] > 0:
                                self.ponder_status[i] -= 1
                                value_to_distribute -= 1
            # if value that should be distributed among ponders is negative
            else:
                for i in seq:
                    if abs(value_to_distribute) == 0:
                        break
                    else:
                        if i != ponder_index:
                            if self.ponder_status[i] >= 0:
                                self.ponder_status[i] += 1
                                value_to_distribute += 1

            return self.ponder_status
