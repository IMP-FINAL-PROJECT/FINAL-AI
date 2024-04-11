from datetime import date

def sql_prompt(id, query):
    question = f'''
    Database name is final.
    You can use sensor table and daily_life_pattern_table only.
    You have to refer to the information on the db table carefully.
    You must answer to make a sentence
    Today is {date.today()}

    This is example 1
    "Query": "ID: dongwook@naver.com, How many steps did I take yesterday?"
    "SQLQuery": "SELECT sum(pedometer) FROM final.sensor WHERE id = 'dongwook@naver.com' AND timestamp = CURDATE() - INTERVAL 1 DAY;"
    "SQLResult": "Result of the SQL query"
    "Answer": 'You've walked a total of 7331 steps!'

    This is example 2
    "Query": "Did I walk more this week than last week?"
    "SQLQuery": "SELECT ROUND(sum(pedometer) / (SELECT sum(pedometer) FROM final.sensor where id = "dongwook@naver.com" AND timestamp BETWEEN "2024-03-31" AND "2024-04-06"), 2) AS divide_pedometer FROM final.sensor where id = "dongwook@naver.com" AND timestamp BETWEEN "2024-04-07" AND "2024-04-13";"
    "SQLResult": "Result of the SQL query"
    "Answer": "I walked 10% compared to last week."

    This is example 3
    "Question":Did you go to more diverse places on April 7th compared to March 30th?
    "SQLQuery": SELECT place_diversity FROM final.daily_life_pattern WHERE id = 'dongwook@naver.com' AND date IN ('2024-03-30', '2024-04-07') ORDER BY date DESC
    "SQLResult": Result of the SQLQuery
    "Answer": You visited 2 places on April 7th and 4 places on March 30th.

    This is example 4
    "Question":Did I go to more diverse places on April 7 compared to April 5th?
    "SQLQuery": SELECT place_diversity FROM final.daily_life_pattern WHERE id = 'dongwook@naver.com' AND date IN ('2024-04-07', '2024-04-05') ORDER BY date DESC
    "SQLResult": Result of the SQLQuery
    "Answer": 2 places on April 5th and 2 places on April 7th and the number of places visited on both dates is the same!

    This is example 5
    "Question": How much sunlight did I see outside?
    "SQLQuery": SELECT sum(day_light_exposure) FROM final.daily_life_pattern WHERE id = 'dongwook@naver.com' AND date IN ('2024-03-30', '2024-03-31', '2024-04-01', '2024-04-02', '2024-04-03', '2024-04-04', '2024-04-05', '2024-04-06', '2024-04-07', '2024-04-08', '2024-04-09', '2024-04-10') ORDER BY date DESC
    "SQLResult": Result of the SQLQuery
    "Answer": When you looked at your last 12 days, you saw 3446 lumen of sunshine.

    This is example 6
    "Question": I don't think I've seen much sunlight this month.
    "SQLQuery": SELECT sum(day_light_exposure) FROM final.daily_life_pattern WHERE id ='dongwook@naver.com' AND date BETWEEN '2024-04-01' AND '2024-04-30' ORDER BY date DESC
    "SQLResult": Result of the SQLQuery
    "Answer": 3277

    This is example 7
    "Question": I think I've been using my cell phone a lot at night.
    "SQLQuery": SELECT avg(night_phone_use_frequency) FROM final.daily_life_pattern WHERE id = 'dongwook@naver.com' AND date BETWEEN '2024-04-01' AND '2024-04-10'
    "SQLResult": Result of the SQLQuery
    "Answer": You've used your phone 4.5 times on average at night between 2024-04-01 and 2024-04-10.

    This is question
    {id}
    "Query": {query}
    "SQLQuery": 
    "SQLResult":
    '''
    
    return question