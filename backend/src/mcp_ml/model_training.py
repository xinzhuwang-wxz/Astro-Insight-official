import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint
import yaml
from data_preprocessing import load_and_preprocess_data, create_dataset
from model_definition import build_model, load_config
import pandas as pd

def train_model(config):
    """Trains the model based on the provided configuration."""
    # config is passed as parameter, no need to reload

    # Load data
    train_df, val_df, _, label_encoder = load_and_preprocess_data(config)
    train_dataset = create_dataset(train_df, config, is_training=True)
    val_dataset = create_dataset(val_df, config, is_training=False)
    num_classes = len(label_encoder.classes_)

    # Build model
    model = build_model(config, num_classes)

    # Compile model
    compiler_config = config['model_training']['compiler']
    model.compile(**compiler_config)

    # Class weights
    class_counts = train_df['Encoded Label'].value_counts()
    total_samples = len(train_df)
    class_weights = {i: total_samples / (num_classes * count) for i, count in class_counts.items()}

    # Callbacks
    checkpoint_config = config['model_training']['checkpoint']
    checkpoint = ModelCheckpoint(
        filepath=checkpoint_config['filepath'],
        monitor=checkpoint_config['monitor'],
        save_best_only=True,
        mode=checkpoint_config['mode'],
        verbose=1
    )

    # Train model
    training_config = config['model_training']
    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=training_config['epochs'],
        class_weight=class_weights,
        callbacks=[checkpoint]
    )
    
    print("Model training complete.")
    return model, history

