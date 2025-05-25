from openai import OpenAI
import os
from dotenv import load_dotenv
from app.models import Article, NewsChat
from typing import List
import ast
import uuid
import re


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

def generate_keywords(title_list: List[str], API_KEY) -> dict:
    client = OpenAI(api_key=API_KEY)

    formatted_titles = "\n".join(f"- {title}" for title in title_list)

    prompt = f'''
다음은 오늘 하루 동안 주요 언론사에서 보도한 뉴스 기사들의 제목입니다.
기사들을 종합해볼 때, 오늘의 핵심 키워드(주제어)와 그 중요도에 대해 답해주세요.

- 단어 최대 10개
- 너무 일반적인 단어는 피하고, 사회적으로 중요하거나 빈도가 높은 이슈 중심
- 단어와 중요도(1~5)를 JSON 형식으로 반환

기사 제목 목록:
{formatted_titles}
    '''

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a news topic analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content
    content = content.strip().removeprefix("```json").removesuffix("```").strip()
    return ast.literal_eval(content)

def generate_highlighted_article(article: Article, API_KEY) -> str:
    client = OpenAI(api_key=API_KEY)

    prompt = f'''
너는 긴 뉴스 기사에서 사용자가 반드시 집중해서 읽어야 할 **중요한 구절이나 문장 전체**를 강조하는 시스템이다.
사용자의 집중을 돕기 위한 "집중 읽기 모드" 기능을 위해 다음 규칙을 따른다:

1. **기사 원문은 절대 수정하거나 요약하지 말 것.** 출력은 반드시 입력된 원문과 정확히 일치해야 한다.
2. 강조는 두 가지 방식으로 할 수 있다:
   - 문장 전체가 중요하면 **문장 전체를 [[highlight]]...[[/highlight]]로 감싼다**.
   - 문장 내 특정 구절만 중요하면 해당 **구절만 [[highlight]]...[[/highlight]]로 감싼다**.
3. 전체 강조 수는 **문서 길이에 따라 5~10개 정도로 제한**한다.
4. **강조 여부는 맥락에 따라 유연하게 판단**하며, 인물·단체·기관이 언급된 문장은 강조 대상일 가능성이 높다.
5. 강조 이외에는 원문을 그대로 유지하고, 문장 순서나 구조도 변경하지 않는다.
6. 강조 마크업 외에는 어떤 텍스트도 추가하지 말고, 오직 원문 전체를 반환할 것.

{article.content}
    '''

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a highlight annotator."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
