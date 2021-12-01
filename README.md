# Transcriber API

This repository provides an interface to the transcription engine (e.g. DeepScribe).

The script is in a folder called 'api' and required transcriber libraries are imported.

Configuration files can be supplied for a variety of combinations of languages and transcriber engines (e.g. deepscribe, wav2vec, HuBERT) as they become available. A set of example files is provided using the dev area location references.



**Running Transcriptions**

The transcriptions can be run as follows:


•	Configuration settings / overrides are delivered to the API when loaded. 
In the example below, settings for English transcription are in a file called 'english.yaml' and stored in the variable 'settings'.


These values are then used on the files to be transcribed in the form transcriber.predict()

	import yaml
	from api.transcribers import load

	with open('/path/to/english.yaml', "r") as configs:
       settings = yaml.load(configs, Loader=yaml.FullLoader)
 
    transcriber = load(settings)
	

•	These are then loaded and used to run the predict method on the files supplied.

	transcriber = load(settings)
	
	result=transcriber.predict(['/path/to//audio_file1.wav','/path/to//audio_file1.wav'])  #List of files

or
	
	result=transcriber.predict(['/path/to//audio/files/directory/'])  #Directory containing audio files


•	The various model parameters can be changed as in the example yaml file below. Note parameters will vary with transcriber engine. The values below are for DeepScribe used with a KenLM language model

english.yaml

	from api.transcribers import Transcriber
	
	transcriber: deepscribe
	model_path: "/path/to/audio/model/deepscribe-0.3.0.pth"
	lm_path: "path/to/language/model/financial-0.1.3.trie"
	punc_path: "/path/to/punctuation/model/punc-0.2.0.pth"
	acronyms_path: "/path/to/acronyms/file/all.acronyms.txt"
	lm_alpha: 0.39
	lm_beta: 0.45
	device: "cuda"  

The values are as follows:

transcriber: transcriber 'engine' / recogniser e.g. DeepScribe, wav2vec, HuBERT

model_path: Audio model location

lm_path: Language model location

acronyms_path: Acronyms file location

lm_alpha: The KenLM language model alpha parameter

lm_beta: The KenLM language model beta parameter

device: cuda or cpu (This is an override - if this is not present, if this is not preent, the api will decide on the basis of whether or not cuda is available in the environment.)

Sample yaml files are supplied in the 'example_configs' directory. These use development environment locations and will need to be set according to the environment in which the api is used.


Note: When using a local installation (as in development), it may be convenient to put the api folder in the top level directory of the transcriber, so that you are sure that the local instance files are being used. For example, with DeepScribe, this would be the top level deepscribe-inference installation directory (in the example below, 'deepscribe-inference) **above** the 'deepscribe_inference' directory.

![image info](./images/api_location.png)

