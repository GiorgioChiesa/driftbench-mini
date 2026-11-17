import time

import pytest

import build_items as bi
from test_build_items_privacy import KEY, abs_path_episode


def test_leak_at_line_start_is_caught(raw):
    d, _ = abs_path_episode(raw)
    for leak in ("gpt-oss:20b is slow", "m-a is fast"):
        ep, entry = bi.make_item(d, "episode", "", KEY)
        ep["final"] = f"first line\n{leak}"
        with pytest.raises(SystemExit, match="leak check"):
            bi.check_leaks([ep], {ep["id"]: entry})


def test_agent_code_with_none_r_is_not_a_leak(raw):
    d, _ = abs_path_episode(raw)
    ep, entry = bi.make_item(d, "episode", "", KEY)
    ep["final"] = "added test_merge_none_raises and test_x_none_r2"
    bi.check_leaks([ep], {ep["id"]: entry})


def test_sibling_runs_and_host_prefixes_are_scrubbed():
    s = bi.scrub("ls ..\nE1_T01_invoice_gpt-oss-20b_none0_none_r3\nE2_T05_configmerge_qwen3-30b_mix4_anchor_r0\n"
                 "/leonardo_work/IscrC_PhaStSur/ahi/x.py /home/giorgio/p.py /opt/.venv/lib/python3/a.py")
    assert s.splitlines()[1:3] == ["<run>", "<run>"]
    assert "/host/ahi/x.py /home/user/p.py /venv/lib/python3/a.py" in s


def test_leak_check_is_fast_on_large_items():
    items = [{"id": str(n), "type": "segment", "card": "c", "opening": "o", "text": "x" * 14000}
             for n in range(200)]
    t0 = time.time()
    bi.check_leaks(items, {"a": {"model": "gpt-oss:20b"}, "b": {"model": "qwen3-coder:30b"}})
    assert time.time() - t0 < 5


def test_group_tokens_in_agent_code_only_warn(raw, capsys):
    d, _ = abs_path_episode(raw)
    ep, entry = bi.make_item(d, "episode", "", KEY)
    ep["final"] = "text4 = 'a b'\nfor u in ['user1', 'user4']: pass\nnone0 = 1"
    bi.check_leaks([ep], {ep["id"]: entry})
    assert "group token" in capsys.readouterr().err


def test_home_rewrite_skips_urls():
    assert bi.scrub("see https://example.org/home/page and /home/bob/x.py") == \
        "see https://example.org/home/page and /home/user/x.py"


def test_python_and_pytest_versions_are_normalised():
    s = bi.scrub("============ test session starts ============\n"
                 "platform linux -- Python 3.11.16, pytest-8.3.3, pluggy-1.7.0\n"
                 "rootdir: /work\n$ python3 --version\nPython 3.12.0rc1\nPython 3.9.6")
    assert s.splitlines()[1] == "platform linux -- Python 3.x, pytest-x, pluggy-x"
    assert s.splitlines()[-2:] == ["Python 3.x", "Python 3.x"]
    assert "3.11" not in s and "8.3.3" not in s
