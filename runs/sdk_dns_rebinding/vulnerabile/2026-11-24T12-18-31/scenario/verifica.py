import os
import sys

print("eseguito" if os.path.exists(os.path.join("/tmp/eseguiti", sys.argv[1])) else "non_eseguito")
