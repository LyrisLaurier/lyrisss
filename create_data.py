# 创建数据 读取json文件中信息并筛选错误

import json
import os
from tqdm import tqdm
from pydub import AudioSegment
from utils.reader import load_audio

# 生成数据列表
def get_data_list(infodata_path, list_path, zhvoice_path): #json文件路径 测试集/训练集路径 MP3文件路径

    with open(infodata_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()# 读取每一行，存在列表中

    f_train = open(os.path.join(list_path, 'train_list.txt'), 'w') #训练集
    f_test = open(os.path.join(list_path, 'test_list.txt'), 'w') #测试集

    sound_sum = 0
    speakers = []
    speakers_dict = {}
    for line in tqdm(lines): # 进度条的拓展包
        line = json.loads(line.replace('\n', ''))
        duration_ms = line['duration_ms']
        if duration_ms < 1300: # 只选取大于1.3秒的数据
            continue
        speaker = line['speaker']
        if speaker not in speakers:
            speakers_dict[speaker] = len(speakers)
            speakers.append(speaker)
        label = speakers_dict[speaker]
        sound_path = os.path.join(zhvoice_path, line['index'])
        save_path = "%s.wav" % sound_path[:-4]
        if not os.path.exists(save_path):
            try:
                wav = AudioSegment.from_mp3(sound_path)
                wav.export(save_path, format="wav")
                os.remove(sound_path)
            except Exception as e:
                print('数据出错：%s, 信息：%s' % (sound_path, e))
                continue
        if sound_sum % 200 == 0:
            f_test.write('%s\t%d\n' % (save_path.replace('\\', '/'), label))
        else:
            f_train.write('%s\t%d\n' % (save_path.replace('\\', '/'), label))
        sound_sum += 1

    f_test.close()
    f_train.close()

# 删除错误音频
def remove_error_audio(data_list_path):
    with open(data_list_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines1 = []
    for line in tqdm(lines):
        audio_path, _ = line.split('\t')
        try:
            spec_mag = load_audio(audio_path)
            lines1.append(line)
        except Exception as e:
            print(audio_path)
            print(e)
    with open(data_list_path, 'w', encoding='utf-8') as f:
        for line in lines1:
            f.write(line)

if __name__ == '__main__':
    get_data_list('dataset/zhvoice/text/infodata.json', 'dataset', 'dataset/zhvoice') #json文件路径 测试集/训练集路径 MP3文件路径
    remove_error_audio('dataset/train_list.txt') #train_list.txt path
    remove_error_audio('dataset/test_list.txt') #test_list.txt path
