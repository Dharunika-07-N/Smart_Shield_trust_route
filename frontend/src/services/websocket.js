export const createWebSocket = (endpoint, onMessage, onOpen, onClose) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    // For development, we might need a specific port if backend is separate
    const wsUrl = `${protocol}//${host}${endpoint}`;

    // Fallback URL logic if needed
    const finalUrl = endpoint.startsWith('ws') ? endpoint : wsUrl;

    const socket = new WebSocket(finalUrl);

    socket.onopen = () => {
        console.log(`[WS] Connected to ${finalUrl}`);
        if (onOpen) onOpen();
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            onMessage(data);
        } catch (err) {
            console.error('[WS] Error parsing message:', err);
        }
    };

    socket.onclose = () => {
        console.log(`[WS] Disconnected from ${finalUrl}`);
        if (onClose) onClose();
    };

    socket.onerror = (error) => {
        console.error('[WS] Error:', error);
    };

    return socket;
};
