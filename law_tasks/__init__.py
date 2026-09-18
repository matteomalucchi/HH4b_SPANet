"""law tasks automating the SPANet training -> prediction -> performance chain.

The package is deliberately free of user specific paths: every location is
resolved by :mod:`law_tasks.config` from ``law.cfg``, environment variables or
generic ``$USER`` based defaults.
"""
