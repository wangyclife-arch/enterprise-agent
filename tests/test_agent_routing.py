"""通知请求判断与收件人解析的回归用例（纯函数，无需数据库与密钥）。"""
from app.services.agent_service import _looks_like_notice_request, _parse_notice_args

# ============ bug 1 回归：弱信号单独出现，不能算通知请求 ============


def test_weak_keyword_alone_is_not_notice_request():
    """弱信号词单独出现不算通知请求（这就是 bug 1 的原始场景）"""
    assert _looks_like_notice_request("提醒我一下，3500乘以12等于多少？") is False
    assert _looks_like_notice_request("把结果发送给我") is False
    assert _looks_like_notice_request("告知我一下年假几天") is False
    assert _looks_like_notice_request("明天的会议提醒") is False


def test_plain_questions_are_not_notice_request():
    """普通问题不含任何通知关键词，必须走正常路径"""
    assert _looks_like_notice_request("3500乘以12等于多少？") is False
    assert _looks_like_notice_request("北京今天天气怎么样？") is False
    assert _looks_like_notice_request("年假有几天？") is False


# ============ 正常路径：真正的通知请求必须被认出来 ============


def test_strong_keyword_always_triggers():
    """强信号词出现即认定为通知请求"""
    assert _looks_like_notice_request("发个公告") is True
    assert _looks_like_notice_request("通知张三") is True
    assert _looks_like_notice_request("给张三发一条通知：明天上午10点开周会") is True


def test_weak_keyword_with_recipient_triggers():
    """弱信号词 + 明确收件人 = 通知请求"""
    assert _looks_like_notice_request("给张三发送提醒") is True
    assert _looks_like_notice_request("给李四转告一下") is True


# ============ 收件人解析不能用贪婪匹配 ============


def test_recipient_name_is_not_greedy():
    """非贪婪匹配：不能把"发一条"并入收件人姓名"""
    emp, content = _parse_notice_args("给张三发一条通知：明天上午10点开周会")
    assert emp == "张三"
    assert "开周会" in content


def test_recipient_parsed_for_various_verbs():
    """发 / 发送 / 转告 等不同动词，都要能正确取到收件人"""
    assert _parse_notice_args("给张三发送提醒")[0] == "张三"
    assert _parse_notice_args("给李四转告一下")[0] == "李四"


def test_recipient_falls_back_when_absent():
    """没有明确收件人时返回占位词"员工"，调用方据此就能判断"这不是格式清晰的通知" """
    assert _parse_notice_args("发个公告")[0] == "员工"
    assert _parse_notice_args("明天的会议提醒")[0] == "员工"
