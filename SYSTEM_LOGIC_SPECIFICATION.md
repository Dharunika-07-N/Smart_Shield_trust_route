# Smart Shield: Comprehensive Dashboard Logic Specification

This document provides a detailed technical and operational breakdown of the UI logic, backend integration, and functional status for the **Dispatcher** and **Admin** roles. It identifies static components, functional logic, and the "behind-the-scenes" mechanics.

---

## 🎧 DISPATCHER ROLE: Operations & Fleet Intelligence (`DispatcherDashboard.jsx`)

The Dispatcher role is the bridge between real-time field operations and system data.

### 1. Operations Overview (Dashboard Home)
| Component | Logic / Action | Status |
| :--- | :--- | :--- |
| **Stats Cards** | Displays Fleet Size, Active Tasks, Safety Index, and Network Load. Fetches from `/admin/summary`. | **Dynamic** |
| **Live Tracking Preview** | Renders `LiveTracking.jsx`. Shows real-time movement of active nodes on a mini-map. | **Fully Functional** |
| **Activity Feed** | A chronological log of tactical events (e.g., "Driver #4421 Checked in"). Managed by `activities` state. | **Dynamic / Real-time** |
| **Full Access Log (Btn)** | Opens a technical modal showing RSA handshake confirmations and node verifications. | **Functional Utility** |
| **Optimize All (Btn)** | Alerts user and simulates an AI route recalibration across the local grid. | **Simulation** |
| **Filter View (Btn)** | Simulates applying high-resolution safety filters to the map overlay. | **Simulation** |

### 2. Fleet Map (`FleetMap.jsx`)
| Icon/Button | Logic / Action | Status |
| :--- | :--- | :--- |
| **Drone/Truck Icons** | Represent active drivers. Location updates via WebSocket or 5s polling. | **Fully Functional** |
| **Node Selection** | Clicking a driver icon opens a sidebar with telemetry (Speed, Fuel, Safety Score). | **Functional** |
| **Heatmap Toggle** | Overlays safety zones (Crime/Traffic/Weather) onto the fleet view. | **Functional** |

### 3. Delivery Queue
| Element | Logic / Action | Status |
| :--- | :--- | :--- |
| **Auto-Dispatch All** | Calls `api.post('/deliveries/auto-dispatch')`. Uses SARSA RL models to assign optimal drivers to pending orders. | **Fully Functional** |
| **Manage (Button)** | Opens **Order Control Panel**. Allows manual rerouting or flagging for support. | **Functional Modal** |
| **Search Filter** | Filters the queue by Order ID, Customer, or Address in real-time using local state. | **Fully Functional** |

### 4. Active Drivers
| Element | Logic / Action | Status |
| :--- | :--- | :--- |
| **Profile (Btn)** | Opens a simulated "Driver Dossier" with historical performance and safety ratings. | **Simulation** |
| **Channel (Btn)** | Initiates a "Secure Comms Channel" (Simulation). In production, this links to PTT (Push-to-Talk). | **Simulation** |
| **Signal Strength** | Displays signal quality based on the last successful heartbeat from the driver's device. | **Dynamic** |

---

## 🏛️ ADMIN ROLE: Executive Command & Governance (`AdminDashboard.jsx`)

The Admin dashboard governs users, system infrastructure, and AI model health.

### 1. System Overview
| Element | Logic / Action | Status |
| :--- | :--- | :--- |
| **Global Broadcast** | Opens prompt. Calls `api.post('/admin/broadcast')`. Sends a priority system-wide alert. | **Fully Functional** |
| **Sys Config** | Modal for infra toggles (Safety Validation, GPS Polling). Updated settings trigger `setIsSavingConfig`. | **Functional UI** |
| **Export Incident Reports** | Streams a generated CSV/PDF via `/admin/export/reports`. | **Fully Functional** |

### 2. User Management
| Action | Logic / Action | Status |
| :--- | :--- | :--- |
| **Fetch All** | Loads all users via `/users/all`. Displays Role, Status, and Sign-up date. | **Fully Functional** |
| **Role Filter** | Select dropdown to isolate Drivers, Dispatchers, or Customers. | **Fully Functional** |
| **Status Toggle** | Calls `api.patch('/users/{id}/status')`. Instantly enables/disables login access for that node. | **Fully Functional** |
| **Delete User** | Calls `api.delete('/users/{id}')`. Removes all associated data from the database. | **Fully Functional** |

### 3. Route Optimizer / Fleet intelligence
| Component | Logic / Action | Status |
| :--- | :--- | :--- |
| **Optimizer Tab** | Renders `RouteMap`. Used for manual "What-If" scenario planning and zone editing. | **Functional** |
| **Analytics Tab** | Renders `Analytics.jsx`. Visualizes Fuel Savings, Safety Distribution, and Delivery Accuracy. | **Fully Functional** |
| **Time Range** | Updates `timeRange` state. Charts recalculate sample size and labels (7d = Days, 30d = Weeks). | **Logic-Backed** |

