import nltk
from nltk import Tree
import spacy
from collections import defaultdict, Counter
from math import log
import json

def to_nltk_tree(node):
    if node.n_lefts + node.n_rights > 0:
        return Tree(node.orth_, [to_nltk_tree(child) for child in node.children])
    else:
        return node.orth_

def get_sentence_parse_height(sent):
    tree = to_nltk_tree(sent.root)
    try:
        return tree.height()
    except Exception as e:
        # Sometimes invalid parses don't successfully become trees
        return 0

def aggregate_statistics(articles, limit=None):
    nlp = spacy.load("en_core_web_sm")
    nltk.download('punkt', quiet=True)
    ids = []
    sentence_lengths = []
    sentence_counts = []
    parse_heights = []
    entity_counts = defaultdict(int)
    entity_count_list = []
    noun_phrase_counts = []
    paragraph_counts = []
    token_counts = defaultdict(int)
    article_lengths = []
    i = -1
    for i, article in enumerate(articles):
        print(i+1, article['id'], article['title'])
        ids.append(article['id'])
        article_length = 0
        for section_title, section_paragraphs in article['text']:
            paragraph_counts.append(len(section_paragraphs))
            for paragraph in section_paragraphs:
                sentences = list(nlp(paragraph).sents)
                sentence_counts.append(len(sentences))
                for sentence in sentences:
                    sentence_lengths.append(len(sentence))
                    article_length += len(sentence)
                    parse_heights.append(get_sentence_parse_height(sentence))
                    entity_count_list.append(len(sentence.ents))
                    noun_phrase_counts.append(len(list(sentence.noun_chunks)))
                    ents = set(sentence.ents)
                    for ent in ents:
                        entity_counts[ent] += 1
                    for token in sentence:
                        token = str(token).lower()
                        token_counts[token] += 1
        article_lengths.append(article_length)
        if limit and i + 1 >= limit:
            break
    n_articles = len(article_lengths)
    n_tokens = sum(sentence_lengths)
    n_unique_tokens(len(token_counts))
    n_sentences = sum(sentence_counts)
    n_paragraphs = sum(paragraph_counts)
    n_entities = sum(entity_count_list)
    n_noun_phrases = sum(noun_phrase_counts)
    
    avg_num_sentences = n_sentences / n_articles
    avg_parse_height = sum(parse_heights) / len(parse_heights)
    avg_sentence_length = n_tokens / n_sentences
    avg_paragraph_count = n_paragraphs / n_articles
    avg_entity_count = n_entities / len(entity_count_list)
    avg_article_length = sum(article_lengths) / len(article_lengths)
    avg_noun_phrase_count = sum(noun_phrase_counts) / len(noun_phrase_counts)
    return {
        'n_articles': i + 1,
        'n_tokens': n_tokens,
        'n_unique_tokens': n_unique_tokens,
        'n_sentences': n_sentences,
        'n_paragraphs': n_paragraphs,
        'n_entities': n_entities,
        'n_noun_phrases': n_noun_phrases,
        'avg_paragraphs_per_article': avg_paragraph_count,
        'avg_sentences_per_article': avg_num_sentences,
        'avg_tokens_per_article': avg_article_length,
        'avg_sentence_parse_height': avg_parse_height,
        'avg_entities_per_sentence': avg_entity_count,
        'avg_noun_phrases_per_sentence': avg_noun_phrase_count
    }, {
        'sentence_lengths': sentence_lengths,
        'parse_heights': parse_heights,
        'entity_count_list': entity_count_list,
        'parse_height_counts': Counter(parse_heights),
        'paragraph_counts': paragraph_counts,
        'token_counts': token_counts,
    }