from aip import AipSpeech
import json
import win32com.client
import urllib.request
import pyaudio
import threading
import wave
from pynput import keyboard
import time

# 初始化语音
speaker = win32com.client.Dispatch('SAPI.SpVoice')

# 百度API只接受.wav等文件类型，因此先将说的内容录音
class Recorder():
    def __init__(self, chunk=1024, channels=1, rate=16000):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._running = True
        self._frames = []

    def start(self):
        threading._start_new_thread(self.__recording, ())

    def __recording(self):
        self._running = True
        # self._frames = []
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        while (self._running):
            data = stream.read(self.CHUNK)
            self._frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self._running = False
        time.sleep(0.1)
        # sleep是为了保证def stop结束前录音线程也结束

    def save(self, filename):

        p = pyaudio.PyAudio()
        if not filename.endswith('.wav'):
            filename = filename + '.wav'
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        self._frames.clear()


# 按下按键后的响应
def on_press(key):
    try:
        if key.char == 't':
            if not len(rec._frames) == 0:
                print('\nThe record has been going on, please check your command!')
            else:
                rec.start()
                print('\nRecording......')
        elif key.char == 'p':
            if len(rec._frames) == 0:
                print('\nThere is no data,please check your command!')
            else:
                rec.stop()
                rec.save('voices/myvoices.wav')
                print('\nWaiting for response......')
                rep_text = listen()
                if (rep_text):
                    res_text = baidu_unit(rep_text)
                    speaker.Speak(res_text)
                else:
                    print('There is something wrong with the server, you can wait for a moment and try again.')
    except AttributeError:
        if key == keyboard.Key.esc:
            return False
        # return false 则with ... as ... 结构结束


# 音频文件转文字：采用百度的语音识别python-SDK。网址：https://ai.baidu.com/tech/speech
# 百度语音识别API配置参数
APP_ID = '16914980'
API_KEY = 'jQMrvm7Ke7Nwgs63gLtTTztE'
SECRET_KEY = 'yDEV2ssS24rB5fdYWBva7Yxlp0b6ABtQ'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
path = 'voices/myvoices.wav'


# 将语音转文本
def listen():
    # 读取录音文件
    with open(path, 'rb') as fp:
        voices = fp.read()
    try:
        # 参数dev_pid表示识别的语种
        result = client.asr(voices, 'wav', 16000, {'dev_pid': 1537, })
        result_text = result['result'][0]
        global num
        num = num + 1
        print('Round {}:'.format(num))
        print('you said:', result_text)
        return result_text
    except KeyError:
        print('KeyError')
        speaker.Speak('我没有听清楚，请再说一遍...')
        return False


# 调用百度UNIT智能对话系统,网址：https://ai.baidu.com/unit/v2?_=1564550428397#/servicesecondary/S20796/waifu/serviceskill
# API配置参数
headers = {'Content-Type': 'application/json'}
access_token = '24.9bc44bc33e8d3d253054a3ce9e01ea60.2592000.1567332982.282335-16942696'
url = 'https://aip.baidubce.com/rpc/2.0/unit/bot/chat?access_token=' + access_token


def baidu_unit(text_words):
    post_data = "{\"bot_session\":\"\",\"log_id\":\"7758521\",\"request\":{\"bernard_level\":1, " \
                "\"client_session\":\"{\\\"client_results\\\":\\\"\\\", \\\"candidate_options\\\":[]}\"," \
                "\"query\":\"" + text_words + "\",\"query_info\":{\"asr_candidates\":[],\"source\":\"KEYBOARD\"," \
                                              "\"type\":\"TEXT\"},\"updates\":\"\",\"user_id\":\"UNIT_DEV_救赎749\"}," \
                                              "\"bot_id\":\"71625\",\"version\":\"2.0\"}"

    request = urllib.request.Request(url, data=post_data.encode('utf-8'), headers=headers)
    response = urllib.request.urlopen(request)
    content = response.read().decode("utf-8")
    content = json.loads(content)
    resp = content['result']['response']['action_list'][0]['say']
    print('robot said:', resp)
    return resp


if __name__ == '__main__':
    num = 0
    rec = Recorder()
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Press \'t\' to start the record, and press \'p\' to stop.\n'
          'After that you only need to wait for the robot\'s response\n'
          'You can quit at any time by pressing esc.')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

        
