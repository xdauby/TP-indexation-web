import json
from typing import List, Tuple
import nltk
from nltk import word_tokenize
import re
import argparse

class Tokenizer:
    """ Class Tokenizer, handle all the logic of tokenization """
    def __init__(self, language : str = 'french') -> None:
        self.language = language
        self.stemmer = nltk.stem.SnowballStemmer(language)

    def tokenize(self, content : str) -> List[str]:
        """ Given a string, return the string tokenized. """
        content = content.lower()
        return word_tokenize(content, language=self.language)

    def stemmerize(self, content : str) -> List[str]:
        """ Given a string, return the string stemmerized. """
        content = content.lower()
        tokens = self.tokenize(content)
        stems = []
        for token in tokens:
            stems += [self.stemmer.stem(token)]
        return stems


class Index:
    """ Class Index, handle all the logic for indexation. """
    def __init__(self, crawled : List[dict], 
                       tokenizer : Tokenizer,
                       fields : List[str]):
        """ 
        crawled is a list of dictionnary
        tokenizer is a Tokenizer instance
        field is the fields of interests in crawled dictionnaries
        """
        self.crawled = crawled
        self.tokenizer = tokenizer
        self.fields = fields
        self.non_positional_index = [dict() for i in range(len(fields))]
        self.positional_index = [dict() for i in range(len(fields))]


    #################################### Metadata related methods #####################################

    def get_number_doc(self) -> int:
        """ Get the number of documents. """
        return len(self.crawled)

    def tokenize(self, content : str) -> List[str]:
        """ Tokenize a given string. """
        return self.tokenizer.tokenize(content)

    def stemmerize(self, content : str) -> List[str]:
        """ Stemmerize a given string. """
        return self.tokenizer.stemmerize(content)

    def get_number_token_by_field_by_doc(self, document : dict, field : str) -> int:
        """ Given a document and a field, count the number of tokens in the field of the
            given document. """
        total_by_field_by_doc = 0
        for in_field in self.fields:
            if in_field == field:
                total_by_field_by_doc = len(self.tokenizer.tokenize(document[field]))
        return total_by_field_by_doc
    
    def get_number_token_by_doc(self, document : dict) -> int:
        """ Given a document, count the number of tokens in it. """
        total_by_doc = 0
        for field in self.fields:
            total_by_doc += self.get_number_token_by_field_by_doc(document=document, field=field)
        return total_by_doc
        
    def get_global_number_token(self) -> int:
        """ Count the total number of tokens in all documents. """
        total = 0
        for document in self.crawled:
            total += self.get_number_token_by_doc(document=document)
        return total

    def get_global_token_by_field(self) -> List[int]:
        """ Count the total number of tokens in all documents for each field. 
            The result is sorted according to the order of the fields list.
            For example, if the fields list is ['a', 'b'], then the returned
            list (total) will store in first position the total number for field 'a'
            and in second position he total number for field 'b'. """

        total = [0]*len(self.fields)

        for document in self.crawled:
            for i, field in enumerate(self.fields):
                total[i] += self.get_number_token_by_field_by_doc(document=document, field=field)

        return total

    def get_metadata(self):
        """ Return a dictionary containing metadata of the crawled urls. """
       
        metadata = {
            "number_doc": self.get_number_doc(),
            "global_number_token": self.get_global_number_token()
        }

        global_token_by_field = self.get_global_token_by_field()

        for i, field in enumerate(self.fields):
            metadata["global_token_by_" + field] = global_token_by_field[i]
            metadata["average_token_by_" + field] = global_token_by_field[i]/self.get_number_doc()

        return metadata


    #######################################################################################################

    #################################### non positional indexation related methods #################################
    
    def get_distinct_stem_by_doc_by_field(self, document : dict, field : str) -> List[str]:
        """ Given a document, returns all distinct stems. """
        stems = self.stemmerize(document[field])
        return list(set(stems))

    def get_distinct_token_by_doc_by_field(self, document : dict, field : str) -> List[str]:
        """ Given a document, returns all distinct tokens. """
        tokens = self.tokenize(document[field])
        return list(set(tokens))

    def non_positional_indexation(self, stemmerize : bool):
        """ 
        Performs non positional indexation by field.
        If stemmerize is True, uses stemmerization instead of tokenization to create the index.
        Returns a list of dictionary. For example, if the fields list is ['a', 'b'], then the returned
        list of dictionary (non_positional_index) will store in first position the index of field 'a'
        and in second position the index of field 'b'. 
        """

        for doc_index, doc in enumerate(self.crawled):
            for index_field, field in enumerate(self.fields):

                if stemmerize:
                    # We use a distinct stem version to avoid adding the documents multiple times to a given
                    # stem key
                    distinct_entities = self.get_distinct_stem_by_doc_by_field(document=doc,field=field)
                else:
                    # We use a distinct token version to avoid adding the documents multiple times to a given
                    # token key
                    distinct_entities = self.get_distinct_token_by_doc_by_field(document=doc,field=field)
                
                # entitie represents a token or a stem
                for entitie in distinct_entities:
                    # if the entitie exists in the index
                    if entitie in self.non_positional_index[index_field]:
                        self.non_positional_index[index_field][entitie].append(doc_index)
                    # else, we have to create it
                    else:
                        self.non_positional_index[index_field][entitie] = [doc_index]   

        return self.non_positional_index

    #######################################################################################################

    ################################ positional indexation related methods ################################

    def get_stem_by_doc_by_field(self, document : dict, field : str) -> List[str]:
        """ Given a document, returns all stems. """
        stems = self.stemmerize(document[field])
        return stems

    def get_token_by_doc_by_field(self, document : dict, field : str) -> List[str]:
        """ Given a document, returns all tokens. """
        tokens = self.tokenize(document[field])
        return tokens


    def positional_indexation(self, stemmerize : bool):
        """ 
        Performs positional indexation by field.
        If stemmerize is True, uses stemmerization instead of tokenization to create the index.
        Returns a list of dictionary. For example, if the fields list is ['a', 'b'], then the returned
        list of dictionary (positional_index) will store in first position the index of field 'a'
        and in second position the index of field 'b'. 
        """

        for doc_index, document in enumerate(self.crawled):
            for index_field, field in enumerate(self.fields):

                if stemmerize:
                    entities_by_field = self.get_stem_by_doc_by_field(document=document,field=field)
                else:
                    entities_by_field = self.get_token_by_doc_by_field(document=document,field=field)
                
                # entitie represents a token or a stem
                # pos is the position of the token or the stem
                for pos, entitie in enumerate(entities_by_field):
                    # if the entitie exists in the index
                    if (entitie in self.positional_index[index_field]):
                        # if the dictionary self.positional_index[index_field] has already seen the doc doc_index, 
                        # that means self.positional_index[index_field][entitie][doc_index] is
                        # a non empty list, then we can add a new position
                        if doc_index in self.positional_index[index_field][entitie]:
                            self.positional_index[index_field][entitie][doc_index].append(pos)
                        # otherwise, that means self.positional_index[index_field][entitie] stores
                        # an dictionnary that does not contains the key doc_index. So wee add
                        # a new key value to the dictionnary self.positional_index[index_field][entitie],
                        # which is key : doc_index and value : [pos]
                        else:    
                            self.positional_index[index_field][entitie][doc_index] = [pos]
                    # if the entitie does not exist, need to create a new dictionary associated for the entitie,
                    # and add the key value doc_index : [pos]
                    else:
                        self.positional_index[index_field][entitie] = {doc_index : [pos]}

        return self.positional_index
    
    #######################################################################################################


