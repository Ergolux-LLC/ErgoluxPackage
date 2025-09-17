import os
import importlib
import pkgutil
from sqlalchemy.orm import DeclarativeMeta, declarative_base

Base: DeclarativeMeta = declarative_base()

# Automatically import all modules in this package
package_dir = os.path.dirname(__file__)
package_name = __name__

for _, module_name, is_pkg in pkgutil.iter_modules([package_dir]):
    if not is_pkg and module_name != "__init__":
        importlib.import_module(f"{package_name}.{module_name}")