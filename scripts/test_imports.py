"""Verify all changes work correctly."""
import py_compile
import os


def main():
    print("=== Syntax check all project files ===")
    files = [
        "state.py", "main.py",
        "cogs/automation.py", "cogs/events.py", "cogs/gacha.py",
        "cogs/giveaway.py", "cogs/moderation.py", "cogs/premium.py",
        "cogs/presence.py", "cogs/reaction_roles.py", "cogs/security.py",
        "cogs/tickets.py", "cogs/utility.py", "cogs/verification.py",
    ]
    all_ok = True
    for f in files:
        try:
            py_compile.compile(f, doraise=True)
            print(f"  OK  {f}")
        except py_compile.PyCompileError as e:
            print(f"  FAIL {f}: {e}")
            all_ok = False

    print()
    print("=== state.py symbols ===")
    import state  # noqa: F811
    print(f"  client: {state.client}")
    print(f"  PREFIX: {state.PREFIX}")
    print(f"  devs: {state.devs}")
    print(f"  COLOR_OK: {hex(state.COLOR_OK)}")

    try:
        state.read_json("test")
        print("  ERROR: read_json did not raise")
        all_ok = False
    except RuntimeError as e:
        print(f"  read_json stub OK: {e}")

    print()
    print("=== No sys.modules['__main__'] references remain ===")
    cog_dir = "cogs"
    exclude = {"__init__.py", "giveaway_views.py", "ticket_views.py"}
    for fname in sorted(os.listdir(cog_dir)):
        if not fname.endswith(".py") or fname in exclude:
            continue
        path = os.path.join(cog_dir, fname)
        content = open(path, encoding="utf-8").read()
        if "__main__" in content:
            print(f"  FAIL: {fname} still has __main__ reference")
            all_ok = False
        else:
            print(f"  OK   {fname}")

    print()
    print("=== Tests ===")
    ret = os.system("python -m pytest tests/ -v")
    if ret != 0:
        all_ok = False

    if all_ok:
        print("\nAll checks passed!")
    else:
        print("\nSome checks FAILED")


if __name__ == "__main__":
    main()
