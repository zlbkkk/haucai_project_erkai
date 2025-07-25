# encoding: utf-8

import io
import logging
import os
import platform
import time
import unittest
from base64 import b64encode
from datetime import datetime
from typing import Iterable

from jinja2 import Template
try:
    from jinja2 import escape
except ImportError:
    from markupsafe import escape

from httprunner.__about__ import __version__
from httprunner.compat import basestring, bytes, json, numeric_types

logger = logging.getLogger("httprunner")


def get_platform():
    return {
        "httprunner_version": __version__,
        "python_version": "{} {}".format(platform.python_implementation(), platform.python_version()),
        "platform": platform.platform(),
    }


def get_summary(result):
    """get summary from test result"""
    summary = {
        "success": result.wasSuccessful(),
        "stat": {
            "testsRun": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "expectedFailures": len(result.expectedFailures),
            "unexpectedSuccesses": len(result.unexpectedSuccesses),
        },
    }
    summary["stat"]["successes"] = (
        summary["stat"]["testsRun"]
        - summary["stat"]["failures"]
        - summary["stat"]["errors"]
        - summary["stat"]["skipped"]
        - summary["stat"]["expectedFailures"]
        - summary["stat"]["unexpectedSuccesses"]
    )

    if getattr(result, "records", None):
        summary["time"] = {
            "start_at": result.start_at,
            "setup_hooks_duration": result.setup_hooks_duration,
            "teardown_hooks_duration": result.teardown_hooks_duration,
            "duration": result.duration,
        }
        summary["records"] = result.records
    else:
        summary["records"] = []

    if getattr(result, "vars_trace", None):
        summary["vars_trace"]: list[dict] = result.vars_trace
    return summary


def aggregate_stat(origin_stat, new_stat):
    """aggregate new_stat to origin_stat.

    Args:
        origin_stat (dict): origin stat dict, will be updated with new_stat dict.
        new_stat (dict): new stat dict.

    """
    for key in new_stat:
        if key not in origin_stat:
            origin_stat[key] = new_stat[key]
        elif key == "start_at":
            # start datetime
            origin_stat[key] = min(origin_stat[key], new_stat[key])
        else:
            origin_stat[key] += new_stat[key]


def render_html_report(summary, html_report_name=None, html_report_template=None):
    """render html report with specified report name and template
    if html_report_name is not specified, use current datetime
    if html_report_template is not specified, use default report template
    """
    if not html_report_template:
        html_report_template = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "templates",
            "report_template.html",
        )
        logger.debug("No html report template specified, use default.")
    else:
        logger.info("render with html report template: {}".format(html_report_template))

    logger.info("Start to render Html report ...")
    logger.debug("render data: {}".format(summary))

    report_dir_path = os.path.join(os.getcwd(), "reports")
    start_at_timestamp = int(summary["time"]["start_at"])
    summary["time"]["start_datetime"] = datetime.fromtimestamp(start_at_timestamp).strftime("%Y-%m-%d %H:%M:%S")
    if html_report_name:
        summary["html_report_name"] = html_report_name
        report_dir_path = os.path.join(report_dir_path, html_report_name)
        html_report_name += "-{}.html".format(start_at_timestamp)
    else:
        summary["html_report_name"] = ""
        html_report_name = "{}.html".format(start_at_timestamp)

    if not os.path.isdir(report_dir_path):
        os.makedirs(report_dir_path)

    for index, suite_summary in enumerate(summary["details"]):
        if not suite_summary.get("name"):
            suite_summary["name"] = "test suite {}".format(index)
        for record in suite_summary.get("records"):
            meta_data = record["meta_data"]
            stringify_data(meta_data, "request")
            stringify_data(meta_data, "response")

    with io.open(html_report_template, "r", encoding="utf-8") as fp_r:
        template_content = fp_r.read()
        report_path = os.path.join(report_dir_path, html_report_name)
        with io.open(report_path, "w", encoding="utf-8") as fp_w:
            rendered_content = Template(template_content, extensions=["jinja2.ext.loopcontrols"]).render(summary)
            fp_w.write(rendered_content)

    logger.info("Generated Html report: {}".format(report_path))

    return report_path


