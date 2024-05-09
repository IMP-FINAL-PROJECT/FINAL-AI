import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from utils.upload_firebase import upload_utterance
from utils.connect_mysql import connect_db
from chat_utterance.utterance_list import *
from datetime import date, timedelta
import pandas as pd
import random

def query_to_df(sql, connection):    # 쿼리 실행 및 DataFrame 생성을 위한 함수
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
        return pd.DataFrame(result)
    
def numerical_abnormality_utterance(id):    # 특정 항목에 대해 최근 추세가 상승하거나 하락한다는 선발화
    conn = connect_db()

    figure = {}

    dayily_life_pattern_columns = ['home_stay_percentage', 'night_phone_use_duration', 'night_light_exposure', 'life_routine_consistency', 'sleeptime_screen_duration']    # 어떤 데이터를 확인할지 정해둔 리스트
    for column in dayily_life_pattern_columns:
        today = date.today()    # 현재 날짜
        this_week_start = today - timedelta(days=6)    # 이번 주의 시작 날짜 (현재 날짜에서 6일 전)
        past_two_weeks_start = this_week_start - timedelta(days=14)    # 지난 2주의 시작 날짜 (이번 주 시작 14일 전)
        past_two_weeks_end = this_week_start - timedelta(days=1)    # 지난 2주의 종료 날짜 (이번 주 시작 1일 전)

        # SQL 쿼리 생성 / 3주전부터 1주 전까지의 데이터와 이번주 데이터 비교. ex) 결과 : 94 -> 이번주 사용량이 지난 두 주간의 사용시간의 94%
        sql_query = f"""
        SELECT
            ROUND(100 * (this_week_usage / past_two_weeks_usage), 2) AS percentage_change
        FROM
            (SELECT 
                SUM(CASE WHEN DATE(date) BETWEEN '{this_week_start}' AND '{today}' AND id='{id}' THEN {column} ELSE 0 END) AS this_week_usage,
                SUM(CASE WHEN DATE(date) BETWEEN '{past_two_weeks_start}' AND '{past_two_weeks_end}' AND id='{id}' THEN {column} ELSE 0 END) AS past_two_weeks_usage
            FROM
                daily_life_pattern
            WHERE
                date BETWEEN '{past_two_weeks_start}' AND '{today}'
            ) AS usage_data;
        """

        numerical_df = query_to_df(sql_query, conn)
        figure[column] = numerical_df['percentage_change'].iloc[0] if not numerical_df.empty else None

    analyze = analyze_results(figure)
    conn.close()

    # analyze 결과에서 랜덤하게 한 메시지를 선택
    if analyze:
        random_message = random.choice(analyze)
        upload_utterance(id, random_message)  # Firestore에 업로드

    return figure

def long_term_nonattendant_utterance(id):
    conn = connect_db()

    figure = {}
    today = date.today()    # 현재 날짜를 구함
    two_weeks_ago = today - timedelta(days=14)    # 오늘로부터 2주 이전 날짜를 계산

    # SQL 쿼리: last_login이 오늘로부터 2주 이전인지 검사
    sql_query = f"""
    SELECT
        id,
        CASE 
            WHEN last_login <= '{two_weeks_ago}' THEN 'inactive'
            ELSE 'active'
        END AS status
    FROM
        user
    WHERE
        id = '{id}';
    """

    long_term_df = query_to_df(sql_query, conn)

    figure['long_term_status'] = long_term_df['status'].iloc[0]
    conn.close()

    return figure

def analyze_results(results):
    print(results)

    messages = []
    message_sources_high = {    # 30% 이상 상승한것에 대한 선발화문
        'home_stay_percentage': HOME_STAY_PERCENTAGE_UTTERANCE_HIGH,
        'night_phone_use_duration': NIGHT_PHONE_USE_DURATION_UTTERANCE_HIGH,
        'night_light_exposure': NIGHT_LIGHT_EXPOSURE_HIGH,
        'sleeptime_screen_duration' : SLEEPTIME_SCREEN_DURATION_HIGH,
        'life_routine_consistency' : LIFE_ROUTINE_CONSISTENCY_HIGH
    }
    message_sources_low = {    # 30% 이상 하락한것에 대한 선발화문
        'home_stay_percentage': HOME_STAY_PERCENTAGE_UTTERANCE_LOW,
        'night_phone_use_duration': NIGHT_PHONE_USE_DURATION_UTTERANCE_LOW,
        'night_light_exposure': NIGHT_LIGHT_EXPOSURE_LOW,
        'sleeptime_screen_duration' : SLEEPTIME_SCREEN_DURATION_LOW,
        'life_routine_consistency' : LIFE_ROUTINE_CONSISTENCY_LOW
    }

    for key, value in results.items():
        if key != 'long_term_status':
            if value is not None:
                if value >= 130:
                    chosen_message = random.choice(message_sources_high[key])
                    messages.append(chosen_message)                    
                elif value <= 70:
                    chosen_message = random.choice(message_sources_low[key])
                    messages.append(chosen_message)                    
        else:
            if value == 'inactive':
                messages.append("오랜시간 앱에 접속하지 않았습니다. 오늘은 앱에 접속해서 최근 상태를 확인해보는건 어떨까요?")

    return messages