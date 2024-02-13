import json
from typing import List
#import nltk
#from nltk import word_tokenize
from collections import Counter
import argparse


class Tokenizer:
    """ Class Tokenizer, handle all the logic of tokenization """
    def __init__(self, language : str = 'french') -> None:
        self.language = language

    def tokenize(self, content : str) -> List[str]:
        """ Given a content, return the content tokenized. """
        # after made some test, I think it is what you have done,
        # so i put nltk tokenizer in comment
        tokens = content.split() #word_tokenize(content, language=self.language)
        tokens = [token.lower() for token in tokens]
        return tokens


class Ranker:

    def __init__(self, index : dict, doc : List[dict]) -> None:
        self.index = index
        self.doc = doc
        self.tokenizer = Tokenizer()
    
    def get_doc_that_contains_at_least_one_req_tokens(self, request : str) -> object:
        """ 
        Given a request, get all docs that contains at least one token from
        the tokenized request. Perform the so called OR request. 
        """

        docs = []
        request_tokens = self.tokenizer.tokenize(request)
        
        for token in request_tokens:
            if token in self.index.keys():
                docs += self.index[token].keys()
        
        return list(set(docs))

    def get_doc_that_contains_exactly_all_req_tokens(self, request : str) -> object:
        """ Given a request, get all docs that contains at all the tokens from
        the tokenized request. Perform the so called AND request. """
        docs = []
        request_tokens = self.tokenizer.tokenize(request)
        
        for token in request_tokens:
            if token in self.index.keys():
                docs += self.index[token].keys()
        
        occurrences = Counter(docs)
        filtered_docs = [item for item, count in occurrences.items() if count == len(request_tokens)]

        return filtered_docs

    def naive_score(self, document : int, request_tokens : List[str]) -> float:
        """ Compute a naive score of a document for a given token list (request).
        Basically, the score is an average between a score given by the frequency
        of a token in the document and the position of the tokens. Return the score.
        """
        score = 0 
        positions = []
        counts = []
        for token in request_tokens:
            if token in self.index:
                if document in self.index[token]:
                    counts.append(self.index[token][document]['count'])
                    positions += self.index[token][document]['positions']
            
        # position score
        if len(positions) > 1:
            sorted_position = sorted(positions)
            distances = [sorted_position[i+1] - sorted_position[i] for i in range(len(sorted_position)-1)]
            avg_distance = sum(distances) / len(distances) if distances else 0.0
            position_score = 1.0 / (1.0 + avg_distance) #hence when avg_distance increases,
                                                        #the position score decreases and vice versa
        else:
            position_score = 0
    
        # count score
        if len(counts) > 0:
            avg_count = sum(counts) / len(counts)
            count_score = 1.0 / (1.0 + 1/avg_count) # When the avg count is high,
                                                    # score is near 1
        else:
            count_score = 0

        # final score is a weighted sum
        score += 0.75*count_score + 0.25*position_score
        return score

    def compute_scores(self, request : str, request_choice : str) -> object:
        """ Compute score for all document in the index for a given request.
            Returned docs are sorted by score.
            Var request_choice allow to choose between AND or OR request.

        """
        if request_choice=="OR":
            doc_indexes = self.get_doc_that_contains_at_least_one_req_tokens(request=request)
        if request_choice=="AND":
            doc_indexes = self.get_doc_that_contains_exactly_all_req_tokens(request=request)

        request_tokens = self.tokenizer.tokenize(content=request)
        scores = {}
        for doc_index in doc_indexes:
            scores[doc_index] = self.naive_score(doc_index, request_tokens)
        sorted_by_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
        self.display_info(len(sorted_by_scores.keys()))
        return sorted_by_scores

    def rank(self, request : str, request_choice : str, treshold : int):
        """ Rank pages given a request. Treshold is the maximum number of pages to return. """
        doc_scores = self.compute_scores(request=request,request_choice=request_choice)
        index_best_docs = list(doc_scores.keys())[:treshold]
        ranked = []
        for index_best_doc in index_best_docs:
            for document in self.doc:
                if document['id'] == int(index_best_doc):
                    ranked.append({'url' : document['url'], 
                                   'title' : document['title']})

        return ranked

    def display_info(self, n_filtered : int):
        print(f"\nNumber doc in index : {len(self.doc)}")
        print(f"Number of document that survived to filter : {n_filtered}\n")

    def display_ranked(self, ranked: List[dict]):
        for i, r in enumerate(ranked):
            print(f"Ranked {i+1} : ")
            print(f"Title : {r['title']}")
            print(f"Url : {r['url']}\n")








if __name__ == "__main__":
    tokenizer = Tokenizer()
    request = "Erreur en informatique"
    with open('title_pos_index.json', 'r') as json_file:
        title_index = json.load(json_file)
    
    with open('documents.json', 'r') as json_file:
        documents = json.load(json_file)
    



def main() -> None:
    #nltk.download()
    
    #  Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--request', '-r', default="")
    parser.add_argument('--request_choice', '-f', default="OR")
    parser.add_argument('--max_urls', '-m', default=30)

    args = parser.parse_args()

    # Retrieve args
    request = args.request
    filter_and_or = args.request_choice
    max_urls = int(args.max_urls)
    
    print(" --------------------- ")
    print(" Parameters: ")
    print(f"request : {request}")
    print(f"filter : {filter_and_or}") 
    print(f"max urls to display : {max_urls}") 


    with open('title_pos_index.json', 'r') as json_file:
        title_index = json.load(json_file)
    
    with open('documents.json', 'r') as json_file:
        documents = json.load(json_file)
    
    ranker = Ranker(title_index, documents)
    ranked = ranker.rank(request = request, request_choice=filter_and_or , treshold=max_urls)
    ranker.display_ranked(ranked)


if __name__ == "__main__":
    main()

   