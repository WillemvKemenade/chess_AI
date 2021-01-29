from keras import layers
from keras import models
from time import time
import keras
from keras.callbacks import ModelCheckpoint, TensorBoard
from keras.optimizers import Adam
import h5py

from train_model import generator


mode = 'moved_from' # or 'moved_to'
num_val = 100000

stime = time()
batch_size = 128
num_classes = 64
epochs = 1


# input image dimensions
img_rows, img_cols = 8, 8
input_shape = (img_rows, img_cols, 12)

cardinality = 32


def residual_network(x):
    """
    ResNeXt by default. For ResNet set `cardinality` = 1 above.

    """

    def add_common_layers(y):
        y = layers.BatchNormalization()(y)
        y = layers.LeakyReLU()(y)

        return y

    def grouped_convolution(y, nb_channels, _strides):
        # when `cardinality` == 1 this is just a standard convolution
        if cardinality == 1:
            return layers.Conv2D(nb_channels, kernel_size=(3, 3), strides=_strides, padding='same')(y)

        assert not nb_channels % cardinality
        _d = nb_channels // cardinality

        # in a grouped convolution layer, input and output channels are divided into `cardinality` groups,
        # and convolutions are separately performed within each group
        groups = []
        for j in range(cardinality):
            group = layers.Lambda(lambda z: z[:, :, :, j * _d:j * _d + _d])(y)
            groups.append(layers.Conv2D(_d, kernel_size=(3, 3), strides=_strides, padding='same')(group))

        # the grouped convolutional layer concatenates them as the outputs of the layer
        y = layers.concatenate(groups)

        return y

    def residual_block(y, nb_channels_in, nb_channels_out, _strides=(1, 1), _project_shortcut=False):
        """
        Our network consists of a stack of residual blocks. These blocks have the same topology,
        and are subject to two simple rules:
        - If producing spatial maps of the same size, the blocks share the same hyper-parameters (width and filter sizes).
        - Each time the spatial map is down-sampled by a factor of 2, the width of the blocks is multiplied by a factor of 2.
        """
        shortcut = y

        # we modify the residual building block as a bottleneck design to make the network more economical
        y = layers.Conv2D(nb_channels_in, kernel_size=(1, 1), strides=(1, 1), padding='same')(y)
        y = add_common_layers(y)

        # ResNeXt (identical to ResNet when `cardinality` == 1)
        y = grouped_convolution(y, nb_channels_in, _strides=_strides)
        y = add_common_layers(y)

        y = layers.Conv2D(nb_channels_out, kernel_size=(1, 1), strides=(1, 1), padding='same')(y)
        # batch normalization is employed after aggregating the transformations and before adding to the shortcut
        y = layers.BatchNormalization()(y)

        # identity shortcuts used directly when the input and output are of the same dimensions
        if _project_shortcut or _strides != (1, 1):
            # when the dimensions increase projection shortcut is used to match dimensions (done by 1×1 convolutions)
            # when the shortcuts go across feature maps of two sizes, they are performed with a stride of 2
            shortcut = layers.Conv2D(nb_channels_out, kernel_size=(1, 1), strides=_strides, padding='same')(shortcut)
            shortcut = layers.BatchNormalization()(shortcut)

        y = layers.add([shortcut, y])

        # relu is performed right after each batch normalization,
        # expect for the output of the block where relu is performed after the adding to the shortcut
        y = layers.LeakyReLU()(y)

        return y

    # conv1
    x = layers.Conv2D(64, kernel_size=(7, 7), strides=(2, 2), padding='same')(x)
    x = add_common_layers(x)

    # conv2
    x = layers.MaxPool2D(pool_size=(3, 3), strides=(2, 2), padding='same')(x)
    for i in range(3):
        project_shortcut = True if i == 0 else False
        x = residual_block(x, 128, 256, _project_shortcut=project_shortcut)

    # conv3
    for i in range(4):
        # down-sampling is performed by conv3_1, conv4_1, and conv5_1 with a stride of 2
        strides = (2, 2) if i == 0 else (1, 1)
        x = residual_block(x, 256, 512, _strides=strides)

    # conv4
    for i in range(6):
        strides = (2, 2) if i == 0 else (1, 1)
        x = residual_block(x, 512, 1024, _strides=strides)

    # conv5
    for i in range(3):
        strides = (2, 2) if i == 0 else (1, 1)
        x = residual_block(x, 1024, 2048, _strides=strides)

    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(1)(x)

    return x


image_tensor = layers.Input(shape=(8, 8, 12))
network_output = residual_network(image_tensor)

model = models.Model(inputs=[image_tensor], outputs=[network_output])
# print(model.summary())

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=Adam(),
              metrics=['accuracy'])

tensorboard = TensorBoard(log_dir=f'/tmp/keras_logs/ChessAI/{mode}')
filepath = f'resnet_{mode}_model.h5'
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
    model_json = model.to_json()
    with open(f"resnet_{mode}_model.json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights(f"resnet_{mode}_weights.h5")
    X_val = X_val.reshape(X_val.shape[0], 8, 8, 12)
    score = model.evaluate(X_val, Y_val, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])
    print('Time taken:', time() - stime)
