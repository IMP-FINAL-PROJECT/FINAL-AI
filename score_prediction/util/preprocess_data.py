from sklearn.preprocessing import MinMaxScaler
from util.columns_to_normalize import columns_to_normalize
import pandas as pd
import pickle
import ast

def preprocess_mood_data(mood_df):
    mood_df['timestamp'] = pd.to_datetime(mood_df['timestamp'])    # timestamp 컬럼을 datetime 형태로 변환
    mood_df['date'] = mood_df['timestamp'].dt.date    # 날짜만 추출하여 새로운 컬럼에 저장
    mood_df = mood_df.groupby(['id', 'date'])['score'].mean().round().astype(int).reset_index()   # 날짜별로 그룹화하여 score의 평균 계산

    return mood_df

def preprocess_daily_life_pattern_data(daily_life_df, drop_list):
    # 각 조건에 대한 불리언 마스크 생성 불량데이터 제거
    condition1 = daily_life_df['home_stay_percentage'] < 0
    condition2 = (daily_life_df['day_time_count'] + daily_life_df['night_time_count']) != 24
    condition3 = (daily_life_df['day_phone_use_duration'] + daily_life_df['night_phone_use_duration']) == 0
    condition4 = (daily_life_df['day_light_exposure'] + daily_life_df['night_light_exposure']) == 0

    mask = condition1 | condition2 | condition3 | condition4    # 조건을 하나의 마스크로 결합

    daily_life_df = daily_life_df[~mask]    # 해당 조건이 False인 행만 필터링

    daily_life_df['place_diversity'] = daily_life_df['place_diversity'].apply(convert_to_list_and_length)    # 위도경도를 방문 장소 개수로 변경
    #daily_life_df.drop(['id', 'life_routine_consistency', 'hour_index', 'home_stay_percentage'], axis=1, inplace = True)    # 필요없는 컬럼 삭제
    daily_life_df.drop(drop_list, axis=1, inplace = True)    # 필요없는 컬럼 삭제

    return daily_life_df

def convert_to_list_and_length(list_str):    # place_diversity 컬럼의 문자열을 실제 리스트로 변환하고 길이를 계산
    try:
        real_list = ast.literal_eval(list_str)    # 문자열을 리스트로 변환
        return len(real_list)    # 리스트의 길이 반환
    except:
        return 0    # 변환 실패 시 0 반환
    
def data_scaling(final_df):
    scaler = MinMaxScaler()    # MinMaxScaler 인스턴스 생성
    
    scaler.fit(final_df[columns_to_normalize])    # 스케일러 학습 및 정규화 실행 
    final_df[columns_to_normalize] = scaler.transform(final_df[columns_to_normalize])

    with open('score_prediction/util/scaler.pkl', 'wb') as file:    # 스케일러 저장
        pickle.dump(scaler, file)

    return final_df