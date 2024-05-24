import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pandas as pd
from util.using_db import connect_db, query_to_df
from util.preprocess_data import preprocess_daily_life_pattern_data, preprocess_mood_data, data_scaling
from util.data_generative import add_custom_noise

def get_data(user_id=None):
    conn = connect_db()    # db연결
    cursor = conn.cursor()    # cursor 생성
    
    drop_list= ['id', 'hour_index']    # 학습에 불필요한 컬럼 리스트

    # daily_life_df를 만들면서 필요 없는 컬럼 제거 및 불량 데이터 제거
    # mood_df를 만들면서 하루에 기분점수가 여러번 찍혀있으면 평균으로 계산하도록

    if user_id == None:
        daily_life_sql = "SELECT * FROM daily_life_pattern"
        mood_sql = "SELECT * FROM mood"
    else:
        daily_life_sql = f"SELECT * FROM daily_life_pattern WHERE id='{user_id}'"
        mood_sql = f"SELECT * FROM mood WHERE id='{user_id}'"

    try:
        daily_life_df = preprocess_daily_life_pattern_data(query_to_df(daily_life_sql, conn, cursor), drop_list)
        mood_df = preprocess_mood_data(query_to_df(mood_sql, conn, cursor))
    except:
        cursor.close()
        return 'pass'

    cursor.close()
    
    combined_df = pd.merge(daily_life_df, mood_df[['date', 'score']], on='date', how='left')
    combined_df.drop(['date'], axis=1, inplace = True)    # 필요없는 컬럼 삭제
    combined_df = combined_df.dropna(subset=['score'])    # score 컬럼에서 NaN 값이 있는 행 제거

    # 사용 예시
    #integer_cols = ['place_diversity', 'score']  # 정수로 증감해야 하는 컬럼
    #exclude_cols = ['day_time_count', 'night_time_count']  # 노이즈를 추가하지 않을 컬럼
    #augmented_noise_df = add_custom_noise(combined_df, noise_level=0.8, integer_columns=integer_cols, exclude_columns=exclude_cols)
    augmented_noise_df = add_custom_noise(combined_df, noise_level=0.8)    # 데이터 증강법 중 노이트 추가법 사용

    final_df = data_scaling(pd.concat([combined_df, augmented_noise_df], ignore_index=True))    # 두 데이터프레임을 수직으로 합치기 (위/아래로 연결)
    
    return final_df