import json
import logging
from datetime import datetime
from threading import Lock

from peewee import Database
from scipy import spatial
from sklearn.metrics.pairwise import cosine_similarity
import tensorflow_hub as hub
import numpy as np
import tensorflow_text
import pandas as pd
import spacy
from spacy import Vocab
import tensorflow as tf

from spacy.symbols import NOUN, PROPN, PRON, ADP, ADJ, PUNCT, PART, VERB, CONJ, CCONJ, SCONJ, SYM, X
import string
import pymorphy2
import nltk
from nltk.stem.snowball import SnowballStemmer
import re

from api.common import env_var
from api.seeds_ranking.asuz.integration import get_procurements
from db.config import db_handle
from db.entity.historical_lot import HistoricalLot

exclude_pos = [ADP, CONJ, CCONJ, PUNCT, SCONJ, SYM]
logger = logging.getLogger(__name__)
historical_lot_cache = {}
historical_lot_cache_lock = Lock()
embedding_loading_lock = Lock()


def noun_chunks(obj):
    """
    Detect base noun phrases from a dependency parse. Works on both Doc and Span.
    """
    labels = [
        "nsubj",
        "dobj",
        "nsubjpass",
        "pcomp",
        "pobj",
        "dative",
        "appos",
        "attr",
        "ROOT",
        'nmod',
        'flat:foreign',
        'obj',
    ]
    doc = obj.doc  # Ensure works on both Doc and Span.
    np_deps = [doc.vocab.strings.add(label) for label in labels]
    conj = doc.vocab.strings.add("conj")
    np_label = doc.vocab.strings.add("NP")
    seen = set()
    for i, word in enumerate(obj):
        if word.pos not in (NOUN, PROPN, X):
            continue
        # Prevent nested chunks from being produced
        if word.i in seen:
            continue
        if word.dep in np_deps: #and word.pos not in exclude:
            if any(w.i in seen for w in word.subtree):
                continue
            seen.update(j for j in range(word.left_edge.i, word.i + 1))
            yield word.left_edge.i, word.i + 1, np_label
        elif word.dep == conj:
            head = word.head
            while head.dep == conj and head.head.i < head.i:
                head = head.head
            # If the head is an NP, and we're coordinated to it, we're an NP
            if head.dep in np_deps:
                if any(w.i in seen for w in word.subtree):
                    continue
                seen.update(j for j in range(word.left_edge.i, word.i + 1))
                yield word.left_edge.i, word.i + 1, np_label


def load_data():
    logger.info('Initialization')
    embedding_path = env_var('EMBEDDING_PATH', 'api/seeds_ranking/embeddings/embeddings.json')
    data = json.load(open(embedding_path, "r", encoding='utf-8'))
    embeddings = pd.DataFrame.from_dict(data)
    logger.info('Precalculated embeddings loaded successfully')
    return embeddings


def load_lib():
    logger.info('Libs loading')
    model_name = 'ru_core_news_lg'
    nlp = None
    try:
        nlp = spacy.load(model_name)
        nlp.vocab.get_noun_chunks = noun_chunks
    except IOError:
        spacy.cli.download(model_name)
        nlp = spacy.load(model_name)
        nlp.vocab.get_noun_chunks = noun_chunks
    morph = pymorphy2.MorphAnalyzer()
    stemmer = SnowballStemmer(language='russian')
    tokenizer = nltk.tokenize.WhitespaceTokenizer()
    logger.info('Libs loaded successfully')
    return nlp, morph, stemmer, tokenizer


nlp, morph, stemmer, tokenizer = load_lib()
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3")
embeddings = None


def get_embeddings():
    try:
        embedding_loading_lock.acquire()
        global embeddings
        if embeddings is None:
            embeddings = load_data()
        return embeddings
    finally:
        embedding_loading_lock.release()


embedding_lazy_loading = env_var('EMBEDDING_LAZY_LOADING', 0)
if embedding_lazy_loading == 0:
    get_embeddings()


