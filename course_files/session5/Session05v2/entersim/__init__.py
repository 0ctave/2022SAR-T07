"""entersim."""
import sys
print("Colored output enabled")
from IPython.core import ultratb
sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=False)
