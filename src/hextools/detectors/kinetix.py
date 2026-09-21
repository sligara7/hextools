"""Kinetix detector support for HEX beamline."""

from ophyd_async.epics.adcore import ADWriterFactory
from ophyd_async.epics.adkinetix import KinetixDetector


def kinetix_factory(num: int, path_provider, name: str):
    """Create a KinetixDetector with an HDF writer for the HEX beamline.

    Parameters
    ----------
    num : int
        The detector number.
    path_provider : PathProvider
        The path provider for the HDF writer.
    name : str
        The name of the detector.

    Returns
    -------
    KinetixDetector
        The created Kinetix detector with HDF writer.
    """
    return KinetixDetector(
        f"XF:27ID1-BI{{Kinetix-Det:{num}}}",
        ADWriterFactory.hdf(path_provider),
        proc_suffix="Proc1:",
        name=name,
    )
