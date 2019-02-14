#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################################
#
# Copyright (c) 2019 Baidu.com, Inc. All Rights Reserved
#
# @file convert_conversation_corpus_to_model_text.py
#
######################################################################

import sys
import json
import collections


def preprocessing_for_one_conversation(text,
                                       candidate_label=[1],
                                       topic_generalization=False,
                                       for_predict=False):

    conversation = json.loads(text.strip(), encoding="utf-8", \
                              object_pairs_hook=collections.OrderedDict)

    chat_path = conversation["chat_path"]
    knowledge = conversation["knowledge"]
    history = conversation["history"]
    if not for_predict:
        candidate = conversation["candidate"]

    topic_a = chat_path[0][1]
    topic_b = chat_path[0][2]
    for i, [s, p, o] in enumerate(knowledge):
        if u"领域" == p:
            if topic_a == s:
                domain_a = o
            elif topic_b == s:
                domain_b = o

    topic_dict = {}
    if u"电影" == domain_a:
        topic_dict["video_topic_a"] = topic_a
    else:
        topic_dict["person_topic_a"] = topic_a

    if u"电影" == domain_b:
        topic_dict["video_topic_b"] = topic_b
    else:
        topic_dict["person_topic_b"] = topic_b

    chat_path_str = ' '.join([' '.join(spo) for spo in chat_path])
    knowledge_str1 = ' '.join([' '.join(spo) for spo in knowledge])
    knowledge_str2 = '\1'.join([' '.join(spo) for spo in knowledge])
    history_str = ' '.join(history)

    candidate_index = []
    model_text = []
    src = chat_path_str + " " + knowledge_str1 + " : " + history_str
    if not for_predict:
        for i, [tgt, label] in enumerate(candidate):
            if label not in candidate_label:
                continue

            text = '\t'.join([src, tgt, knowledge_str2])
            model_text.append(text)
            candidate_index.append(i)
    else:
        text = '\t'.join([src, knowledge_str2])
        model_text.append(text)

    if topic_generalization:
        topic_list = sorted(topic_dict.items(), key=lambda item: len(item[1]), reverse=True)
        for i, text in enumerate(model_text):
            for key, value in topic_list:
                text = text.replace(value, key)
            model_text[i] = text

    return model_text, topic_dict, candidate_index


def convert_conversation_corpus_to_model_text(corpus_file, text_file, topic_file, index_file, \
                                              topic_generalization=False, candidate_label=[1]):
    fout_text = open(text_file, 'w')
    fout_topic = open(topic_file, 'w')
    fout_index = open(index_file, 'w')
    with open(corpus_file, 'r') as f:
        for i, line in enumerate(f):
            model_text, topic_dict, candidate_index = \
                preprocessing_for_one_conversation(line.strip(), \
                                                   candidate_label=candidate_label, \
                                                   topic_generalization=topic_generalization)
            assert len(model_text) == len(candidate_index)
            topic_dict = json.dumps(topic_dict, ensure_ascii=False)
            for j, text in enumerate(model_text):
                fout_text.write(text + "\n")
                fout_index.write(str(i) + "\t" + str(candidate_index[j]) + "\n")
                fout_topic.write(topic_dict + "\n")

    fout_text.close()
    fout_topic.close()
    fout_index.close()


def main():
    topic_generalization = int(sys.argv[5]) > 0
    candidate_label = sys.argv[6:]
    for i, label in enumerate(candidate_label):
        candidate_label[i] = int(label)
    convert_conversation_corpus_to_model_text(sys.argv[1],
                                              sys.argv[2],
                                              sys.argv[3],
                                              sys.argv[4],
                                              topic_generalization,
                                              candidate_label)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nExited from the program ealier!")
