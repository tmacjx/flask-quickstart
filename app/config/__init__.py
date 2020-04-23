"""
# @Author  wk
# @Time 2020/4/22 10:40

"""

import os


def load_config():
    """加载配置类"""
    mode = os.environ.get('MODE', None)
    try:
        if mode == 'PRODUCTION':
            # 线上环境 配置实际 路径
            # sys.path.append('/var/www/dream/webapp/conf')
            # from production import ProductionConfig
            from .production import ProductionConfig
            return ProductionConfig
        elif mode == 'TESTING':
            from .test import TestConfig
            return TestConfig
        elif mode == 'DEVELOP':
            from .develop import DevelopConfig
            return DevelopConfig
        else:
            from .default import Config
            return Config
    except ImportError:
        from .default import Config
        return Config
