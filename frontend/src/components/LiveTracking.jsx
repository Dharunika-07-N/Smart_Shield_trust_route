/**
 * LiveTracking.jsx — Real-Time GPS Delivery Tracker
 * ==================================================
 * Self-contained component with a full-screen-aware layout.
 * Works both on the /tracking standalone page AND embedded inside dashboards.
 */

import React, { useEffect, useState, useRef, useMemo, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useRealTimeTracking, useRiderGPS } from '../hooks/useRealTimeTracking';
import { API_ROOT_URL } from '../utils/constants';

// ─── Map Pan Controller ──────────────────────────────────────────────────────
const MapController = ({ center, zoom, animate }) => {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      if (animate) {
        map.flyTo(center, zoom || map.getZoom(), { animate: true, duration: 1.0 });
      } else {
        map.setView(center, zoom || map.getZoom());
      }
    }
  }, [center, zoom, animate, map]);
  return null;
};

// ─── Animated Rider Marker ───────────────────────────────────────────────────
const createRiderIcon = (heading, isSimulated = false) => {
  const color = isSimulated ? '#f59e0b' : '#4f46e5';
  const rotation = heading ? `rotate(${heading}deg)` : 'rotate(0deg)';
  return L.divIcon({
    className: '',
    html: `
      <div style="position:relative;width:46px;height:46px">
        <div style="
          position:absolute;inset:-8px;border-radius:50%;
          background:${color};opacity:0.18;
          animation:ltPing 1.5s cubic-bezier(0,0,.2,1) infinite;
        "></div>
        <div style="
          position:absolute;inset:-2px;border-radius:50%;
          border:2px solid ${color};opacity:0.35;
        "></div>
        <div style="
          width:46px;height:46px;border-radius:50%;
          background:${color};
          border:3px solid white;
          box-shadow:0 4px 20px ${color}55,0 0 0 4px ${color}22;
          display:flex;align-items:center;justify-content:center;
          font-size:20px;
          transform:${rotation};
          transition:transform 0.8s ease;
        ">
          <span style="transform:rotate(0deg);display:block;">🏍</span>
        </div>
        ${isSimulated ? '<div style="position:absolute;top:-20px;left:50%;transform:translateX(-50%);background:#f59e0b;color:white;font-size:9px;font-weight:bold;padding:2px 7px;border-radius:4px;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,0.2)">SIM</div>' : ''}
      </div>
      <style>
        @keyframes ltPing {
          75%, 100% { transform: scale(2.2); opacity: 0; }
        }
      </style>
    `,
    iconSize: [46, 46],
    iconAnchor: [23, 23],
    popupAnchor: [0, -23]
  });
};

