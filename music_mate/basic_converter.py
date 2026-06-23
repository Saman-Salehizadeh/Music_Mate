#Importing Libraries
from imageio_ffmpeg import get_ffmpeg_exe
from subprocess import run
from librosa import load
from noisereduce import reduce_noise
from soundfile import write
from basic_pitch.inference import predict_and_save, ICASSP_2022_MODEL_PATH
from music21.midi import MidiFile, translate, environment
from os.path import splitext, basename, join, dirname
from os import makedirs
from lilypond import executable
from tempfile import TemporaryDirectory
from shutil import copystat, copy
from platform import system
lilypond_path=str(executable())
if system()=="Windows" and not lilypond_path.lower().endswith('.exe'):
    lilypond_path+='.exe'
us=environment.UserSettings()
us['lilypondPath']=lilypond_path
    
#Main Function
def media_to_notes(input_path,output_path,lilypond_path=lilypond_path):
    makedirs(dirname(output_path),exist_ok=True)
    file_extension=splitext(input_path)[1]
    file_name=splitext(basename(input_path))[0]
    
    #Saving Between Files in Temp Directory
    with TemporaryDirectory() as tmp:
        #Correcting File Format
        if file_extension.lower()!='.wav':
            run([get_ffmpeg_exe(),'-y','-i',input_path,join(tmp,file_name+'.wav')],check=True)
            wav_path=join(tmp,file_name+'.wav')
        else:
            wav_path=input_path
        #Noise Reduction
        y,sr=load(wav_path,sr=None,mono=True)
        noise_reduced_music=reduce_noise(y=y,sr=sr,stationary=True,prop_decrease=0.6)
        write(join(tmp,file_name+'_denoised.wav'),noise_reduced_music,sr)

        #Making The MIDI
        predict_and_save(
            audio_path_list=[join(tmp,file_name+'_denoised.wav')],
            output_directory=tmp,
            save_midi=True,
            sonify_midi=False,
            save_model_outputs=False,
            save_notes=True,
            model_or_model_path=ICASSP_2022_MODEL_PATH)
            
        #Making The Ly
        mf=MidiFile()
        mf.open(join(tmp,file_name+'_denoised_basic_pitch.mid'))
        mf.read()
        mf.close()
        s=translate.midiFileToStream(mf)
        s.write('lily', fp=join(tmp,file_name+'.ly'))

        #Correcting The Layout
        with open(join(tmp,file_name+'.ly'),'r',encoding='utf-8') as f:
            ly=f.read()
        if r'\include "lilypond-book-preamble.ly"' in ly:
            ly=ly.replace(r'\include "lilypond-book-preamble.ly"',rf'\include "{file_name}_wrapper.ly"')
        else:
            ly=rf'\include "{file_name}_wrapper.ly"'+'\n'+ly
        with open(join(tmp,file_name+'_wrapper.ly'),'w',encoding='utf-8') as f:
            f.write(r'\header { tagline = ##f }')
        with open(join(tmp,file_name+'.ly'),'w',encoding='utf-8') as f:
            f.write(ly)
            
        #Making The PDF
        run([lilypond_path,"-I",tmp,"-o",join(tmp,file_name),join(tmp,file_name+'.ly')],check=True)
        copy(join(tmp,file_name+'.pdf'),output_path)
        try:
            copystat(join(tmp,file_name+'.pdf'),output_path)
        except:
            pass

        print(f"Notes PDF saved to {output_path}.")
