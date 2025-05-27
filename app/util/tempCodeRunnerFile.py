

# def generate_chat(article: Article, API_KEY) -> List[NewsChat]:
#     """
#     Generate a chat summary for the given article using OpenAI's API.
    
#     Args:
#         article (Article): The article for which to generate the chat summary.
    
#     Returns:
#         NewsChat: The generated chat summary.
#     """
#     client = OpenAI(api_key=API_KEY)

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are an article-to-conversation converter."},
#             {"role": "user", "content": f"""다음은 뉴스 기사입니다. 이 기사의 주요 인물들이 실제로 말하는 것처럼, 대화를 구성해주세요. 아래의 조건을 반드시 지켜 주세요:
#                                           - "나", "친구"와 같은 기사 외 화자는 사용하지 마세요.
#                                           - 오직 기사 속 실제 인물, 단체, 기관(예: 바비킴, 제작진, 학생, 관객, 네티즌 등)만 발화할 수 있습니다.
#                                           - 각 인물에는 숫자 형태의 고유 id를 부여하세요.
#                                           - 각 발화는 1~2문장 이내로 자연스럽고 간결하게 작성하세요.
#                                           - 말투는 실제 대화처럼 질문, 반응, 설명이 섞인 형태여야 합니다.
#                                           - 정보의 흐름은 기사 순서를 따라가며 너무 과장되거나 요약식이 되지 않도록 하세요.
#                                           - 출력은 아래 형식의 JSON 딕셔너리로만 하세요. JSON 외 출력은 하지 마세요.
#                                             json dict entry의 키는 순서를 나타내며, 내용은 "id": 고유번호, "speaker": 기사 등장인물, "content": 대사 로 이루어져있습니다.
#                                                       {article.content}
#                                         """
#               }
#         ]
#     )

    
#     chat_summary_str = response.choices[0].message.content
#     if not chat_summary_str:
#         raise 
    
#     chat_summary_str = re.sub(r"```(?:json)?\n?", "", chat_summary_str).replace("```", "").strip()
    
#     chat_summary_dict = ast.literal_eval(chat_summary_str)

#     news_chats = []

#     for key, value in chat_summary_dict.items():
#         news_chats.append(NewsChat(
#             id=uuid.uuid4(),
#             article_id=article.id,
#             speaker=value["id"],
#             speaker_name=value["speaker"],
#             content=value["content"],
#             order=key
#           )
#         )

#     return news_chats