// ─── Status Badge ────────────────────────────────────────────────────────────
const ConnBadge = ({ connected, connectionMode, error }) => {
  if (error) return (
    <span style={{ fontSize: 11, fontWeight: 700, padding: '4px 11px', borderRadius: 20, background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca' }}>
      ● Error
    </span>
  );
  if (connected) {
    const label = connectionMode === 'sse' ? '● SSE Live' : '● WS Live';
    const color = connectionMode === 'sse' ? '#d97706' : '#059669';
    const bg = connectionMode === 'sse' ? '#fffbeb' : '#ecfdf5';
    const bdr = connectionMode === 'sse' ? '#fde68a' : '#a7f3d0';
    return (
      <span style={{ fontSize: 11, fontWeight: 700, padding: '4px 11px', borderRadius: 20, background: bg, color, border: `1px solid ${bdr}` }}>
        {label}
      </span>
    );
  }
  return (
    <span style={{ fontSize: 11, fontWeight: 700, padding: '4px 11px', borderRadius: 20, background: '#f9fafb', color: '#6b7280', border: '1px solid #e5e7eb' }}>
      ● Connecting…
    </span>
  );
};

// ─── Main Component ──────────────────────────────────────────────────────────
const LiveTracking = ({ deliveryId: propDeliveryId, isRider = false }) => {
  const [deliveryIdInput, setDeliveryIdInput] = useState(propDeliveryId || '');
  const [followRider, setFollowRider] = useState(true);
  const [isSimulating, setIsSimulating] = useState(false);

  const tracking = useRealTimeTracking(
    isRider ? null : deliveryIdInput,
    { enabled: !isRider && deliveryIdInput.trim().length >= 3 }
  );

  const riderGps = useRiderGPS(
    isRider ? deliveryIdInput : null,
    null,
    { enabled: isRider && !!deliveryIdInput }
  );

  const displayLocation = isRider
    ? (riderGps.currentLocation ? [riderGps.currentLocation.latitude, riderGps.currentLocation.longitude] : null)
    : tracking.currentLocation;

  const centerPosition = displayLocation || [11.0168, 76.9558]; // Coimbatore default

  const handleSimulate = useCallback(async () => {
    if (!deliveryIdInput) return;
    setIsSimulating(true);
    try {
      const token = localStorage.getItem('auth_token');
      const res = await fetch(`${API_ROOT_URL}/api/v1/tracking/simulate/${deliveryIdInput}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
      });
      const data = await res.json();
      if (data.success) {
        alert(`✅ GPS simulation started!\nWaypoints: ${data.waypoints}\nDuration: ~${data.total_duration_seconds}s\n\nWatch the 🏍 marker move across Coimbatore.`);
      } else {
        alert('Simulation response: ' + JSON.stringify(data));
      }
    } catch (e) {
      alert('❌ Failed to start simulation. Is the backend running?\n\n' + e.message);
    } finally {
      setTimeout(() => setIsSimulating(false), 36000);
    }
  }, [deliveryIdInput]);

  const riderIcon = useMemo(() =>
    createRiderIcon(tracking.heading, isSimulating),
    [tracking.heading, isSimulating]
  );

  const statusColor = { delivered: '#10b981', in_transit: '#4f46e5', pending: '#f59e0b', failed: '#ef4444', picked_up: '#3b82f6' };
  const sc = statusColor[tracking.status] || '#9ca3af';

  const timeAgo = (d) => {
    if (!d) return 'Never';
    const s = Math.floor((new Date() - d) / 1000);
    if (s < 60) return `${s}s ago`;
    if (s < 3600) return `${Math.floor(s / 60)}m ago`;
    return `${Math.floor(s / 3600)}h ago`;
  };

  /* ─── Layout ─────────────────────────────────────────────────────────────── */
  return (
    <div style={{ fontFamily: "'Inter',sans-serif", display: 'flex', flexDirection: 'column', gap: 0 }}>
      <style>{`
        @keyframes ltPulse { 0%,100%{opacity:1} 50%{opacity:.4} }
        @keyframes ltSpin   { to{transform:rotate(360deg)} }
        .lt-input {
          flex:1; border:1.5px solid #e5e7eb; border-radius:10px;
          padding:10px 16px; font-size:14px; font-weight:600; color:#111827;
          outline:none; font-family:inherit; transition:border-color .2s,box-shadow .2s;
        }
        .lt-input:focus { border-color:#4f46e5; box-shadow:0 0 0 3px rgba(79,70,229,.1); }
        .lt-sim-btn {
          background:linear-gradient(135deg,#f59e0b,#d97706);
          color:white; border:none; border-radius:10px;
          padding:10px 20px; font-size:12px; font-weight:800;
          cursor:pointer; letter-spacing:.5px; white-space:nowrap;
          text-transform:uppercase; transition:opacity .2s,transform .1s;
          box-shadow:0 4px 14px rgba(245,158,11,.35);
        }
        .lt-sim-btn:hover:not(:disabled) { opacity:.9; transform:translateY(-1px); }
        .lt-sim-btn:disabled { opacity:.45; cursor:not-allowed; transform:none; }
        .lt-stat-box {
          background:#f9fafb; border-radius:10px; padding:12px 14px;
          border:1px solid #f3f4f6; display:flex; flex-direction:column; gap:4px;
        }
      `}</style>

      {/* ══ TOP BAR ═══════════════════════════════════════════════════════════ */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '16px 20px', background: 'white',
        borderBottom: '1px solid #f3f4f6', borderRadius: '16px 16px 0 0',
        boxShadow: '0 1px 4px rgba(0,0,0,.04)'
      }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 20, fontWeight: 900, color: '#111827', display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 22 }}>{isRider ? '📡' : '🗺️'}</span>
            {isRider ? 'Share My Location' : 'Live Delivery Tracker'}
          </h2>
          <p style={{ margin: '3px 0 0', fontSize: 11, color: '#6b7280', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1 }}>
            {isRider ? 'GPS Broadcasting Active' : 'WebSocket Push · Cache-First · SSE Fallback'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          {!isRider && (
            <ConnBadge connected={tracking.connected} connectionMode={tracking.connectionMode} error={tracking.error} />
          )}
          {tracking.lastUpdate && !isRider && (
            <span style={{ fontSize: 11, color: '#9ca3af', fontWeight: 600 }}>Updated {timeAgo(tracking.lastUpdate)}</span>
          )}
        </div>
      </div>

      {/* ══ SEARCH BAR ════════════════════════════════════════════════════════ */}
      <div style={{
        padding: '14px 20px', background: 'white',
        borderBottom: '1px solid #f3f4f6',
        display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap'
      }}>
        <input
          className="lt-input"
          type="text"
          value={deliveryIdInput}
          onChange={e => setDeliveryIdInput(e.target.value)}
          placeholder="Enter delivery ID (e.g. DEL-001)"
          disabled={isRider && !!propDeliveryId}
        />
        {!isRider && (
          <button
            className="lt-sim-btn"
            onClick={handleSimulate}
            disabled={!deliveryIdInput || deliveryIdInput.trim().length < 3 || isSimulating}
            title="Simulate a GPS-moving rider — no real device needed"
          >
            {isSimulating ? '⏳ Simulating…' : '▶ Demo GPS'}
          </button>
        )}
        <div style={{
          flex: '1 1 100%', padding: '8px 14px',
          background: '#f0f4ff', borderRadius: 8, border: '1px solid #c7d2fe'
        }}>
          <p style={{ margin: 0, fontSize: 11, color: '#4338ca', fontWeight: 600 }}>
            🏗️ <strong>Architecture:</strong> Rider GPS → Backend → WebSocket push → Marker update (no page reload).
            Location stored in <strong>in-memory cache</strong> for instant access. DB not on hot path.
          </p>
        </div>
      </div>

      {/* ══ ALERTS ════════════════════════════════════════════════════════════ */}
      {tracking.error && !isRider && (
        <div style={{ padding: '10px 20px', background: '#fef2f2', borderBottom: '1px solid #fecaca' }}>
          <p style={{ margin: 0, fontSize: 13, color: '#dc2626', fontWeight: 700 }}>⚠️ {tracking.error}</p>
          <p style={{ margin: '3px 0 0', fontSize: 11, color: '#ef4444' }}>
            Make sure the backend is running: <code style={{ background: '#fee2e2', padding: '1px 5px', borderRadius: 4 }}>cd backend && uvicorn api.main:app --reload</code>
          </p>
        </div>
      )}
      {tracking.reoptimizationNeeded && (
        <div style={{ padding: '10px 20px', background: '#fffbeb', borderBottom: '1px solid #fde68a', display: 'flex', gap: 10, alignItems: 'center' }}>
          <span style={{ fontSize: 20 }}>⚠️</span>
          <div>
            <p style={{ margin: 0, fontSize: 13, fontWeight: 700, color: '#92400e' }}>Route Deviation Detected</p>
            <p style={{ margin: '2px 0 0', fontSize: 12, color: '#b45309' }}>Rider has deviated from planned route. Reoptimization recommended.</p>
          </div>
        </div>
      )}

      {/* ══ MAIN BODY: 2-col grid ════════════════════════════════════════════ */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '300px 1fr',
        gridTemplateRows: '1fr',
        minHeight: 560,
        background: 'white',
        borderTop: 'none',
        borderRadius: '0 0 16px 16px',
        overflow: 'hidden',
        boxShadow: '0 4px 24px rgba(0,0,0,.07)'
      }}>

        {/* ── LEFT PANEL ───────────────────────────────────────────────────── */}
        <div style={{
          padding: 16, overflowY: 'auto', borderRight: '1px solid #f3f4f6',
          display: 'flex', flexDirection: 'column', gap: 12, background: '#fafafa'
        }}>

          {/* Status Card */}
          <div style={{ background: 'white', borderRadius: 12, border: '1px solid #f0f0f0', padding: 16, boxShadow: '0 1px 4px rgba(0,0,0,.04)' }}>
            <p style={{ margin: '0 0 12px', fontSize: 11, fontWeight: 800, color: '#374151', textTransform: 'uppercase', letterSpacing: .5 }}>
              {isRider ? 'GPS Status' : 'Delivery Status'}
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <div style={{
                width: 12, height: 12, borderRadius: '50%',
                background: sc, boxShadow: `0 0 0 4px ${sc}33`,
                animation: 'ltPulse 2s infinite'
              }} />
              <span style={{ fontSize: 15, fontWeight: 800, color: '#111827', textTransform: 'capitalize' }}>
                {(tracking.status || 'waiting…').replace(/_/g, ' ')}
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {[
                { label: 'Speed', value: tracking.speed != null ? `${tracking.speed.toFixed(1)} km/h` : '—', icon: '🚀' },
                { label: 'Heading', value: tracking.heading != null ? `${Math.round(tracking.heading)}°` : '—', icon: '🧭' },
                { label: 'Battery', value: tracking.batteryLevel != null ? `${tracking.batteryLevel}%` : '—', icon: '🔋' },
                { label: 'Mode', value: isRider ? 'Sender' : (tracking.connectionMode?.toUpperCase() || '—'), icon: '📡' }
              ].map(({ label, value, icon }) => (
                <div key={label} className="lt-stat-box">
                  <span style={{ fontSize: 10, color: '#9ca3af', fontWeight: 700, textTransform: 'uppercase' }}>{icon} {label}</span>
                  <span style={{ fontSize: 15, fontWeight: 800, color: '#111827' }}>{value}</span>
                </div>
              ))}
            </div>

            {tracking.batteryLevel != null && (
              <div style={{ marginTop: 12, background: '#f3f4f6', borderRadius: 999, height: 5, overflow: 'hidden' }}>
                <div style={{
                  height: '100%', borderRadius: 999,
                  width: `${tracking.batteryLevel}%`,
                  background: tracking.batteryLevel > 50 ? '#10b981' : tracking.batteryLevel > 20 ? '#f59e0b' : '#ef4444',
                  transition: 'width .5s ease'
                }} />
              </div>
            )}
          </div>

          {/* Location badge */}
          {displayLocation && (
            <div style={{ background: 'white', borderRadius: 12, border: '1px solid #f0f0f0', padding: 14, boxShadow: '0 1px 4px rgba(0,0,0,.04)' }}>
              <p style={{ margin: '0 0 4px', fontSize: 11, fontWeight: 700, color: '#6b7280', textTransform: 'uppercase' }}>📍 Current GPS</p>
              <p style={{ margin: 0, fontSize: 13, fontWeight: 800, color: '#111827', fontVariantNumeric: 'tabular-nums' }}>
                {displayLocation[0].toFixed(5)}°N
              </p>
              <p style={{ margin: 0, fontSize: 13, fontWeight: 800, color: '#111827', fontVariantNumeric: 'tabular-nums' }}>
                {displayLocation[1].toFixed(5)}°E
              </p>
            </div>
          )}

          {/* Track history */}
          {!isRider && tracking.locationHistory.length > 0 && (
            <div style={{ background: 'white', borderRadius: 12, border: '1px solid #f0f0f0', padding: 14, boxShadow: '0 1px 4px rgba(0,0,0,.04)', display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 38, height: 38, borderRadius: 10, background: '#ede9fe', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>📍</div>
              <div>
                <p style={{ margin: 0, fontSize: 10, color: '#6b7280', fontWeight: 700, textTransform: 'uppercase' }}>Track Points</p>
                <p style={{ margin: '3px 0 0', fontSize: 22, fontWeight: 900, color: '#4f46e5' }}>{tracking.locationHistory.length}</p>
              </div>
            </div>
          )}

          {/* Rider GPS tx stats */}
          {isRider && (
            <div style={{ background: 'white', borderRadius: 12, border: '1px solid #f0f0f0', padding: 14, boxShadow: '0 1px 4px rgba(0,0,0,.04)' }}>
              <p style={{ margin: '0 0 10px', fontSize: 11, fontWeight: 800, color: '#374151', textTransform: 'uppercase' }}>📡 Transmitting</p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                <div style={{ background: '#f0fdf4', borderRadius: 8, padding: '10px 12px', border: '1px solid #bbf7d0' }}>
                  <p style={{ margin: 0, fontSize: 10, color: '#059669', fontWeight: 700, textTransform: 'uppercase' }}>Updates Sent</p>
                  <p style={{ margin: '4px 0 0', fontSize: 20, fontWeight: 900, color: '#065f46' }}>{riderGps.sendCount}</p>
                </div>
                <div style={{ background: '#fefce8', borderRadius: 8, padding: '10px 12px', border: '1px solid #fef08a' }}>
                  <p style={{ margin: 0, fontSize: 10, color: '#d97706', fontWeight: 700, textTransform: 'uppercase' }}>Interval</p>
                  <p style={{ margin: '4px 0 0', fontSize: 20, fontWeight: 900, color: '#92400e' }}>5s</p>
                </div>
              </div>
            </div>
          )}

          {/* Auto-follow toggle */}
          <div style={{ background: 'white', borderRadius: 12, border: '1px solid #f0f0f0', padding: '14px 16px', boxShadow: '0 1px 4px rgba(0,0,0,.04)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'auto' }}>
            <div>
              <p style={{ margin: 0, fontSize: 13, fontWeight: 700, color: '#111827' }}>Auto-follow rider</p>
              <p style={{ margin: '2px 0 0', fontSize: 11, color: '#6b7280' }}>Map pans to rider</p>
            </div>
            <button
              onClick={() => setFollowRider(f => !f)}
              aria-label="Toggle auto-follow"
              style={{
                width: 46, height: 26, borderRadius: 13, border: 'none', cursor: 'pointer',
                background: followRider ? '#4f46e5' : '#d1d5db',
                position: 'relative', transition: 'background .2s', flexShrink: 0
              }}
            >
              <div style={{
                position: 'absolute', top: 3, left: followRider ? 23 : 3,
                width: 20, height: 20, borderRadius: '50%', background: 'white',
                boxShadow: '0 1px 3px rgba(0,0,0,.3)', transition: 'left .2s'
              }} />
            </button>
          </div>
        </div>

        {/* ── RIGHT: MAP ───────────────────────────────────────────────────── */}
        <div style={{ position: 'relative', minHeight: 560 }}>

          {/* Map header strip */}
          <div style={{
            position: 'absolute', top: 0, left: 0, right: 0, zIndex: 1000,
            padding: '10px 16px', background: 'rgba(255,255,255,.92)',
            backdropFilter: 'blur(8px)',
            borderBottom: '1px solid #f3f4f6',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center'
          }}>
            <span style={{ fontSize: 12, fontWeight: 700, color: '#374151' }}>
              🗺️ Live Map {displayLocation
                ? `— ${displayLocation[0].toFixed(4)}°N, ${displayLocation[1].toFixed(4)}°E`
                : '— Waiting for GPS signal…'}
            </span>
            {isSimulating && (
              <span style={{
                fontSize: 11, background: '#fef3c7', color: '#d97706',
                padding: '3px 10px', borderRadius: 999, fontWeight: 800,
                animation: 'ltPulse 1s infinite'
              }}>🔴 SIMULATING</span>
            )}
          </div>

          {/* The map — fills the entire right column */}
          <MapContainer
            center={centerPosition}
            zoom={15}
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
            zoomControl={true}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <MapController
              center={followRider ? displayLocation : null}
              zoom={16}
              animate={true}
            />

            {displayLocation && (
              <Marker position={displayLocation} icon={riderIcon}>
                <Popup>
                  <div style={{ fontFamily: 'Inter,sans-serif', fontSize: 13, lineHeight: 1.6 }}>
                    <strong>🏍 Rider Location</strong><br />
                    Status: <span style={{ color: sc, fontWeight: 700 }}>{tracking.status?.replace(/_/g, ' ') || 'unknown'}</span><br />
                    {tracking.speed != null && <span>Speed: {tracking.speed.toFixed(1)} km/h<br /></span>}
                    {tracking.heading != null && <span>Heading: {Math.round(tracking.heading)}°<br /></span>}
                    {tracking.lastUpdate && <span style={{ color: '#9ca3af', fontSize: 11 }}>Updated {timeAgo(tracking.lastUpdate)}</span>}
                  </div>
                </Popup>
              </Marker>
            )}

            {tracking.locationHistory.length > 1 && (
              <Polyline
                positions={tracking.locationHistory.map(h => h.location)}
                pathOptions={{ color: '#4f46e5', weight: 4, opacity: .75 }}
              />
            )}
          </MapContainer>
        </div>
      </div>

      {/* ══ ARCHITECTURE CARD ═════════════════════════════════════════════════ */}
      <div style={{
        marginTop: 16, padding: 20,
        background: 'linear-gradient(135deg,#1e1b4b,#312e81)',
        borderRadius: 16, border: 'none'
      }}>
        <p style={{ margin: '0 0 14px', fontSize: 11, fontWeight: 800, color: '#c7d2fe', textTransform: 'uppercase', letterSpacing: 1 }}>
          ⚡ System Architecture — How Real-Time GPS Works
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', gap: 12 }}>
          {[
            { icon: '📱', title: 'GPS Events', desc: 'Rider sends coords every 5-15s via lightweight POST' },
            { icon: '⚡', title: 'Push-Based', desc: 'Backend pushes via WebSocket — no polling, no page refresh' },
            { icon: '🔑', title: 'Per-Order Channel', desc: 'order_id → isolated WS channel. Only relevant users receive updates' },
            { icon: '📦', title: 'In-Memory Cache', desc: 'Latest location in dict (Redis-like). DB not on hot path' },
            { icon: '🗺️', title: 'Marker-Only Update', desc: 'Only the rider dot moves. Map tiles never reload' },
            { icon: '🌐', title: 'SSE Fallback', desc: 'If WS is blocked, EventSource takes over automatically' },
          ].map(({ icon, title, desc }) => (
            <div key={title} style={{ background: 'rgba(255,255,255,.08)', borderRadius: 10, padding: '12px 14px' }}>
              <p style={{ margin: '0 0 4px', fontSize: 18 }}>{icon}</p>
              <p style={{ margin: '0 0 4px', fontSize: 12, fontWeight: 800, color: '#e0e7ff' }}>{title}</p>
              <p style={{ margin: 0, fontSize: 11, color: '#a5b4fc', lineHeight: 1.5 }}>{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LiveTracking;