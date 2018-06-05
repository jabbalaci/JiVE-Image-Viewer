#!/usr/bin/env python3

if __name__ == "__main__":
    import os
    import sys
    src_dir = os.path.join(os.path.dirname(__file__), "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
# endif

import jive

jive.main()
