from nltk.corpus import wordnet
import argparse
import json

parser = argparse.ArgumentParser(description='get information from dbpedia and wordnet')
parser.add_argument('--word', default='bottle', help='input word ')
args = parser.parse_args()
word = str.lower(args.word)

from SPARQLWrapper import SPARQLWrapper, JSON


def get_info_from_dbpedia(word):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    # <http://purl.org/dc/terms/subject>
    sparql.setQuery("""
        select distinct *
        WHERE {
          <http://dbpedia.org/resource/""" + str.title(word) + """> 
          <http://purl.org/dc/terms/subject> 
          ?o .
        } LIMIT 100
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    cats = []
    for r in results["results"]["bindings"]:
        cats.append(r['o']['value'])
    sparql.setQuery("""
            select distinct *
            WHERE {
              <http://dbpedia.org/resource/""" + str.title(word) + """> 
              ?p 
              ?o .
            } LIMIT 100
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    absts = []
    for r in results["results"]["bindings"]:
        if r['p']['value'].endswith('comment') and r['o']['type'] == 'literal' and r['o']['xml:lang'] == 'en':
            absts.append(r['o']['value'])
    return cats, absts


def get_similarity(word1, word2):
    w1 = wordnet.synset(word1 + '.n.01')
    w2 = wordnet.synset(word2 + '.n.01')
    return w1.wup_similarity(w2)


def get_info_from_wordnet(word):
    synonyms = []
    hypernyms = []
    for syn in wordnet.synsets(word, pos=wordnet.NOUN):
        for l in syn.lemmas():
            if "_" not in l.name() and "-" not in l.name():
                synonyms.append(l.name())
        for h in syn.hypernyms():
            tmp_h = h.name().split(".")
            if tmp_h[1] == 'n':
                hypernyms.append(tmp_h[0])

    return synonyms, hypernyms


if __name__ == '__main__':
    i_dbpedia = get_info_from_dbpedia(word)
    i_wordnet = get_info_from_wordnet(word)
    js = {}
    js['abst'] = i_dbpedia[1]
    js['cat'] = i_dbpedia[0]
    js['syn'] = i_wordnet[0]
    js['hyp'] = i_wordnet[1]
    print(js)
    fw = open('test.json', 'w')
    json.dump(js, fw, indent=3)
