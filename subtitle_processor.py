#!/usr/bin/env python
# coding=utf-8

from sys import exit


#def convert_mp4_to_wma(mp4_path):
#    '''This function converts an mp4 file into audio wma file
#    using ffmpeg'''
#
#    import pathlib
#
#    wav_path = mp4_path.replace('.mp4', '.wav')
#
#    if pathlib.Path(wav_path).is_file():
#        return wav_path
#
#
#    import subprocess
#
#    command = "ffmpeg -i " + mp4_path + " -ab 160k -ac 2 -ar 44100 -vn " + wav_path
#    subprocess.call(command, shell=True)
#
#    return wav_path

#def force_alignment(audio_path, txt_path, srt_path):
#    '''This function do the forced alignment job
#    and create an srt file for video'''
#
#    from aeneas.executetask import ExecuteTask
#    from aeneas.task import Task
#
#    # create Task object
#    config_string = u"task_language=eng|is_text_type=plain|os_task_file_format=srt"
#    task = Task(config_string=config_string)
#    task.audio_file_path_absolute = audio_path
#    task.text_file_path_absolute = txt_path
#    task.sync_map_file_path_absolute = srt_path
#    # process Task
#    ExecuteTask(task).execute()
#
#    # output sync map to file
#    task.output_sync_map_file()


def convert_timestamp(time_in_seconds):
    seconds = float(time_in_seconds)
    hour_part = int(seconds/3600)
    minute_part = int((seconds - hour_part*3600)/60)
    second_part = int(seconds - hour_part*3600 - minute_part*60)

    float_part = seconds - hour_part*3600 - minute_part*60 - second_part

    float_part = round(float_part, 3)

    

    convert_time = str(hour_part).zfill(2) + ':' + \
                   str(minute_part).zfill(2) + ':' + \
                   str(second_part).zfill(2) + ',' + \
                   str(float_part).replace('0.','')
                   #'(' + str(time_in_seconds) + ')'
    return convert_time



def create_srt_from_gentle_alignment(txt_path, csv_path):
    """After getting the align file from https://lowerquality.com/gentle/
    pass nessesary things in to this function to create srt file for the video"""

    import re


    # read the txt file and convert to a list of strings
    with open(txt_path, 'r') as file_object:
        txt = file_object.read()
        txt = re.sub(r'\n+','\n',txt) # remove double linefeed
        txt = re.sub(r'^\n','',txt) # remove linefeed at the beginning
        txt = re.sub(r'\n$','',txt) # remove linefeed at the end

        txt_lines = txt.split('\n')

    # read the cvs file and convert to a list of word level timestamps
    with open(csv_path, 'r') as file_object:
        cvs = file_object.read()
        word_timestamps = cvs.split('\n')

    # concatenate word by word to make a sentence that matches the subtitle line
    concatenated_string = ''
    for word_timestamp in word_timestamps:
        # split word_timestamp line into a list which has word and times
        word_timestamp_parts = word_timestamp.split(',')
        # concatenate
        concatenated_string = concatenated_string  + ' ' + word_timestamp_parts[0]
        # trim spaces to make a clean string
        concatenated_string = concatenated_string.strip()


    line_count = 0
    subtitles = []
    for line in txt_lines:
        line_count += 1
        original_line = line

        # standardize string for word searching
        line = re.sub(r'[,-\.\?\!]', ' ', line) # replace special chars by space
        line = re.sub(r' +', ' ', line) # remove multi spaces
        line = line.strip() # trim spaces

        # check if all sentences match
        if line in concatenated_string:
            #print(line, '   : True')
            pass
        else:
            print(line, '   : False')
            print('>>> check false line!!!')
            return None


        # finding the begin time
        # concatenate word by word to make a sentence that matches the subtitle line
        check_line = line
        accumulated_string = ''
        for word_count in range(0, len(word_timestamps)):
            
            # split word_timestamp line into a list which has word and times
            word_timestamp_parts = word_timestamps[word_count].split(',')

            # check if the concatenated_string starts with the check line
            if concatenated_string.startswith(check_line):
                begin_time = convert_timestamp(word_timestamp_parts[2])
                break

            

            accumulated_string = accumulated_string + ' ' + word_timestamp_parts[0]
            accumulated_string = accumulated_string.strip()
            check_line = accumulated_string + ' ' + line


        # finding the begin time
        accumulated_string = ''
        for word_count_continue in range(word_count, len(word_timestamps)):
            # split word_timestamp line into a list which has word and times
            word_timestamp_parts = word_timestamps[word_count_continue].split(',')

            accumulated_string = accumulated_string  + ' ' + word_timestamp_parts[0]
            accumulated_string = accumulated_string.strip()


            if accumulated_string == line:
                end_time = convert_timestamp(word_timestamp_parts[3])
                break

        subtitles.append([line_count, original_line, begin_time, end_time])

    # rearrnage time by using the begin time of the next sentence for the end time of previous
    for i in range(0,len(subtitles)):
        subtitles[i][0] = subtitles[i][0]
        subtitles[i][1] = subtitles[i][1]
        subtitles[i][2] = subtitles[i][2]

        if i == len(subtitles)-1:
            subtitles[i][3] = subtitles[i][3]
        else:
            subtitles[i][3] = subtitles[i + 1][2]


    srt = ''
    for subtitle in subtitles:
        print(subtitle[0])
        print(subtitle[2], '-->', subtitle[3])
        print(subtitle[1])
        print('')

        srt += str(subtitle[0]) + '\n' + \
        	   str(subtitle[2]) + ' --> ' + str(subtitle[3]) + '\n' + \
        	   str(subtitle[1]) + '\n\n'

    srt_path = txt_path.replace('.txt','.srt')
    with open(srt_path, 'w') as fobj: 
        data = fobj.write(srt)



