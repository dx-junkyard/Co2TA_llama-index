import os
import re
from openai import AzureOpenAI
import sqlite3
from database import get_markdown_by_id

client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_KEY"),  
  api_version = "2023-03-15-preview",
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
)

def get_available_forms():
    """
    データベースから利用可能な申請書のリストを取得します。
    """
    conn = sqlite3.connect('application_forms.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM forms")
    forms = cursor.fetchall()
    conn.close()
    return forms

def get_application_form(user_input):

    # データベースから選択肢を取得
    forms = get_available_forms()
    
    if not forms:
        return "現在利用可能な申請書がありません。"

    # プロンプト用に選択肢をフォーマット
    options = "\n\n".join([f"{form[0]}. {form[1]}" for form in forms])

    # プロンプト作成
    prompt = f"""ユーザーから以下のリクエストがありました：「{user_input}」。このリクエストに関係のある申請書は次の中からどれですか？

{options}

回答は番号でお願いします。
"""
    # ChatCompletionを使用
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは申請書を特定するアシスタントです。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10,
        temperature=0
    )
    # レスポンスから回答を取得
    answer = response.choices[0].message.content
    print(answer)
    match = re.search(r'\d+', answer)  # 最初に出現する数字を探す
    if match:
        answer = match.group()  # 数字部分を取得
    else:
        return "数字が見つかりませんでした。"

    # データベースからMarkdownを取得
    markdown_content = get_markdown_by_id(answer)

    if markdown_content:
        return markdown_content  # Markdownの内容を返す
    else:
        return "該当する申請書が見つかりませんでした。"