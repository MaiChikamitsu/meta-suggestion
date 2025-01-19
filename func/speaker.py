import os
import speech_recognition as sr
from gtts import gTTS
import threading

#テキスト→音声
def text_to_speech(text, language="ja", filename="output", on_complete=None):
    text2speech = gTTS(text, lang=language)
    text2speech.save(filename + ".mp3")
    os.system(f"afplay {filename}.mp3")  # macOSの場合
    print("Sota:"+text)

    # 再生完了後にコールバックを実行
    if on_complete is not None:
        on_complete()

#音声→テキスト
def speech_to_text():
    # 音声認識器を初期化
    r = sr.Recognizer()
    r.pause_threshold = 1.5
    with sr.Microphone() as source:
        print("何かを話してください...")
        audio = r.listen(source)
    # 音声をテキストに変換
    try:
        text = r.recognize_google(audio, language="ja-JP")  # 日本語の音声認識
        print("認識結果: " ,text)
        return text
    except sr.UnknownValueError:
        print("音声を認識できませんでした。")
        #バリエーション増やす？？
        # text_to_speech('うーん')
        return speech_to_text()
    except sr.RequestError as e:
        print(f"音声認識エラー: {e}")
        return speech_to_text()
    
def play_audio_complete_event(text):
        event = threading.Event()

        def on_complete():
            event.set()  # 再生完了イベントを設定

        text_to_speech(text, on_complete=on_complete)
        event.wait()  # 再生完了を待つ

#使わない，音声→テキスト
class InterruptHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listener_thread = threading.Thread(target=self._listen_in_background)
        self.listener_thread.daemon = True
        self.callback = None  # 割り込み時に呼び出す関数を設定
        self.running = False

    def start_listening(self, callback):
        """バックグラウンドで音声認識を開始"""
        self.callback = callback
        self.running = True
        self.listener_thread.start()

    def _listen_in_background(self):
        """音声をバックグラウンドでリスニングし続ける"""
        with self.microphone as source:
            print("Listening for audio...")
            self.recognizer.adjust_for_ambient_noise(source)  # ノイズを調整
            while self.running:
                try:
                    print("Waiting for speech...")
                    # 音声入力を待機し、聞き取る
                    audio = self.recognizer.listen(source, timeout=None)
                    
                    # 音声をテキストに変換
                    text = self.recognizer.recognize_google(audio, language="ja-JP")
                    print(f"Detected speech: {text}")
                    
                    # 音声入力が終わった後にコールバックを実行
                    if self.callback:
                        self.callback(text)

                except sr.UnknownValueError:
                    print("音声を認識できませんでした。")
                except sr.RequestError as e:
                    print(f"APIへのリクエストエラー: {e}")
                except Exception as e:
                    print(f"音声認識エラー: {e}")

    def stop_listening(self):
        """音声認識を停止"""
        self.running = False
