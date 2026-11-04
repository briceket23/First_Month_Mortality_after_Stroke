"""No data-driven feature selection (ticket MODEL-LEAK-002): all candidates enter the L2 model; the penalty is tuned by inner CV. choose_features only applies the missingness ceiling."""
from .stage3_models import choose_features  # noqa: F401
