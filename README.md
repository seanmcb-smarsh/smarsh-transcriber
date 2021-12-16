# Transcriber API

This repository provides an interface to the transcription engine (e.g. DeepScribe).

The API script is called transcribers.py and is in a folder called 'api'. Required transcriber modules are imported to the class for the transcriber. For example, DeepScribe modules are imported into the 'deepscribe' class.

Configuration files can be supplied for a variety of combinations of languages and transcriber engines (e.g. deepscribe, wav2vec, HuBERT) as they become available. A set of example files is provided using the dev area location references.

**Installation**

Ensure you are using python 3.6

    bash install.sh

To run tests:
    
    bash download_english_models.sh
    bash download_test_data.sh
    pytest tests

**Running Transcriptions**

The transcriptions can be run as follows:


•	Configuration settings / overrides are delivered to the API when loaded. 
In the example below, settings for English transcription are in a file called 'english.yaml' and stored in the variable 'settings'.


These values are then used on the files to be transcribed in the form transcriber.predict()

	cfg = DeepscribeConfig(
            decoder=DeepscribeDecoderConfig(
                lm_path = "path/to/lm.trie"
            ),
            model=DeepscribeModelConfig(
                model_path="path/to/model.pth"
            ),
            text_postprocessing=DeepscribeTextPostProcessingConfig(
                punc_path="path/to/punc.pth",
                acronyms_path="path/to/acronyms.txt"
            )
        )


        
	
	

•	These are then loaded and used to run the predict method on the files supplied.

	transcriber = cfg.load()

	result=transcriber.predict(['/path/to//audio_file1.wav','/path/to//audio_file1.wav'])  #List of files

or
	
	result=transcriber.predict(['/path/to//audio/files/directory/'])  #Directory containing audio files

•   The returned transcription object can then be iterated through to get the transcribed tokens, as well as the start and end timestamps for each token.

    for token in result[input].tokens:
            print(token.text,token.start_time,token.end_time)

•	The various model parameters can be changed as in the configuration objects:

	
	class DeepscribeDecoderConfig(BaseModel):
        lm_path = ''   # Path to an (optional) kenlm language model for use with beam search
        alpha = 0.39 # Language model weight Default is tuned for English
        beta = 0.45  # Language model word bonus (all words) Default is tuned for English
        cutoff_top_n = 40    # Keep top cutoff_top_n characters with highest probs in beam search
        cutoff_prob = 1.0  # Cutoff probability in pruning. 1.0 means no pruning
        lm_workers = 8  # Number of LM processes to use for beam search
        beam_width = 32 # Beam width to use for beam search

    class DeepscribeTextPostProcessingConfig(BaseModel):
        punc_path = ''  # Path to a DeepScribe Punctuation model
        acronyms_path = ''  # Path to acronym whitelist (collapse and capitalize)

    class DeepscribeModelConfig(BaseModel):
        model_path = ''  # Path to acoustic model

    class DeepscribeHardwareConfig(BaseModel):
        cuda = True  # Use CUDA for inference

    class DeepscribeConfig(TranscriberConfig):
        decoder = DeepscribeDecoderConfig()
        text_postprocessing = DeepscribeTextPostProcessingConfig()
        model = DeepscribeModelConfig()
        hardware = DeepscribeHardwareConfig()


![image info](./images/api_location.png)

