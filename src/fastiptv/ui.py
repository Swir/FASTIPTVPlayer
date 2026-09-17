from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .epg import EPGGuide, parse_xmltv
from .i18n import translator
from .models import Channel
from .network import download_epg, download_playlist_text
from .playlist import load_playlist_file, parse_m3u
from .settings import AppSettings, save_settings
from .vlc import VLCError, discover_vlc, launch_vlc

MAX_RENDERED_ROWS = 3000


class TaskSignals(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()


class BackgroundTask(QRunnable):
    def __init__(self, function: Callable[[], Any]) -> None:
        super().__init__()
        self.function = function
        self.signals = TaskSignals()

    def run(self) -> None:
        try:
            self.signals.result.emit(self.function())
        except Exception as exc:  # background/network boundary
            self.signals.error.emit(str(exc))
        finally:
            self.signals.finished.emit()


class FastIPTVWindow(QMainWindow):
    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self.settings = settings
        self.tr = translator()
        self.channels: list[Channel] = []
        self.visible_channels: list[Channel] = []
        self.guide: EPGGuide | None = None
        self.pool = QThreadPool.globalInstance()
        self._tasks: set[BackgroundTask] = set()

        self.setWindowTitle("FastIPTV Player 2 — by Swir")
        self.resize(1120, 710)
        self.setMinimumSize(780, 520)
        self._build_ui()
        self._apply_theme()
        self._refresh_recent_combo()

    def _build_ui(self) -> None:
        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 14)
        root.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("FASTIPTV PLAYER 2")
        title.setObjectName("title")
        subtitle = QLabel("M3U/M3U8 • XMLTV • VLC")
        subtitle.setObjectName("muted")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(subtitle)
        root.addLayout(header)

        primary = QHBoxLayout()
        self.open_file_button = QPushButton(self.tr("open_file"))
        self.open_file_button.clicked.connect(self.open_file)
        primary.addWidget(self.open_file_button)
        self.open_url_button = QPushButton(self.tr("open_url"))
        self.open_url_button.clicked.connect(self.open_url)
        primary.addWidget(self.open_url_button)
        self.epg_button = QPushButton(self.tr("load_epg"))
        self.epg_button.clicked.connect(self.load_epg_url)
        primary.addWidget(self.epg_button)
        self.epg_sources_button = QPushButton(self.tr("epg_sources"))
        self.epg_sources_button.clicked.connect(self.manage_epg_sources)
        primary.addWidget(self.epg_sources_button)
        self.vlc_button = QPushButton(self.tr("vlc_path"))
        self.vlc_button.clicked.connect(self.choose_vlc)
        primary.addWidget(self.vlc_button)
        primary.addStretch(1)
        self.play_button = QPushButton(self.tr("play"))
        self.play_button.clicked.connect(self.play_selected)
        primary.addWidget(self.play_button)
        self.favorite_button = QPushButton(self.tr("favorite"))
        self.favorite_button.clicked.connect(self.toggle_favorite)
        primary.addWidget(self.favorite_button)
        self.copy_button = QPushButton(self.tr("copy_url"))
        self.copy_button.clicked.connect(self.copy_selected_url)
        primary.addWidget(self.copy_button)
        root.addLayout(primary)

        recent = QHBoxLayout()
        recent_label = QLabel(self.tr("recent"))
        recent_label.setObjectName("muted")
        recent.addWidget(recent_label)
        self.recent_combo = QComboBox()
        self.recent_combo.setMinimumWidth(300)
        recent.addWidget(self.recent_combo, 1)
        self.open_recent_button = QPushButton(self.tr("open_recent"))
        self.open_recent_button.clicked.connect(self.open_recent)
        recent.addWidget(self.open_recent_button)
        root.addLayout(recent)

        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(self.tr("search"))
        self.search.textChanged.connect(self.apply_filters)
        filters.addWidget(self.search, 2)
        self.group = QComboBox()
        self.group.addItem(self.tr("all_groups"), "")
        self.group.currentIndexChanged.connect(self.apply_filters)
        filters.addWidget(self.group, 1)
        self.favorites_only = QCheckBox(self.tr("favorites_only"))
        self.favorites_only.stateChanged.connect(self.apply_filters)
        filters.addWidget(self.favorites_only)
        root.addLayout(filters)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            self.tr("channel"), self.tr("group"), self.tr("now"), self.tr("next"), self.tr("status")
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self.play_selected)
        root.addWidget(self.table, 1)

        footer = QHBoxLayout()
        self.status = QLabel(self.tr("ready"))
        self.status.setObjectName("muted")
        footer.addWidget(self.status)
        footer.addStretch(1)
        author = QLabel('by Swir • <a href="https://github.com/Swir">github.com/Swir</a>')
        author.setOpenExternalLinks(True)
        author.setObjectName("author")
        footer.addWidget(author)
        root.addLayout(footer)
        self.setCentralWidget(central)

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #06111e; color: #e8f2ff; font-size: 13px; }
            QLabel#title { font-size: 23px; font-weight: 800; color: #4fb8ff; letter-spacing: 2px; }
            QLabel#muted, QLabel#author { color: #7992aa; }
            QLabel#author a { color: #4fb8ff; }
            QLineEdit, QComboBox { background: #0d1d30; border: 1px solid #294c69; border-radius: 7px; padding: 8px; }
            QLineEdit:focus, QComboBox:focus { border-color: #4fb8ff; }
            QPushButton { background: #12314e; border: 1px solid #2d628b; border-radius: 7px; padding: 8px 11px; font-weight: 600; }
            QPushButton:hover { background: #174566; border-color: #4fb8ff; }
            QPushButton:disabled { color: #52687d; background: #0b1928; }
            QCheckBox { spacing: 7px; }
            QTableWidget { background: #091827; alternate-background-color: #0c1e31; border: 1px solid #203e58; border-radius: 8px; gridline-color: #17334c; }
            QHeaderView::section { background: #10273d; color: #9ed6ff; padding: 8px; border: 0; border-right: 1px solid #20425e; font-weight: 700; }
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:selected { background: #155078; }
            """
        )

    def _set_busy(self, busy: bool) -> None:
        for widget in (
            self.open_file_button,
            self.open_url_button,
            self.open_recent_button,
            self.epg_button,
            self.epg_sources_button,
        ):
            widget.setEnabled(not busy)
        if busy:
            self.status.setText(self.tr("working"))

    def _start_task(self, function: Callable[[], Any], on_result: Callable[[Any], None], on_error_key: str) -> None:
        task = BackgroundTask(function)
        self._tasks.add(task)
        self._set_busy(True)
        task.signals.result.connect(on_result)
        task.signals.error.connect(lambda message: self.status.setText(self.tr(on_error_key, error=message)))

        def finished() -> None:
            self._tasks.discard(task)
            if not self._tasks:
                self._set_busy(False)

        task.signals.finished.connect(finished)
        self.pool.start(task)

    def open_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, self.tr("open_file"), "", "Playlists (*.m3u *.m3u8);;All files (*)")
        if not filename:
            return
        path = Path(filename)
        self._start_task(
            lambda: load_playlist_file(path),
            lambda channels: self._playlist_loaded(channels, path.name, str(path)),
            "playlist_error",
        )

    def open_url(self) -> None:
        url, accepted = QInputDialog.getText(self, self.tr("open_url"), self.tr("url_prompt"))
        url = url.strip()
        if not accepted or not url:
            return
        self._start_task(
            lambda: parse_m3u(download_playlist_text(url)),
            lambda channels: self._playlist_loaded(channels, url, url),
            "playlist_error",
        )

    def _refresh_recent_combo(self) -> None:
        current = self.recent_combo.currentData()
        self.recent_combo.blockSignals(True)
        self.recent_combo.clear()
        for source in self.settings.recent_playlists:
            label = source if len(source) <= 100 else f"{source[:97]}…"
            self.recent_combo.addItem(label, source)
        if current:
            index = self.recent_combo.findData(current)
            if index >= 0:
                self.recent_combo.setCurrentIndex(index)
        self.recent_combo.blockSignals(False)
        self.open_recent_button.setEnabled(bool(self.settings.recent_playlists) and not self._tasks)

    def open_recent(self) -> None:
        source = str(self.recent_combo.currentData() or "").strip()
        if not source:
            self.status.setText(self.tr("recent_empty"))
            return
        if source.lower().startswith(("http://", "https://")):
            self._start_task(
                lambda: parse_m3u(download_playlist_text(source)),
                lambda channels: self._playlist_loaded(channels, source, source),
                "playlist_error",
            )
            return
        path = Path(source).expanduser()
        if not path.is_file():
            self.status.setText(self.tr("recent_missing", source=source))
            return
        self._start_task(
            lambda: load_playlist_file(path),
            lambda channels: self._playlist_loaded(channels, path.name, str(path)),
            "playlist_error",
        )

    def _playlist_loaded(self, channels: list[Channel], source: str, recent: str) -> None:
        self.channels = channels
        if recent:
            self.settings.recent_playlists = [recent] + [item for item in self.settings.recent_playlists if item != recent]
            self.settings.recent_playlists = self.settings.recent_playlists[:10]
            save_settings(self.settings)
            self._refresh_recent_combo()
        self._rebuild_groups()
        self.apply_filters()
        self.status.setText(self.tr("loaded", count=len(channels), source=source))

    def _rebuild_groups(self) -> None:
        current = self.group.currentData() or ""
        groups = sorted({channel.group for channel in self.channels}, key=str.casefold)
        self.group.blockSignals(True)
        self.group.clear()
        self.group.addItem(self.tr("all_groups"), "")
        for value in groups:
            self.group.addItem(value, value)
        index = self.group.findData(current)
        self.group.setCurrentIndex(index if index >= 0 else 0)
        self.group.blockSignals(False)

    def load_epg_url(self) -> None:
        sources = list(self.settings.epg_sources)
        new_label = self.tr("new_epg_source")
        if sources:
            choice, accepted = QInputDialog.getItem(
                self,
                self.tr("load_epg"),
                self.tr("epg_prompt"),
                sources + [new_label],
                0,
                False,
            )
            if not accepted:
                return
            if choice == new_label:
                url, accepted = QInputDialog.getText(self, self.tr("load_epg"), self.tr("epg_prompt"))
            else:
                url = choice
        else:
            url, accepted = QInputDialog.getText(self, self.tr("load_epg"), self.tr("epg_prompt"), text=self.settings.epg_url)
        url = str(url).strip()
        if not accepted or not url:
            return
        if not url.lower().startswith(("http://", "https://")):
            self.status.setText(self.tr("epg_error", error="EPG source must use http:// or https://"))
            return
        if url not in self.settings.epg_sources:
            self.settings.epg_sources.insert(0, url)
            self.settings.epg_sources = self.settings.epg_sources[:25]
        self.settings.epg_url = url
        save_settings(self.settings)
        self._start_task(lambda: parse_xmltv(download_epg(url)), lambda guide: self._epg_loaded(guide, url), "epg_error")

    def manage_epg_sources(self) -> None:
        actions = [self.tr("add_epg_source"), self.tr("remove_epg_source")]
        action, accepted = QInputDialog.getItem(
            self,
            self.tr("epg_sources"),
            self.tr("epg_manage_prompt"),
            actions,
            0,
            False,
        )
        if not accepted:
            return
        if action == self.tr("add_epg_source"):
            url, accepted = QInputDialog.getText(self, self.tr("epg_sources"), self.tr("epg_prompt"))
            url = url.strip()
            if not accepted or not url:
                return
            if not url.lower().startswith(("http://", "https://")):
                self.status.setText(self.tr("epg_error", error="EPG source must use http:// or https://"))
                return
            if url not in self.settings.epg_sources:
                self.settings.epg_sources.insert(0, url)
                self.settings.epg_sources = self.settings.epg_sources[:25]
            self.settings.epg_url = url
            save_settings(self.settings)
            self.status.setText(self.tr("epg_source_added"))
            return

        if not self.settings.epg_sources:
            self.status.setText(self.tr("epg_source_none"))
            return
        source, accepted = QInputDialog.getItem(
            self,
            self.tr("epg_sources"),
            self.tr("remove_epg_source"),
            self.settings.epg_sources,
            0,
            False,
        )
        if not accepted or not source:
            return
        self.settings.epg_sources = [item for item in self.settings.epg_sources if item != source]
        if self.settings.epg_url == source:
            self.settings.epg_url = self.settings.epg_sources[0] if self.settings.epg_sources else ""
        save_settings(self.settings)
        self.status.setText(self.tr("epg_source_removed"))

    def _epg_loaded(self, guide: EPGGuide, url: str) -> None:
        self.guide = guide
        self.settings.epg_url = url
        if url not in self.settings.epg_sources:
            self.settings.epg_sources.insert(0, url)
            self.settings.epg_sources = self.settings.epg_sources[:25]
        save_settings(self.settings)
        self.apply_filters()
        self.status.setText(self.tr("epg_loaded", count=len(guide.names)))

    def choose_vlc(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, self.tr("vlc_path"), self.settings.vlc_path or "", "VLC (vlc.exe vlc);;All files (*)")
        if filename:
            self.settings.vlc_path = filename
            save_settings(self.settings)
            self.status.setText(filename)

    def apply_filters(self) -> None:
        needle = self.search.text().strip().casefold()
        group = str(self.group.currentData() or "")
        favorites_only = self.favorites_only.isChecked()
        favorites = set(self.settings.favorites)
        matches: list[Channel] = []
        for channel in self.channels:
            if group and channel.group != group:
                continue
            if favorites_only and channel.favorite_key not in favorites:
                continue
            if needle and needle not in channel.name.casefold() and needle not in channel.group.casefold() and needle not in channel.tvg_id.casefold():
                continue
            matches.append(channel)
        total = len(matches)
        self.visible_channels = matches[:MAX_RENDERED_ROWS]
        self._render_table()
        if total > MAX_RENDERED_ROWS:
            self.status.setText(self.tr("display_limit", shown=MAX_RENDERED_ROWS, total=total))

    def _render_table(self) -> None:
        favorites = set(self.settings.favorites)
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.visible_channels))
        for row, channel in enumerate(self.visible_channels):
            favorite = channel.favorite_key in favorites
            channel_item = QTableWidgetItem(("★ " if favorite else "") + channel.name)
            channel_item.setData(Qt.ItemDataRole.UserRole, channel)
            group_item = QTableWidgetItem(channel.group)
            current_title = "—"
            next_title = "—"
            if self.guide:
                current, upcoming = self.guide.current_next(channel)
                current_title = current.title if current else "—"
                next_title = upcoming.title if upcoming else "—"
            current_item = QTableWidgetItem(current_title)
            next_item = QTableWidgetItem(next_title)
            status_item = QTableWidgetItem("Favorite" if favorite else "Ready")
            if favorite:
                channel_item.setForeground(QColor("#ffd65a"))
            self.table.setItem(row, 0, channel_item)
            self.table.setItem(row, 1, group_item)
            self.table.setItem(row, 2, current_item)
            self.table.setItem(row, 3, next_item)
            self.table.setItem(row, 4, status_item)
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, min(max(self.table.columnWidth(0), 220), 380))
        self.table.setColumnWidth(2, min(max(self.table.columnWidth(2), 220), 420))
        self.table.setColumnWidth(3, min(max(self.table.columnWidth(3), 220), 420))

    def _selected_channel(self) -> Channel | None:
        row = self.table.currentRow()
        if row < 0:
            self.status.setText(self.tr("no_selection"))
            return None
        item = self.table.item(row, 0)
        channel = item.data(Qt.ItemDataRole.UserRole) if item else None
        if isinstance(channel, Channel):
            return channel
        self.status.setText(self.tr("no_selection"))
        return None

    def play_selected(self, *_args) -> None:
        channel = self._selected_channel()
        if not channel:
            return
        executable = discover_vlc(self.settings.vlc_path)
        if not executable:
            self.status.setText(self.tr("vlc_missing"))
            return
        try:
            launch_vlc(channel.url, executable)
        except VLCError as exc:
            self.status.setText(self.tr("vlc_error", error=exc))
            return
        self.status.setText(self.tr("vlc_started", name=channel.name))

    def toggle_favorite(self) -> None:
        channel = self._selected_channel()
        if not channel:
            return
        key = channel.favorite_key
        if key in self.settings.favorites:
            self.settings.favorites.remove(key)
            message = self.tr("favorite_removed", name=channel.name)
        else:
            self.settings.favorites.append(key)
            message = self.tr("favorite_added", name=channel.name)
        save_settings(self.settings)
        self.apply_filters()
        self.status.setText(message)

    def copy_selected_url(self) -> None:
        channel = self._selected_channel()
        if not channel:
            return
        QApplication.clipboard().setText(channel.url)
        self.status.setText(self.tr("copied"))

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt API name
        save_settings(self.settings)
        self.pool.waitForDone(1500)
        super().closeEvent(event)
