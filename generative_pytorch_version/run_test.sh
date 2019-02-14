#!/bin/bash

######################################################################
#
# Copyright (c) 2019 Baidu.com, Inc. All Rights Reserved
#
# @file run_test.sh
#
######################################################################

pythonpath='python'
prefix=demo
testfile=test.txt
datapath=./data

corpus_file=${datapath}/resource/${testfile}
text_file=${datapath}/${prefix}.test
topic_file=${datapath}/${prefix}.test.topic
index_file=${datapath}/${prefix}.test.index
${pythonpath} ./tools/convert_conversation_corpus_to_model_text.py ${corpus_file} ${text_file} ${topic_file} ${index_file} 1 0 1

${pythonpath} ./network.py --test --ckpt models/best.model --gen_file ./output/test.result --gold_score_file ./output/gold.scores --use_posterior False --gpu 0 > log.txt 2>&1

${pythonpath} ./tools/topic_materialization.py ./output/test.result ./output/test.result.final ${topic_file} ${index_file}

${pythonpath} ./toos/convert_result_for_eval.py ${corpus_file} ./output/test.result.final ./output/gold.scores ${index_file} ./output/test.result.eval

${pythonpath} ./tools/eval.py ./output/test.result.eval gen
