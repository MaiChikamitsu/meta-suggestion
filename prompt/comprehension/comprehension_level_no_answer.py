def comprehension_level_no_answer_func(user_input):
    comprehension = f"""
    ユーザーが問題に取り組んでいます。
    問題の内容は添付画像に示したとおりです。
    ユーザーの発言から，ユーザーが問題をどれくら理解しているのかを推定して下さい
    ユーザーの発言: "{user_input}"
    目安として，理解度の指標は以下を参考とします．

    理解度1:全く見当違いである
    理解度10:正解している
    
    出力:0~10の数字のみ
    """

    return comprehension