def save_json(filename : str, data : dict) -> None:
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)
    return

def load_json(filename : str) -> object:
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data


def main() -> None:
    #nltk.download()
    
    #  Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--metadata', '-mt', default="True")
    parser.add_argument('--positional_index', '-pi', default="False")
    parser.add_argument('--stemmerize', '-s', default="False")
    args = parser.parse_args()

    # Retrieve args
    metadata = eval(args.metadata)
    positional_index = eval(args.positional_index)
    stemmerize = eval(args.stemmerize)
    
    print(" --------------------- ")
    print(" Parameters: ")
    print(f"metadata : {metadata}")
    print(f"positional_index : {positional_index}") 
    print(f"stemmerize : {stemmerize}")

    crawled = load_json(filename='crawled_urls.json')
    tokenizer = Tokenizer(language='french')
    fields = ["title", "content", "h1"] 
    index = Index(crawled=crawled, tokenizer=tokenizer, fields=fields)
    
    if metadata:
        print('Computing statistics ...')
        metadata = index.get_metadata()
        print('Statistics computed.')
        save_json(filename="metadata.json", data=metadata)
        print('Computed statistics saved in metadata.json.')


    if positional_index:
        print('Creating positional index ...')
        positional_indexation = index.positional_indexation(stemmerize=stemmerize)
        print('Positional index created.')
        
        for i, field in enumerate(fields):
            if stemmerize:
                save_json(filename=f'snowballStemmer.{field}.pos_index.json', data=positional_indexation[i])
                print(f'snowballStemmer.{field}.pos_index.json saved.')
            else:
                save_json(filename=f'{field}.pos_index.json', data=positional_indexation[i])
                print(f'{field}.pos_index.json saved.')

    else:
        print('Creating non positional index ...')
        non_positional_indexation =index.non_positional_indexation(stemmerize=stemmerize)
        print('Non positional index created.')
        
        for i, field in enumerate(fields):
            if stemmerize:
                save_json(filename=f'snowballStemmer.{field}.non_pos_index.json', data=non_positional_indexation[i])
                print(f'snowballStemmer.{field}.non_pos_index.json saved.')
            else:
                save_json(filename=f'{field}.non_pos_index.json', data=non_positional_indexation[i])
                print(f'{field}.non_pos_index.json saved.')        


if __name__ == "__main__":
    main()

    

    

    
