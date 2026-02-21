import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
    FiNavigation, FiVolume2, FiVolumeX, FiChevronRight,
    FiClock, FiMapPin, FiCheckCircle, FiAlertTriangle,
    FiArrowLeft, FiArrowRight, FiCornerDownLeft, FiCornerDownRight,
    FiArrowUp, FiRepeat, FiShare2
} from 'react-icons/fi';

// ─────────────────────────────────────────────
//  Maneuver Data: icon name + color per action
// ─────────────────────────────────────────────
const MANEUVER_MAP = {
    'turn-left': { svg: 'left', label: 'Turn Left', color: '#4f46e5', bg: '#eef2ff' },
    'turn-slight-left': { svg: 'slight-left', label: 'Slight Left', color: '#7c3aed', bg: '#f5f3ff' },
    'turn-sharp-left': { svg: 'sharp-left', label: 'Sharp Left', color: '#dc2626', bg: '#fef2f2' },
    'turn-right': { svg: 'right', label: 'Turn Right', color: '#4f46e5', bg: '#eef2ff' },
    'turn-slight-right': { svg: 'slight-right', label: 'Slight Right', color: '#7c3aed', bg: '#f5f3ff' },
    'turn-sharp-right': { svg: 'sharp-right', label: 'Sharp Right', color: '#dc2626', bg: '#fef2f2' },
    'uturn-left': { svg: 'uturn', label: 'U-Turn', color: '#d97706', bg: '#fffbeb' },
    'uturn-right': { svg: 'uturn', label: 'U-Turn', color: '#d97706', bg: '#fffbeb' },
    'roundabout-left': { svg: 'roundabout', label: 'Roundabout', color: '#0891b2', bg: '#ecfeff' },
    'roundabout-right': { svg: 'roundabout', label: 'Roundabout', color: '#0891b2', bg: '#ecfeff' },
    'merge': { svg: 'merge', label: 'Merge', color: '#059669', bg: '#ecfdf5' },
    'ramp-left': { svg: 'left', label: 'Take Ramp Left', color: '#7c3aed', bg: '#f5f3ff' },
    'ramp-right': { svg: 'right', label: 'Take Ramp Right', color: '#7c3aed', bg: '#f5f3ff' },
    'fork-left': { svg: 'left', label: 'Keep Left', color: '#4f46e5', bg: '#eef2ff' },
    'fork-right': { svg: 'right', label: 'Keep Right', color: '#4f46e5', bg: '#eef2ff' },
    'straight': { svg: 'straight', label: 'Continue Straight', color: '#16a34a', bg: '#f0fdf4' },
    'destination': { svg: 'dest', label: 'Destination', color: '#dc2626', bg: '#fef2f2' },
    'depart': { svg: 'straight', label: 'Start', color: '#16a34a', bg: '#f0fdf4' },
};

