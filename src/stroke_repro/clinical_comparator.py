"""Clinical-reference comparator: unpenalised logistic regression on config.CLINICAL_REFERENCE, refitted in each training set with the same imputation."""
from . import config as C
from .models import make
PREDICTORS = C.CLINICAL_REFERENCE


def comparator(seed=C.SEED):
    return make('ClinRef', seed)
