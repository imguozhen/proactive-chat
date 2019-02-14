#!/bin/bash

######################################################################
#
# Copyright (c) 2019 Baidu.com, Inc. All Rights Reserved
#
# @file run_train.sh
#
######################################################################

pythonpath='python'
prefix=demo
datatype=(train dev test)
datapath=./data

for ((i=0; i<${#datatype[*]}; i++))
do
    corpus_file=${datapath}/resource/${datatype[$i]}.txt
    text_file=${datapath}/${prefix}.${datatype[$i]}
    topic_file=${datapath}/${prefix}.${datatype[$i]}.topic
    index_file=${datapath}/${prefix}.${datatype[$i]}.index
    ${pythonpath} ./tools/convert_conversation_corpus_to_model_text.py ${corpus_file} ${text_file} ${topic_file} ${index_file} 1 1
done

${pythonpath} ./network.py --gpu 0 > log.txt
