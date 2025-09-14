import os
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
import yaml

def load_config(config_path):
    """Loads YAML configuration file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def load_and_preprocess_data(config):
    """
    Loads, preprocesses, and splits the data according to the provided configuration.
    """
    # config is passed as parameter, no need to reload

    # Load data paths from config
    image_dir = config['data_preprocessing']['image_dir']
    
    # Create a DataFrame with image paths and labels
    data = []
    for label_folder in os.listdir(image_dir):
        folder_path = os.path.join(image_dir, label_folder)
        if os.path.isdir(folder_path):
            for img_file in os.listdir(folder_path):
                if img_file.endswith('.jpg'):
                    data.append({
                        'File Path': os.path.join(folder_path, img_file),
                        'Label': label_folder
                    })
    data_df = pd.DataFrame(data)

    # Encode labels
    label_encoder = LabelEncoder()
    data_df['Encoded Label'] = label_encoder.fit_transform(data_df['Label'])

    # Split data
    split_ratios = config['data_preprocessing']['split_ratios']
    random_state = config['data_preprocessing']['random_state']
    train_df, val_df, test_df = np.split(
        data_df.sample(frac=1, random_state=random_state),
        [int(split_ratios['train'] * len(data_df)), int((split_ratios['train'] + split_ratios['validation']) * len(data_df))]
    )

    return train_df, val_df, test_df, label_encoder

def create_dataset(df, config, is_training=True):
    """
    Creates a TensorFlow dataset from a DataFrame.
    """
    # config is passed as parameter, no need to reload

    batch_size = config['data_preprocessing']['batch_size']
    target_size = tuple(config['data_preprocessing']['image_size'])
    aug_config = config['data_preprocessing']['augmentation']

    file_paths = df['File Path'].values
    labels = df['Encoded Label'].values.astype(np.int32)
    
    dataset = tf.data.Dataset.from_tensor_slices((file_paths, labels))

    def resize_image(image_path, label):
        img = tf.io.read_file(image_path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, target_size)
        return img, label

    def augment_image(image, label):
        if aug_config.get('random_flip_left_right', False):
            image = tf.image.random_flip_left_right(image)
        if aug_config.get('random_flip_up_down', False):
            image = tf.image.random_flip_up_down(image)
        if 'random_brightness_delta' in aug_config:
            image = tf.image.random_brightness(image, max_delta=aug_config['random_brightness_delta'])
        if 'random_contrast_lower' in aug_config and 'random_contrast_upper' in aug_config:
            image = tf.image.random_contrast(image, lower=aug_config['random_contrast_lower'], upper=aug_config['random_contrast_upper'])
        return image, label

    def normalize_image(image, label):
        image = tf.cast(image, tf.float32) / 255.0
        return image, label

    dataset = dataset.map(resize_image, num_parallel_calls=tf.data.AUTOTUNE)
    if is_training:
        dataset = dataset.map(augment_image, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.map(normalize_image, num_parallel_calls=tf.data.AUTOTUNE)
    
    dataset = dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    
    return dataset

