#!/bin/bash

######################################################################
#
# Copyright (c) 2019 Baidu.com, Inc. All Rights Reserved
#
# @file run_test.sh
#
######################################################################

#pythonpath='/opt/compiler/gcc-4.8.2/lib/ld-linux-x86-64.so.2 --library-path /opt/compiler/gcc-4.8.2/lib /home/talk2/xuxinchao01/knowledge_tagging/krl-p40-local/pytorch1/bin/python'
pythonpath='python'
prefix=demo
datapart=dev
datapath=./data

corpus_file=${datapath}/resource/${datapart}.txt
sample_file=${datapath}/resource/sample.${datapart}.txt
text_file=${datapath}/${prefix}.test
topic_file=${datapath}/${prefix}.test.topic

if [ "${datapart}"x = "test"x ]; then
    sample_file=${corpus_file}
else
    ${pythonpath} ./tools/convert_session_to_sample.py ${corpus_file} ${sample_file}
fi

${pythonpath} ./tools/convert_conversation_corpus_to_model_text.py ${sample_file} ${text_file} ${topic_file} 1

#${pythonpath} ./network.py --test --ckpt models/best.model --gen_file ./output/test.result --use_posterior False --gpu 0 > log.txt 2>&1
${pythonpath} ./network.py --test --ckpt models/best.model --gen_file ./output/test.result --use_posterior False > log.txt 2>&1


${pythonpath} ./tools/topic_materialization.py ./output/test.result ./output/test.result.final ${topic_file}

${pythonpath} ./tools/convert_result_for_eval.py ${sample_file} ./output/test.result.final ./output/test.result.eval

${pythonpath} ./tools/eval.py ./output/test.result.eval

