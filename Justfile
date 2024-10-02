cat:
    cat {{justfile()}}

run:
    uv run start.py

_fn-process-ui in out:
    pyuic5 {{in}} -o {{out}}
    sed -i "s/import icons_rc/from jive import icons_rc/g" {{out}}

compile_ui:
    just _fn-process-ui "jive/tabs.ui" "jive/showTabs.py"
    just _fn-process-ui "jive/urllist.ui" "jive/showUrlList.py"
    just _fn-process-ui "jive/folding.ui" "jive/showFolding.py"

compile_rc:
    pyrcc5 "jive/icons.qrc" -o "jive/icons_rc.py"

compile: compile_ui compile_rc

test:
    PYTHONPATH=. uv run pytest -vs tests/

mypy:
    uv run mypy --config-file mypy.ini jive/ --exclude /vendor/
