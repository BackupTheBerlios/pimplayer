import os.path

file_valid=os.path.abspath("data/audio/test.ogg")
file_random=os.path.abspath("data/audio/random_data.ogg")

file_not_exist=os.path.abspath("data/audio/notexist")

audio_files=[file_valid,file_random,file_not_exist,None]


playlist=[str(i) for i in range(1,20)]