def get_timestamps_csv(audio_fpath, txt_fpath):
    '''get timestamps via web page'''
    import pathlib
    import requests

    print('getting timestamps cvs file ... please wait ...')
    csv_fpath = txt_fpath.replace('.txt', '.csv')

    # skip the function if csv file exist
    if pathlib.Path(csv_fpath).is_file():
        print('found csv timestamps file, skip the function')
        return csv_fpath

    url = r'http://gentle-demo.lowerquality.com/transcriptions'

    # get transcipt from txt file
    with open(txt_fpath, 'r') as f:
        txt = f.read()

    # upload file and script
    with open(audio_fpath, 'rb') as f:
        r = requests.post(url, files={'audio': f}, data={'transcript':txt})

    # create csv url
    csv_timestamps_url = r.url + r'align.csv'
    print('timestamps url:  ', csv_timestamps_url)

    # save csv url
    r = requests.get(csv_timestamps_url)
    with open(csv_fpath, 'wb') as f:
        f.write(r.content)

    print('completed getting timestamps')

    return csv_fpath





print('Hướng dẫn sử dụng soft tự động căn chỉnh thời gian subtitle theo file transcript:')
print('- Nhập đường link của file âm thanh (mp3, mp4, wav ...) rồi enter')
print('- Nhập đường link của file transcript rồi enter')
print('- Soft bắt đầu chạy và tạo file srt, thời gian có thể hơi lâu tùy vào độ dài của file âm thanh')
print('\n')
while 1:
    try:
        audio_fpath = input('audio_fpath: ')
        txt_fpath = input('txt_fpath: ')


        #audio_fpath = r'C:\Users\ThienNguyen\Desktop\Youtube Videos\1419 - Elllo - Is it cheap or expensive to live in your country-\1419 Is it cheap or expensive to live in your country-.mp4'
        #txt_fpath = r'C:\Users\ThienNguyen\Desktop\Youtube Videos\1419 - Elllo - Is it cheap or expensive to live in your country-\1419 Is it cheap or expensive to live in your country-.txt'

        # remove " from path
        audio_fpath = audio_fpath.replace('"','')
        txt_fpath = txt_fpath.replace('"','')


        csv_fpath = get_timestamps_csv(audio_fpath, txt_fpath)

        create_srt_from_gentle_alignment(txt_fpath, csv_fpath)

        print('\n\n')
    except Exception as e:
        print(e)




#mp4_path = 'Holiday.mp4'
#wav_path = convert_mp4_to_wma(mp4_path)
#
#audio_path = wav_path
#txt_path = audio_path.replace('wav', 'txt')
#srt_path =  audio_path.replace('wav', 'srt')
#force_alignment(audio_path, txt_path, srt_path)


