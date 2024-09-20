import os
import re
import openai
from database import get_markdown_by_id

# OpenAI APIキーの設定（環境変数から取得）
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_application_form(user_input):
    # プロンプト作成
    prompt = f"""ユーザーから以下のリクエストがありました：「{user_input}」。このリクエストに関係のある申請書は次の中からどれですか？

1. 水稲栽培における中干し期間の延長
2. 太陽光発電設備の導入
3. バイオ炭の農地施用

回答は番号でお願いします。
"""
    try:
        # ChatCompletionを使用
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # または"gpt-4"を使用可能
            messages=[
                {"role": "system", "content": "あなたは申請書を特定するアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )
        # レスポンスから回答を取得
        answer = response.choices[0].message.content
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
    except Exception as e:
        return f"エラーが発生しました: {e}"