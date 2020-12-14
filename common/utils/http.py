"""
# @Author  wk
# @Time 2020/4/22 15:23

"""
import time
import json
import requests
import logging
from requests.exceptions import RequestException


import xmltodict

logger = logging.getLogger(__name__)


def xml_to_dict(xml_str):
    data_dict = xmltodict.parse(xml_str)
    return data_dict


class HttpAPIClient(object):
    def __init__(self, base_url, headers=None, http_service=requests, retry=3, timeout=5):
        if headers is None:
            headers = {}
        self.base_url = base_url
        self.headers = headers
        self.http_service = http_service
        self.retry = retry
        self.timeout = timeout

    def request(
            self,
            http_method,
            uri_path,
            headers=None,
            query_params=None,
            post_args=None,
            files=None,
            retry=3,
            timeout=5):

        # explicit values here to avoid mutable default values
        if headers is None:
            headers = self.headers
        if query_params is None:
            query_params = {}
        if post_args is None:
            post_args = {}

        # if files specified, we don't want any data
        data = None
        if files is None:
            data = json.dumps(post_args)

        # set content type and accept headers to handle JSON
        if http_method in ("POST", "PUT", "DELETE") and not files:
            headers['Content-Type'] = 'application/json; charset=utf-8'

        headers['Accept'] = 'application/json'

        # construct the full URL without query parameters
        if uri_path[0] == '/':
            uri_path = uri_path[1:]
        url = '%s/%s' % (self.base_url, uri_path)

        http_status, resp_data, consume_time = -1, None, None
        for i in range(retry):
            try:
                before_time = int(time.time() * 1000)
                response = self.http_service.request(http_method, url, params=query_params,
                                                     headers=headers, data=data,
                                                     files=files, timeout=timeout)
                consume_time = int(time.time() * 1000) - before_time

                content_type = response.headers.get('content-type', 'application/json')
                # xml
                if 'xml' in content_type:
                    resp_data = xml_to_dict(response.content)
                else:
                    resp_data = response.json()
            except RequestException as e:
                logger.error('请求异常 {url} {exc}'.format(url=url, exc=e), exc_info=True)
                continue
            except Exception as e:
                logger.error('请求异常 {url} {exc}'.format(url=url, exc=e), exc_info=True)
                return -1, None
            else:
                http_status = response.status_code
                break
        if http_status not in [200, 201]:
            logger.info("请求失败")
        else:
            logger.info("请求成功")
        logger.info('{url} {data} {status} {resp_data} 耗时{consume_time} '.format(
                url=url, data=data, status=http_status, resp_data=resp_data, consume_time=consume_time))

        return http_status, resp_data

    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request("POST", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request("PUT", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request("DELETE", *args, **kwargs)


