import os
import soundfile
import re
import argparse
from tqdm import tqdm
from multiprocessing import Pool

#https://github.com/facebookresearch/fairseq/issues/2819
#https://github.com/facebookresearch/fairseq/issues/2654

parser = argparse.ArgumentParser()
parser.add_argument('--folder', required=True)
parser.add_argument('--save_folder', required=True)
parser.add_argument('--tag', required=True)
parser.add_argument('--sr', default=16000)
parser.add_argument('--save_dict', action='store_true', default=False)
parser.add_argument('--nj', default=8)
parser.add_argument('--text_prep', action='store_true', default=False)
parser.add_argument('--wav_prep', action='store_true', default=False)
parser.add_argument('--dialect_prep',action='store_true', default=False)
parser.add_argument('--lexicon', action='store_true', default=False)
parser.add_argument('--dir_path', default='.')


def check_files():
    files = os.listdir(args.folder)
    assert 'wav.scp' in files
    assert 'text' in files
    assert args.tag in ['train', 'dev', 'test']
    
def create_save_path():
    if not os.path.exists(args.save_folder): os.makedirs(args.save_folder)

def extract_letter_and_word():
    with open(os.path.join(args.folder, 'text'), 'r') as f:
        lines = sorted(f.read().splitlines())
    words, letters = [], []
    letter_dict = {}
    for line in tqdm(lines):
        id = re.split('[ \t]', line)[0].split('_')[-1]
        text = ' '.join(re.split('[ \t]', line)[1:]).strip().split(' ')
        letter_dict['|'] = 1
        for ch in ' '.join(text):
            if ch == ' ': continue
            if ch not in letter_dict: letter_dict[ch] = 0
            letter_dict[ch] += 1
        words.append(' '.join(text).strip())
        letters.append(' '.join(list('|'.join(text)))+' |')
    print(f'num of lines found:', len(letters))
    return words, letters, letter_dict

def save_text_metatdata(data):
    words, letters, letter_dict = data
    word_save_path = os.path.join(args.save_folder, args.tag+'.wrd')
    letter_save_path = os.path.join(args.save_folder, args.tag+'.ltr')
    print(f'saving word metadata: {word_save_path}')
    print(f'saving letter metadata: {letter_save_path}')
    with open(word_save_path, 'w') as f:
        for line in words:
            f.write(line+'\n')
    with open(letter_save_path, 'w') as f:
        for line in letters:
            f.write(line+'\n')
    
    if args.save_dict:
        letter_dict_save_path = os.path.join(args.save_folder, 'dict.ltr.txt')
        with open(letter_dict_save_path, 'w') as f:
            for key in letter_dict:
                if key == ' ': continue
                f.write(f'{key} {letter_dict[key]}\n')
    
    if args.lexicon:
        lexicon_save_path = os.path.join(args.save_folder, 'lexicon.lst')
        word_dict = {}
        for line in words:
            for word in line.split(' '):
                if word not in word_dict: word_dict[word] = ' '.join(list(word))+' |'
        with open(lexicon_save_path, 'w') as f:
            if ' ' in word_dict:
                del word_dict[' ']
            for word in word_dict:
                f.write(f'{word}\t{word_dict[word]}\n')
                
def save_wav_metatdata(data):
    wavs, frames = data
    wav_save_path = os.path.join(args.save_folder, args.tag+'.tsv')
    print(f'saving wav metadata: {wav_save_path}')
    with open(wav_save_path, 'w') as f:
        f.write(args.dir_path+'\n')
        for idx in range(len(wavs)):
            f.write(f'{wavs[idx]}\t{frames[idx]}\n')


def make_manifest():
    
    with open(os.path.join(args.folder, 'wav.scp'), 'r') as f:
        lines = sorted(f.read().splitlines())
    wavs = [re.split('[ \t]', l)[-1] for l in lines]
    
    print(f'num of lines found:', len(wavs))
    with Pool(args.nj) as p:
        frames = list(tqdm(p.imap(get_frames, wavs), total=len(wavs)))
    return wavs, frames

def get_frames(path):
   frames = soundfile.info(path).frames
   return frames 

def make_dialect():
    with open(os.path.join(args.folder, 'utt2dial'), 'r') as f:
        lines = sorted(f.read().splitlines())
    utt2lang = ['{}\t{}'.format(re.split('[ \t]',l)[0].split('_',2)[-1], re.split('[ \t]', l )[1]) for l in lines]
    return utt2lang
    
def save_dialect(data):
    dialect_save_path = os.path.join(args.save_folder, "utt2dialect_{}".format(args.tag))
    print(f'saving dialect metadata: {dialect_save_path}')
    with open(dialect_save_path, 'w') as f:
        for i in data:
            f.write(f'{i}\n')
    
            
def main():
    check_files()
    create_save_path()

    if args.text_prep:
        data = extract_letter_and_word()
        save_text_metatdata(data)
    if args.wav_prep:
        data = make_manifest()
        save_wav_metatdata(data)
    if args.dialect_prep:
        data = make_dialect()
        save_dialect(data)
        
        
if __name__ == '__main__':
    args = parser.parse_args()

    main()