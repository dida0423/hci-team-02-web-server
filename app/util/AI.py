from openai import OpenAI
import os
from dotenv import load_dotenv
from app.models import Article, NewsChat, StorySummary
from typing import List
import ast
import uuid
import re
import json

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")


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
        '다음은 뉴스 기사입니다. 이 기사를 일상적인 이야기로 비유해서 독자가 더 쉽게 이해할 수 있도록 재작성해주세요.\n'
        '\n'
        '요구 사항:\n'
        '1. 반드시 현실과 다른 **비유적 상황**으로 바꿔 설명해주세요. (예: 회사, 마을, 학교, 동물 이야기 등)\n'
        '2. 기사에 등장하는 **실제 인물, 단체, 국가 이름은 절대 그대로 사용하지 마세요.**\n'
        '3. 영어 단어나 외래어를 쓰지 마세요. 모든 표현은 자연스러운 한국어로만 작성하세요.\n'
        '4. 사건의 긍정 또는 부정 감정의 흐름을 비유에서도 동일하게 유지하세요.\n'
        '5. 반드시 아래와 같은 JSON 형식으로만 출력하세요 (기타 문장, 설명, 개행 금지):\n\n'
        '```json\n'
        '[\n'
        '  {\n'
        '    "narrative": "<비유 본문 내용>",\n'
        '    "dictionary": {\n'
        '      " 비유용어1 ": "실제용어1",\n'
        '      " 비유용어2 ": "실제용어2"\n'
        '    }\n'
        '  }\n'
        ']\n'
        '```\n\n'
        '※ narrative는 한글로 된 비유 이야기이며, dictionary는 실제 개념과의 매핑입니다.\n\n'
        f'다음은 기사 내용입니다:\n{article.content}'
        )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an article-to-narrative converter."},
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content
    # content 정제
    if content.startswith("```json"):
        content = content.removeprefix("```json").removesuffix("```").strip()
    elif content.startswith("```"):
        content = content.removeprefix("```").removesuffix("```").strip()

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

  
def generate_keywords(title_list: List[str], API_KEY) -> dict:
    client = OpenAI(api_key=API_KEY)

    formatted_titles = "\n".join(f"- {title}" for title in title_list)

    prompt = f'''
다음은 오늘 하루 동안 주요 언론사에서 보도한 뉴스 기사들의 제목입니다.
기사들을 종합해볼 때, 오늘의 핵심 키워드(주제어)와 그 중요도에 대해 답해주세요.

- 단어 5개
- 너무 일반적인 단어는 피하고, 빈도가 높은 이슈 중심
- 단어와 중요도(1~5)를 아래와 같은 JSON 형식으로 반환

{{
  "keywords": [
    {{"keyword": "키워드1", "score": "<중요도>"}},
    {{"keyword": "키워드2", "score": "<중요도>"}},
    {{"keyword": "키워드3", "score": "<중요도>"}},
    {{"keyword": "키워드4", "score": "<중요도>"}},
    {{"keyword": "키워드5", "score": "<중요도>"}}
  ]
}}

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
    
    print("[DEBUG] GPT 응답 원문:\n", content)

    content = content.strip().removeprefix("```json").removesuffix("```").strip() if content else ""
    try:
        return json.loads(content)
    except Exception as e:
        print(f"[ERROR] JSON 파싱 실패: {e}")
        raise

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

    return response.choices[0].message.content.strip() if response.choices[0].message.content else ""

def detect_article_bias(media_name: str, content: str, API_KEY: str) -> dict:
    from openai import OpenAI
    import ast

    client = OpenAI(api_key=API_KEY)

    prompt = f"""
다음은 특정 언론사가 보도한 뉴스 기사입니다.
이 기사에서 등장하는 인물이나 기관의 발언 내용은 판단 대상이 아닙니다.

당신의 임무는 해당 언론사가 가진 정치적 성향에 따라, 이 기사의 편집 방식(표현, 강조, 묘사 등)이 그 성향과 일치하는 편향을 보여주는지 평가하는 것입니다.

기준:

- 감정적인 단어, 주관적인 논평, 일방적 강조 등이 사용되었는가?
- 그 편향이 해당 언론사의 성향과 일치하는 방향인가?

결과는 다음과 같은 JSON 형식으로 출력하세요:

{{
"media_bias": "보수 / 진보 / 중도",
"reporting_bias": "있음 / 없음"
}}

언론사: {media_name}
기사:
\"\"\"
{content}
\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a political bias evaluator."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content.strip().replace("```json", "").replace("```", "") if response.choices[0].message.content else ""
    try:
        return ast.literal_eval(content)
    except Exception as e:
        print("[ERROR] Failed to parse bias response:\n", content)
        raise e
