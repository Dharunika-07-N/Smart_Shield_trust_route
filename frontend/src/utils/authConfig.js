import {
    FiUser, FiTruck, FiBriefcase, FiShield, FiHeadphones
} from 'react-icons/fi';

/**
 * User Roles & Their Configuration
 */
export const ROLE_OPTIONS = [
    {
        value: 'rider',
        label: 'Rider',
        icon: FiUser,
        needsLogin: true,
        canSelfRegister: true,
        defaultRoute: '/rider/dashboard',
        permissions: ['book_ride', 'view_own_rides', 'rate_driver', 'manage_profile']
    },
    {
        value: 'driver',
        label: 'Driver',
        icon: FiTruck,
        needsLogin: true,
        canSelfRegister: true,
        requiresApproval: true,
        defaultRoute: '/driver/dashboard',
        permissions: ['view_assigned_rides', 'accept_rides', 'update_location', 'manage_profile']
    },
    {
        value: 'dispatcher',
        label: 'Dispatcher',
        icon: FiHeadphones,
        needsLogin: true,
        canSelfRegister: false,
        defaultRoute: '/dispatcher/dashboard',
        permissions: ['view_all_rides', 'assign_drivers', 'manage_bookings', 'customer_support']
    },
    {
        value: 'admin',
        label: 'Admin',
        icon: FiBriefcase,
        needsLogin: true,
        canSelfRegister: false,
        defaultRoute: '/admin/dashboard',
        permissions: ['manage_users', 'manage_drivers', 'manage_dispatchers', 'view_analytics', 'system_settings']
    },
    {
        value: 'super_admin',
        label: 'Super Admin',
        icon: FiShield,
        needsLogin: true,
        canSelfRegister: false,
        showInUI: false,
        defaultRoute: '/super-admin/dashboard',
        permissions: ['all']
    }
];

/**
 * Login Page Display & Behavior Configuration
 */
export const LOGIN_PAGE_CONFIG = {
    showRoleSelection: true,

    visibleRoles: [
        'rider',
        'driver',
        'dispatcher',
        'admin'
    ],

    allowRegistration: {
        rider: true,
        driver: true,
        dispatcher: false,
        admin: false,
        super_admin: false
    },

    requiresVerification: {
        rider: false,
        driver: true,
        dispatcher: false,
        admin: false,
        super_admin: false
    }
};
