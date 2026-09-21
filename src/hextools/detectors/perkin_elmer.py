"""Perkin Elmer detector support for HEX beamline."""

from ophyd_async.core import PathProvider
from ophyd_async.epics.adcore import ADWriterFactory, ContAcqDetector


def perkin_elmer_factory(
    path_provider: PathProvider, name: str = "perkin-elmer", num: int = 1
) -> ContAcqDetector:
    """Create the HEX Perkin Elmer as a continuously-acquiring detector.

    The camera free-runs and frames are taken out of a circular buffer, so the
    plugin chain matters: the HDF writer sits behind the process plugin, which
    sits behind the circular buffer. ``cb_suffix`` carries the default the
    beamline's IOC uses.

    Parameters
    ----------
    path_provider : PathProvider
        Where the HDF writer should write. At HEX this is a Windows path
        provider, because the detector host writes to a mapped drive.
    name : str, optional
        The device name, which becomes the asset directory.
    num : int, optional
        The detector number.

    Returns
    -------
    ContAcqDetector
        The Perkin Elmer with its HDF writer, process plugin and circular
        buffer wired up.
    """
    return ContAcqDetector(
        f"XF:27ID1-ES{{PE-Det:{num}}}",
        ADWriterFactory.hdf(path_provider),
        proc_suffix="Proc1:",
        cb_suffix="CB1:",
        name=name,
    )
