import os
import logging.config
import yaml

def configure_logging():
    """Configure the application's logging system"""
    default_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'brief': {
                'format': '%(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'brief',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'logs',
                    'app.log'
                ),
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    }
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'logs'
    )
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging
    try:
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'logging.yaml'
        )
        
        if os.path.exists(config_path):
            with open(config_path, 'rt') as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
        else:
            logging.config.dictConfig(default_config)
    except Exception as e:
        print(f"Error configuring logging: {e}")
        # Fall back to basic configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(os.path.join(logs_dir, 'fallback.log'))
            ]
        )