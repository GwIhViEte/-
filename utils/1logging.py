"""
日志模块 - 提供应用程序的日志功能。
"""
import os
import sys
import logging
from datetime import datetime

# 创建日志目录
def setup_logging(log_level=logging.INFO):
    """
    设置日志系统
    :param log_level: 日志级别，默认为INFO
    :return: 配置好的日志记录器
    """
    # 确保日志目录存在
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名，包含时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'novel_generator_{timestamp}.log')
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 创建日志记录器
    logger = logging.getLogger('novel_generator')
    logger.setLevel(log_level)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    logger.info("日志系统初始化完成")
    return logger

# 获取记录器的简便函数
def get_logger():
    """
    获取配置好的日志记录器
    :return: 日志记录器实例
    """
    logger = logging.getLogger('novel_generator')
    if not logger.handlers:
        return setup_logging()
    return logger 