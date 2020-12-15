"""
# @Time    : 2020/12/15 10:34
# @Author  : tmackan
"""

from concurrent.futures.thread import ThreadPoolExecutor

# ThreadPoolExecutor max_workers 未指定的话 为 (os.cpu_count() or 1) * 5
# ThreadPoolExecutor 默认Queue大小为无穷
taskExecutor = ThreadPoolExecutor()
