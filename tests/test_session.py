from bloguero import session


def test_con_token_se_conecta_haya_o_no_cache():
    assert session.startup_state(True, True) == session.CONNECT
    assert session.startup_state(True, False) == session.CONNECT


def test_sin_token_y_con_cache_ofrece_iniciar_sesion_sin_perder_los_datos_locales():
    assert session.startup_state(False, True) == session.OFFLINE_LOGIN


def test_sin_token_ni_cache_muestra_la_pantalla_de_login():
    assert session.startup_state(False, False) == session.LOGIN
