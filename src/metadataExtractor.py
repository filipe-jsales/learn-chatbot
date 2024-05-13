import spacy
import re

class EntityExtractor:
    def __init__(self, model="en_core_web_sm"):
        self.nlp = spacy.load(model)

    def extract_entities(self, text):
        doc = self.nlp(text)
        # Filter to only include ORG and PERSON entities
        entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in {"ORG", "PERSON"}]
        return entities

    def get_inverted_dict(self, text):
        arr = self.extract_entities(text)
        original_dict = dict(arr)
        inverted_dict = {}
        for key, value in original_dict.items():
            if value not in inverted_dict:
                inverted_dict[value] = []
            inverted_dict[value].append(key)
        return inverted_dict
    
    def extract_source_link(self, text):
        pattern = r"Source: (https?://[^\s]+)"
        match = re.search(pattern, text)
        if match:
            return match.group(1)  # Returns the matched URL
        else:
            return ""

