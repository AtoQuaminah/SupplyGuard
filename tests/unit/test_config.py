from supplyguard.config import DEFAULT_CONFIG


def test_default_config_exists():
    assert DEFAULT_CONFIG.scanner_version == "0.1.0"
    assert DEFAULT_CONFIG.score_warning_threshold > 0
