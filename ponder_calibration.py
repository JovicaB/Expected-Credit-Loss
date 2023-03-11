import ast
import itertools
import os
import random
import threading
import xml.etree.ElementTree as eT


class XMLData:
    def __init__(self):
        self.xml_path = "data/ponder_values.xml"
        self.lock = threading.Lock()

    def create_xml(self):
        """
        creates XML file in data sub folder with 2 nodes 'risk' and 'ponder' with default values for both
        :return: None
        """
        if os.path.exists(self.xml_path):
            print("File already exists.")
            return

        root = eT.Element("root")
        risk = eT.SubElement(root, "risk")
        risk.text = "{0: 0, 1: 0, 2: 0, 3: 0, 4: 0}"
        ponder = eT.SubElement(root, "ponder")
        ponder.text = "{0: 20, 1: 20, 2: 20, 3: 20, 4: 20}"

        tree = eT.ElementTree(root)
        tree.write(self.xml_path, xml_declaration=False)

    def get_xml_value(self, node):
        """
        loads ponder or risk value from xml file
        :param node: 'ponder' or 'risk'
        :return: dictionary with 5 keys and values
        """
        tree = eT.parse(self.xml_path)
        root = tree.getroot()
        node_value = root.find(node)
        return ast.literal_eval(node_value.text)

    def write_xml_value(self, node, value):
        """
        saves ponder or risk value into xml file
        :param node: 'ponder' or 'risk'
        :param value:
        :return: None
        """
        with self.lock:
            self.create_xml()
            tree = eT.parse(self.xml_path)
            root = tree.getroot()
            risk = root.find(node)
            risk.text = value
            tree.write(self.xml_path)


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
