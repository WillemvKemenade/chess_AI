from time import time
import h5py
import keras
import os
import numpy as np
from keras.callbacks import ModelCheckpoint, TensorBoard
from keras.layers import Activation, Conv2D, Dense, Flatten, LSTM
from keras.models import Sequential, model_from_json
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split

from input_board import convert_position_prediction, make_clean_board, move_from

mode = 'moved_from' # or 'moved_to'
num_val = 100000


def generator(inputs, outputs, batch_size, training_examples=0, validation_examples=0):
    'Generator that chunks the data, and processes.'
    training_steps = training_examples//batch_size
    validation_steps = validation_examples//batch_size
    start_val = inputs.shape[0] - validation_examples

    if validation_examples == 0:
        while 1:
            for i in range(training_steps):
                batch_x = inputs[i*batch_size:(i+1)*batch_size]
                batch_y = outputs[i*batch_size:(i+1)*batch_size]

                batch_x = batch_x.reshape(batch_x.shape[0], 8, 8, 12)
                yield batch_x, batch_y
    else:
        while 1:
            for i in range(validation_steps):
                batch_x = inputs[(i*batch_size)+start_val:((i+1)*batch_size)+start_val]
                batch_y = outputs[(i*batch_size)+start_val:((i+1)*batch_size)+start_val]

                batch_x = batch_x.reshape(batch_x.shape[0], 8, 8, 12)
                yield batch_x, batch_y

# ----------The network----------
stime = time()
batch_size = 128
num_classes = 64
epochs = 30

# input image dimensions
img_rows, img_cols = 8, 8
input_shape = (img_rows, img_cols, 12)

model = Sequential()
model.add(LSTM(batch_size, input_shape)),
model.add(Activation('relu')),
model.add(Conv2D(128, kernel_size=(2, 2),
                 input_shape=input_shape))
model.add(Activation('relu'))

model.add(Conv2D(128, kernel_size=(2, 2)))
model.add(Activation('relu'))

model.add(Flatten())

model.add(Dense(1024))
model.add(Activation('relu'))

model.add(Dense(1024))
model.add(Activation('relu'))

model.add(Dense(num_classes, activation='softmax'))

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=Adam(),
              metrics=['accuracy'])

tensorboard = TensorBoard(log_dir=f'/tmp/keras_logs/ChessAI/{mode}')
filepath = f'{mode}_model.h5'
checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1,
                             save_best_only=True, mode='max')
callbacks = [tensorboard, checkpoint]

h5f = h5py.File('traintestdata.h5', 'r')

X = h5f['input_position'][:-num_val]
Y = h5f[mode][:-num_val]

X_val = h5f['input_position'][-num_val:]
Y_val = h5f[mode][-num_val:]

num_training_examples = len(X)
num_val_examples = len(X_val)

print(f'Number of training examples: {num_training_examples}')
print(f'Number of validation examples: {num_val_examples}')


training_batch_gen = generator(X, Y, batch_size, training_examples=num_training_examples)
validation_batch_gen = generator(X_val, Y_val, batch_size, validation_examples=num_val_examples)


if __name__ == '__main__':
    model.fit_generator(generator=training_batch_gen,
                        steps_per_epoch=(num_training_examples // batch_size),
                        use_multiprocessing=True,
                        epochs=epochs,
                        shuffle=True,
                        verbose=1,
                        callbacks=callbacks,
                        validation_data=validation_batch_gen,
                        validation_steps=(num_val_examples // batch_size),
                        workers=16,
                        max_queue_size=32)

    score = model.evaluate(X_val, Y_val, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])
    print('Time taken:', time() - stime)
