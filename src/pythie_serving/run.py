import logging
import os
import sys
from argparse import ArgumentParser
from logging.config import dictConfig

from google.protobuf import text_format
from pythie_serving import serve
from pythie_serving.tensorflow_proto.tensorflow_serving.config import \
    model_server_config_pb2


def run():
    model_choice_set = {'xgboost'}
    model_choice_str = ','.join(model_choice_set)

    parser = ArgumentParser(description=f'A GRPC server to serve different kind of model amongst: {model_choice_str}')
    parser.add_argument('model_config_file_path', type=str,
                        help='Path to a model config file of the format '
                             'https://www.tensorflow.org/tfx/serving/serving_config#model_server_configuration')
    parser.add_argument('--worker-count', default=10, type=int, help='Number of concurrent threads for the GRPC server')
    parser.add_argument('--port', default=9090, type=int, help='Port number to listen to')

    dictConfig({
        'disable_existing_loggers': True,
        'version': 1,
        'formatters': {
            'console_formatter': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                '()': 'logging.Formatter'
            }
        },
        'handlers': {
            'stdout_handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'console_formatter',
                'level': 'INFO',
                'stream': sys.stdout
            }
        },
        'root': {'level': 'INFO', 'handlers': ['stdout_handler'], 'formatter': ['console_formatter']}
    })
    logger = logging.getLogger('pythie_serving')

    ns = parser.parse_args()

    if not os.path.exists(ns.model_config_file_path):
        raise ValueError(f'No config file found at {ns.model_config_file_path}')

    model_server_config = model_server_config_pb2.ModelServerConfig()
    with open(ns.model_config_file_path, 'r') as opened_config_file:
        text_format.Parse(opened_config_file.read(), model_server_config)

    serve(model_server_config=model_server_config, worker_count=ns.worker_count, port=ns.port, _logger=logger)


if __name__ == '__main__':
    run()
