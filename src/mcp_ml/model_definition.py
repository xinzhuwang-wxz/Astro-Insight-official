import tensorflow as tf
import yaml

def load_config(config_path):
    """Loads YAML configuration file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def build_model(config, num_classes):
    """Builds a Keras Sequential model from configuration."""
    # config is passed as parameter, no need to reload
    
    model_config = config['model_training']['model']
    model = tf.keras.Sequential()
    # Input layer
    model.add(tf.keras.layers.Input(shape=tuple(model_config['input_shape'])))
    # Hidden layers
    for layer_conf in model_config['layers']:
        layer_type = layer_conf.pop('type')
        if layer_type == 'Dense' and 'units' not in layer_conf:
            layer_conf['units'] = num_classes
        layer_class = getattr(tf.keras.layers, layer_type)
        model.add(layer_class(**layer_conf))
        # Restore type for potential reuse
        layer_conf['type'] = layer_type
    return model