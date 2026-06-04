"""SolOSDK — shared toolkit for Sol OS actors, workers, and agents."""

__version__ = "0.1.0"

# Top-level imports for main submodules
from sol import auth, config, notion, platforms, runs

__all__ = ["auth", "config", "notion", "platforms", "runs", "__version__"]