def normalize(text: str) -> str:
    return text.translate(str.maketrans('', '', string.punctuation))


def get_clean_noun_chunks(input_texts):
    result = []
    docs = nlp.pipe(input_texts, n_process=1)

    for doc in docs:

        #     for token in doc:
        #         token_text = token.text
        #         token_pos = token.pos_
        #         token_dep = token.dep_
        #         token_head = token.head.text
        #         print(f"{token_text:<30}{token_pos:<10}{token_dep:<10}{token_head:<12}")

        # from spacy import displacy
        # displacy.render(doc, style='dep', jupyter=True)

        # from spacy import displacy
        # displacy.render(doc, style='dep', jupyter=True)

        sub_result = []
        names = []
        for ent in doc.ents:
            logger.debug(ent.text, ent.start_char, ent.end_char, ent.label_)
            ner_text = ent.text.lower()
            if 'газпром' not in ner_text:
                names.append(ner_text)
        for chunk in doc.noun_chunks:
            logger.debug(chunk.text, chunk.start_char, chunk.end_char, chunk.label_)
            exclude_chunk = False
            for ent in doc.ents:
                if ent.start_char <= chunk.start_char <= ent.end_char or ent.start_char <= chunk.end_char <= ent.end_char \
                        or (chunk.start_char <= ent.start_char <= chunk.end_char and chunk.start_char <= ent.end_char <= chunk.end_char):
                    exclude_chunk = True
                    break
            if exclude_chunk:
                continue
            clean_words = []
            for t in chunk:
                text = t.text.strip()
                if t.pos not in exclude_pos and len(text) > 1:
                    if t.pos == X or t.pos == PROPN:
                        names.append(t.text.lower())
                    elif t.pos == VERB and morph.parse(t.lower_)[0].inflect({'sing', 'nomn'}) is not None:
                        clean_words.append(morph.parse(t.lower_)[0].inflect({'sing', 'nomn'}).word)
                    else:
                        clean_words.append(t.lemma_)
            if len(clean_words) > 0:
                sub_result.append(" ".join(clean_words))
        result.append((sub_result, names))
    return result


def find_nearest_chunks(chunks, n=1):
    embedding_vocab = get_embeddings()
    input_embedding = embed(chunks)
    sim_mat = cosine_similarity(np.array(input_embedding), np.array(embedding_vocab['embedding'].tolist()))
    result = []
    for idx, sim_arr in enumerate(sim_mat):
        ind = np.argpartition(sim_arr, -n)[-n:]
        sorted_ind = ind[np.argsort(-sim_arr[ind])]
        result.append(embedding_vocab['noun_chunk'][sorted_ind].tolist())
    return list(map(list, zip(*result)))


# def find_nearest_kernel(text):
#     input_embedding = embed([text])
#     sim_mat = cosine_similarity(np.array(input_embedding), np.array(kernels['centroid'].tolist()))
#     max_similarity = -1
#     best_kernel = None
#     for idx, similarity in enumerate(sim_mat[0]):
#         if similarity > max_similarity:
#             # print(idx)
#             # print(similarity)
#             best_kernel = kernels['chunks'][idx]
#             max_similarity = similarity
#     return max_similarity, best_kernel


def exclude_stop_words(chunks: []):
    result = []
    for chunk in chunks:
        exclude = False
        for stop_word in stop_words:
            if stop_word in chunk:
                exclude = True
        if not exclude:
            result.append(chunk)
    if len(result) == 0:
        result = chunks
    return result


def exclude_stop_words_from_query(query: str):
    result = ''
    doc = nlp(query)
    exclude = set()
    for stop_word in stop_words:
        stop_sub_words = stop_word.split(' ')
        matched = []
        for token in doc:
            if token.lemma_.lower() == stop_sub_words[0]:
                matched.append(token.i)
                if token.i + 1 < len(doc):
                    nbor = token.nbor()
                    for k, stop_sub_word in enumerate(stop_sub_words[1:]):
                        if nbor.lemma_.lower() == stop_sub_word:
                            matched.append(token.i + 1 + k)
                        if nbor.i + 1 == len(doc):
                            break
                        nbor = nbor.nbor()
                if len(matched) == len(stop_sub_words):
                    exclude.update(matched)
                    matched.clear()
            else:
                matched.clear()
    for token in doc:
        if token.i not in exclude:
            result += token.text_with_ws
    if len(result) == 0:
        result = query
    return result


