"""工具层用例：计算器与天气工具（断言针对行为契约，而非具体数据）。"""
from app.tools.calculator import calculator
from app.tools.weather import get_weather


def test_calculator_add():
    assert calculator.func("1+1") == 2


def test_calculator_complex():
    assert calculator.func("(3+5)*2") == 16


def test_weather_returns_city_and_temperature():
    """不管走实时 API 还是降级数据，都必须包含城市名和温度单位"""
    result = get_weather.func("北京")
    assert "北京" in result
    assert "°C" in result
    # 要么是真 API 的数据，要么是降级数据 —— 二者必居其一（说明降级机制生效）
    assert ("实时数据" in result) or ("本地缓存" in result)


def test_weather_unknown_city():
    """查不到的城市：要么明确说'未找到'，要么降级数据里也没有 —— 但不能崩"""
    result = get_weather.func("不存在的城市zzz")
    assert ("未找到" in result) or ("暂无" in result)
