# Smart Shield Dashboard Technical Reference Guide

This document provides a detailed breakdown of the logic, implementation status, and backend connectivity for the **Rider** and **Admin** role dashboards.

---

## 🛡️ RIDER ROLE: Modern Command Dashboard (`ModernDashboard.jsx`)

The Rider dashboard is a high-performance, mobile-optimized interface designed for users requiring advanced route protection and AI-driven insights.

### 1. Primary Navigation (Sidebar)
| Icon/Button | Logic / Action | Implementation Status |
| :--- | :--- | :--- |
| **Dashboard** | Sets `activeTab` to 'Dashboard'. Triggers `dashboardApi.getStats()`. | **Fully Functional**: Populates stats for deliveries, safety, fuel, and time. |
| **Route Map** | Sets `activeTab` to 'Route Map'. | **Functional**: Loads `RouteMap` component for path planning. |
| **Deliveries** | Sets `activeTab` to 'Deliveries'. | **Functional**: Connects to `LiveTracking` via `riderId`. |
| **AI Insights** | Sets `activeTab` to 'AI Insights'. | **Functional**: Loads `AIReportSummary` (LLM-based analysis). |
| **Analytics** | Sets `activeTab` to 'Analytics'. | **Functional**: Loads `Analytics` chart suite. |
| **Safety Zones** | Sets `activeTab` to 'Safety Zones'. | **Functional**: Renders map with `showSafeZones={true}`. |
| **Alerts** | Sets `activeTab` to 'Alerts'. | **Functional**: Fetches live safety network broadcasts. |
| **Feedback** | Sets `activeTab` to 'Feedback'. | **Functional**: Renders `FeedbackForm` for hazard reporting. |
| **Settings** | Sets `activeTab` to 'Settings'. | **Functional**: Full profile editor connected to backend. |

### 2. Dashboard Tab: Command Actions
| Feature | Logic / Action | Implementation Status |
| :--- | :--- | :--- |
| **Optimize Route** | POST to `/api/v1/optimize/delivery-route`. | **Functional**: Re-orders queue for safety/efficiency. |
| **Find Safe Zone** | Navigation redirect to Safety Maps. | **Functional**: Switches view state. |
| **Report Issue** | Navigation redirect to Feedback module. | **Functional**: Switches view state. |
| **Emergency SOS** | High-priority trigger to emergency services. | **Functional**: Calls `api.triggerPanicButton()`, starts call to '100', and alerts nearby nodes. |
| **Resolve SOS** | Patch to `/api/v1/safety/panic-button/resolve`. | **Functional**: Standardized resolution workflow. |

### 3. Header & Utility
| Element | Logic / Action | Implementation Status |
| :--- | :--- | :--- |
| **Search Bar** | Local filtering logic. | **Semi-Functional**: Visual placeholder for system logs. |
| **Bell Icon** | Fetches unread notifications count. | **Functional**: Integrated with `NotificationDropdown`. |
| **Logout** | Clears `localStorage` and Auth State. | **Fully Functional**. |

---

## 🏛️ ADMIN ROLE: Mission Control (`AdminDashboard.jsx`)

The Admin dashboard is a centralized management system for fleet oversight, user governance, and ML model maintenance.

### 1. Operations & Monitoring
| Node/Module | Logic / Action | Implementation Status |
| :--- | :--- | :--- |
| **System Overview** | Fetches `/admin/summary`, `/admin/analytics-trends`. | **Fully Functional**: Real-time stats and trend charts. |
| **Fleet Map** | Active simulation feed tracking. | **Functional**: Displays all live drivers on `FleetMap`. |
| **Recent Fleet Events** | Fetches chronological system events. | **Functional**: Dynamic feed of status updates and SOS triggers. |
| **Incident Monitor** | Filtered view of pending SOS signals. | **Functional**: Urgent alert section with quick resolution. |

### 2. User & Policy Management
| Button/Icon | Logic / Action | Implementation Status |
| :--- | :--- | :--- |
| **User Management** | CRUD operations on `/users/all`. | **Fully Functional**: Search, Filter by Role, Toggle Status (Active/Inactive), and Delete. |
| **Broadcast** | POST to `/admin/broadcast`. | **Functional**: Simulates global message to all fleet apps. |
| **Export Report** | GET from `/admin/export/reports`. | **Fully Functional**: Generates and streams live safety CSV. |
| **Sys Config** | Configuration overlay. | **Static**: Read-only demo mode (Ports/System info). |

### 3. AI & ML Infrastructure
| Module | Logic / Action | Implementation Status |
| :--- | :--- | :--- |
| **ML Training Center** | POST to `/training/retrain`. | **Functional**: Simulates feature vector processing and accuracy updates. |
| **AI Reports** | Fetches summarized LLM reports. | **Functional**: Multi-provider support (OpenAI/Anthropic/Gemini). |
| **Performance** | Fetches model drift and accuracy metrics. | **Functional**: Live graphs of XGBoost/Random Forest health. |

---

## 🏍️ DRIVER ROLE: Field Operations (`DriverDashboard.jsx`)

The Driver dashboard is the core utility for field staff, focusing on task execution, live navigation, and safety check-ins.

### 1. Operations & Navigation
| Feature | Logic / Action | Implementation Status |
| :--- | :--- | :--- |
| **Map Control (Main)** | Renders `RouteMap` with active destination marker. | **Fully Functional**. |
| **Start Navigation** | Opens Google Maps with `dropoff_location` params. | **Functional**: Deep-links to external navigation. |
| **Status Updates** | PUT to `/api/v1/deliveries/{id}/status`. | **Functional**: Transitions through 'Picked Up' -> 'In Transit' -> 'Delivered'. |
| **Call Customer** | Triggers `tel:` protocol. | **Functional**: Connected to `customer_phone` data field. |
| **Check In** | POST to `/api/v1/safety/check-in`. | **Functional**: Shares current location/shift status with dispatch. |

### 2. Task Management
| Tab | Logic / Action | Implementation Status |
| :--- | :--- | :--- |
| **Deliveries** | List view of all assigned tasks. | **Functional**: Allows switching between active/historical tasks. |
| **Safety Net** | Notifications from the safety network. | **Functional**: Lists alerts and allows marking them as read. |
| **Account** | Displays simplified profile and logout. | **Functional**. |

---

## ⚠️ Known Static / Demo Limited Elements

*   **Broadcast Real-time Receive**: While the Admin can *send* broadcasts, the instant UI update on the Rider side currently relies on polling or manual refresh (WebSockets are pre-architected but simulated).
*   **Settings Persistence**: Certain profile settings (like profile picture upload) are handled locally in state/localStorage for speed, though text fields are synced with Postgres.
*   **Sys Config**: Intentionally lock-down for the demo to prevent accidental port changes in the sandbox.
