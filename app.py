import os
import threading
import time
from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from faster_whisper import WhisperModel
from dotenv import load_dotenv
from openai import OpenAI
from google.protobuf.json_format import MessageToDict
import json
import socket
import time
import speech_recognition as sr
from gtts import gTTS
import ast
import threading

#コード
from prompt.mode.bridging_teaching import bridging_teaching_mode  # 橋渡教示ありモードの関数をインポート
from prompt.mode.bridging_teaching_2 import bridging_teaching_mode_2
from prompt.mode.no_bridging_teaching import no_bridging_teaching_mode  # 橋渡教示なしモードの関数をインポート
from prompt.mode.co_working import co_working_mode  # 自由共同モードの関数をインポート
from prompt.mode.bridging_teaching_3 import bridging_teaching_mode_3

from prompt.answer.answer import answer_func
from prompt.answer.answer_step import answer_step_func
from prompt.answer.answer_step_half import answer_step_half_func

from prompt.advice.advice import advice_func

from func.speaker import text_to_speech, InterruptHandler, speech_to_text, play_audio_complete_event

from func.pre_metasuggestion import save_image_to_s3, load_task_and_questions, load_task_and_questions_2, encode_image, load_task_and_questions_c1, load_task_and_questions_c2, load_task_and_questions_c3,load_task_and_questions_c4

from prompt.comprehension.comprehension_level_step import comprehension_level_step_func
from prompt.comprehension.comprehension_level_step_half import comprehension_level_step_half_func
from prompt.comprehension.comprehension_level_no_answer import comprehension_level_no_answer_func
from prompt.comprehension.comprehension_level import comprehension_level_func

from prompt.comprehension.comprehension_problem import comprehension_problem_func

from prompt.concreteness.concreteness import concreteness_func

from prompt.confidence.confidence import confidence_func

#OpenAPI
load_dotenv()
client = OpenAI(api_key=os.environ.get('OPENAI_API'))

