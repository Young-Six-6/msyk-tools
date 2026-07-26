import time
from datetime import datetime


VALID_SECONDS = 3600
MAPPING = (6, 7, 8, 9, 10, 1, 0, 3, 2, 5, 4)


def decode(code):
    source = code.upper()
    transformed = list(source)
    for i, char in enumerate(source):
        target = i + 6 if i <= len(source) - 7 else i - (6 if i % 2 == 0 else 4)
        transformed[target] = char

    digits = list(str(int("".join(transformed), 16)))
    key = ""
    for offset in (3, 2, 1):
        index = int(digits[-offset])
        key = digits[index] + key
        del digits[index]

    key = int(key)
    factor = 89 if key % 89 == 0 else 87 if key % 87 == 0 else 0
    return factor, int("".join(digits))


def build_at(timestamp, factor):
    c3, c2, c1 = f"{factor:03d}"

    for d3 in range(10):
        stage2 = list(str(timestamp))
        stage2.insert(d3, c3)
        if int(stage2[-1]) != d3:
            continue

        for d2 in range(10):
            stage1 = stage2.copy()
            stage1.insert(d2, c2)
            if int(stage1[-2]) != d2:
                continue

            for d1 in range(10):
                digits = stage1.copy()
                digits.insert(d1, c1)
                if int(digits[-3]) != d1:
                    continue

                transformed = f"{int(''.join(digits)):X}"
                if len(transformed) != 11:
                    continue

                code = "".join(transformed[target] for target in MAPPING)
                if decode(code) == (factor, timestamp):
                    return code


def generate(factor, now):
    """优先使用当前时间，必要时在当前时间前后 5 分钟内寻找可构造秒数。"""
    for distance in range(301):
        timestamps = (now,) if distance == 0 else (now + distance, now - distance)
        for timestamp in timestamps:
            code = build_at(timestamp, factor)
            if code:
                return code, timestamp
    raise RuntimeError(f"无法生成 factor={factor} 的编码")


def main():
    now = int(time.time())

    for factor in (89, 87):
        code, timestamp = generate(factor, now)
        checked_factor, checked_timestamp = decode(code)
        passed = (
            checked_factor == factor
            and checked_timestamp == timestamp
            and abs(now - timestamp) <= VALID_SECONDS
        )

        print(f"factor     : {factor}")
        print(f"code       : {code}")
        print(f"timestamp  : {timestamp}")
        print(f"self-check : {'OK' if passed else 'FAILED'}")
        print(
            "expires at : "
            + datetime.fromtimestamp(timestamp + VALID_SECONDS).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        print()


if __name__ == "__main__":
    main()
