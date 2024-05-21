import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from utils.connect_mysql import connect_db, query_to_df
from config.Config_list import *
from datetime import date, timedelta
import openai

def additional_answer(user_id):
    conn = connect_db()
    columns_score_query = f"SELECT * FROM final.daily_life_pattern WHERE id='{user_id} AND date='{date.today()-timedelta(days=1)}'"
    #columns_score_query = f"SELECT * FROM final.daily_life_pattern WHERE id='{user_id}' AND date='2024-05-15'"    # 테스트용 특정 날짜 지정

    today_score_df = query_to_df(columns_score_query, conn)

    # open ai에서 발급받은 api key를 등록합니다
    openai.api_key = OPENAI_CONFIG['OPENAI_API_KEY']

    MODEL = "gpt-4o"
    USER_INPUT_MSG = f"""각 항목이 행복점수에 미치는 영향을 알려주고 점수가 낮다면 개선 방법을 알려줘.
                    점수가 60점 이상이라면 잘하고 있다는 응원의 메시지를 넣어줘. 그리고 보고서 형식으로 작성해줘.
                    만들어진 텍스트 그대로 사용자에게 전달될거니까 들여쓰기를 잘 해줘.
                    활동 점수 : {round(today_score_df['activity_score'].values[0])}, 
                    빛 노출량 점수 : {round(today_score_df['illumination_exposure_score'].values[0])}, 
                    장소의 다양성 점수 : {round(today_score_df['location_diversity_score'].values[0])}, 
                    생활의 규칙성 점수 : {round(today_score_df['circadian_rhythm_score'].values[0])}, 
                    핸드폰 사용 시간 점수 : {round(today_score_df['phone_usage_score'].values[0])}"""

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": USER_INPUT_MSG}
        ],
        temperature=0,
    )

    answer = response["choices"][0]["message"]["content"].replace('**', '').replace('#', '')

    return answer