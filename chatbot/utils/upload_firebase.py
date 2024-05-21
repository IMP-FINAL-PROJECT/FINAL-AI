import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import pytz

def upload_utterance(id, message_text):
    # Firebase 인증 정보를 제공하는 서비스 계정 키 파일을 다운로드하고 경로를 설정합니다.
    cred = credentials.Certificate('chatbot/utils/firebase_key.json')
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    # Firestore 데이터베이스를 가져옵니다.
    db = firestore.client()

    # 데이터를 추가할 컬렉션과 문서 ID를 설정합니다.
    collection_name = id
    document_id = '0'  # Firestore에서는 문서 ID가 문자열 형태로 되어야 합니다.

    # 한국 시간대를 설정합니다.
    korea_timezone = pytz.timezone('Asia/Seoul')
    current_korea_time = datetime.now(korea_timezone)

    # chat 필드에 추가할 새 메시지 데이터를 정의합니다.
    message = {
        'response': message_text,
        'chat_time': current_korea_time
    }

    # 문서 참조를 가져옵니다.
    doc_ref = db.collection(collection_name).document(document_id)

    # 문서가 존재하는지 확인 후 존재하지 않는 경우 새로 생성, 존재하는 경우 업데이트
    doc = doc_ref.get()
    if doc.exists:
        # 문서가 존재하는 경우 채팅 필드 업데이트
        doc_ref.update({
            'chat': firestore.ArrayUnion([message]),
            'update_at': current_korea_time
        })
    else:
        # 문서가 존재하지 않는 경우 새 문서 생성
        doc_ref.set({
            'chat': [message],
            'name' : '선발화 동욱봇',
            'update_at': current_korea_time
        }, merge=True)

    print(f'{id} : 채팅 메시지가 성공적으로 추가되었습니다.')

    return