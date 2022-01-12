# import os
# import logging
# _LOGGER = logging.getLogger(__name__)

# model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "models", "handwritten.model")
# def load_model():
#     from keras.models import load_model as load
#     return load(model_path)

# def generate_model():
#     if os.path.exists(model_path):
#         _LOGGER.info("AI model already exists.")
#         return
    
#     _LOGGER.info("Creating AI model for digits recognition. This may take a while.")
#     import tensorflow as tf
#     from tensorflow import keras

#     # Helper libraries
#     import numpy as np
#     import random
#     mnist = keras.datasets.mnist
#     (train_images, train_labels), (test_images, test_labels) = mnist.load_data()
#     train_images = train_images / 255.0
#     test_images = test_images / 255.0
#     model = keras.Sequential([
#         keras.layers.InputLayer(input_shape=(28, 28)),
#         keras.layers.Reshape(target_shape=(28, 28, 1)),
#         keras.layers.Conv2D(filters=32, kernel_size=(3, 3), activation=tf.nn.relu),
#         keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation=tf.nn.relu),
#         keras.layers.MaxPooling2D(pool_size=(2, 2)),
#         keras.layers.Dropout(0.25),
#         keras.layers.Flatten(),
#         keras.layers.Dense(10)
#     ])

#     # Define how to train the model
#     model.compile(optimizer='adam',
#                 loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
#                 metrics=['accuracy'])

#     # Train the digit classification model
#     model.fit(train_images, train_labels, epochs=5)
#     test_loss, test_acc = model.evaluate(test_images, test_labels)
#     model.save(model_path)