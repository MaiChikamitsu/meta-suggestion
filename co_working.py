def co_working_mode(user_input):
    """
    GPTに送信するプロンプトを作成し、それを返す関数。
    
    :param meta_suggestion: メタサジェスチョンの質問一覧
    :param user_input: ユーザーが何に悩んでいるのか
    :return: GPTに送信するプロンプト（文字列）
    """
    prompt = f"""
    ユーザーが問題に取り組んでいます。
    問題の内容は添付画像に示したとおりです。
    ユーザーは問題を解きながら以下のように悩んでいます。
    ユーザーの発言: "{user_input}"
    
    ユーザーの発言を元に、問題について考え，その問題の答えを教えてくダサい

    問題の答え：
    手がかり：

    """

    return prompt
