setup: anaconda
	#install anaconda 3
	wget "https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh"
	bash Anaconda3-2021.11-Linux-x86_64.sh
	#create new anaconda environment
	conda create -n vfxpipeline python=3.7
	#activate the environment

setup: requirements.txt
	conda activate vfxpipeline
    pip install -r requirements.txt