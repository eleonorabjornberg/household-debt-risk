"""Raw-download provenance: manifest lines, content-addressed immutable store, api_key redaction.
No network: requests.get/head are replaced by a fake that serves fixed bytes."""
from __future__ import annotations

import hashlib
import io
import json
import zipfile

import pytest
import requests

from hhdebt import config
from hhdebt import extract as ex
from hhdebt.extract import fred, nyfed, z1


class FakeResp:
    def __init__(self, content: bytes, status: int = 200, headers: dict | None = None, url: str = ""):
        self.content, self.status_code, self.headers, self.url = content, status, headers or {}, url

    def __enter__(self): return self
    def __exit__(self, *a): return False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} for url: {self.url}")

    def iter_content(self, chunk_size=1):
        for i in range(0, len(self.content), 3):   # tiny chunks exercise the streaming path
            yield self.content[i:i + 3]


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)
    served = {}  # url-substring -> bytes or (bytes, status, headers)

    def fake_get(url, headers=None, params=None, stream=False, timeout=None, allow_redirects=True, **kw):
        full = requests.Request("GET", url, params=params).prepare().url
        for key, val in served.items():
            if key in full:
                body, status, hdrs = val if isinstance(val, tuple) else (val, 200, {})
                return FakeResp(body, status, hdrs, full)
        return FakeResp(b"", 404, {}, full)

    monkeypatch.setattr(requests, "get", fake_get)
    return tmp_path, served


def manifest(tmp_path):
    p = tmp_path / "data" / "manifest.jsonl"
    return [json.loads(line) for line in p.read_text().splitlines()]


def test_fields_hash_and_redaction(env):
    tmp, served = env
    served["series/observations"] = b'{"observations": []}'
    rec = ex.download_raw("fred", f"{config.FRED_API_URL}/series/observations", "X_observations.json",
                          params={"series_id": "X", "api_key": "SECRETKEY123", "file_type": "json"}, vintage="2026-01-02")
    (m,) = manifest(tmp)
    payload = b'{"observations": []}'
    assert m["source"] == "fred" and m["http_status"] == 200 and m["vintage"] == "2026-01-02"
    assert m["bytes"] == len(payload) and m["sha256"] == hashlib.sha256(payload).hexdigest()
    assert m["url"].startswith(f"{config.FRED_API_URL}/series/observations?")
    assert "api_key=REDACTED" in m["url"] and "series_id=X" in m["url"] and "SECRETKEY123" not in m["url"]
    assert m["path"] == f"data/raw/fred/{m['sha256'][:16]}_X_observations.json"
    assert (tmp / m["path"]).read_bytes() == payload and rec.path == tmp / m["path"]
    assert m["retrieved_at"].endswith("+00:00") and m["source_path"] is None
    assert "SECRETKEY123" not in (tmp / "data" / "manifest.jsonl").read_text()


def test_immutable_and_content_addressed(env):
    tmp, served = env
    url = "https://example.org/a.csv"
    served["a.csv"] = b"v1"
    ex.download_raw("fred", url, "a.csv")
    first = manifest(tmp)[0]
    path = tmp / first["path"]
    mtime = path.stat().st_mtime_ns
    ex.download_raw("fred", url, "a.csv")                      # same bytes: reuse file, new line
    assert len(list(path.parent.glob("*_a.csv"))) == 1 and path.stat().st_mtime_ns == mtime
    assert len(manifest(tmp)) == 2 and manifest(tmp)[1]["path"] == first["path"]
    served["a.csv"] = b"v2"                                    # different bytes: second file, first intact
    ex.download_raw("fred", url, "a.csv")
    assert len(list(path.parent.glob("*_a.csv"))) == 2 and path.read_bytes() == b"v1"
    assert manifest(tmp)[2]["path"] != first["path"]
    assert not list(path.parent.glob(".*.part"))


def test_failed_download_records_nothing_and_hides_key(env):
    tmp, served = env
    with pytest.raises(RuntimeError) as e:
        ex.download_raw("fred", "https://x.org/s", "s.json", params={"api_key": "SECRETKEY123"})
    assert "SECRETKEY123" not in str(e.value)
    assert not (tmp / "data" / "manifest.jsonl").exists()
    assert not list((tmp / "data" / "raw" / "fred").glob("*"))


