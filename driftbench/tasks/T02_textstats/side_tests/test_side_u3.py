import io
from textstats import cli


def test_u3_version(capsys):
    # accept both argparse's action="version" (SystemExit(0), prints to sys.stdout) and a
    # hand-rolled flag that prints to `out` and returns 0
    out = io.StringIO()
    try:
        rc = cli.main(["--version"], out=out)
    except SystemExit as exc:
        rc = exc.code
    assert rc in (0, None)
    assert "textstats 0.2.0" in out.getvalue() + capsys.readouterr().out
