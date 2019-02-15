#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################################
#
# Copyright (c) 2019 Baidu.com, Inc. All Rights Reserved
#
# @file eval.py
#
######################################################################

import sys
import json
import math
from collections import OrderedDict

if len(sys.argv) < 3:
    strUsage = "Usage: " + sys.argv[0] + " test_file model_type[rank|gen]\n"
    strUsage += "\trank: ranking model\n"
    strUsage += "\tgen: generative model\n"
    sys.stderr.write(strUsage)
    exit()

def error_check(item, model_type):
    if item.get("candidate") is None:
        sys.stderr.write("Format Error: no candidate item in data!\n")
        return False
    if len(item["candidate"]) != 10:
        sys.stderr.write("Format Error: candidate number is error!\n")
        return False
    golden_number = 0
    for cand in item["candidate"]:
        if len(cand) != 3:
            sys.stderr.write("Format Error: candidate format is error!\n")
            return False
        is_golden = cand[1]
        if is_golden != 0 and is_golden != 1:
            sys.stderr.write("Data Error: no golden information in data!\n")
            return False
        if is_golden == 1:
            golden_number += 1
    if golden_number != 1:
        sys.stderr.write("Data Error: golden response number is error!\n")
        return False
    if item.get("response") is None and model_type == "gen":
        sys.stderr.write("Format Error: no response item in data!\n")
        return False
    return True 


def eval_hits(data):
    total = len(data)
    if total == 0:
        return [0, 0]
    hits_1 = 0.0
    hits_3 = 0.0
    for item in data:
        if item[0][0] == 1:
            hits_1 += 1
            hits_3 += 1
        if item[1][0] == 1:
            hits_3 += 1
        if item[2][0] == 1:
            hits_3 += 1
    return [hits_1/total, hits_3/total] 

    
def eval_ppl(data):
    total_words = 0.0
    total_score = 0.0
    for golden_response, score in data:
        num = len(golden_response.strip().split(" ")) + 1
        total_words += num
        total_score += score
    if total_words == 0:
        return 0
    return math.exp(-total_score/total_words)


def eval_f1(data):
    golden_char_total = 0.0
    pred_char_total = 0.0
    hit_char_total = 0.0
    for golden_response, response in data:
        golden_response = golden_response.replace(" ", "")
        response = response.replace(" ", "")
        for char in response:
            if char in golden_response:
                hit_char_total += 1
        golden_char_total += len(golden_response)
        pred_char_total += len(response)
    p = hit_char_total/pred_char_total
    r = hit_char_total/golden_char_total
    f1 = 2*p*r/(p+r)
    return f1


hits_data = []
ppl_data = []
f1_data = []

test_file = sys.argv[1]
model_type = sys.argv[2]
for line in open(test_file):
    item = json.loads(line.strip(), object_pairs_hook=OrderedDict);  
    if not error_check(item, model_type):
        exit()
    candidate_list = item["candidate"]
    response = ""
    if model_type == "gen": 
        response = item["response"] 
    golden_response = ""
    hits_item = []
    for cand in candidate_list:
        cand_response, is_golden, score = cand
        if is_golden:
            golden_response =  cand_response
            ppl_data.append((golden_response, score))
            f1_data.append((golden_response, response))
        if model_type == "gen":
            cand_len = len(cand_response.strip().split(" ")) + 1
            hits_item.append((is_golden, score/cand_len))
        else:
            hits_item.append((is_golden, score))
    sorted_hits_item = sorted(hits_item, key = lambda d: d[1], reverse = True)
    hits_data.append(sorted_hits_item)


    
output_str = ""
hits_1, hits_3 = eval_hits(hits_data)
output_str += "hits@1: %.2f%%\n"%(hits_1*100)
output_str += "hits@3: %.2f%%\n"%(hits_3*100)
if model_type == "gen":
    ppl = eval_ppl(ppl_data)
    f1 = eval_f1(f1_data)
    output_str += "f1: %.2f%%\n"%(f1*100)
    output_str += "ppl: %.2f\n"%ppl
sys.stdout.write(output_str)
