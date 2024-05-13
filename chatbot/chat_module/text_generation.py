import time
import google.generativeai as genai
from peft import PeftModel, PeftConfig
from transformers import AutoTokenizer, AutoModelForCausalLM
from config.Config_list import GOOGLE_CONFIG
from chat_module.translator import en_to_ko

'''
# 모델과 토크나이저 초기화
tokenizer = AutoTokenizer.from_pretrained("daekeun-ml/phi-2-ko-v0.1")
base_model = AutoModelForCausalLM.from_pretrained("daekeun-ml/phi-2-ko-v0.1")
config = PeftConfig.from_pretrained("ledu1017/phi2-ko-mental-chat")
model = PeftModel.from_pretrained(base_model, "ledu1017/phi2-ko-mental-chat")

def daily_conversation_response(user_input):
    start = time.time()
    user_input = "[INST]" + user_input + "[/INST]"
    input_ids = tokenizer.encode(user_input, return_tensors='pt')
    output = model.generate(input_ids, max_length=180, num_return_sequences=1)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    end = time.time()
    total = end-start
    print(f"총 실행 시간: {total}")
    return response
'''
def additional_answer(user_input):
    genai.configure(api_key=GOOGLE_CONFIG['GOOGLE_PALM_API'])
    model = genai.GenerativeModel('gemini-pro')

    convo = model.start_chat(history=[
        {
            'role' : 'user',
            'parts' : ["Health Analysis"]
        },
        {
            'role' : 'model',
            'parts' : [
                        """
                        I'm going to say the message that the user typed at the beginning unconditionally and start. 
                        Please let me know if the user trend is good or bad according to the trend. If the trend is bad,
                        please let me know how to improve it. The standard of bad trend is unhealthy behavior. Please answer in natural sentences.
                        
                        For example
                        input_text = "Recently, the night time cell phone usage time is 5% less than the night time cell phone usage time from April 7th to April 13th!"
                        answer = "Recently, the night time cell phone usage time is 5% less than the night time cell phone usage time from April 7th to April 13th! This can have some positive effects: Improving Sleep Quality: Less screen time before bed can improve sleep quality because blue light from the screen can interfere with melatonin production and disrupt the sleep cycle. Improved well-being: Less screen time can potentially improve mental health and well-being by reducing exposure to stress-induced content. Increased Productivity: With less time spent on cellphones at night, individuals can find more time to relax, so they can be more productive during the day. Reduced Eye Fatigue: Reducing screen time, especially in low-light conditions, can help reduce eye fatigue and prevent long-term eye health problems. These benefits contribute to improved overall health and a more balanced lifestyle"
                        """
                       ]
        }
    ])
    convo.send_message(user_input)
    ko_answer = en_to_ko(convo.last.text)
    
    return ko_answer