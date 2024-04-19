from typing import TYPE_CHECKING, Any, Callable

from CheeseSignal import Signal

if TYPE_CHECKING:
    from CheeseAPI.app import App

class _Signal:
    def __init__(self, app: 'App'):
        self.app: 'App' = app

        self.server_beforeStarting: Signal = Signal()
        self.server_afterStarting: Signal = Signal()
        self.server_running: Signal = Signal()
        self.server_beforeStopping: Signal = Signal()
        self.server_afterStopping: Signal = Signal()

        self.worker_beforeStarting: Signal = Signal()
        self.worker_afterStarting: Signal = Signal()
        self.worker_running: Signal = Signal()
        self.worker_beforeStopping: Signal = Signal()
        self.worker_afterStopping: Signal = Signal()

        self.http_beforeRequest: Signal = Signal()
        self.http_afterRequest: Signal = Signal()
        self.http_static: Signal = Signal()
        self.http_custom: Signal = Signal()
        self.http_404: Signal = Signal()
        self.http_options: Signal = Signal()
        self.http_405: Signal = Signal()
        self.http_500: Signal = Signal()
        self.http_beforeResponse: Signal = Signal()
        self.http_afterResponse: Signal = Signal()

        self.websocket_afterRequest: Signal = Signal()
        self.websocket_404: Signal = Signal()
        self.websocket_405: Signal = Signal()
        self.websocket_500: Signal = Signal()
        self.websocket_beforeResponse: Signal = Signal()
        self.websocket_afterResponse: Signal = Signal()
        self.websocket_beforeSubprotocol: Signal = Signal()
        self.websocket_afterSubprotocol: Signal = Signal()
        self.websocket_beforeConnection: Signal = Signal()
        self.websocket_afterConnection: Signal = Signal()
        self.websocket_beforeMessage: Signal = Signal()
        self.websocket_afterMessage: Signal = Signal()
        self.websocket_beforeSending: Signal = Signal()
        self.websocket_afterSending: Signal = Signal()
        self.websocket_beforeClosing: Signal = Signal()
        self.websocket_afterClosing: Signal = Signal()
        self.websocket_afterDisconnection: Signal = Signal()