// ─────────────────────────────────────────────────────────────
//  ManeuverIcon — draws the correct arrow SVG for the maneuver
// ─────────────────────────────────────────────────────────────
const ManeuverIcon = ({ type = 'straight', size = 40, color = '#4f46e5' }) => {
    const s = size;
    const c = color;
    switch (type) {
        case 'left':
            return (
                <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
                    <path d="M28 8 L12 8 L12 22" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M12 8 L6 14 L12 20" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                    <path d="M28 8 L28 32" stroke={c} strokeWidth="3.5" strokeLinecap="round" />
                    <path d="M22 26 L28 32 L34 26" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            );
        case 'slight-left':
            return (
                <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
                    <path d="M28 8 L16 8 L10 18" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M16 8 L10 14" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M28 8 L28 32" stroke={c} strokeWidth="3.5" strokeLinecap="round" />
                    <path d="M22 26 L28 32 L34 26" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            );
        case 'sharp-left':
            return (
                <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
                    <path d="M28 8 L8 8 L8 30" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M2 24 L8 30 L14 24" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M28 8 L28 32" stroke={c} strokeWidth="3.5" strokeLinecap="round" />
                    <path d="M22 26 L28 32 L34 26" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            );
        case 'right':
            return (
                <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
                    <path d="M12 8 L28 8 L28 22" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M28 8 L34 14 L28 20" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                    <path d="M12 8 L12 32" stroke={c} strokeWidth="3.5" strokeLinecap="round" />
                    <path d="M6 26 L12 32 L18 26" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            );
        case 'slight-right':
            return (
                <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
                    <path d="M12 8 L24 8 L30 18" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M24 8 L30 14" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M12 8 L12 32" stroke={c} strokeWidth="3.5" strokeLinecap="round" />
                    <path d="M6 26 L12 32 L18 26" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            );
        case 'sharp-right':
            return (
                <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
                    <path d="M12 8 L32 8 L32 30" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M26 24 L32 30 L38 24" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M12 8 L12 32" stroke={c} strokeWidth="3.5" strokeLinecap="round" />
                    <path d="M6 26 L12 32 L18 26" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            );
        case 'uturn':
            return (
                <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
                    <path d="M14 32 L14 16 Q14 8 22 8 Q30 8 30 16 L30 22" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                    <path d="M24 16 L30 22 L36 16" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M8 26 L14 32 L20 26" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            );
        case 'roundabout':
            return (
                <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
                    <circle cx="20" cy="20" r="8" stroke={c} strokeWidth="3" fill="none" />
                    <path d="M20 6 L20 12" stroke={c} strokeWidth="3.5" strokeLinecap="round" />
                    <path d="M14 8 L20 6 L20 12" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M20 28 L20 34" stroke={c} strokeWidth="3.5" strokeLinecap="round" />
                    <path d="M14 32 L20 34 L26 32" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            );
        case 'merge':
            return (
                <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
                    <path d="M20 32 L20 8" stroke={c} strokeWidth="3.5" strokeLinecap="round" />
                    <path d="M14 14 L20 8 L26 14" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                    <path d="M8 28 L20 20" stroke={c} strokeWidth="2.5" strokeLinecap="round" strokeDasharray="2 2" />
                    <path d="M32 28 L20 20" stroke={c} strokeWidth="2.5" strokeLinecap="round" strokeDasharray="2 2" />
                </svg>
            );
        case 'dest':
            return (
                <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
                    <path d="M20 36 C20 36 8 24 8 16 C8 9.37 13.37 4 20 4 C26.63 4 32 9.37 32 16 C32 24 20 36 20 36Z" stroke={c} strokeWidth="3" fill={c + '20'} />
                    <circle cx="20" cy="16" r="4" fill={c} />
                </svg>
            );
        default: // straight
            return (
                <svg width={s} height={s} viewBox="0 0 40 40" fill="none">
                    <path d="M20 32 L20 8" stroke={c} strokeWidth="3.5" strokeLinecap="round" />
                    <path d="M14 14 L20 8 L26 14" stroke={c} strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            );
    }
};

// ─────────────────────────────────────────────────────────────
//  Haversine distance in meters
// ─────────────────────────────────────────────────────────────
function haversine(lat1, lon1, lat2, lon2) {
    const R = 6371e3;
    const φ1 = lat1 * Math.PI / 180;
    const φ2 = lat2 * Math.PI / 180;
    const Δφ = (lat2 - lat1) * Math.PI / 180;
    const Δλ = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(Δφ / 2) ** 2 + Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function stripHtml(html) {
    const d = document.createElement('div');
    d.innerHTML = html;
    return d.textContent || d.innerText || '';
}

function fmtDist(m) {
    if (!m) return '—';
    return m < 1000 ? `${Math.round(m)} m` : `${(m / 1000).toFixed(1)} km`;
}

function fmtTime(s) {
    if (!s) return '—';
    const m = Math.floor(s / 60);
    if (m < 60) return `${m} min`;
    const h = Math.floor(m / 60);
    return `${h}h ${m % 60}m`;
}

// ─────────────────────────────────────────────────────────────
//  Main Component
// ─────────────────────────────────────────────────────────────
const LiveNavigationHUD = ({
    route,
    currentLocation,
    onClose,
    onDeliveryComplete,
    destination,
    compact = false
}) => {
    const [stepIdx, setStepIdx] = useState(0);
    const [voiceOn, setVoiceOn] = useState(true);
    const spokenRef = useRef(-1);
    const alertedRef = useRef(false);

    // Flatten all steps from all segments
    const allSteps = React.useMemo(() => {
        if (!route) return [];
        const steps = [];
        (route.segments || []).forEach(seg => {
            if (Array.isArray(seg.instructions)) {
                seg.instructions.forEach(ins => {
                    // Normalize structure
                    if (typeof ins === 'string') {
                        steps.push({ instruction: ins, maneuver: 'straight', distance: '', distance_value: 0, duration_value: 0 });
                    } else {
                        steps.push(ins);
                    }
                });
            }
        });
        // If no segments, try flat instructions
        if (steps.length === 0 && route.instructions) {
            route.instructions.forEach(ins => steps.push(
                typeof ins === 'string'
                    ? { instruction: ins, maneuver: 'straight', distance: '', distance_value: 0, duration_value: 0 }
                    : ins
            ));
        }
        // Fallback
        if (steps.length === 0) {
            steps.push({ instruction: 'Head towards destination', maneuver: 'straight', distance: '', distance_value: 0, duration_value: 0 });
        }
        return steps;
    }, [route]);

    const currentStep = allSteps[stepIdx] || {};
    const nextStep = allSteps[stepIdx + 1];
    const maneuverKey = currentStep?.maneuver || 'straight';
    const maneuverInfo = MANEUVER_MAP[maneuverKey] || MANEUVER_MAP['straight'];

    // Remaining distance & time from current step onwards
    const remaining = React.useMemo(() => {
        let dist = 0, time = 0;
        for (let i = stepIdx; i < allSteps.length; i++) {
            dist += allSteps[i]?.distance_value || 0;
            time += allSteps[i]?.duration_value || 0;
        }
        // Fallback to route totals if step values are 0
        if (dist === 0) {
            dist = route?.total_distance_meters || 0;
            time = route?.total_duration_seconds || 0;
        }
        return { dist, time };
    }, [stepIdx, allSteps, route]);

    // Voice guidance
    const speak = useCallback((text) => {
        if (!voiceOn || !window.speechSynthesis) return;
        window.speechSynthesis.cancel();
        const utt = new SpeechSynthesisUtterance(text);
        utt.rate = 0.92;
        utt.pitch = 1.0;
        window.speechSynthesis.speak(utt);
    }, [voiceOn]);

    // Auto-advance based on GPS proximity
    useEffect(() => {
        if (!currentLocation || !currentStep) return;
        const endLoc = currentStep.end_location;
        if (!endLoc) return;
        const dist = haversine(
            currentLocation.latitude, currentLocation.longitude,
            endLoc.lat || endLoc.latitude, endLoc.lng || endLoc.longitude
        );
        if (dist < 50 && stepIdx < allSteps.length - 1) {
            const next = stepIdx + 1;
            setStepIdx(next);
            if (spokenRef.current !== next) {
                const ns = allSteps[next];
                speak(stripHtml(ns?.instruction || 'Continue'));
                spokenRef.current = next;
            }
        }
        // Warn 200m before turn
        if (dist < 200 && dist > 50 && spokenRef.current !== stepIdx && stepIdx < allSteps.length - 1) {
            const label = MANEUVER_MAP[allSteps[stepIdx + 1]?.maneuver]?.label || 'turn';
            if (!alertedRef.current) {
                speak(`In ${Math.round(dist)} metres, ${label}`);
                alertedRef.current = true;
            }
        } else {
            alertedRef.current = false;
        }
    }, [currentLocation, currentStep, stepIdx, allSteps, speak]);

    // Speak first step on mount
    useEffect(() => {
        if (allSteps.length > 0 && spokenRef.current === -1) {
            setTimeout(() => {
                speak(stripHtml(allSteps[0]?.instruction || 'Start navigation'));
                spokenRef.current = 0;
            }, 800);
        }
    }, [allSteps, speak]);

    if (!route && !compact) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 py-10">
                <FiNavigation size={40} className="mb-3 opacity-30" />
                <p className="font-bold text-sm">No route loaded</p>
            </div>
        );
    }

    if (compact) {
        // Compact banner — shown at top of DriverDashboard map view
        return (
            <div
                className="flex items-center gap-3 px-4 py-3 rounded-2xl shadow-xl"
                style={{ background: maneuverInfo.bg, border: `1.5px solid ${maneuverInfo.color}22` }}
            >
                <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
                    style={{ background: maneuverInfo.color + '18' }}
                >
                    <ManeuverIcon type={maneuverInfo.svg} size={32} color={maneuverInfo.color} />
                </div>
                <div className="flex-1 min-w-0">
                    <p className="text-[10px] font-black uppercase tracking-widest" style={{ color: maneuverInfo.color }}>
                        {maneuverInfo.label}
                    </p>
                    <p
                        className="text-sm font-bold text-slate-900 truncate"
                        dangerouslySetInnerHTML={{ __html: currentStep?.instruction || 'Continue straight' }}
                    />
                </div>
                <div className="text-right shrink-0">
                    <p className="text-lg font-black text-slate-900">{fmtDist(currentStep?.distance_value)}</p>
                    <p className="text-[10px] text-slate-400 font-bold">{fmtTime(remaining.time)} left</p>
                </div>
            </div>
        );
    }

    // ── Full Panel ───────────────────────────────────────────
    return (
        <div className="flex flex-col h-full bg-white overflow-hidden">

            {/* ── Top HUD: Big maneuver card ── */}
            <div
                className="px-6 pt-6 pb-5 relative"
                style={{
                    background: `linear-gradient(135deg, ${maneuverInfo.color}14 0%, ${maneuverInfo.color}06 100%)`,
                    borderBottom: `1px solid ${maneuverInfo.color}22`
                }}
            >
                <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Live Navigation</span>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => { setVoiceOn(v => !v); if (voiceOn) window.speechSynthesis?.cancel(); }}
                            className="p-2 rounded-xl transition-all"
                            style={{ background: voiceOn ? maneuverInfo.color + '18' : '#f1f5f9' }}
                            title={voiceOn ? 'Mute voice' : 'Enable voice'}
                        >
                            {voiceOn
                                ? <FiVolume2 size={16} style={{ color: maneuverInfo.color }} />
                                : <FiVolumeX size={16} className="text-slate-400" />}
                        </button>
                        {onClose && (
                            <button
                                onClick={onClose}
                                className="p-2 rounded-xl bg-rose-50 text-rose-500 hover:bg-rose-100 transition-all text-[10px] font-black"
                            >
                                END
                            </button>
                        )}
                    </div>
                </div>

                {/* Arrow + Instruction */}
                <div className="flex items-center gap-5 my-4">
                    <div
                        className="w-20 h-20 rounded-3xl flex items-center justify-center shrink-0 shadow-lg"
                        style={{
                            background: `linear-gradient(135deg, ${maneuverInfo.color}22, ${maneuverInfo.color}10)`,
                            border: `2px solid ${maneuverInfo.color}30`
                        }}
                    >
                        <ManeuverIcon type={maneuverInfo.svg} size={52} color={maneuverInfo.color} />
                    </div>
                    <div className="flex-1 min-w-0">
                        <p
                            className="text-2xl font-black text-slate-900 leading-tight"
                            style={{ color: maneuverInfo.color }}
                        >
                            {maneuverInfo.label}
                        </p>
                        <p
                            className="text-sm font-semibold text-slate-700 mt-1 leading-snug"
                            dangerouslySetInnerHTML={{ __html: currentStep?.instruction || 'Continue straight' }}
                        />
                    </div>
                </div>

                {/* Distance to this step */}
                <div className="flex items-center gap-4">
                    <div className="flex-1 bg-white/80 backdrop-blur rounded-2xl px-4 py-2 border border-slate-100 text-center">
                        <p className="text-[10px] text-slate-400 font-bold uppercase">Next Turn</p>
                        <p className="text-lg font-black text-slate-900">
                            {currentStep?.distance || fmtDist(currentStep?.distance_value) || '—'}
                        </p>
                    </div>
                    <div className="flex-1 bg-white/80 backdrop-blur rounded-2xl px-4 py-2 border border-slate-100 text-center">
                        <p className="text-[10px] text-slate-400 font-bold uppercase">ETA</p>
                        <p className="text-lg font-black text-slate-900">{fmtTime(remaining.time)}</p>
                    </div>
                    <div className="flex-1 bg-white/80 backdrop-blur rounded-2xl px-4 py-2 border border-slate-100 text-center">
                        <p className="text-[10px] text-slate-400 font-bold uppercase">Remaining</p>
                        <p className="text-lg font-black text-slate-900">{fmtDist(remaining.dist)}</p>
                    </div>
                </div>
            </div>

            {/* ── Next step preview ── */}
            {nextStep && (
                <div className="px-6 py-3 bg-slate-50 border-b border-slate-100">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-slate-200 flex items-center justify-center shrink-0">
                            <ManeuverIcon
                                type={MANEUVER_MAP[nextStep.maneuver || 'straight']?.svg || 'straight'}
                                size={20}
                                color="#94a3b8"
                            />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-[10px] text-slate-400 font-bold uppercase">Then</p>
                            <p
                                className="text-xs text-slate-600 font-semibold truncate"
                                dangerouslySetInnerHTML={{ __html: nextStep.instruction || '' }}
                            />
                        </div>
                        <span className="text-xs font-bold text-slate-400 shrink-0">{nextStep.distance || ''}</span>
                    </div>
                </div>
            )}

            {/* ── Step List ── */}
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2">
                <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest px-2 mb-3">
                    All Steps ({allSteps.length})
                </p>
                {allSteps.map((step, idx) => {
                    const m = MANEUVER_MAP[step.maneuver || 'straight'] || MANEUVER_MAP['straight'];
                    const isActive = idx === stepIdx;
                    const isDone = idx < stepIdx;
                    return (
                        <button
                            key={idx}
                            onClick={() => setStepIdx(idx)}
                            className={`w-full flex items-center gap-3 p-3 rounded-2xl transition-all text-left ${isActive
                                    ? 'shadow-md'
                                    : isDone
                                        ? 'opacity-40'
                                        : 'hover:bg-slate-50'
                                }`}
                            style={isActive ? { background: m.bg, border: `1.5px solid ${m.color}30` } : {}}
                        >
                            <div
                                className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
                                style={{
                                    background: isActive ? m.color + '20' : isDone ? '#f1f5f9' : '#f8fafc',
                                    border: `1px solid ${isActive ? m.color + '30' : '#e2e8f0'}`
                                }}
                            >
                                {isDone
                                    ? <FiCheckCircle size={16} className="text-emerald-500" />
                                    : <ManeuverIcon type={m.svg} size={20} color={isActive ? m.color : '#94a3b8'} />
                                }
                            </div>
                            <div className="flex-1 min-w-0">
                                <p
                                    className={`text-xs font-bold leading-snug truncate ${isActive ? 'text-slate-900' : 'text-slate-600'}`}
                                    dangerouslySetInnerHTML={{ __html: step.instruction || '' }}
                                />
                                {step.distance && (
                                    <p className="text-[10px] text-slate-400 font-medium mt-0.5 flex items-center gap-1">
                                        <FiMapPin size={10} /> {step.distance}
                                        {step.duration && <> · <FiClock size={10} /> {step.duration}</>}
                                    </p>
                                )}
                            </div>
                            <div className="flex flex-col items-end gap-1 shrink-0">
                                {isActive && (
                                    <span
                                        className="text-[9px] font-black uppercase px-2 py-0.5 rounded-full"
                                        style={{ background: m.color, color: '#fff' }}
                                    >
                                        NOW
                                    </span>
                                )}
                                <span className="text-[10px] text-slate-300 font-bold">#{idx + 1}</span>
                            </div>
                        </button>
                    );
                })}
            </div>

            {/* ── Action Bar ── */}
            <div className="px-6 pb-6 pt-4 border-t border-slate-100 space-y-3">
                {/* Step controls */}
                <div className="flex gap-2">
                    <button
                        onClick={() => setStepIdx(i => Math.max(0, i - 1))}
                        disabled={stepIdx === 0}
                        className="flex-1 py-2.5 bg-slate-50 text-slate-500 rounded-2xl font-bold text-xs border border-slate-200 disabled:opacity-40 transition-all hover:bg-slate-100"
                    >
                        ← Prev Step
                    </button>
                    <button
                        onClick={() => {
                            const ni = Math.min(allSteps.length - 1, stepIdx + 1);
                            setStepIdx(ni);
                            if (voiceOn && allSteps[ni]?.instruction) speak(stripHtml(allSteps[ni].instruction));
                        }}
                        disabled={stepIdx === allSteps.length - 1}
                        className="flex-1 py-2.5 text-white rounded-2xl font-bold text-xs transition-all disabled:opacity-40"
                        style={{
                            background: stepIdx < allSteps.length - 1
                                ? `linear-gradient(135deg, ${maneuverInfo.color}, ${maneuverInfo.color}cc)`
                                : '#e2e8f0'
                        }}
                    >
                        Next Step →
                    </button>
                </div>

                {/* Complete delivery */}
                {onDeliveryComplete && (
                    <button
                        onClick={onDeliveryComplete}
                        className="w-full py-4 bg-emerald-500 hover:bg-emerald-600 text-white rounded-2xl font-black text-sm transition-all shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2"
                    >
                        <FiCheckCircle size={18} /> MARK AS DELIVERED
                    </button>
                )}
            </div>
        </div>
    );
};

export default LiveNavigationHUD;
export { ManeuverIcon, MANEUVER_MAP, fmtDist, fmtTime };
