"""
Create dummy models for development and testing.
This script creates basic dummy models to allow the fraud detection service to run
without errors when the real models are not available.
"""

import tensorflow as tf
from tensorflow import keras
import os
import numpy as np

def create_dummy_model(input_shape, num_classes, model_name):
    """Create a simple CNN model that accepts the given input shape and outputs class probabilities"""
    model = keras.Sequential([
        keras.layers.InputLayer(input_shape=input_shape),
        keras.layers.Conv2D(8, kernel_size=(3, 3), activation='relu'),
        keras.layers.MaxPooling2D(pool_size=(2, 2)),
        keras.layers.Flatten(),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Save the model
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, model_name)
    model.save(model_path)
    
    print(f"Created dummy model: {model_path}")
    
    return model

if __name__ == "__main__":
    # Create ELA model (binary classification: Real vs Tampered)
    ela_model = create_dummy_model(
        input_shape=(128, 128, 3),
        num_classes=2,
        model_name="model_ela.h5"
    )
    
    # Create Weather model (4 classes: Lightning, Rainy, Snow, Sunny)
    weather_model = create_dummy_model(
        input_shape=(128, 128, 3),
        num_classes=4,
        model_name="Weather_Model.h5"
    )
    
    print("Dummy models created successfully!")