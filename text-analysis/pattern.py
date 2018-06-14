import string
import ast
import re
from itertools import chain

class Pattern(object):
    PREP = "Prep~"
    PUNC = 'Punc~'
    WORD = 'Word~'
    DIGI = 'Digi~'
    UNIT = 'Unit~'
    prepos = ['aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid', 'among', 'anti', 'around',
              'as',
              'at', 'before', 'behind', 'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'but', 'by',
              'concerning', 'considering', 'despite', 'down', 'during', 'except', 'excepting', 'excluding',
              'following',
              'for', 'from', 'in', 'inside', 'into', 'like', 'minus', 'near', 'of', 'off', 'on', 'onto',
              'opposite',
              'outside',
              'over', 'past', 'per', 'plus', 'regarding', 'round', 'save', 'since', 'than', 'through', 'to',
              'toward',
              'towards',
              'under', 'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'via', 'with', 'within', 'without',
              'and', 'or']
    punc = set(string.punctuation)
    # could be made more robust by taking the list of units from grobid. This is certainly not comprehensive
    units = ['ft', 'gal', 'ppa', 'psi', 'lbs', 'lb', 'bpm', 'bbls', 'bbl', '\'', "\"", "'", "°", "$", 'hrs']

    def __init__(self, tokens, page_num, doc_name):
        self.instance = tokens
        self.page_num = page_num
        self.hpattern = self._create_hpattern(self.instance)
        self.base_pattern = self.get_base_pattern(self.hpattern)
        self.instances = [tokens]
        self.page_nums = [page_num]
        self.doc_name = doc_name

    def has_numeric(self, token):
        if re.search(r"\d", token):
            return True
        else:
            return False

    def ispunc(self, s):
        if re.match('[^a-zA-Z\d]', s):
            return True
        return False

    def _create_hpattern(self, instance):
        '''
        creates a heirarchy of 'denominations/classes' for each base pattern
        :param instance: list, tokenized string
        :return: base_pattern, h_pattern
        '''

        signature = []
        #print(instance)
        for token in instance:
            #print(token)
            if token in Pattern.prepos:
                signature.append((token, token, Pattern.PREP))
            # elif token.isnumeric():
            elif self.has_numeric(token):
                signature.append((token, Pattern.DIGI, Pattern.DIGI))
            elif token.isalpha():
                sign = [token, token, Pattern.WORD]
                if token.lower() in Pattern.units:
                    sign.append(Pattern.UNIT)
                signature.append(tuple(sign))

            #maybe use spacy or nltk instead of ispunc
            elif self.ispunc(token):
                signature.append((token, token, Pattern.PUNC))
            else:
                if token:
                    signature.append(tuple(token))

        return tuple(signature)

    def get_base_pattern(self, hpattern):
            '''
            takes the second level of an hpattern (non variable tokens)
            :param hpattern:
            :return:
            '''
            base_pattern = []
            for patt in hpattern:
                base_pattern.append(patt[1])

            return tuple(base_pattern)

    def add_instance(self, new_instance):
        self.instances.append(new_instance)

    def add_page_num(self, new_page_num):
        self.page_nums.append(new_page_num)

    def get_string(self):
        """
        Represents the objects variables in a nice little sentence
        :return: as_string, string
        """
        ins = " ".join(self.instance)
        bp = " ".join(self.base_pattern)
        flat_h = []
        for p in self.hpattern: flat_h += p
        c = " ".join(flat_h)
        as_string = "instance: " + ins + "\n base_pattern: " + bp + "\n hpattern: " + c + "\n page num: " + str(self.page_num)
        return as_string

    def get_dict(self):
        as_dict = {'instances': self.instances, 'page_numbers': self.page_nums, 'hpattern': self.hpattern,
                   'base_pattern': self.base_pattern, 'doc_name': self.doc_name}
        return as_dict