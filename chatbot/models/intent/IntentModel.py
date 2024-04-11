import tensorflow as tf
from config.GlobalParams import MAX_SEQ_LEN
from tensorflow.keras.models import Model, load_model
from tensorflow.keras import preprocessing

class IntentModel:
    def __init__(self, model_name, proprocess):
        # 의도 클래스별 레이블
        self.labels = {0:"용어설명", 1:'이유설명', 2:'추세및기록', 3:'기타'}
        # 의도 분류 모델 불러오기
        self.model = load_model(model_name)
        # 챗봇 Preprocess 객체
        self.p = proprocess
        
    # 의도 클래스 예측
    def predict_class(self, query):
        # 형태소 분석
        pos = self.p.pos(query)
        
        # 문장 내 키워드 추출(불용어 제거)
        keywords = self.p.get_keywords(pos, without_tag = True)
        sequences = [self.p.get_wordidx_sequence(keywords)]
        
        # 패딩처리
        padded_seqs = preprocessing.sequence.pad_sequences(sequences, maxlen = MAX_SEQ_LEN, padding = 'post')
        #padded_seqs = preprocessing.sequence.pad_sequences(sequences, padding = 'post')
        
        predict = self.model.predict(padded_seqs)
        predict_class = tf.math.argmax(predict, axis = 1)
        return predict_class.numpy()[0]