def stringify_data(meta_data, request_or_response):
    """
    meta_data = {
        "request": {},
        "response": {}
    }
    """
    headers = meta_data[request_or_response]["headers"]
    request_or_response_dict = meta_data[request_or_response]

    for key, value in request_or_response_dict.items():
        if isinstance(value, list):
            value = json.dumps(value, indent=2, ensure_ascii=False)

        elif isinstance(value, bytes):
            try:
                encoding = meta_data["response"].get("encoding")
                if not encoding or encoding == "None":
                    encoding = "utf-8"

                if (
                    request_or_response == "response"
                    and key == "content"
                    and "image" in meta_data["response"]["content_type"]
                ):
                    # display image
                    value = "data:{};base64,{}".format(
                        meta_data["response"]["content_type"],
                        b64encode(value).decode(encoding),
                    )
                else:
                    value = escape(value.decode(encoding))
            except UnicodeDecodeError:
                pass

        elif not isinstance(value, (basestring, numeric_types, Iterable)):
            # class instance, e.g. MultipartEncoder()
            value = repr(value)

        meta_data[request_or_response][key] = value


class HtmlTestResult(unittest.TextTestResult):
    """A html result class that can generate formatted html results.

    Used by TextTestRunner.
    """

    def __init__(self, stream, descriptions, verbosity):
        super(HtmlTestResult, self).__init__(stream, descriptions, verbosity)
        self.records = []
        # before, update, after step_name, step_index, run_times
        self.vars_trace: list[dict] = []

    def _record_test(self, test, status, attachment=""):
        data = {
            "name": test.shortDescription(),
            "status": status,
            "attachment": attachment,
            "meta_data": {},
        }
        if hasattr(test, "meta_data"):
            # client初始化meta_data
            # 经过runner一次性操作http_client_session
            # 最后在HttpRunner再赋值validators和logs
            data["meta_data"] = test.meta_data

        self.records.append(data)

    def startTestRun(self):
        self.start_at = time.time()

    def startTest(self, test):
        """add start test time"""
        super(HtmlTestResult, self).startTest(test)
        logger.info(test.shortDescription())

    def addSuccess(self, test):
        super(HtmlTestResult, self).addSuccess(test)
        self._record_test(test, "success")
        print("")

    def addError(self, test, err):
        super(HtmlTestResult, self).addError(test, err)
        self._record_test(test, "error", self._exc_info_to_string(err, test))
        print("")

    def addFailure(self, test, err):
        super(HtmlTestResult, self).addFailure(test, err)
        self._record_test(test, "failure", self._exc_info_to_string(err, test))
        print("")

    def addSkip(self, test, reason):
        super(HtmlTestResult, self).addSkip(test, reason)
        self._record_test(test, "skipped", reason)
        print("")

    def addExpectedFailure(self, test, err):
        super(HtmlTestResult, self).addExpectedFailure(test, err)
        self._record_test(test, "ExpectedFailure", self._exc_info_to_string(err, test))
        print("")

    def addUnexpectedSuccess(self, test):
        super(HtmlTestResult, self).addUnexpectedSuccess(test)
        self._record_test(test, "UnexpectedSuccess")
        print("")

    @property
    def duration(self):
        case_elapsed = 0
        for record in self.records:
            elapsed_ms = record["meta_data"]["response"]["elapsed_ms"]
            if isinstance(elapsed_ms, (int, float)):
                case_elapsed += record["meta_data"]["response"]["elapsed_ms"]
        # 毫秒转秒级，保留三位
        total_duration = case_elapsed / 1000 + self.setup_hooks_duration + self.teardown_hooks_duration
        return round(total_duration, 3)

    @property
    def setup_hooks_duration(self):
        # 整个case的前置函数消耗时间
        res = 0
        for record in self.records:
            setup_hooks_duration = record["meta_data"]["request"].get("setup_hooks_duration")
            if setup_hooks_duration:
                res += setup_hooks_duration
        return res

    @property
    def teardown_hooks_duration(self):
        # 整个case的后置函数消耗时间
        res = 0
        for record in self.records:
            teardown_hooks_duration = record["meta_data"]["response"].get("teardown_hooks_duration")
            if teardown_hooks_duration:
                res += teardown_hooks_duration
        return res