def test_fred_csv_and_api_paths(env, monkeypatch):
    tmp, served = env
    served["fredgraph.csv"] = b"observation_date,X\n2020-01-01,1.5\n2020-02-01,.\n"
    df, vintage = fred._via_csv("X")
    assert list(df.columns) == ["date", "value"] and len(df) == 2
    m = manifest(tmp)[-1]
    assert m["url"] == config.FRED_CSV_URL.format(id="X") and m["vintage"] == vintage.isoformat()

    served.clear()
    served["/series/observations"] = b'{"observations": [{"date": "2020-01-01", "value": "2"}]}'
    served["/series?"] = b'{"seriess": [{"last_updated": "2026-05-06 08:00:00-05"}]}'
    df, lu = fred._via_api("X", "KEYKEY")
    assert df.value.tolist() == ["2"] and str(lu) == "2026-05-06"
    lines = manifest(tmp)[-2:]
    assert all("api_key=REDACTED" in m["url"] for m in lines)
    assert lines[1]["vintage"] == "2026-05-06" and lines[0]["vintage"] is None
    assert "KEYKEY" not in (tmp / "data" / "manifest.jsonl").read_text()


def _zip_bytes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(zipfile.ZipInfo("Z1.csv", (2026, 9, 11, 0, 0, 0)), b"series_name,date,value\n")
    return buf.getvalue()


def test_z1_download_then_cache_reuse(env, monkeypatch):
    tmp, served = env
    payload = _zip_bytes()
    served["FRB_Z1_csv.zip"] = payload
    monkeypatch.setattr(requests, "head", lambda *a, **k: type("H", (), {"headers": {"content-length": str(len(payload))}})())
    dest = tmp / "data" / "z1" / "FRB_Z1_csv.zip"
    assert z1.download_zip() == dest and dest.read_bytes() == payload
    (m,) = manifest(tmp)
    assert m["url"] == config.Z1_ZIP_URL and m["vintage"] == "2026-09-11"
    assert m["sha256"] == hashlib.sha256(payload).hexdigest() and (tmp / m["path"]).read_bytes() == payload
    z1.download_zip()                                          # cache current: no new download, no duplicate line
    assert len(manifest(tmp)) == 1


def test_z1_preexisting_cache_is_registered_once(env, monkeypatch):
    tmp, served = env
    payload = _zip_bytes()
    dest = tmp / "data" / "z1" / "FRB_Z1_csv.zip"
    dest.parent.mkdir(parents=True)
    dest.write_bytes(payload)
    monkeypatch.setattr(requests, "head", lambda *a, **k: type("H", (), {"headers": {"content-length": str(len(payload))}})())
    z1.download_zip(); z1.download_zip()
    (m,) = manifest(tmp)
    assert m["url"] is None and m["source_path"] == "data/z1/FRB_Z1_csv.zip" and m["http_status"] is None
    assert m["sha256"] == hashlib.sha256(payload).hexdigest() and (tmp / m["path"]).read_bytes() == payload


def test_local_shortcuts(env):
    tmp, _ = env
    zp = tmp / "mine.zip"
    zp.write_bytes(_zip_bytes())
    ex.record_local("z1", zp, vintage="2026-09-11")
    ex.record_local("z1", zp)                                  # shortcuts log every use
    xl = tmp / "w.xlsx"
    xl.write_bytes(b"PKfake")
    ex.record_local("nyfed", xl)
    a, b, c = manifest(tmp)
    assert a["url"] is None and a["source_path"] == "mine.zip" and a["vintage"] == "2026-09-11"
    assert a["sha256"] == hashlib.sha256(zp.read_bytes()).hexdigest() and a["bytes"] == zp.stat().st_size
    assert a["path"] == b["path"] and c["source"] == "nyfed" and c["path"].startswith("data/raw/nyfed/")


def test_nyfed_probe_records_only_the_accepted_workbook(env):
    tmp, served = env
    served["hhdc"] = (b"<html>no links</html>", 200, {})
    served["HHD_C_Report_2026Q3.xlsx"] = (b"PKxlsx-bytes", 200, {"Last-Modified": "Wed, 01 Oct 2025 12:00:00 GMT"})
    import datetime as dt
    url, content, vintage = nyfed.find_latest_xlsx(dt.date(2026, 11, 3))
    assert url.endswith("HHD_C_Report_2026Q3.xlsx") and content == b"PKxlsx-bytes" and str(vintage) == "2025-10-01"
    page, wb = manifest(tmp)
    assert page["path"].endswith("hhdc_page.html") and wb["vintage"] == "2025-10-01"
    assert wb["url"] == url and wb["bytes"] == len(content)
