#!/usr/bin/env python
# -*- coding:utf-8 –*-

import os
import sys
import time
import json
import requests
import argparse
from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf-8')
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
headers = {"Content-Type": "application/json",
           "Authorization": "Bearer {}".format(ACCESS_TOKEN)}
ATOMCI_SERVER = os.environ['ATOMCI_SERVER']


def print_message(msg):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def check_app_status(atomci_server, cluster, namespace, service_name):
    now = datetime.now()
    url = "{}/atomci/api/v1/clusters/{}/namespaces/{}/apps/{}".format(atomci_server, cluster, namespace, service_name)
    try:
        response = requests.get(url, headers=headers)
    except requests.exceptions.HTTPError as e:
        print_message(e.message)
        return False
    if response.status_code != 200:
        return False
    else:
        pods = []
        data = response.json()
        if isinstance(data, dict):
            pods = data.get('Data', {}).get('pods', [])
        for pod in pods:
            if pod['status'] != "Running":
                return False
    return True

def time_format():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def health_check(cluster, namespace, service_name, app_name, project_id, stage_id, publish_job_id, enable_api_auto_test,
                 enable_ui_auto_test):
    running = False
    print_message("\033[1;34;40m----------容器部署信息----------\033[0m")
    #app_url = "{}/project/service/{}/{}/{}/{}".format(ATOMCI_SERVER, cluster, namespace, service_name, project_id)
    #print_message("\033[1;32;40m| 容器状态: {}\033[0m".format(app_url))
    print_message("\033[1;32;40m-------------------------------\033[0m")
    for i in xrange(1, 121):
        time_str = time_format()
        print_message("\033[1;33;40m[{}]第{}次容器运行状态检查\033[0m".format(time_str, i))
        if check_app_status(ATOMCI_SERVER, cluster, namespace, service_name):
            print_message("\033[1;32;40m成功: {} 容器运行状态检查通过\033[0m".format(service_name))
            running = True
            break

        print_message("\033[1;31;40m错误: {} 容器运行状态检查不通过\033[0m".format(service_name))
        time.sleep(5)

    print_message("\033[1;32;40m----------容器健康检查-Summary----------\033[0m")
    if not running:
        print_message("\033[1;31;40m| 健康检查结果: 不通过\033[0m")
    else:
        print_message("\033[1;34;40m| 健康检查结果: 已通过\033[0m")
    print_message("\033[1;32;40m| 容器状态: {}\033[0m".format(app_url))
    print_message("\033[1;32;40m-------------------------------\033[0m")
    if not running:
        return False
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Apps Health Check")
    parser.add_argument("--project-id", metavar="project_id", type=str,
                        required=True, help="项目ID")
    parser.add_argument("--stage-id", metavar="stage_id", type=str,
                        required=True, help="发布任务类型")
    parser.add_argument("--publish-job-id", metavar="publish_job_id", type=str,
                        required=True, help="发布任务ID")
    parser.add_argument("--cluster",
                        dest="cluster",
                        type=str,
                        required=True)
    parser.add_argument("--namespace",
                        dest="namespace",
                        type=str,
                        required=True,
                        help="命名空间")
    parser.add_argument("--service-name",
                        dest='service_name',
                        type=str,
                        required=True,
                        help="服务名称")
    parser.add_argument("--app-name",
                        dest='app_name',
                        type=str,
                        required=False,
                        help="应用名")
    parser.add_argument("--enable-api-auto-test",
                        dest='enable_api_auto_test',
                        type=str,
                        required=False,
                        help="是否启用接口自动化测试")
    parser.add_argument("--enable-ui-auto-test",
                        dest='enable_ui_auto_test',
                        type=str,
                        required=False,
                        help="是否启用ui自动化测试")
    args = parser.parse_args()

    if not health_check(args.cluster, args.namespace, args.service_name, args.app_name, args.project_id, args.stage_id,
                        args.publish_job_id, args.enable_api_auto_test, args.enable_ui_auto_test):
        sys.exit(1)
    else:
        sys.exit(0)
