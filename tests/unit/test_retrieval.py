import io
import json

from supplyguard.retrieval import pypi


def test_get_package_artifact_prefers_pypi_current_version(tmp_path, monkeypatch):
    payload = {
        "info": {"version": "1.10"},
        "releases": {
            "1.9": [{"packagetype": "bdist_wheel", "url": "https://files.pythonhosted.org/old.whl"}],
            "1.10": [{"packagetype": "bdist_wheel", "url": "https://files.pythonhosted.org/current.whl"}],
        },
    }
    requested_urls = []

    def fake_urlopen(url, timeout):
        requested_urls.append(url)
        content = json.dumps(payload).encode() if url.endswith("/json") else b"wheel bytes"
        return io.BytesIO(content)

    monkeypatch.setattr(pypi.urllib.request, "urlopen", fake_urlopen)

    artifact_path, artifact_type = pypi.get_package_artifact("example", str(tmp_path))

    assert requested_urls[-1] == "https://files.pythonhosted.org/current.whl"
    assert artifact_path.endswith("current.whl")
    assert artifact_type == "bdist_wheel"
    assert (tmp_path / "current.whl").read_bytes() == b"wheel bytes"