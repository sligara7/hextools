from pathlib import Path

import pytest
from ophyd_async.core import (
    StaticFilenameProvider,
    StaticPathProvider,
    init_devices,
)
from ophyd_async.epics.adcore import NDPluginBaseIO, NDProcessIO

from hextools.detectors.perkin_elmer import perkin_elmer_factory


@pytest.fixture
def perkin_elmer(RE, tmp_path: Path):
    with init_devices(mock=True):
        det = perkin_elmer_factory(
            StaticPathProvider(StaticFilenameProvider("scan"), tmp_path)
        )
    return det


def test_perkin_elmer_uses_the_hex_pv_prefix(perkin_elmer):
    assert "XF:27ID1-ES{PE-Det:1}cam1:Acquire" in perkin_elmer.driver.acquire.source


def test_perkin_elmer_wires_proc_and_circular_buffer(perkin_elmer):
    """The writer sits behind Proc1, which sits behind CB1.

    The Perkin Elmer free-runs, so frames are pulled out of the circular
    buffer rather than triggered one at a time. If either plugin is missing
    the detector cannot collect at all.
    """
    assert isinstance(perkin_elmer.proc, NDProcessIO)
    assert "XF:27ID1-ES{PE-Det:1}Proc1:NumFilter" in perkin_elmer.proc.num_filter.source

    assert isinstance(perkin_elmer.cb, NDPluginBaseIO)
    assert "XF:27ID1-ES{PE-Det:1}CB1:" in perkin_elmer.cb.nd_array_port.source


def test_perkin_elmer_keeps_its_hyphenated_name(perkin_elmer):
    """The name becomes the asset directory, so a mangled one misfiles data.

    This pins the FACTORY only. The profile separately pokes _name back after
    construction, which is about how devices are auto-initialised there and is
    not what this covers.
    """
    assert perkin_elmer.name == "perkin-elmer"