def contain_names(names: [str], test_str: str) -> float:
    result = 0.0
    lower_test_str = test_str.lower()
    for name in names:
        name_parts = name.lower().split(' ')
        name_words_qty = len(name_parts)
        matched = 0
        for name_part in name_parts:
            if name_part in lower_test_str:
                matched += 1
        if name_words_qty != 0:
            result = result + matched / name_words_qty
    return result / len(names)


def extract_names(query: str) -> [str]:
    result = set()
    doc = nlp(query)
    for entity in doc.ents:
        ner_text = entity.text.lower()
        if 'газпром' not in ner_text:
            result.add(ner_text)
    for t in doc:
        text = t.text.strip()
        if t.pos not in exclude_pos and len(text) > 1:
            if t.pos == X or t.pos == PROPN:
                if 'газпром' not in t.text.lower():
                    result.add(t.text.lower())
    return list(result)


def generate_queries(query, length=0, n=10):
    chunks = get_clean_noun_chunks([query])[0]
    logger.debug(chunks)
    names = exclude_stop_words(chunks[1])
    unique_names = set(names)
    result = []
    names = ' '.join(unique_names)
    if len(chunks[0]) > 0:
        chunks4replace = exclude_stop_words(chunks[0])
        logger.debug(chunks4replace)
        nearest_chunks = find_nearest_chunks(chunks4replace, n)
        result.append(' '.join(chunks4replace))

        if length != 0:
            for nc in nearest_chunks:
                for x in range(0, len(nc), length):
                    if x+length >= len(nc):
                        result.append(" ".join(nc[-length:]))
                    else:
                        result.append(" ".join(nc[x:x+length]))
        else:
            for nc in nearest_chunks:
                result.append(' '.join(nc))
    return result[:n], names


def sort_seeds(original_query, seed_queries):
    queries = [original_query]
    embeddings = embed(queries.extend(seed_queries))


def stemming(text):
    tokens = [stemmer.stem(w) for w in tokenizer.tokenize(text)]
    return " ".join(tokens)


stop_words = ['открытый двухэтапный отбор', 'оказание услуг', 'оказание', 'закупка', 'покупка', 'открытый конкурентный отбор', 'организация', 'конкурентный отбор',
              'отбор исполнитель', 'выполнение работа', 'договор субподряд', 'газпром', 'поставка', 'нужда', 'открытый отбор', 'приобретение', 'выполнение',
              'кадастровый номер', 'услуга', 'гг']


def generate_seeds(query):
    query = re.sub('Деятельность в области', '', query)
    query = re.sub('\s(ао|АО|ООО|ПАО|ооо|пао)\s', ' ', query)
    query = re.sub(r'\d{3,}', '', query)
    query = re.sub(r'по +адресу.*',"", query)
    query = re.sub(r'адрес +объект.*', '', query)
    query = re.sub(r'на +объект.*', '', query)

    seed_queries, names = generate_queries(query, length=3)
    zakupki_queries = []
    if len(names) > 0:
        zakupki_queries.append(names)
    res_set = set()
    for sq in seed_queries:
        res = stemming(sq)
        if res not in res_set:
            zakupki_queries.append(res)
            res_set.add(res)
    marker_queries = []
    first = True
    res_set = set()
    if len(names) > 0:
        res_set.add(names)
        marker_queries.append(names)
    for sq in seed_queries:
        if sq not in res_set:
            if first:
                first_query = sq + ' ' + names
                first_query = first_query.strip()
                marker_queries.append(first_query)
                res_set.add(first_query)
                first = False
            else:
                marker_queries.append(sq)
                res_set.add(sq)
    return zakupki_queries, marker_queries


