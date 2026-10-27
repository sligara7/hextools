"""Compact view of the session's plan queue for the top of the HEX window."""

from __future__ import annotations

from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtWidgets import QFormLayout, QGroupBox, QLabel, QVBoxLayout, QWidget

from hextools.plan_queue import PlanQueue

_SHOWN = 5
_MAX_CHARS = 60


def _elide(text: str) -> str:
    return text if len(text) <= _MAX_CHARS else text[: _MAX_CHARS - 1] + "\u2026"


class QtQueueStatus(QWidget):
    """State, current item and the first five pending items of a :class:`PlanQueue`.

    Clicking anywhere on it emits :attr:`clicked`; the window opens the Queue tab.

    Parameters
    ----------
    queue : PlanQueue
        The session's queue.
    parent : QWidget, optional
        Parent widget.
    poll_period : float, optional
        Interval between refreshes, in seconds. Default: 0.5.
    """

    clicked = Signal()

    def __init__(self, queue: PlanQueue, parent=None, *, poll_period: float = 0.5):
        super().__init__(parent)
        self._queue = queue
        self._shown: tuple = ()
        self._state = QLabel()
        self._current = QLabel()
        self._pending = QLabel()
        self._pending.setTextFormat(Qt.TextFormat.PlainText)

        form = QFormLayout()
        form.setContentsMargins(8, 6, 8, 6)
        form.addRow("Queue:", self._state)
        form.addRow("Current:", self._current)
        form.addRow(QLabel("Next:"))
        form.addRow(self._pending)

        group_box = QGroupBox("Queue Status")
        group_box.setLayout(form)
        vbox = QVBoxLayout(self)
        vbox.addWidget(group_box)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Open the Queue tab to edit, run and see the history.")

        self._timer = QTimer(self)
        self._timer.setInterval(int(poll_period * 1000))
        self._timer.timeout.connect(self.refresh)
        self._timer.start()
        self.refresh()

    def state_text(self) -> str:
        """Return the queue state and the number of pending items."""
        return f"{self._queue.state}, {len(self._queue.pending)} pending"

    def pending_lines(self) -> list[str]:
        """Return the first five pending items, numbered, then how many more."""
        pending = self._queue.pending
        if not pending:
            return ["Empty"]
        lines = [f"{i}. {item}" for i, item in enumerate(pending[:_SHOWN], 1)]
        if len(pending) > _SHOWN:
            lines.append(f"+{len(pending) - _SHOWN} more")
        return lines

    def refresh(self):
        """Redraw from the queue when its content changed."""
        queue = self._queue
        shown = (
            queue.state,
            queue.current,
            tuple((item, str(item)) for item in queue.pending),
        )
        if shown == self._shown:
            return
        self._shown = shown
        self._state.setText(self.state_text())
        current = queue.current
        self._current.setText(_elide(str(current)) if current is not None else "\u2014")
        lines = self.pending_lines()
        self._pending.setText("\n".join(_elide(line) for line in lines))
        self._pending.setToolTip("\n".join(lines))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def closeEvent(self, event):
        self._timer.stop()
        super().closeEvent(event)
