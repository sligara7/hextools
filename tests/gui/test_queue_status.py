import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("qtpy")
pytest.importorskip("bluesky_widgets")

import bluesky.plans as bp  # noqa: E402
from bluesky import RunEngine  # noqa: E402
from IPython.core.interactiveshell import InteractiveShell  # noqa: E402
from ophyd.sim import det  # noqa: E402  # type: ignore
from qtpy.QtCore import QPoint, Qt  # noqa: E402
from qtpy.QtTest import QTest  # noqa: E402
from qtpy.QtWidgets import QApplication, QTabWidget  # noqa: E402

from hextools.gui.__main__ import QtDataAcquisitionWindow  # noqa: E402
from hextools.gui.queue_status import QtQueueStatus  # noqa: E402
from hextools.plan_queue import PlanQueue  # noqa: E402


def _queue() -> PlanQueue:
    QApplication.instance() or QApplication([])
    return PlanQueue(RunEngine({}))


def test_status_shows_the_first_five_pending_and_how_many_more():
    queue = _queue()
    items = [queue.add(bp.count, [det], num=n) for n in range(1, 8)]
    status = QtQueueStatus(queue)

    assert status.pending_lines() == [
        f"{i}. {item}" for i, item in enumerate(items[:5], 1)
    ] + ["+2 more"]
    assert status.state_text() == "idle, 7 pending"


def test_status_says_when_the_queue_is_empty():
    status = QtQueueStatus(_queue())

    assert status.pending_lines() == ["Empty"]
    assert status.state_text() == "idle, 0 pending"


def test_status_follows_edits_made_at_the_prompt():
    queue = _queue()
    status = QtQueueStatus(queue)
    item = queue.add(bp.count, [det])

    status.refresh()

    assert status.pending_lines() == [f"1. {item}"]


def test_clicking_queue_status_opens_the_queue_tab():
    app = QApplication.instance() or QApplication([])
    shell = InteractiveShell.instance()
    RE = RunEngine({})
    shell.user_ns.update(RE=RE, queue=PlanQueue(RE))
    window = QtDataAcquisitionWindow(re_client=RE)
    try:
        selector = window.qt_widget
        tabs = selector.findChild(QTabWidget, "mainViewerTabs")
        assert tabs.currentWidget() is not selector.queue_panel

        status = selector.queue_status
        QTest.mouseClick(status, Qt.MouseButton.LeftButton, pos=QPoint(5, 5))
        app.processEvents()

        assert tabs.currentWidget() is selector.queue_panel
    finally:
        window._qt_window.close()
        shell.user_ns.pop("queue", None)
