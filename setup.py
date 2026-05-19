from setuptools import setup,find_packages
setup(
    name="Music_Mate",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "imageio-ffmpeg==0.6.0",
        "lilypond==2.24.3",
        "librosa==0.11.0",
        "noisereduce==3.0.3",
        "soundfile==0.13.1",
        "basic-pitch==0.4.0",
        "music21==9.9.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires="==3.11.*",
)
