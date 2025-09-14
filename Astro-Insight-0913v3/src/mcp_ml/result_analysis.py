import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np
import yaml
import os
from data_preprocessing import load_and_preprocess_data, create_dataset

def load_config(config_path):
    """Loads YAML configuration file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def evaluate_model(model, history, test_dataset, label_encoder, config, output_manager=None, process_id=None):
    """Evaluates the model and generates analysis plots."""
    # config is passed as parameter, no need to reload

    analysis_config = config['result_analysis']

    # Plot training history
    if analysis_config.get('plot_history', False):
        plot_training_history(history, output_manager, process_id)

    # Confusion matrix
    if analysis_config.get('confusion_matrix', {}).get('enabled', False):
        plot_confusion_matrix(model, test_dataset, label_encoder, analysis_config['confusion_matrix'], output_manager, process_id)


def plot_training_history(history, output_manager=None, process_id=None):
    """Plots training and validation accuracy and loss."""
    # config is passed as parameter, no need to reload

    plt.figure(figsize=(12, 5))

    # Accuracy plot
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()

    # Loss plot
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    
    # 保存图片
    if output_manager:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            plt.savefig(tmp_file.name, dpi=300, bbox_inches='tight')
            tmp_file.close()  # 关闭文件句柄
            output_manager.save_image(tmp_file.name, process_id, 'training_history')
            try:
                os.unlink(tmp_file.name)
            except OSError:
                pass  # 忽略删除临时文件时的错误
    else:
        plt.show()
    
    plt.close()

def plot_confusion_matrix(model, test_dataset, label_encoder, cm_config, output_manager=None, process_id=None):
    """Generates and plots the confusion matrix."""
    # config is passed as parameter, no need to reload

    y_true = np.concatenate([y.numpy() for _, y in test_dataset])
    y_pred_probs = model.predict(test_dataset)
    y_pred = np.argmax(y_pred_probs, axis=1)

    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=tuple(cm_config.get('figsize', [10, 8])))
    sns.heatmap(cm, annot=True, fmt='d', cmap=cm_config.get('cmap', 'Blues'),
                xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    
    # 保存图片
    if output_manager:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            plt.savefig(tmp_file.name, dpi=300, bbox_inches='tight')
            tmp_file.close()  # 关闭文件句柄
            output_manager.save_image(tmp_file.name, process_id, 'confusion_matrix')
            try:
                os.unlink(tmp_file.name)
            except OSError:
                pass  # 忽略删除临时文件时的错误
    else:
        plt.show()
    
    plt.close()
