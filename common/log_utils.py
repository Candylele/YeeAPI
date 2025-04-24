from nb_log import LogManager

logger = LogManager('candytest').get_logger_and_add_handlers(is_add_stream_handler=True,
                                                             log_filename='candytest.log',
                                                             log_level_int=10)
if __name__ == '__main__':
    logger.info('info级别的日志')
    logger.warning('warn --++++')
    logger.error('error --++++')
    logger.fatal('fatal --++++')
