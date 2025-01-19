def answer_func(conversation):
    """
    GPTに送信するプロンプトを作成し、それを返す関数。
    
    :param history: 過去の対話履歴
    """
    prompt_answer = f"""
    ユーザーが問題に取り組んでいます。
    問題の内容は添付画像に示したとおりです。
    また，今までの，ユーザの発言と，それに対するあなたの返答の履歴は，以下のようになっています．
    ユーザの発言(user)とそれに対するあなたメタサジェスチョンの答え(gpt): "{conversation}"
    この対話の流れをヒントにし，この問題を解いてください．

    """

    return prompt_answer
