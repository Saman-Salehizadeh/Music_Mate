#Importing Libraries
from imageio_ffmpeg import get_ffmpeg_exe
from subprocess import run
from librosa import load
from noisereduce import reduce_noise
from soundfile import write
from basic_pitch.inference import predict_and_save, ICASSP_2022_MODEL_PATH
from music21.midi import MidiFile, translate, environment
from os.path import splitext, basename, join, dirname, abspath, isdir
from os import makedirs
from lilypond import executable
from tempfile import TemporaryDirectory
from shutil import copy
from platform import system
    
#Main Function
def media_to_notes(input_path,output_path):
    supplementary_files=[]
    lilypond_path=str(executable())
    if system()=="Windows" and not lilypond_path.lower().endswith('.exe'):
        lilypond_path+='.exe'
    us=environment.UserSettings()
    us['lilypondPath']=lilypond_path
    output_dir = dirname(abspath(output_path))
    makedirs(output_dir, exist_ok=True)
    file_extension=splitext(input_path)[1]
    file_name=splitext(basename(input_path))[0]
    
    #Saving Between Files in Temp Directory
    with TemporaryDirectory() as tmp:
        #Correcting File Format
        if file_extension.lower()!='.wav':
            wav_path=join(tmp,file_name+'.wav')
            run([get_ffmpeg_exe(),'-y','-i',input_path,wav_path],check=True)
            supplementary_files.append(wav_path)
        else:
            wav_path=input_path

        #Noise Reduction
        y,sr=load(wav_path,sr=None,mono=True)
        denoised_music=reduce_noise(y=y,sr=sr,stationary=True,prop_decrease=0.6)
        denoised_music_path=join(tmp,file_name+'_denoised.wav')
        write(denoised_music_path,denoised_music,sr)
        supplementary_files.append(denoised_music_path)
        #Making The MIDI
        predict_and_save(
            audio_path_list=[denoised_music_path],
            output_directory=tmp,
            save_midi=True,
            sonify_midi=False,
            save_model_outputs=False,
            save_notes=True,
            model_or_model_path=ICASSP_2022_MODEL_PATH)
        mid_path=join(tmp,file_name+'_denoised_basic_pitch.mid')
        supplementary_files.append(mid_path)
        supplementary_files.append(join(tmp,file_name+'_denoised_basic_pitch.csv'))
            
        #Making The Ly
        mf=MidiFile()
        mf.open(mid_path)
        mf.read()
        mf.close()
        s=translate.midiFileToStream(mf)
        ly_path=join(tmp,file_name+'.ly')
        s.write('lily', fp=ly_path)
        supplementary_files.append(ly_path)

        #Correcting The Layout
        with open(ly_path,'r',encoding='utf-8') as f:
            ly=f.read()
        if r'\include "lilypond-book-preamble.ly"' in ly:
            ly=ly.replace(r'\include "lilypond-book-preamble.ly"',rf'\include "{file_name}_wrapper.ly"')
        else:
            ly=rf'\include "{file_name}_wrapper.ly"'+'\n'+ly
        wrapper_path=join(tmp,file_name+'_wrapper.ly')
        with open(wrapper_path,'w',encoding='utf-8') as f:
            f.write(r'\header { tagline = ##f }')
        with open(ly_path,'w',encoding='utf-8') as f:
            f.write(ly)
        supplementary_files.append(wrapper_path)
            
        #Making The PDF
        run([lilypond_path,"-I",tmp,"-o",join(tmp,file_name),join(tmp,file_name+'.ly')],check=True)
        pdf_path=join(tmp,file_name+'.pdf')
        copy(pdf_path,output_path)
        
        #Saving The Supplementary Files
        supplementary_user=input('Do you want the supplementary files (Y/n)? ').strip().lower()
        while supplementary_user!='y' and supplementary_user!='n':
            supplementary_user=input('Please answer with "Y" or "n":').strip().lower()
        if supplementary_user=='y':
            counter=0
            supplementary_dir=join(output_dir,'Supplementary Files')
            while isdir(supplementary_dir):
                counter+=1
                supplementary_dir=join(output_dir,f'Supplementary Files ({counter})')
            makedirs(supplementary_dir)
            for supplementary_file in supplementary_files:
                destination=join(supplementary_dir,basename(supplementary_file))
                copy(supplementary_file,destination)
            print(f"Supplementary files saved to {supplementary_dir}.")
        print(f"Notes PDF saved to {output_path}.")