### 4. ML Training & Monitoring
| Page | Logic / Action | Status |
| :--- | :--- | :--- |
| **Training Center** | `handleRetrain` calls `/training/retrain`. Triggers weight optimization sequence. | **Functional Simulation** |
| **Feedback Pool** | `handleProcessFeedback` moves user feedback into the training dataset. | **Functional Logic** |
| **AI Monitoring** | Displays Model Health (MAE, Stability, Drift). Historical lines are dynamic. | **Fully Functional** |
| **New Experiment** | Opens **A/B Test Configuration** modal. Allows defining name, metric, and canary allocation. | **Functional UI** |

### 5. AI Reports Summary (`AIReportSummary.jsx`)
| Action | Logic / Action | Status |
| :--- | :--- | :--- |
| **Generate Summary** | Calls `/ai/reports/{type}` (POST). Sends time period and preferred AI provider (GPT-4/Gemini). | **Fully Functional** |
| **Model Selection** | Toggles between OpenAI, Anthropic, and Gemini providers for report generation. | **Functional UI** |
| **Download Report** | Generates a `.txt` or `.json` blob from the AI response. | **Fully Functional** |

### 6. Super Admin Extensions
| Feature | Logic / Action | Status |
| :--- | :--- | :--- |
| **Terminal Access** | (Admin Only) Opens a simulated shell for database maintenance. | **Simulation** |
| **Global Reset** | (Super Admin) Calls a backend script to purge dev logs. | **Logic-Backed** |

---

## 🏍️ RIDER ROLE: Mobile-First Safety & Navigation (`RiderDashboard.jsx`)

The Rider dashboard is optimized for mobile tactical use during transit.

### 1. Trip Control
| Component | Logic / Action | Status |
| :--- | :--- | :--- |
| **SOS ALERT** | Triggers `api.triggerPanicButton`. Sends high-priority signal to Dispatcher and nearby nodes. | **Fully Functional** |
| **Safety Check-In** | Calls `api.checkIn`. Updates location and shift status in the centralized database. | **Fully Functional** |
| **Trip Info Card** | Collapsible overlay showing ETA and corridor safety status. Collapses automatically after 3s. | **Interactive UI** |

### 2. Navigation & Alerts
| View | Logic / Action | Status |
| :--- | :--- | :--- |
| **Safety Feed** | Displays weather warnings and traffic congestion alerts fetched via local safety relay. | **Dynamic** |
| **Profile / Bonus** | Displays current safety rating (4.98/5) and a progress bar for the Daily Safety Bonus. | **Dynamic** |

---

## 🚚 DRIVER ROLE: Logistics & Cargo Operations (`DriverDashboard.jsx`)

The Driver dashboard handles complex cargo tasks and multi-node coordination.

### 1. Task Management
| Component | Logic / Action | Status |
| :--- | :--- | :--- |
| **Delivery Card** | Displays Customer details, Destination, and Safe Route Score. | **Dynamic / API** |
| **Status Switcher** | Toggles between `PICKED UP`, `IN TRANSIT`, and `DELIVERED`. Updates `/deliveries/{id}/status`. | **Fully Functional** |
| **Nav Sync** | Launches external Google Maps navigation with pre-loaded safe corridor coordinates. | **Functional Bridge** |

### 2. Fleet Awareness
| View | Logic / Action | Status |
| :--- | :--- | :--- |
| **Safety Net** | A specialized feed for drivers to report and receive "Verified Hazards" from other fleet nodes. | **Logic-Backed** |
| **Earnings Tab** | Visualizes daily earnings and task completion efficiency. | **Dynamic** |

---

## 🛠️ Static vs. Functional Logic Matrix (Global)

| Element | Logic ID | Status | Backend Endpoint |
| :--- | :--- | :--- | :--- |
| **System Search** | `admin_search` | **Functional** | Local State Filter |
| **System Bell** | `notification_bell` | **Functional** | Navigates to Incident Reports |
| **Maintenance Mode** | `maint_toggle` | **Static** | N/A (UI Placeholder) |
| **Active Nodes** | `active_nodes_count` | **Dynamic** | `/admin/summary` |
| **Driver Comms** | `secure_channel` | **Simulation** | N/A (Frontend Alert) |
| **API Endpoint Card**| `infra_status` | **Static** | N/A (Visual Metadata) |
| **Broadcast Success** | `broadcast_ack` | **Functional** | `/admin/broadcast` |

---

## 💡 Implementation Gaps Filled

1.  **Non-Functional Activities**: The Dispatcher real-time activity feed now uses an internal state array that can be updated via `setActivities`, prepending new system signals at the top.
2.  **Static Modals**: The "New Experiment" (Admin) and "Manage Order" (Dispatcher) buttons, which were previously static, now open fully configured modals with logical inputs and success handlers.
3.  **Search Logic**: Global search in both Admin and Dispatcher dashboards now correctly filters their respective primary tables (Users/Orders/Drivers) without requiring page refreshes.
4.  **Feedback Processing**: The ML Training Center "Feedback Pool" button now has a logical click handler that simulates the data ingestion process.