# UDPソケットの作成
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# sotaくん
IP = "192.168.1.128"
PORT = 9980
serv_address = (IP, PORT)
default_posture = {"Waist_Y": 0, "RShoulder_P": -900, "RElbow_P": 0, "LShoulder_P": 900, "LElbow_P": 0, "Head_Y": 0, "Head_P": 0, "Head_R": 0}
pos = default_posture.copy()
message = json.dumps(pos)
sock.sendto(message.encode("utf-8"), serv_address)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["JSON_AS_ASCII"] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/speech_to_text', methods=['POST'])
def handle_speech_to_text():
    types = request.form.get('types')  # モードを取得
    mode = request.form.get('mode')  # モードを取得
    meta = request.form.get('meta') # メタサジェスチョンを取得
    quiz = request.form.get('quiz') #クイズを取得

    session['types'] = types
    session['mode'] = mode
    session['meta'] = meta
    session['quiz'] = quiz

    print(f"実験モード: {types}")
    print(f"Selected mode: {mode}")
    print(f"メタサジェスチョン： {meta}")

    start_time = time.time()

    # 会話履歴をセッションに保存
    if 'history' not in session:
        session['history'] = []
        session['user_input_history'] = []
        session['conversation'] = []
        session['answer_data'] = []

        session['comprehension_problem'] = []
        session['confidence_response'] = []
        session['comprehension_level'] = []
        session['concreteness_problem'] = []

    history = session['history']
    user_input_history = session['user_input_history']
    conversation = session['conversation']
    answer_data = session['answer_data']
    previous_comprehension_level = session.get('previous_comprehension_level', None)

    try:
        print("音声認識中...（終了するには Ctrl+C を押してください）")
        if types == 'observation':
            user_input = input("標準入力からデータを入力してください: ")
        else:
            print("音声認識を開始します...") # スピーカーから音声認識
            user_input = speech_to_text()
        print("user_input:",user_input)
        elapsed_time = time.time() - start_time  # ⭐︎⭐︎ ここで経過時間を計測

        quiz_images = {
            'quiz1': 'question.png',
            'quiz2': 'question_quiz_qnock1.png',
            'quiz3': 'question_quiz_qnock2.png',
            'quiz4': 'question_1.png',
            'quiz5': 'question_2.png',
            'quiz6': 'question_3.png',
        }
        if quiz in quiz_images:
            image_data = quiz_images[quiz]
        print('image_data:',image_data)

        if meta == 'meta_all':
            meta_suggestion = load_task_and_questions()
        elif meta == 'meta_genre':
            meta_suggestion = load_task_and_questions_2()

        # 橋渡し教示あり_1(ステップを考えさせる，答えを知った上での理解度)
        if mode == 'bridging_teaching_1':
            print("このモードでは，ステップも答えも考えます")
            base64_image = encode_image(image_data)

            #答えを推測させるプロンプト
            answer_prompt = answer_step_func(history) 
            print("answer_prompt:" ,answer_prompt)
            answers = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": answer_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            answer = answers.choices[0].message.content
            print('my answer =',answer)
            answer_data.append({"answer": answer})

            #理解度を推定させるプロンプト
            comprehension_level_prompt = comprehension_level_step_func(user_input,answer)
            print('comprehension_level_prompt=',comprehension_level_prompt)

            comprehension_level_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": comprehension_level_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            print('comprehension_level_response=',comprehension_level_response)

            comprehension_level_pre = comprehension_level_response.choices[0].message.content
            print('comprehension_level_pre=',comprehension_level_pre)

            comprehension_level_list = ast.literal_eval(comprehension_level_pre)
            comprehension_level = sum(comprehension_level_list)
            print('comprehension_level=',comprehension_level)

            if previous_comprehension_level is None:
                change_in_understanding = float(comprehension_level) /elapsed_time 
            else:
                change_in_understanding = (float(comprehension_level) - float(previous_comprehension_level))/elapsed_time 
            session['previous_comprehension_level'] = comprehension_level

            #メタサジェスチョン生成プロンプト
            prompt = bridging_teaching_mode(meta_suggestion, user_input, conversation, comprehension_level, change_in_understanding)
            print('prompt=',prompt)
            response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            result = response.choices[0].message.content
            print('result=', result)

        # 橋渡し教示あり_2(問題の答えを考えさせないパターン)
        elif mode == 'bridging_teaching_2':
            print("このモードでは，答えは考えません")
            base64_image = encode_image(image_data)

            #理解度を推定させるプロンプト
            comprehension_level_prompt = comprehension_level_no_answer_func(user_input)
            print('comprehension_level_prompt=',comprehension_level_prompt)
            comprehension_level_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": comprehension_level_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            comprehension_level = comprehension_level_response.choices[0].message.content
            print('comprehension_level=',comprehension_level)
            print('comprehension_level_response=',comprehension_level_response)

            if previous_comprehension_level is None:
                change_in_understanding = float(comprehension_level) /elapsed_time 
            else:
                change_in_understanding = (float(comprehension_level) - float(previous_comprehension_level))/elapsed_time 
            session['previous_comprehension_level'] = comprehension_level

            #メタサジェスチョン生成プロンプト
            prompt = bridging_teaching_mode(meta_suggestion, user_input, conversation, comprehension_level, change_in_understanding)
            print('prompt=',prompt)
            response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            result = response.choices[0].message.content
        
        # 橋渡し教示あり_3(答えは考えさせるが，ステップを分けて考えさせない場合)
        elif mode == 'bridging_teaching_3':
            print("このモードでは，答えは考えますが，ステップを分けて考えません")
            base64_image = encode_image(image_data)

            #答えを推測させるプロンプト
            answer_prompt = answer_func(history) 
            print("answer_prompt:" ,answer_prompt)
            answers = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": answer_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            answer = answers.choices[0].message.content
            answer_data.append({"answer": answer})
            print('my answer =',answer)

            #理解度を推定させるプロンプト
            comprehension_level_prompt = comprehension_level_func(user_input,answer)
            print('comprehension_level_prompt=',comprehension_level_prompt)
            comprehension_level_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": comprehension_level_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            comprehension_level = comprehension_level_response.choices[0].message.content
            print('comprehension_level=',comprehension_level)
            print('comprehension_level_response=',comprehension_level_response)

            if previous_comprehension_level is None:
                change_in_understanding = float(comprehension_level) /elapsed_time 
            else:
                change_in_understanding = (float(comprehension_level) - float(previous_comprehension_level))/elapsed_time 
            session['previous_comprehension_level'] = comprehension_level

            #メタサジェスチョン生成プロンプト
            prompt = bridging_teaching_mode(meta_suggestion, user_input, conversation, comprehension_level, change_in_understanding)
            print('prompt=',prompt)
            response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            result = response.choices[0].message.content

        # 橋渡し教示あり_4(ステップを自分で考えさせる，答えを知った上での理解度)
        elif mode == 'bridging_teaching_4':
            print("このモードでは，ステップも答えも考えます")
            base64_image = encode_image(image_data)

            #答えを推測させるプロンプト
            answer_prompt = answer_step_half_func(history) 
            print("answer_prompt:" ,answer_prompt)
            answers = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": answer_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            answer = answers.choices[0].message.content
            answer_data.append({"answer": answer})
            print('my answer =',answer)

           #理解度を推定させるプロンプト
            comprehension_level_prompt = comprehension_level_step_half_func(user_input,answer)
            print('comprehension_level_prompt=',comprehension_level_prompt)
            comprehension_level_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": comprehension_level_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            comprehension_level = comprehension_level_response.choices[0].message.content
            print('comprehension_level=',comprehension_level)
            print('comprehension_level_response=',comprehension_level_response)

            if previous_comprehension_level is None:
                change_in_understanding = float(comprehension_level) /elapsed_time 
            else:
                change_in_understanding = (float(comprehension_level) - float(previous_comprehension_level))/elapsed_time 
            session['previous_comprehension_level'] = comprehension_level

            #メタサジェスチョン生成プロンプト
            prompt = bridging_teaching_mode(meta_suggestion, user_input, conversation, comprehension_level, change_in_understanding)
            print('prompt=',prompt)
            response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            result = response.choices[0].message.content
            print('result=', result)

        # 橋渡し教示あり_5(問題の理解度，確信度，進捗度，プラン具体性)
        elif mode == 'bridging_teaching_5':
            print("問題の理解度，確信度，進捗度，プラン具体性")
            base64_image = encode_image(image_data)
            user_input_history.append(user_input)

            #答えを推測させるプロンプト
            answer_prompt = answer_step_half_func(conversation,user_input) 
            print("answer_prompt:" ,answer_prompt)
            answers = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": answer_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            answer = answers.choices[0].message.content
            answer_data.append({"answer": answer})
            print('my answer =',answer)

           #問題文の理解度を推定させるプロンプト
            comprehension_problem_prompt = comprehension_problem_func(user_input_history,answer)
            print('comprehension_problem_prompt=',comprehension_problem_prompt)
            comprehension_problem_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": comprehension_problem_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            comprehension_problem = comprehension_problem_response.choices[0].message.content
            print('comprehension_problem=',comprehension_problem)
            #print('comprehension_problem_response=',comprehension_problem_response)
            session['comprehension_problem'] = comprehension_problem

            #確信度を推定させるプロンプト
            confidence_prompt = confidence_func(user_input_history,answer)
            print('confidence_prompt=',confidence_prompt)
            confidence_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": confidence_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            confidence_prompt = confidence_response.choices[0].message.content
            print('confidence_prompt=',confidence_prompt)
            #print('confidence_response=',confidence_response)
            session['confidence_prompt'] = confidence_prompt


            #理解度を推定させるプロンプト
            comprehension_level_prompt = comprehension_level_step_half_func(user_input_history,answer)
            print('comprehension_level_prompt=',comprehension_level_prompt)
            comprehension_level_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": comprehension_level_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            comprehension_level = comprehension_level_response.choices[0].message.content
            print('comprehension_level=',comprehension_level)
            #print('comprehension_level_response=',comprehension_level_response)
            session['comprehension_level'] = comprehension_level


            #プランの具体性を推定させるプロンプト
            concreteness_prompt = concreteness_func(user_input_history,answer)
            print('concreteness_prompt=',concreteness_prompt)
            concreteness_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": concreteness_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            concreteness_problem = concreteness_response.choices[0].message.content
            print('concreteness_problem=',concreteness_problem)
            #print('concreteness_problem_response=',concreteness_response)
            session['concreteness_problem'] = concreteness_problem

            #ユーザが答えに辿り着くまでに何が必要か考えるプロンプト
            advice_prompt = advice_func(user_input_history,answer,user_input)
            print('advice_prompt=',advice_prompt)
            advice_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": advice_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            advice_problem = advice_response.choices[0].message.content
            print('advice_problem=',advice_problem)
            session['advice_problem'] = advice_problem

            # if float(comprehension_problem) < 3.0:
            #     meta_suggestion = load_task_and_questions_c1()
            # else:
            #     minimum_value = min(float(confidence_prompt), float(comprehension_level), float(concreteness_problem))
            #     if float(confidence_prompt) == minimum_value:
            #         meta_suggestion = load_task_and_questions_c2()
            #     elif float(comprehension_level) == minimum_value:
            #         meta_suggestion = load_task_and_questions_c3()
            #     elif float(concreteness_problem) == minimum_value:
            #         meta_suggestion = load_task_and_questions_c4()



            #メタサジェスチョン生成プロンプト
            prompt = bridging_teaching_mode_2(meta_suggestion, user_input, conversation, comprehension_problem, comprehension_level, concreteness_problem, confidence_prompt, advice_problem)
            print('prompt=',prompt)
            response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            result = response.choices[0].message.content
            print('result=', result)

        # 橋渡し教示あり_6(問題の理解度，確信度，進捗度，プラン具体性，答えを教える)
        elif mode == 'bridging_teaching_6':
            print("問題の理解度，確信度，進捗度，プラン具体性")
            base64_image = encode_image(image_data)
            user_input_history.append(user_input)

            #答えを推測させるプロンプト
            if quiz == 'quiz1':
                answer == ''
            elif quiz == 'quiz2':
                answer == ''
            elif quiz == 'quiz3':
                answer == ''
            elif quiz == 'quiz4':
                answer = '''
                答え:答える箇所の上段の数字21と36の数字2,1,3,6を足し合わせた数字
                2+1+3+6=12

                考え方のステップ：
                - 初めに、「右の数字から左の数字を引いたら次の下の段の数字になるのではないか」と仮説を立てた。
                - 仮説をすべての段に適用してみる。
                - 一部の段ではこの仮説が成立するが、一番最後の段で成立しないことに気づく。
                - 最後の段で仮説が成立しないため、新たな規則を探す。
                - 上段の2つの数字をそれぞれ一の位と十の位に分解してみる。
                - それらの数字（4つ）を足し合わせると、次の段の下の数字と一致することに気づく。
                - 見つけた規則をすべての段に適用し、成立することを確認する。
                - 正しい規則は、「上段の数字を一の位と十の位に分解し、それらをすべて足し合わせた数字が次の段の下の数字になる」である。'''

            elif quiz == 'quiz5':
                answer = '''
                答え：それぞれの三角形の上段の二つの数字を掛け合わせ、下の数字で割った数字が、左右の三角形で同じになる。
                そのため、2✖️4÷8=1✖️7÷7になることから、答えは7である。

                考え方のステップ：
                - 初めに、それぞれの三角形の規則を観察した。
                - 上段の二つの数字を何らかの演算で下段の数字と関係づける規則を考えた。
                - 「上段の二つの数字を掛け合わせ、下段の数字で割る」という操作を試した。
                - 左右の三角形で、この操作を適用した結果が一致することに気づいた。
                - すべての三角形にこの規則を適用し、問題が成立することを確認した。
                - 答えは、「2✖️4÷8」と「1✖️7÷7」の計算結果が一致することから、答えは7であると導いた。'''

            elif quiz == 'quiz6':
                answer = '''
                答え：縦に見た時に,それぞれの数字を足し合わせると,左から3~9に1ずつ大きくなっていく.真ん中の列は6なので,答えは6-1-3-1=1である．
                考え方のステップ：
                - はじめに，縦の列で考えることに気づく
                - 縦の列の数字を足し算してみる
                - 左から1つずつ大きくなることに気づく
                - 規則性がわかったら，答えを計算する'''


           #問題文の理解度を推定させるプロンプト
            comprehension_problem_prompt = comprehension_problem_func(user_input_history,answer)
            print('comprehension_problem_prompt=',comprehension_problem_prompt)
            comprehension_problem_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": comprehension_problem_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            comprehension_problem = comprehension_problem_response.choices[0].message.content
            print('comprehension_problem=',comprehension_problem)
            #print('comprehension_problem_response=',comprehension_problem_response)
            session['comprehension_problem'] = comprehension_problem

            #確信度を推定させるプロンプト
            confidence_prompt = confidence_func(user_input_history,answer)
            print('confidence_prompt=',confidence_prompt)
            confidence_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": confidence_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            confidence_prompt = confidence_response.choices[0].message.content
            print('confidence_prompt=',confidence_prompt)
            #print('confidence_response=',confidence_response)
            session['confidence_prompt'] = confidence_prompt

            #理解度を推定させるプロンプト
            comprehension_level_prompt = comprehension_level_step_half_func(user_input_history,answer)
            print('comprehension_level_prompt=',comprehension_level_prompt)
            comprehension_level_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": comprehension_level_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            comprehension_level = comprehension_level_response.choices[0].message.content
            print('comprehension_level=',comprehension_level)
            #print('comprehension_level_response=',comprehension_level_response)
            session['comprehension_level'] = comprehension_level


            #プランの具体性を推定させるプロンプト
            concreteness_prompt = concreteness_func(user_input_history,answer)
            print('concreteness_prompt=',concreteness_prompt)
            concreteness_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": concreteness_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            concreteness_problem = concreteness_response.choices[0].message.content
            print('concreteness_problem=',concreteness_problem)
            #print('concreteness_problem_response=',concreteness_response)
            session['concreteness_problem'] = concreteness_problem

            # if float(comprehension_problem) < 3.0:
            #     meta_suggestion = load_task_and_questions_c1()
            # else:
            #     minimum_value = min(float(confidence_prompt), float(comprehension_level), float(concreteness_problem))
            #     if float(confidence_prompt) == minimum_value:
            #         meta_suggestion = load_task_and_questions_c2()
            #     elif float(comprehension_level) == minimum_value:
            #         meta_suggestion = load_task_and_questions_c3()
            #     elif float(concreteness_problem) == minimum_value:
            #         meta_suggestion = load_task_and_questions_c4()

            #ユーザが答えに辿り着くまでに何が必要か考えるプロンプト
            advice_prompt = advice_func(user_input_history,answer,user_input)
            print('advice_prompt=',advice_prompt)
            advice_response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": advice_prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            advice_problem = advice_response.choices[0].message.content
            print('advice_problem=',advice_problem)
            session['advice_problem'] = advice_problem

            #メタサジェスチョン生成プロンプト
            prompt = bridging_teaching_mode_3(meta_suggestion, user_input, conversation, comprehension_problem, comprehension_level, concreteness_problem, confidence_prompt, advice_problem, answer)
            print('prompt=',prompt)
            response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            result = response.choices[0].message.content
            print('result=', result)

        # 橋渡し教示なし
        elif mode == 'no_bridging_teaching':
            time.sleep(9)
            result = no_bridging_teaching_mode(meta_suggestion)
            change_in_understanding = 0
            comprehension_problem = 0
            comprehension_level = 0
            confidence_prompt = 0
            concreteness_problem = 0


        # 自由協働，一旦無視
        elif mode == 'co_working':
            meta_suggestion, image_data = load_task_and_questions()  # 画像データを読み取る
            image_url = save_image_to_s3(image_data)  # 画像をS3にアップロード
            prompt = co_working_mode(user_input)
            response = client.chat.completions.create(model="gpt-4o",messages=[{"role": "user","content": [{"type": "text","text": prompt},{"type": "image_url","image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}])
            result = response.choices[0].message.content

        else:
            print("おかしいよね")
            return "Invalid mode selected !!!!!", 400
        
        event = threading.Event()

        def sota_motion():
            motion_sequence = [{"Waist_Y": 0, "RShoulder_P": -900, "RElbow_P": 0, "LShoulder_P": 900, "LElbow_P": 0, "Head_Y": 600, "Head_P": -100, "Head_R": 0}]
            for position in motion_sequence:
                pos = default_posture.copy()  # 初期姿勢をコピー
                pos.update(position)          # 動作の位置を更新
                message = json.dumps(pos)     # JSONに変換
                sock.sendto(message.encode("utf-8"), serv_address)  # サーバーに送信
            event.set()  # 動作完了を通知

        

        # Sotaの動作を別スレッドで実行
        motion_thread = threading.Thread(target=sota_motion)
        motion_thread.start()

        # 動作完了を待つ
        event.wait()
        
        # # sotaくん
        # event = threading.Event()
        # def on_complete():
        #     event.set()  # 再生完了イベントを設定
        # motion_sequence = [{"Waist_Y": 0, "RShoulder_P": -900, "RElbow_P": 0, "LShoulder_P": 900, "LElbow_P": 0, "Head_Y": 600, "Head_P": -100, "Head_R": 0},]
        # for position in motion_sequence:
        #     pos = default_posture.copy()  # 初期姿勢をコピー
        #     pos.update(position)          # 動作の位置を更新
        #     message = json.dumps(pos)     # JSONに変換
        #     sock.sendto(message.encode("utf-8"), serv_address)  # サーバーに送信
        # event.wait()  # 再生完了を待つ
        # #time.sleep(2)
        
        speak = f"{user_input}、というふうに考えているのですね。"
        play_audio_complete_event(speak) # 再生終了を待つ
        play_audio_complete_event(result)  # 再生終了を待つ
        pos = default_posture.copy()
        message = json.dumps(pos)
        sock.sendto(message.encode("utf-8"), serv_address)

        # history(全ての履歴)の更新
        history.append({"elapsed_time":elapsed_time, "gpt": result, "user": user_input, "comprehension_problem":comprehension_problem, "confidence_prompt":confidence_prompt, "comprehension_level":comprehension_level, "concreteness_problem":concreteness_problem})
        session['history'] = history
        session['user_input_history'] = user_input_history
        print("history is ",history)
        print("user_input_history is ",user_input_history)

        # conversation(会話履歴)の更新
        conversation.append({"gpt": result,"user": user_input})
        session['conversation'] = conversation
        print("conversation is ",conversation)

        print("result is ",result)
        return render_template('result.html', history=session['history'], mode=session['mode'], quiz=session['quiz'], types=session['types'], meta=session['meta'])
        # response_data = {"history": session['history'], "result": result}
        # return jsonify(response_data)
    
    except KeyboardInterrupt:
        print("\nプログラムを終了します。")

@app.route('/result')
def result():
    return render_template('result.html', result=session.get('result', ''),
        history=session.get('history', []),
        mode=session.get('mode', '')
    )

@app.route('/reset', methods=['POST'])
def reset():
    session.pop('history', None)
    session.pop('mode', None)  # モードもリセット
    return redirect('/')

@app.route('/back', methods=['POST'])
def back():
    # 履歴が存在する場合、最後のエントリを削除
    if 'history' in session and session['history']:
        session['history'].pop()  # 最後のエントリを削除
        session.modified = True
        print("Updated conversation history after back:", session['history'])  # デバッグ出力
    return redirect(url_for('result'))


if __name__ == '__main__':
    app.run(debug=True)
