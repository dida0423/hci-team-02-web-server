from openai import OpenAI
import os
from dotenv import load_dotenv
from app.models import Article, NewsChat, StorySummary
from typing import List
import ast
import uuid
import re
import json

def generate_chat(article: Article, API_KEY) -> List[NewsChat]:
    """
    Generate a chat summary for the given article using OpenAI's API.
    
    Args:
        article (Article): The article for which to generate the chat summary.
    
    Returns:
        NewsChat: The generated chat summary.
    """
    client = OpenAI(api_key=API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an article-to-conversation converter."},
            {"role": "user", "content": f"""다음은 뉴스 기사입니다. 이 기사의 주요 인물들이 실제로 말하는 것처럼, 대화를 구성해주세요. 아래의 조건을 반드시 지켜 주세요:
                                          - "나", "친구"와 같은 기사 외 화자는 사용하지 마세요.
                                          - 오직 기사 속 실제 인물, 단체, 기관(예: 바비킴, 제작진, 학생, 관객, 네티즌 등)만 발화할 수 있습니다.
                                          - 각 인물에는 숫자 형태의 고유 id를 부여하세요.
                                          - 각 발화는 1~2문장 이내로 자연스럽고 간결하게 작성하세요.
                                          - 말투는 실제 대화처럼 질문, 반응, 설명이 섞인 형태여야 합니다.
                                          - 정보의 흐름은 기사 순서를 따라가며 너무 과장되거나 요약식이 되지 않도록 하세요.
                                          - 출력은 아래 형식의 JSON 딕셔너리로만 하세요. JSON 외 출력은 하지 마세요.
                                            json dict entry의 키는 순서를 나타내며, 내용은 "id": 고유번호, "speaker": 기사 등장인물, "content": 대사 로 이루어져있습니다.
                                                      {article.content}
                                        """
              }
        ]
    )

    
    chat_summary_str = response.choices[0].message.content
    if not chat_summary_str:
        raise 
    
    chat_summary_str = re.sub(r"```(?:json)?\n?", "", chat_summary_str).replace("```", "").strip()
    
    chat_summary_dict = ast.literal_eval(chat_summary_str)

    news_chats = []

    for key, value in chat_summary_dict.items():
        news_chats.append(NewsChat(
            id=uuid.uuid4(),
            article_id=article.id,
            speaker=value["id"],
            speaker_name=value["speaker"],
            content=value["content"],
            order=key
          )
        )

    return news_chats


def generate_narrative(article: Article, API_KEY) -> StorySummary:
    """
    Generate a chat summary for the given article using OpenAI's API.
    
    Args:
        article (Article): The article for which to generate the chat summary.
    
    Returns:
        NewsChat: The generated chat summary.
    """
    client = OpenAI(api_key=API_KEY)

    prompt = (
        '다음은 뉴스 기사입니다. 이 기사를 일상적인 이야기에 비유해서 이해하기 쉽게 써주세요. 같은 흐름을 이해하기 더 쉬운 상황으로 단순화해서 작성해주세요.\n'
        '- 비유 네러티브에서 기사의 키워드와 대응되는 dictionary도 작성해주세요.\n'
        '- dictionary에서 비유 용어와 실제 용어가 교체되는 단어는 단어의 길이가 같도록 whitespace로 앞뒤를 꾸며주세요.\n'
        '- 정보의 흐름은 기사 순서를 따라가며 너무 과장되지 않도록 하세요.\n'
        '- 출력은 아래 형식의 JSON 배열로만 하세요. JSON 외 출력은 하지 마세요.\n'
        '{"narrative": content, "dictionary": {"비유 용어": "실제 용어"}} 형태로 작성해주세요.\n'
        '다음은 기사 내용입니다:\n'
        f'{article.content}'
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an article-to-narrative converter."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    narrative = ""
    dictionary = {}
    data = None
    if content:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Raw content received from OpenAI:\n{content}")
            return None  # or handle as appropriate
    else:
        print("No content received from OpenAI.")
        return None
    print(data)
    if isinstance(data, list) and data:
        item= data[0]
        narrative = item.get("narrative", "")
        dictionary = item.get("dictionary", {})
    elif isinstance(data, dict):
        narrative = data.get("narrative", "")
        dictionary = data.get("dictionary", {})

    print(f"Generated narrative: {narrative}")
    print(f"Generated dictionary: {dictionary}")

    return StorySummary(
        id=uuid.uuid4(),
        article_id=article.id,
        story=narrative,
        dictionary=dictionary
    )