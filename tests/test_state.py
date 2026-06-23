import pytest


def test_state_module_can_be_imported():
    import state
    assert state is not None


def test_state_has_expected_symbols():
    import state
    assert hasattr(state, "client")
    assert hasattr(state, "devs")
    assert hasattr(state, "is_premium")
    assert hasattr(state, "read_json")
    assert hasattr(state, "write_json")
    assert hasattr(state, "PREFIX")
    assert hasattr(state, "COLOR_OK")
    assert hasattr(state, "COLOR_WARN")
    assert hasattr(state, "COLOR_BAD")
    assert hasattr(state, "COLOR_INFO")


def test_state_symbols_default_to_none_or_valid_type():
    import state
    assert state.client is None
    assert state.devs == []
    assert state.PREFIX == "/"
    assert state.COLOR_OK == 0x57F287


def test_state_functions_raise_before_init():
    import state
    with pytest.raises(RuntimeError, match="state not initialized"):
        state.read_json("test")


@pytest.mark.asyncio
async def test_state_async_functions_raise_before_init():
    import state
    with pytest.raises(RuntimeError, match="state not initialized"):
        await state.is_premium(0)
