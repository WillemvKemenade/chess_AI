####To create dataset for training the models, there are few steps:
1) Create folder ".../chess_AI/create_test_data/fics_data" and save any chess pgn file or files into it
2) Run split_data.py file which split the whole dataset into small batches 

    - this script creates folder: "trainingdata" and saves files ("trainingbatch1.txt", "trainingbatch2.txt", ...) with max_games_per_files=300 games in one file (the parameter can be changed)
3) Run data_maker.py file which convert files for training to h5 format 

    - this script creates folder "testtrainingfiles" and saves files from "trainingdata" in h5 format and saves combined file to train the models
4) Run train_model.py file which train the models: moved_from or moved_in 

    - to run "moved_in" model the mode variable should be set to "moved_in"
