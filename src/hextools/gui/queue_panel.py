"""A panel that shows and drives the plan queue in the IPython session.

The panel works on the same ``queue`` object the operator edits at the IPython
prompt, so the GUI and the prompt always see one queue. It lists the current
item, the pending items and the history, refreshed by polling.

Edits (move up, move down, remove) call the queue directly: the GUI shares the
RunEngine's thread, so an edit lands between two RunEngine steps and is safe
while the queue runs. Run, Resume, Skip and Hold block until the queue holds or
empties, so they are sent to the IPython shell like the plan Run button, never
called on a worker thread, and only when no queue call is already running.
"""

from __future__ import annotations

from bluesky.utils import RunEngineInterrupted
from qtpy.QtCore import QTimer, Signal
from qtpy.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from hextools.gui._ipython import run_in_ipython
from hextools.log import _unwrap_failed_status
from hextools.plan_queue import PlanQueue

QUEUE_NAME = "queue"
"""Name of the :class:`PlanQueue` in the IPython namespace (set by the profile)."""


class QtPlanQueuePanel(QWidget):
    """Show and drive a :class:`PlanQueue` that lives in the IPython namespace.

    Parameters
    ----------
    queue : PlanQueue
        The queue, reachable in the IPython namespace as ``queue_name``.
    parent : QWidget, optional
        Parent widget.
    queue_name : str, optional
        Name of ``queue`` in the IPython namespace. Default ``"queue"``.
    poll_period : float, optional
        Interval between refreshes, in seconds. Default: 0.5.
    """

    title_changed = Signal(str)

    def __init__(
        self,
        queue: PlanQueue,
        parent=None,
        *,
        queue_name: str = QUEUE_NAME,
        poll_period: float = 0.5,
    ):
        super().__init__(parent)
        self._queue = queue
        self._queue_name = queue_name
        self._busy = False
        self._shown: tuple = ()
        self._title = ""

        self._state_label = QLabel()
        self._current_label = QLabel()
        self._current_label.setWordWrap(True)
        self._pending_list = QListWidget()
        self._pending_list.currentRowChanged.connect(self._update_buttons)
        self._history_list = QListWidget()
        self._status_label = QLabel()
        self._status_label.setWordWrap(True)

        self._up_button = QPushButton("Move Up")
        self._down_button = QPushButton("Move Down")
        self._remove_button = QPushButton("Remove")
        self._run_button = QPushButton("Run Queue")
        self._resume_button = QPushButton("Resume")
        self._skip_button = QPushButton("Skip")
        self._hold_button = QPushButton("Hold")
        self._up_button.clicked.connect(lambda: self._move_selected(-1))
        self._down_button.clicked.connect(lambda: self._move_selected(1))
        self._remove_button.clicked.connect(self._remove_selected)
        self._run_button.setToolTip("Run the pending items in order (queue.run()).")
        self._resume_button.setToolTip(
            "Resume the paused item, or continue a held queue (queue.resume())."
        )
        self._skip_button.setToolTip(
            "Stop the paused item, or drop the item at the front, "
            "then continue (queue.skip())."
        )
        self._hold_button.setToolTip(
            "Abort the paused item, put it back at the front "
            "and free the RunEngine (queue.hold())."
        )
        for button, method in (
            (self._run_button, "run"),
            (self._resume_button, "resume"),
            (self._skip_button, "skip"),
            (self._hold_button, "hold"),
        ):
            button.clicked.connect(lambda _=False, m=method: self._start(m))

        run_row = QHBoxLayout()
        for button in (
            self._run_button,
            self._resume_button,
            self._skip_button,
            self._hold_button,
        ):
            run_row.addWidget(button)
        run_row.addStretch()

        current_box = QGroupBox("Current")
        current_layout = QVBoxLayout(current_box)
        current_layout.addWidget(self._state_label)
        current_layout.addWidget(self._current_label)

        pending_box = QGroupBox("Pending")
        pending_layout = QGridLayout(pending_box)
        pending_layout.addWidget(self._pending_list, 0, 0, 4, 1)
        pending_layout.addWidget(self._up_button, 0, 1)
        pending_layout.addWidget(self._down_button, 1, 1)
        pending_layout.addWidget(self._remove_button, 2, 1)

        history_box = QGroupBox("History (newest first)")
        history_layout = QVBoxLayout(history_box)
        history_layout.addWidget(self._history_list)

        hint = QLabel(
            f"The same queue as <code>{queue_name}</code> at the IPython prompt. "
            "Add plans with each plan's <b>Add to Queue</b> button, or "
            f"<code>{queue_name}.add(plan, ...)</code>."
        )
        hint.setWordWrap(True)

        vbox = QVBoxLayout(self)
        vbox.addWidget(hint)
        vbox.addLayout(run_row)
        vbox.addWidget(self._status_label)
        vbox.addWidget(current_box)
        vbox.addWidget(pending_box, stretch=2)
        vbox.addWidget(history_box, stretch=1)

        self._timer = QTimer(self)
        self._timer.setInterval(int(poll_period * 1000))
        self._timer.timeout.connect(self.refresh)
        self._timer.start()
        self.refresh()

    # -- Display ---------------------------------------------------------------

    def title(self) -> str:
        """Tab title: the pending count, plus the queue state unless idle."""
        state = self._queue.state
        count = len(self._queue.pending)
        return f"Queue ({count})" if state == "idle" else f"Queue ({count}, {state})"

    def refresh(self):
        """Redraw from the queue; lists are rebuilt only when their content changed."""
        queue = self._queue
        pending = queue.pending
        shown = (
            queue.state,
            queue.current,
            tuple((item, str(item)) for item in pending),
            len(queue.history),
        )
        if shown != self._shown:
            self._shown = shown
            self._redraw(pending)
        title = self.title()
        if title != self._title:
            self._title = title
            self.title_changed.emit(title)
        self._update_buttons()

    def _redraw(self, pending):
        queue = self._queue
        self._state_label.setText(f"State: {queue.state}")
        current = queue.current
        self._current_label.setText(str(current) if current is not None else "\u2014")

        row = self._pending_list.currentRow()
        self._pending_list.blockSignals(True)
        self._pending_list.clear()
        self._pending_list.addItems([str(item) for item in pending])
        self._pending_list.setCurrentRow(min(row, len(pending) - 1))
        self._pending_list.blockSignals(False)

        self._history_list.clear()
        for entry in reversed(queue.history):
            runs = len(entry.result.run_start_uids)
            self._history_list.addItem(
                f"{entry.result.exit_status}: {entry.description} ({runs} runs)"
            )

    def _update_buttons(self, *_):
        queue = self._queue
        state = queue.state
        has_pending = bool(queue.pending)
        re_idle = queue.RE.state == "idle"
        free = not self._busy
        self._run_button.setEnabled(
            free and state in ("idle", "held") and has_pending and re_idle
        )
        self._resume_button.setEnabled(
            free
            and (state == "paused" or (state == "held" and has_pending and re_idle))
        )
        self._skip_button.setEnabled(
            free
            and (state == "paused" or (state == "held" and has_pending and re_idle))
        )
        self._hold_button.setEnabled(free and state == "paused")

        row = self._pending_list.currentRow()
        count = self._pending_list.count()
        self._up_button.setEnabled(row > 0)
        self._down_button.setEnabled(0 <= row < count - 1)
        self._remove_button.setEnabled(0 <= row < count)

    # -- Editing ---------------------------------------------------------------

    def _move_selected(self, step: int):
        row = self._pending_list.currentRow()
        if not 0 <= row + step < len(self._queue.pending):
            return
        self._queue.move(row, row + step)
        self.refresh()
        self._pending_list.setCurrentRow(row + step)

    def _remove_selected(self):
        row = self._pending_list.currentRow()
        if not 0 <= row < len(self._queue.pending):
            return
        self._queue.remove(row)
        self.refresh()

    # -- Running ---------------------------------------------------------------

    def _start(self, method: str):
        if self._busy:
            return
        # A second click before the call returns would start a second queue call.
        self._busy = True
        self._update_buttons()
        self._set_status(f"{method.title()}\u2026")
        # Defer so the click handler returns before IPython executes the cell.
        QTimer.singleShot(0, lambda: self._execute(method))

    def _execute(self, method: str):
        try:
            error = run_in_ipython(f"{self._queue_name}.{method}()")
        finally:
            self._busy = False
        self.refresh()
        if isinstance(error, RunEngineInterrupted):
            self._set_status("Paused. Resume, Skip or Hold the current item.")
        elif error is not None:
            cause = _unwrap_failed_status(error)
            self._set_status(f"{type(cause).__name__}: {cause}", error=True)
        elif self._queue.state == "held":
            self._set_status("Held. Resume continues with the next item.")
        else:
            self._set_status("Done.")

    def _set_status(self, message: str, *, error: bool = False):
        self._status_label.setText(message)
        self._status_label.setStyleSheet("color: #DB3526;" if error else "")

    def closeEvent(self, event):
        self._timer.stop()
        super().closeEvent(event)
