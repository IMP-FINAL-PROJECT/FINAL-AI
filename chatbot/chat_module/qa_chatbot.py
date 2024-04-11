import pandas as pd
import logging
from utils.Preprocess import Preprocess
from models.intent.IntentModel import IntentModel
from models.ner.NerModel import NerModel
from chat_module.term_explain import term_explain
from chat_module.record_trend_answer import get_db_chain
from chat_module.sql_prompt import sql_prompt
#from chat_module.text_generation import *

id = 'dongwook@naver.com'    # 추후 아이디 넘어오는게 바로 들어가도록 수정 예정

# 로깅 설정
logging.basicConfig(filename='chatbot.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    encoding='utf-8')  # UTF-8 인코딩 지정

def answer_q(query):
    no_data = '죄송합니다. 답변드릴 수 없습니다.'
    p = Preprocess(word2index_dic = './train_tools/dict/chatbot_dict.bin',
              userdic = './utils/user_dic.tsv')

    try:
        # 의도 파악
        intent = IntentModel(model_name = './models/intent/intent_model_v2.h5', proprocess = p)
        predict = intent.predict_class(query)
        intent_name = intent.labels[predict]
        print(intent_name)
        logging.info(f'Intent recognized: {intent_name}')

        # 개체명 인식
        #try:
        '''
        ner = NerModel(model_name = './models/ner/test_model.h5', proprocess = p)
        predicts = ner.predict(query)
        ner_tags, ner_words = ner.predict_tags(query)
        logging.info(f"Question: {query}")
        logging.info(f"Intent: {intent_name}, NER Predictions: {predicts}, NER Tags: {ner_tags}, NER Words: {ner_words}")
        print(f"Intent: {intent_name}, NER Predictions: {predicts}, NER Tags: {ner_tags}, NER Words: {ner_words}")
        '''
        #except Exception as ex:
            #print(ex)
            #return no_data
    except Exception as ex:    # 개체명이나 의도명을 찾을 수 없을때 ex) 안녕?
        #print('return no_data')
        #print(ex)
        logging.error('*****Error processing the query*****')
        logging.info(f"Question: {query}")
        logging.exception(ex)  # 예외의 스택 트레이스를 로그에 남김
        return no_data
    try:
        if intent_name == '용어설명' or intent_name == '이유설명':
            return term_explain(query)
        elif intent_name == '추세및기록':
            chain = get_db_chain()
            question = sql_prompt(id, query)
            response = chain.run(question)
            return response
    except Exception as ex:
        print(ex)
        return "죄송합니다. 다시 입력해주실 수 있을까요?"

    #return search_intent(intent_name, ner_tags, ner_words)