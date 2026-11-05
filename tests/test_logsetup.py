import logging

from bloguero import logsetup


def test_setup_writes_caught_exceptions_to_the_log_file(tmp_path, monkeypatch):
    monkeypatch.setattr(logsetup, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(logsetup, "LOG_PATH", tmp_path / "bloguero.log")
    root = logging.getLogger("bloguero")
    handlers_before = list(root.handlers)
    try:
        logsetup.setup()
        try:
            raise TimeoutError("sin respuesta de Blogger")
        except TimeoutError:
            logging.getLogger("bloguero.ui.window").exception("Falló _login_worker")
        for handler in root.handlers:
            handler.flush()

        text = (tmp_path / "bloguero.log").read_text(encoding="utf-8")
        assert "Falló _login_worker" in text
        assert "TimeoutError: sin respuesta de Blogger" in text
    finally:
        for handler in list(root.handlers):
            if handler not in handlers_before:
                root.removeHandler(handler)
                handler.close()
