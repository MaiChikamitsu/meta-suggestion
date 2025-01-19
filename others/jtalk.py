import subprocess
import os  # ファイル確認用

def jtalk(text):
    # open_jtalk の実行コマンドを設定
    open_jtalk = [
        'open_jtalk',
        '-x', '/opt/homebrew/opt/open-jtalk/dic',  # 修正済み辞書のパス
        '-m', '/opt/homebrew/opt/open-jtalk/voice/mei/mei_normal.htsvoice',  # 修正済み音声ファイルのパス
        '-r', '1.5',  # 音声スピード
        '-ow', 'sample_jtalk.wav'  # 出力ファイル名
    ]

    # open_jtalk にテキストを渡して実行
    subprocess.run(open_jtalk, input=text.encode())

    # ファイルが生成されているかを確認してから再生
    if os.path.exists('sample_jtalk.wav'):
        print("音声ファイルが生成されました: sample_jtalk.wav")
        aplay = ['afplay', 'sample_jtalk.wav']
        subprocess.run(aplay)
    else:
        print("エラー: 音声ファイルが生成されませんでした")
