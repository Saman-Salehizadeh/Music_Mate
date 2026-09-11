#Imports
from subprocess import run
from imageio_ffmpeg import get_ffmpeg_exe
from music21.midi import MidiFile, translate, environment
from tempfile import TemporaryDirectory
from os.path import splitext, basename, join, dirname, abspath
from lilypond import executable
from shlex import quote
supplementary_files=[]
lilypond_path=str(executable())
us=environment.UserSettings()
us['lilypondPath']=lilypond_path

#Transcription
audio_path=input()
file_name=splitext(basename(audio_path))[0]
file_extension=splitext(audio_path)[1]
with TemporaryDirectory() as tmp:
    #Correcting the Input Format
    if file_extension.lower()!='.wav':
        wav_path=join(tmp,file_name+'.wav')
        run([get_ffmpeg_exe(),'-y','-i',audio_path,wav_path],check=True)
    else:
        wav_path=audio_path
    mid_path=join("./piano-reduction-with-midibert/case",file_name+'.mid')
    run(f""". a2p/bin/activate; muscriptor transcribe {quote(wav_path)} --model medium --device cuda -o {quote(mid_path)}""", check=True, cwd='.', shell=True)

#Arrangement
run(""". a2p2/bin/activate
cd ./piano-reduction-with-midibert/MidiBERT/prepare_data/CP
python main.py --task custom --name case --input_dir ../../../case
cd ../../CP
mv ../data/CP/case.npy ../../data/CP/case.npy
python eval.py --task reduction --case case --dict_file ../dict/CP.pkl --batch_size 2 --num_workers 4 --cuda_devices 0
cd ../..
python -c "from postprocessing.postprocessing import postprocess; postprocess('MidiBERT/CP/reduction.mid', 'MidiBERT/CP/final.mid')"
""", check=True, cwd='.', shell=True)
mid_path="./piano-reduction-with-midibert/MidiBERT/CP/final.mid"

#Engraving
with TemporaryDirectory() as tmp:
        #Making the Ly
        mf=MidiFile()
        mf.open(mid_path)
        mf.read()
        mf.close()
        s=translate.midiFileToStream(mf)
        ly_path=join(tmp,file_name+'.ly')
        s.write('lily', fp=ly_path)

        #Correcting the Layout
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
            
        #Making The PDF
        output_path=input("Save PDF at: ")
        output_dir=dirname(abspath(output_path))
        output_name=splitext(basename(output_path))[0]
        run([lilypond_path,"-I",tmp,"-o",join(output_dir,output_name),join(tmp,file_name+'.ly')],check=True)
        run("""rm -rf ./piano-reduction-with-midibert/case/*""", check=True, cwd='.', shell=True)
