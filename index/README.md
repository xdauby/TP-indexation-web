
# Crawler
Author : Antoine De Paepe

## Brief description of ```Tokenizer```'s methods :

* ```tokenize``` : Given a string, return the string tokenized.

* ```get_robots_path``` : Given a string, return the string stemmerized.


## Brief description of ```Index```'s methods :

### Metadata related methods

* ```get_number_doc```: Get the number of documents.


* ```tokenize```: Tokenize a given string.


* ```stemmerize```: Stemmerize a given string.


* ```get_number_token_by_field_by_doc```: Given a document and a field, count the number of tokens in the field of the given document.


* ```get_number_token_by_doc```: Given a document, count the number of tokens in it.


* ```get_global_number_token```: Count the total number of tokens in all documents.

* ```get_global_token_by_field```: Count the total number of tokens in all documents for each field. The result is sorted according to the order of the fields list. For example, if the fields list is ['a', 'b'], then the returned list (total) will store in first position the total number for field 'a' and in second position he total number for field 'b'.


* ```get_metadata```: Return a dictionary containing metadata of the crawled urls.


### Non positional indexation related methods

* ```get_distinct_stem_by_doc_by_field```: Given a document, returns all distinct stems.

* ```get_distinct_token_by_doc_by_field```: Given a document, returns all distinct tokens.

* ```non_positional_indexation```: Performs non positional indexation by field. If stemmerize is True, uses stemmerization instead of tokenization to create the index. Returns a list of dictionary. For example, if the fields list is ['a', 'b'], then the returned list of dictionary (non_positional_index) will store in first position the index of field 'a' and in second position the index of field 'b'.

### Positional indexation related methods

* ```get_stem_by_doc_by_field```: Given a document, returns all stems.

* ```get_token_by_doc_by_field```: Given a document, returns all tokens.    

* ```non_positional_indexation```: Performs positional indexation by field. If stemmerize is True, uses stemmerization instead of tokenization to create the index. Returns a list of dictionary. For example, if the fields list is ['a', 'b'], then the returned list of dictionary (positional_index) will store in first position the index of field 'a' and in second position the index of field 'b'. 

## What has been implemented

```Basics``` have been implemented, as well as ```Bonus 1``` and ```Bonus 2```.

## How to use :


To run the program :

```pip install -r requirements.txt```

Default args :

`metadata` : True (if True, compute and save metadata)

`positional_index` : False (if True, performs a positional indexation)

`stemmerize` : False (if True, index is built from stems)


run python code

```python3 main.py```

Change parameters :

```python3 main.py --metadata True  --positional_index True --stemmerize True```


    python3 main.py --metadata False  --positional_index False --stemmerize True

(I deleted snowballStemmer.content.pos_index.json and content.pos_index.json due to their size)