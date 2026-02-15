export const createWebSocket = (endpoint, onMessage, onOpen, onClose, onError) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;

    // For development, backend WebSocket might be on a different port
    // Adjust this if your backend runs on a different port (e.g., 8000)
    const backendHost = process.env.REACT_APP_WS_HOST || host.replace(':3000', ':8000');
    const wsUrl = `${protocol}//${backendHost}${endpoint}`;

    // Fallback URL logic if needed
    const finalUrl = endpoint.startsWith('ws') ? endpoint : wsUrl;

    let socket;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 3000; // 3 seconds

    const connect = () => {
        try {
            console.log(`[WS] Attempting to connect to ${finalUrl}`);
            socket = new WebSocket(finalUrl);

            socket.onopen = (event) => {
                console.log(`[WS] ✅ Connected to ${finalUrl}`);
                reconnectAttempts = 0; // Reset on successful connection
                if (onOpen) onOpen(event);
            };

            socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    onMessage(data);
                } catch (err) {
                    console.error('[WS] Error parsing message:', err, 'Raw data:', event.data);
                }
            };

            socket.onclose = (event) => {
                console.log(`[WS] 🔌 Disconnected from ${finalUrl}`, {
                    code: event.code,
                    reason: event.reason || 'No reason provided',
                    wasClean: event.wasClean
                });

                if (onClose) onClose(event);

                // Attempt to reconnect if not a clean close and under max attempts
                if (!event.wasClean && reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    console.log(`[WS] 🔄 Reconnecting... (Attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
                    setTimeout(connect, reconnectDelay);
                } else if (reconnectAttempts >= maxReconnectAttempts) {
                    console.warn('[WS] ⚠️ Max reconnection attempts reached. WebSocket will remain disconnected.');
                    console.info('[WS] 💡 This is normal if the backend WebSocket server is not running. The app will continue to work with REST API only.');
                }
            };

            socket.onerror = (event) => {
                // Enhanced error logging
                console.error('[WS] ❌ WebSocket Error:', {
                    type: event.type,
                    target: event.target,
                    readyState: socket?.readyState,
                    url: finalUrl,
                    message: event.message || 'Connection failed'
                });

                // Common error explanations
                if (socket?.readyState === WebSocket.CLOSED || socket?.readyState === WebSocket.CLOSING) {
                    console.info('[WS] 💡 Tip: Make sure the backend WebSocket server is running on the correct port.');
                    console.info('[WS] 💡 Expected URL:', finalUrl);
                }

                if (onError) onError(event);
            };

        } catch (err) {
            console.error('[WS] Failed to create WebSocket connection:', err);
            if (onError) onError(err);
        }
    };

    // Initial connection
    connect();

    // Return socket with additional methods
    return {
        get socket() { return socket; },
        close: () => {
            if (socket) {
                reconnectAttempts = maxReconnectAttempts; // Prevent reconnection
                socket.close(1000, 'Client closed connection');
            }
        },
        send: (data) => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(typeof data === 'string' ? data : JSON.stringify(data));
            } else {
                console.warn('[WS] Cannot send message: WebSocket is not connected');
            }
        }
    };
};
