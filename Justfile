cat:
    cat {{justfile()}}

run:
    uv run start.py

compile_ui:
    pyuic5 "jive/tabs.ui" -o "jive/showTabs.py"
    sed -i "s/import icons_rc/from jive import icons_rc/g" "jive/showTabs.py"

    pyuic5 "jive/urllist.ui" -o "jive/showUrlList.py"
    sed -i "s/import icons_rc/from jive import icons_rc/g" "jive/showUrlList.py"

    pyuic5 "jive/folding.ui" -o "jive/showFolding.py"
    sed -i "s/import icons_rc/from jive import icons_rc/g" "jive/showFolding.py"

compile_rc:
    pyrcc5 "jive/icons.qrc" -o "jive/icons_rc.py"

compile: compile_ui compile_rc

test:
    PYTHONPATH=. uv run pytest -vs tests/

mypy:
    uv run mypy --config-file mypy.ini jive/ --exclude /vendor/
