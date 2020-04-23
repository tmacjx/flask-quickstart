"""
# @Author  wk
# @Time 2020/4/22 10:41

"""
from .default import Config


class ProductionConfig(Config):
    DEBUG = False