def filter_condition(lot: [dict], start_date: datetime, end_date: datetime, service_code: str, service_name: str) -> bool:
    lot_date = None
    if lot.get('purchase_date', '') != '':
        try:
            lot_date = datetime.fromisoformat(lot['purchase_date'])
        except Exception as ex:
            logger.error(f'Purchase date: {lot.get("purchase_date")}')
            logger.exception(ex)
    if lot_date is not None:
        if start_date is not None and lot_date < start_date:
            return False
        if end_date is not None and lot_date > end_date:
            return False
    if service_code is not None and lot['usl_code'] != service_code:
        return False
    if service_name is not None and lot['usl_name'] != service_name:
        return False
    return True


def filter_by_similarity(input_str: str, lots: [dict], subject_field: str, similarity_threshold=-1) -> [dict]:
    clear_input = re.sub('\\s+', ' ', input_str)
    clear_input = re.sub('\s(ао|АО|ООО|ПАО|ооо|пао)\s', ' ', clear_input)

    names = extract_names(clear_input)
    clear_input = exclude_stop_words_from_query(clear_input)
    input_embedding = embed(clear_input)
    result = []
    for lot in lots:
        if lot.get('embedding') is None:
            embedding = embed(lot['name_objects'])
        else:
            embedding = lot['embedding']
        similarity = 1 - spatial.distance.cosine(embedding, input_embedding) / 2
        if len(names) > 0:
            name_percent = contain_names(names, lot[subject_field])
            similarity += 0.15 * name_percent
            if similarity >= 1:
                similarity = 0.99
        if similarity > similarity_threshold:
            lot['similarity'] = similarity
            result.append(lot)
    return sorted(result, key=lambda elem: elem['similarity'], reverse=True)


def update_asuz_data_cache(lots):
    if len(historical_lot_cache) == 0:
        db_lots = HistoricalLot.select()
        for historical_lot in db_lots.dicts().iterator():
            key = historical_lot['konkurs_id'] + '_' + historical_lot['ofr_id']
            historical_lot['embedding'] = tf.convert_to_tensor(np.frombuffer(historical_lot['embedding'], dtype=np.single))
            historical_lot_cache[key] = historical_lot

    for lot in lots:
        key = lot['konkurs_id'] + '_' + lot['ofr_id']
        if historical_lot_cache.get(key) is None:
            embedding = embed(lot['lot_name'])
            lot['embedding'] = embedding.numpy().tobytes()
            if lot.get('purchase_date', '') == '':
                lot['purchase_date'] = None
            HistoricalLot.create(**lot)
            lot['embedding'] = embedding
            historical_lot_cache[key] = lot
        else:
            lot['embedding'] = historical_lot_cache[key]['embedding']
    return lots


def filter_asuz_data(request_json):
    lots = get_procurements()
    try:
        historical_lot_cache_lock.acquire()
        lots = update_asuz_data_cache(lots)
    finally:
        historical_lot_cache_lock.release()

    search_request = request_json.get('search_request')
    start_date = request_json.get('start_pur_date')
    if start_date is not None:
        start_date = datetime.fromisoformat(start_date)
    end_date = request_json.get('finish_pur_date')
    if end_date is not None:
        end_date = datetime.fromisoformat(end_date)
    service_code = request_json.get('usl_code')
    service_name = request_json.get('usl_name')
    lots = [lot for lot in lots if filter_condition(lot, start_date, end_date, service_code, service_name)]
    lots = filter_by_similarity(search_request, lots, 'lot_name')
    result = []
    for lot in lots:
        elem = {
            'subject': lot['lot_name'],
            'subject_similarity': lot['similarity'],
            'konkurs_id': lot['konkurs_id'],
            'ofr_id': lot['ofr_id'],
            'purchase_date': lot['purchase_date']
        }
        result.append(elem)
    return result
