import random

def no_bridging_teaching_mode(meta_suggestion):
    # ランダムにリストから一つの質問を選ぶ
    random_question = random.choice(meta_suggestion).strip()  # strip()で余分なスペースや改行を削除
    return random_question