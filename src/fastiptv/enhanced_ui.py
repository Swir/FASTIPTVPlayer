from __future__ import annotations

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QInputDialog

from .settings import save_settings
from .ui import FastIPTVWindow
from .vlc import VLCError, discover_vlc, launch_vlc, normalize_http_proxy


class EnhancedFastIPTVWindow(FastIPTVWindow):
    """v2.2 compatibility layer for useful classic playback workflows.

    The classic program offered proxy playback but mixed it with automatic public
    proxy-list harvesting and testing. v2.2 restores only the safe/manual part:
    the user may provide a proxy they already control or are authorized to use.
    """

    def __init__(self, settings, *, smoke_mode: bool = False) -> None:
        super().__init__(settings)
        self._install_playback_menu()
        if smoke_mode:
            self.status.setText(self.tr("smoke_ready"))

    def _install_playback_menu(self) -> None:
        menu = self.menuBar().addMenu(self.tr("playback"))
        action = QAction(self.tr("manual_proxy"), self)
        action.triggered.connect(self.configure_manual_proxy)
        menu.addAction(action)
        self.proxy_action = action

    def configure_manual_proxy(self) -> None:
        value, accepted = QInputDialog.getText(
            self,
            self.tr("manual_proxy"),
            self.tr("proxy_prompt"),
            text=self.settings.proxy_url,
        )
        if not accepted:
            return
        try:
            proxy = normalize_http_proxy(value)
        except VLCError as exc:
            self.status.setText(self.tr("proxy_error", error=exc))
            return
        self.settings.proxy_url = proxy
        save_settings(self.settings)
        if proxy:
            self.status.setText(self.tr("proxy_enabled", proxy=proxy))
        else:
            self.status.setText(self.tr("proxy_disabled"))

    def play_selected(self, *_args) -> None:
        channel = self._selected_channel()
        if not channel:
            return
        executable = discover_vlc(self.settings.vlc_path)
        if not executable:
            self.status.setText(self.tr("vlc_missing"))
            return
        try:
            launch_vlc(channel.url, executable, self.settings.proxy_url)
        except VLCError as exc:
            self.status.setText(self.tr("vlc_error", error=exc))
            return
        self.status.setText(self.tr("vlc_started", name=channel.name))
