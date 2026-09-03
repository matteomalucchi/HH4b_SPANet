"""Task collection, imported by law through the ``[modules]`` section of law.cfg."""

from law_tasks.tasks.training import Training  # noqa: F401
from law_tasks.tasks.predict import Predict  # noqa: F401
from law_tasks.tasks.register import RegisterModel  # noqa: F401
from law_tasks.tasks.plots import (  # noqa: F401
    TrainingMetrics,
    EfficiencyPlot,
    EfficiencyPlots,
    RocPlot,
    RocPlots,
)
from law_tasks.tasks.performance import Performance  # noqa: F401
