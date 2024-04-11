from pinecone import Pinecone, ServerlessSpec, PodSpec
from sentence_transformers import SentenceTransformer
from config.Config_list import PINECONE_CONFIG
import torch

model = None

def load_model():
    global model

    # Load the model only if it hasn't been loaded before
    if model is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = SentenceTransformer('daekeun-ml/phi-2-ko-v0.1', device=device)

    return model

def term_explain(query):    # 용어설명 답변
    no_data = '죄송합니다. 답변드릴 수 없습니다.'
    try:
        index_name = 'sample-search'
        api_key = PINECONE_CONFIG['PINECONE_API_KEY']
        pc = Pinecone(api_key=api_key)
        index = pc.Index(index_name)
        
        model = load_model()
        embedded_query = model.encode(query).tolist()
        results = index.query(vector = embedded_query, top_k = 1, include_metadata=True)
        score = results['matches'][0]['score']
        text = results['matches'][0]['metadata']['text']
        print(text, score)
        if score > 0.5:
            return text
        else:
            return no_data
    except Exception as ex:
        print(ex)
        return no_data
    