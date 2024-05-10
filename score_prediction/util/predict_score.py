import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from util.using_db import connect_db, query_to_df
from util.preprocess_data import preprocess_daily_life_pattern_data
from util.columns_to_normalize import columns_to_normalize
from datetime import date, timedelta
import pickle
import joblib
import json

def predict_score(user_ids):
    conn = connect_db()
    cursor = conn.cursor()

    for user_id in user_ids:
        try:
            #predict_sql = f"SELECT * FROM daily_life_pattern WHERE id='{user_id}' AND date='{date.today()-timedelta(days=1)}'"    # 날짜에 해당하는 데이터가 아직 없음
            predict_sql = f"SELECT * FROM daily_life_pattern WHERE id='{user_id}' AND date='2024-05-04'"

            drop_list = ['id', 'hour_index', 'date']    # 점수 판별에 불필요한것들 리스트
            predict_df = preprocess_daily_life_pattern_data(query_to_df(predict_sql, conn, cursor), drop_list)
            
            with open('score_prediction/util/scaler.pkl', 'rb') as file:    # 스케일러 불러오기
                loaded_scaler = pickle.load(file)

            predict_df[columns_to_normalize] = loaded_scaler.transform(predict_df[columns_to_normalize])    # 데이터 정규화

            user_model_folder = f'score_prediction/model/{user_id}'    # 사용자 맞춤 모델의 경로
            score_file_path = f'{user_model_folder}/{user_id}_fine_tuned_model_scores.json'    # 사용자 맞춤 모델의 RMSE값이 있는 json파일 경로

            if os.path.exists(score_file_path):    # 사용자 맞춤 RMSE값 있는 json파일 읽어오기
                with open(score_file_path, 'r') as file:
                    model_scores = json.load(file)
            else:
                base_score_file_path = 'score_prediction/model/base_model/model_scores.json'    # 사용자 맞춤 모델 점수 파일이 없으면 기본 점수 사용
                with open(base_score_file_path, 'r') as file:
                    model_scores = json.load(file)
            
            predictions = {}
            models = ['GradientBoosting', 'XGBoost', 'LightGBM', 'RandomForest']
            
            for model_name in models:
                fine_tuned_model_path = f'{user_model_folder}/{model_name}_fine_tuned.joblib'
                if os.path.exists(fine_tuned_model_path):    # fine_tuning모델이 있을 때 해당 모델 가져오기
                    model = joblib.load(fine_tuned_model_path)
                    predictions[model_name] = model.predict(predict_df)
                    print(f'Using fine-tuned {model_name} model for prediction.')
                else:    # fine_tuning 모델이 없을 때 base_model을 가져와서 점수 예측
                    print(f'No fine-tuned model found for {model_name} at {fine_tuned_model_path}, using base model instead.')
                    base_model_path = f'score_prediction/model/base_model/{model_name}.joblib'
                    if os.path.exists(base_model_path):
                        model = joblib.load(base_model_path)
                        predictions[model_name] = model.predict(predict_df)

            total_weight = sum((1. / score for score in model_scores.values()))    # 가중 평균 계산
            pred_combined = sum((predictions[name] * (1. / score) for name, score in model_scores.items())) / total_weight    # 최종 예측 결과
            pred_combined = round(pred_combined[0], 1)
        
            insert_sql = 'INSERT INTO happiness (id, point, timestamp) VALUES (%s, %s, %s)'
            upload_data = (user_id, pred_combined, date.today())
            cursor.execute(insert_sql, upload_data)
            conn.commit()
            cursor.close()

            #return pred_combined
        except Exception as ex:
            print(ex)
            continue

#user_ids = ['ledu1017@naver.com', 'joowon@naver.com']
#print(predict_score(user_ids))