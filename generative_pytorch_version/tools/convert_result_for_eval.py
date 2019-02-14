#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################################
#
# Copyright (c) 2019 Baidu.com, Inc. All Rights Reserved
#
# @file convert_result_for_eval.py
#
######################################################################

import sys
import json
import collections


def convert_result_for_eval(resource_file, pred_result_file, gold_score_file, index_file, output_file):
    resource_list = [line.strip() for line in open(resource_file, 'r')]
    pred_result_list = [line.strip() for line in open(pred_result_file, 'r')]
    gold_score_list = [line.strip() for line in open(gold_score_file, 'r')]
    index_list = [line.strip() for line in open(index_file, 'r')]

    for i, resource in enumerate(resource_list):
        resource_list[i] = json.loads(resource, encoding="utf-8", \
                              object_pairs_hook=collections.OrderedDict)

    assert len(pred_result_list) == len(gold_score_list)
    assert len(pred_result_list) == len(index_list)
    for i, pred_result in enumerate(pred_result_list):
        pred_text, pred_score = pred_result.split('\t')
        pred_score = float(pred_score)

        gold_score = round(float(gold_score_list[i]), 3)

        session_index, candidate_index = index_list[i].split('\t')
        session_index = int(session_index)
        candidate_index = int(candidate_index)

        resource_list[session_index]["response"] = pred_text
        resource_list[session_index]["candidate"][candidate_index].append(gold_score)

    fout = open(output_file, 'w')
    for i, resource in enumerate(resource_list):
        for j, candidate in enumerate(resource["candidate"]):
            if len(candidate) == 2:
                resource["candidate"][j] = resource["candidate"][j].append(0)

        out_data = json.dumps(resource, ensure_ascii=False)
        fout.write(out_data + "\n")

    fout.close()


def main():
    convert_result_for_eval(sys.argv[1],
                            sys.argv[2],
                            sys.argv[3],
                            sys.argv[4],
                            sys.argv[5])


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nExited from the program ealier!")
