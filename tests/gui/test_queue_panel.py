import os
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("qtpy")
pytest.importorskip("bluesky_widgets")

import bluesky.plans as bp  # noqa: E402
import matplotlib  # noqa: E402
from bluesky import RunEngine  # noqa: E402
from bluesky import plan_stubs as bps  # noqa: E402
from IPython.core.interactiveshell import InteractiveShell  # noqa: E402
from ophyd import Device  # noqa: E402
from ophyd.sim import det, motor  # noqa: E402  # type: ignore
from qtpy.QtCore import QTimer  # noqa: E402
from qtpy.QtWidgets import QApplication  # noqa: E402

from hextools.gui.__main__ import QtDataAcquisitionWindow  # noqa: E402
from hextools.gui.plan_widget import QtPlanWidget  # noqa: E402
from hextools.gui.queue_panel import QtPlanQueuePanel  # noqa: E402
from hextools.plan_queue import PlanQueue  # noqa: E402


def count_dets(detectors: list[Device], num: int = 1):
    yield from bp.count(detectors, num=num)


def _slow_step(detectors, step, pos_cache):
    yield from bps.one_nd_step(detectors, step, pos_cache)
    yield from bps.sleep(0.1)


def _session(with_queue=True):
    """An IPython shell holding RE, devices and maybe ``queue``, as the profile does."""
    # As in the GUI: with a Qt matplotlib backend, RE() keeps Qt events flowing.
    matplotlib.use("qtagg")
    app = QApplication.instance() or QApplication([])
    shell = InteractiveShell.instance()
    RE = RunEngine({})
    shell.user_ns.update(RE=RE, bp=bp, det=det, motor=motor)
    shell.user_ns.pop("queue", None)
    queue = None
    if with_queue:
        queue = PlanQueue(RE)
        shell.user_ns["queue"] = queue
    return app, RE, queue


def _run_until(app, done, timeout=10.0):
    deadline = time.monotonic() + timeout
    timer = QTimer()
    timer.timeout.connect(
        lambda: (done() or time.monotonic() > deadline) and app.quit()
    )
    timer.start(50)
    app.exec()
    timer.stop()


def _pending_texts(panel):
    return [
        panel._pending_list.item(i).text() for i in range(panel._pending_list.count())
    ]


# AJ, 2026-10-26: plans built in the GUI forms go into the same queue IPython edits.
def test_add_to_queue_queues_the_form_plan_with_device_objects():
    _, RE, queue = _session()
    widget = QtPlanWidget(RE, count_dets)
    widget._device_fields[0]["widget"].set_selected_devices(["det"])

    widget._queue_button.click()

    assert len(queue.pending) == 1
    item = queue.pending[0]
    assert item.plan is count_dets
    assert item.kwargs == {"detectors": [det], "num": 1}
    assert RE.state == "idle" and not queue.history  # queued, not run
    assert "1 pending" in widget._status_label.text()


def test_add_to_queue_without_a_queue_says_so():
    _, RE, _ = _session(with_queue=False)
    widget = QtPlanWidget(RE, count_dets)
    widget._device_fields[0]["widget"].set_selected_devices(["det"])

    widget._queue_button.click()

    assert "queue" in widget._status_label.text().lower()
    assert "#DB3526" in widget._status_label.styleSheet()


def test_edit_buttons_reorder_and_remove_pending_items():
    _, _, queue = _session()
    a = queue.add(bp.count, [det])
    b = queue.add(bp.count, [det], num=2)
    c = queue.add(bp.count, [det], num=3)
    panel = QtPlanQueuePanel(queue)
    panel.refresh()
    assert _pending_texts(panel) == [str(a), str(b), str(c)]

    panel._pending_list.setCurrentRow(2)
    panel._up_button.click()
    assert queue.pending == (a, c, b)
    assert panel._pending_list.currentRow() == 1

    panel._down_button.click()
    assert queue.pending == (a, b, c)
    assert panel._pending_list.currentRow() == 2

    panel._remove_button.click()
    assert queue.pending == (a, b)
    assert _pending_texts(panel) == [str(a), str(b)]


def test_run_button_runs_the_queue_in_the_shell():
    app, _, queue = _session()
    queue.add(bp.count, [det])
    queue.add(bp.scan, [det], motor, 0, 1, 3)
    panel = QtPlanQueuePanel(queue)
    panel.refresh()
    assert panel._run_button.isEnabled()
    assert not panel._resume_button.isEnabled()
    assert panel.title() == "Queue (2)"

    QTimer.singleShot(0, panel._run_button.click)
    _run_until(app, lambda: len(queue.history) == 2)
    panel.refresh()

    assert [e.result.exit_status for e in queue.history] == ["success", "success"]
    assert queue.state == "idle" and not queue.pending
    assert panel.title() == "Queue (0)"
    assert panel._history_list.count() == 2


@pytest.mark.parametrize(
    ("button", "statuses", "state", "pending", "at_end"),
    [
        ("resume", ["success", "success"], "idle", 0, True),
        ("skip", ["success", "success"], "idle", 0, False),
        ("hold", ["abort"], "held", 2, False),
    ],
)
def test_a_paused_queue_continues_from_the_panel(
    button, statuses, state, pending, at_end
):
    app, RE, queue = _session()
    scan = queue.add(bp.scan, [det], motor, 0, 1, 10, per_step=_slow_step)
    queue.add(bp.count, [det])
    panel = QtPlanQueuePanel(queue)
    enabled = {}

    def press():
        panel.refresh()
        enabled.update(
            run=panel._run_button.isEnabled(),
            resume=panel._resume_button.isEnabled(),
            skip=panel._skip_button.isEnabled(),
            hold=panel._hold_button.isEnabled(),
        )
        getattr(panel, f"_{button}_button").click()

    QTimer.singleShot(0, panel._run_button.click)
    QTimer.singleShot(300, lambda: RE.request_pause(False))
    QTimer.singleShot(800, press)
    _run_until(
        app,
        lambda: (
            queue.state != "paused"
            and len(queue.history) == len(statuses)
            and RE.state == "idle"
            and enabled
        ),
    )
    panel.refresh()

    assert enabled == {"run": False, "resume": True, "skip": True, "hold": True}
    assert [e.result.exit_status for e in queue.history] == statuses
    assert queue.state == state
    assert len(queue.pending) == pending
    assert bool(motor.position == pytest.approx(1)) is at_end
    if button == "hold":
        assert queue.pending[0] is scan
        assert panel.title() == "Queue (2, held)"


def test_the_window_has_a_queue_tab_when_the_session_has_a_queue():
    _, RE, queue = _session()
    window = QtDataAcquisitionWindow(re_client=RE)
    try:
        assert window.qt_widget.queue_panel is not None
        assert window.qt_widget.queue_panel._queue is queue
    finally:
        window._qt_window.close()
