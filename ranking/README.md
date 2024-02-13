
# Ranker
Author : Antoine De Paepe

## Brief description of ```Tokenizer```'s methods :

* ```tokenize``` : Given a string, return the string tokenized.

## Brief description of ```Ranker```'s methods :

* ```get_doc_that_contains_at_least_one_req_tokens```: Given a request, get all docs that contains at least one token from the tokenized request. Perform the so called OR request. 


* ```get_doc_that_contains_exactly_all_req_tokens```: Given a request, get all docs that contains at all the tokens from the tokenized request. Perform the so called AND request.


* ```naive_score```: Compute a naive score of a document for a given token list (request). Basically, the score is an average between a score given by the frequency of a token in the document and the position of the tokens. Return the score.


* ```compute_scores```: Compute score for all document in the index for a given request. Take into account the request_choice (i.e. AND or OR request). Returned docs are sorted by score.


* ```rank```: Rank pages given a request. Treshold is the maximum number of pages to return. 


## What has been implemented

```Basics``` have been implemented, as well as ```Bonus 1```.

## How to use :


Default args :

`--request` : the request in quotes (ex : "What error?")

`--request_choice` : choose between "OR" or "AND" request

`--max_urls` : maximum urls to display





run python code

```python3 main.py```

Change parameters :

```python3 main.py -r "Erreur jeu filles"  -f "AND" -m 50```


