import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    FiUser, FiLock, FiMail, FiCheckCircle, FiShield,
    FiTruck, FiPhone, FiCreditCard, FiList,
    FiBriefcase, FiKey, FiAlertTriangle, FiEye, FiEyeOff,
    FiFileText
} from 'react-icons/fi';

import { API_BASE_URL as API_URL } from '../utils/constants';
import { ROLE_OPTIONS, LOGIN_PAGE_CONFIG } from '../utils/authConfig';

const Auth = ({ setAuth }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [role, setRole] = useState('rider');

    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        confirmPassword: '',
        full_name: '',
        phone: '',
        email: '',
        admin_code: '',
        license_number: '',
        vehicle_type: 'motorcycle',
        vehicle_number: '',
        gender: 'female',
        emergency_contact_phone: '',
        emergency_contact_email: ''
    });
    const [errors, setErrors] = useState({});
    const [globalError, setGlobalError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    // Check if registration is allowed for current role
    const canRegister = LOGIN_PAGE_CONFIG.allowRegistration[role];

    // Filter visible roles for selection
    const visibleRoles = ROLE_OPTIONS.filter(r =>
        LOGIN_PAGE_CONFIG.visibleRoles.includes(r.value)
    );

    // Sync isLogin with canRegister when role changes
    useEffect(() => {
        if (!canRegister && !isLogin) {
            setIsLogin(true);
        }
    }, [role, canRegister, isLogin]);

    // Real-time validation
    useEffect(() => {
        if (!isLogin) {
            validateField('email', formData.email);
            validateField('password', formData.password);
            if (formData.confirmPassword) {
                validateField('confirmPassword', formData.confirmPassword);
            }
        }
    }, [formData.email, formData.password, formData.confirmPassword, isLogin]);

    const validateField = (name, value) => {
        let newErrors = { ...errors };

        switch (name) {
            case 'email':
                if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                    newErrors.email = 'Invalid email format';
                } else {
                    delete newErrors.email;
                }
                break;
            case 'password':
                if (!isLogin && value && value.length < 6) {
                    newErrors.password = 'Password must be at least 6 characters';
                } else {
                    delete newErrors.password;
                }
                break;
            case 'confirmPassword':
                if (value && value !== formData.password) {
                    newErrors.confirmPassword = 'Passwords do not match';
                } else {
                    delete newErrors.confirmPassword;
                }
                break;
            case 'phone':
                if (value && !/^\+?[\d\s-()]+$/.test(value)) {
                    newErrors.phone = 'Invalid phone number';
                } else {
                    delete newErrors.phone;
                }
                break;
            default:
                break;
        }

        setErrors(newErrors);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
        validateField(name, value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setGlobalError('');

        // Validate all fields
        if (!isLogin && formData.password !== formData.confirmPassword) {
            setGlobalError('Passwords do not match');
            setLoading(false);
            return;
        }

        if (Object.keys(errors).length > 0) {
            setGlobalError('Please fix all errors before submitting');
            setLoading(false);
            return;
        }

        try {
            const endpoint = isLogin ? '/auth/login' : '/auth/register';

            const payload = isLogin
                ? {
                    username: formData.email,
                    password: formData.password,
                    role: role // Pass role to login for backend validation
                }
                : {
                    ...formData,
                    username: formData.email,
                    role: role
                };

            const response = await axios.post(`${API_URL}${endpoint}`, payload);

            if (isLogin) {
                localStorage.setItem('auth_token', response.data.access_token);
                localStorage.setItem('user', response.data.username);
                localStorage.setItem('user_id', response.data.user_id);
                localStorage.setItem('role', response.data.role);

                if (rememberMe) {
                    localStorage.setItem('rememberMe', 'true');
                }

                if (response.data.role === 'rider') {
                    localStorage.setItem('rider_id', response.data.user_id);
                }

                setAuth(true);

                // Get default route from config
                const configRole = ROLE_OPTIONS.find(r => r.value === response.data.role);
                navigate(configRole?.defaultRoute || '/dashboard');
            } else {
                setIsLogin(true);
                if (role === 'driver') {
                    setGlobalError('Application submitted successfully! Our team will review your account.');
                } else {
                    setGlobalError('Account created successfully! Please sign in.');
                }
            }
        } catch (err) {
            setGlobalError(err.response?.data?.detail || 'An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0F172A] via-slate-900 to-[#0F172A] px-4 py-12 relative overflow-hidden">
            {/* Animated Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
                <div className="absolute top-[-20%] left-[-15%] w-[500px] h-[500px] bg-[#2563EB]/20 rounded-full blur-[150px] animate-pulse"></div>
                <div className="absolute bottom-[-20%] right-[-15%] w-[500px] h-[500px] bg-[#10B981]/20 rounded-full blur-[150px] animate-pulse" style={{ animationDelay: '1s' }}></div>
            </div>

            <div className="max-w-2xl w-full z-10 transition-all transform duration-500">
                {/* Dev Bypass */}
                <div className="absolute top-4 right-4 z-50">
                    <button
                        onClick={() => {
                            localStorage.setItem('auth_token', 'dev_token');
                            localStorage.setItem('role', 'rider');
                            setAuth(true);
                            navigate('/dashboard');
                        }}
                        className="text-[10px] text-white/20 hover:text-white/50 bg-white/5 px-2 py-1 rounded"
                    >
                        Skip Login (Dev)
                    </button>
                </div>

                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center p-4 bg-gradient-to-br from-[#2563EB] to-[#1e40af] rounded-3xl mb-5 shadow-2xl relative group">
                        <FiShield size={40} className="text-white relative z-10" />
                        <div className="absolute inset-0 bg-white opacity-20 blur-xl rounded-full scale-50 group-hover:scale-100 transition-transform"></div>
                    </div>
                    <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 mb-3 tracking-tight">
                        Smart Shield
                    </h1>
                    <p className="text-gray-400 text-lg font-light tracking-wide uppercase text-xs">AI-Powered Multi-Role Trust Route</p>
                </div>

                <div className="bg-white/5 backdrop-blur-3xl border border-white/10 p-1 rounded-3xl shadow-3xl overflow-hidden">
                    <div className="p-8 md:p-10">
                        {/* Role Tabs */}
                        <div className="flex flex-wrap justify-center gap-3 mb-10">
                            {visibleRoles.map((option) => {
                                const Icon = option.icon;
                                const isSelected = role === option.value;
                                return (
                                    <button
                                        key={option.value}
                                        type="button"
                                        onClick={() => setRole(option.value)}
                                        className={`flex items-center gap-2 px-5 py-2.5 rounded-full border transition-all duration-300 ${isSelected
                                            ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-600/20'
                                            : 'border-white/10 text-gray-400 hover:border-white/30 hover:text-white bg-white/5'
                                            }`}
                                    >
                                        <Icon size={18} />
                                        <span className="font-semibold text-sm tracking-wide">{option.label}</span>
                                    </button>
                                );
                            })}
                        </div>

                        {/* Login/Signup Toggle */}
                        <div className="flex bg-black/40 p-1 rounded-2xl mb-8 border border-white/5 max-w-sm mx-auto">
                            <button
                                onClick={() => setIsLogin(true)}
                                className={`flex-1 py-3 text-sm font-bold rounded-xl transition-all duration-300 ${isLogin
                                    ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg'
                                    : 'text-gray-500 hover:text-white'
                                    }`}
                            >
                                Sign In
                            </button>
                            {canRegister && (
                                <button
                                    onClick={() => setIsLogin(false)}
                                    className={`flex-1 py-3 text-sm font-bold rounded-xl transition-all duration-300 ${!isLogin
                                        ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg'
                                        : 'text-gray-500 hover:text-white'
                                        }`}
                                >
                                    Register
                                </button>
                            )}
                        </div>

                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Email */}
                                <div className={!isLogin ? "md:col-span-1" : "md:col-span-2"}>
                                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Login Email</label>
                                    <div className="relative group">
                                        <FiMail className={`absolute left-4 top-1/2 -translate-y-1/2 ${errors.email ? 'text-red-400' : 'text-gray-500 group-focus-within:text-blue-400'} transition-colors`} />
                                        <input
                                            type="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleInputChange}
                                            required
                                            className={`w-full bg-black/20 border rounded-2xl py-3.5 pl-12 pr-4 text-white focus:ring-2 focus:border-transparent outline-none transition-all placeholder:text-gray-700 ${errors.email ? 'border-red-500/50 focus:ring-red-500/20' : 'border-white/10 focus:ring-blue-500/20'}`}
                                            placeholder="Enter your email"
                                        />
                                    </div>
                                    {errors.email && <p className="mt-1.5 text-xs text-red-400 px-1">{errors.email}</p>}
                                </div>

                                {/* Full Name (Signup only) */}
                                {!isLogin && (
                                    <div className="md:col-span-1">
                                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Full Name</label>
                                        <div className="relative group">
                                            <FiUser className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-blue-400 transition-colors" />
                                            <input
                                                type="text"
                                                name="full_name"
                                                value={formData.full_name}
                                                onChange={handleInputChange}
                                                required
                                                className="w-full bg-black/20 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-white focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                                                placeholder="Legal name"
                                            />
                                        </div>
                                    </div>
                                )}

                                {/* Password */}
                                <div className={!isLogin ? "md:col-span-1" : "md:col-span-2"}>
                                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Password</label>
                                    <div className="relative group">
                                        <FiLock className={`absolute left-4 top-1/2 -translate-y-1/2 ${errors.password ? 'text-red-400' : 'text-gray-500 group-focus-within:text-blue-400'} transition-colors`} />
                                        <input
                                            type={showPassword ? "text" : "password"}
                                            name="password"
                                            value={formData.password}
                                            onChange={handleInputChange}
                                            required
                                            className={`w-full bg-black/20 border rounded-2xl py-3.5 pl-12 pr-12 text-white focus:ring-2 focus:border-transparent outline-none transition-all placeholder:text-gray-700 ${errors.password ? 'border-red-500/50 focus:ring-red-500/20' : 'border-white/10 focus:ring-blue-500/20'}`}
                                            placeholder="••••••••"
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowPassword(!showPassword)}
                                            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-600 hover:text-white"
                                        >
                                            {showPassword ? <FiEyeOff size={18} /> : <FiEye size={18} />}
                                        </button>
                                    </div>
                                    {errors.password && <p className="mt-1.5 text-xs text-red-400 px-1">{errors.password}</p>}
                                </div>

                                {/* Confirm Password (Signup) */}
                                {!isLogin && (
                                    <div className="md:col-span-1">
                                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Confirm Password</label>
                                        <div className="relative group">
                                            <FiLock className={`absolute left-4 top-1/2 -translate-y-1/2 ${errors.confirmPassword ? 'text-red-400' : 'text-gray-500 group-focus-within:text-blue-400'} transition-colors`} />
                                            <input
                                                type={showConfirmPassword ? "text" : "password"}
                                                name="confirmPassword"
                                                value={formData.confirmPassword}
                                                onChange={handleInputChange}
                                                required
                                                className={`w-full bg-black/20 border rounded-2xl py-3.5 pl-12 pr-12 text-white focus:ring-2 focus:border-transparent outline-none transition-all placeholder:text-gray-700 ${errors.confirmPassword ? 'border-red-500/50 focus:ring-red-500/20' : 'border-white/10 focus:ring-blue-500/20'}`}
                                                placeholder="••••••••"
                                            />
                                            <button
                                                type="button"
                                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-600 hover:text-white"
                                            >
                                                {showConfirmPassword ? <FiEyeOff size={18} /> : <FiEye size={18} />}
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {!isLogin && (
                                    <>
                                        {/* Common Profile Fields */}
                                        <div className="md:col-span-1">
                                            <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Phone Number</label>
                                            <div className="relative group">
                                                <FiPhone className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
                                                <input
                                                    type="text"
                                                    name="phone"
                                                    value={formData.phone}
                                                    onChange={handleInputChange}
                                                    required
                                                    className="w-full bg-black/20 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-white outline-none focus:ring-2 focus:ring-blue-500/20"
                                                    placeholder="+1"
                                                />
                                            </div>
                                        </div>

                                        {/* Driver Specific Registration */}
                                        {role === 'driver' && (
                                            <>
                                                <div className="md:col-span-1">
                                                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">License ID</label>
                                                    <div className="relative group">
                                                        <FiCreditCard className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
                                                        <input
                                                            type="text"
                                                            name="license_number"
                                                            value={formData.license_number}
                                                            onChange={handleInputChange}
                                                            required
                                                            className="w-full bg-black/20 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-white outline-none focus:ring-2 focus:ring-blue-500/20"
                                                            placeholder="AB12345"
                                                        />
                                                    </div>
                                                </div>
                                                <div className="md:col-span-1">
                                                    <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Vehicle Number</label>
                                                    <div className="relative group">
                                                        <FiBriefcase className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
                                                        <input
                                                            type="text"
                                                            name="vehicle_number"
                                                            value={formData.vehicle_number}
                                                            onChange={handleInputChange}
                                                            required
                                                            className="w-full bg-black/20 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-white outline-none focus:ring-2 focus:ring-blue-500/20"
                                                            placeholder="TN 01 AB 1234"
                                                        />
                                                    </div>
                                                </div>
                                            </>
                                        )}

                                        {/* Rider Specific Registration */}
                                        {role === 'rider' && (
                                            <div className="md:col-span-1">
                                                <label className="block text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Gender</label>
                                                <div className="relative">
                                                    <FiUser className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 z-10" />
                                                    <select
                                                        name="gender"
                                                        value={formData.gender}
                                                        onChange={handleInputChange}
                                                        className="w-full bg-black/20 border border-white/10 rounded-2xl py-3.5 pl-12 pr-4 text-white outline-none focus:ring-2 focus:ring-blue-500/20 appearance-none"
                                                    >
                                                        <option value="female" className="bg-slate-900 leading-tight">Female</option>
                                                        <option value="male" className="bg-slate-900 leading-tight">Male</option>
                                                        <option value="other" className="bg-slate-900 leading-tight">Other</option>
                                                    </select>
                                                </div>
                                            </div>
                                        )}
                                    </>
                                )}
                            </div>

                            {/* Status and Info Messages for non-self registrable roles */}
                            {!canRegister && !isLogin && (
                                <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-2xl flex items-start gap-3">
                                    <FiAlertTriangle className="text-amber-500 shrink-0 mt-0.5" />
                                    <p className="text-xs text-amber-200/80 leading-relaxed">
                                        Accounts for {role === 'dispatcher' ? 'Dispatchers' : 'Admins'} are managed by the organization.
                                        Please contact your system administrator for access.
                                    </p>
                                </div>
                            )}

                            {/* Error Reporting */}
                            {globalError && (
                                <div className={`p-4 rounded-2xl flex items-center gap-3 backdrop-blur-md animate-in fade-in slide-in-from-top-2 duration-300 ${globalError.includes('successfully') ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border border-red-500/20 text-red-400'}`}>
                                    {globalError.includes('successfully') ? <FiCheckCircle className="shrink-0" /> : <FiAlertTriangle className="shrink-0" />}
                                    <span className="text-sm font-medium">{globalError}</span>
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={loading || (Object.keys(errors).length > 0) || (!canRegister && !isLogin)}
                                className="w-full py-4 bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white font-bold rounded-2xl shadow-xl shadow-blue-500/10 transition-all active:scale-[0.98] disabled:opacity-30 disabled:grayscale disabled:cursor-not-allowed group"
                            >
                                {loading ? (
                                    <div className="flex items-center justify-center gap-2">
                                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                        <span>Processing...</span>
                                    </div>
                                ) : (
                                    <div className="flex items-center justify-center gap-2">
                                        <span>{isLogin ? 'Enter Dashboard' : (role === 'driver' ? 'Submit Application' : 'Create Account')}</span>
                                        <FiShield className="group-hover:translate-x-1 transition-transform" />
                                    </div>
                                )}
                            </button>
                        </form>

                        <div className="mt-8 text-center">
                            {isLogin ? (
                                <p className="text-gray-500 text-sm">
                                    {canRegister ? (
                                        <>New to Smart Shield? <span onClick={() => setIsLogin(false)} className="text-blue-400 font-bold cursor-pointer hover:underline underline-offset-4 decoration-2">Apply Now</span></>
                                    ) : (
                                        <span className="opacity-50 italic italic">Restricted Access: Organizational Login Only</span>
                                    )}
                                </p>
                            ) : (
                                <p className="text-gray-500 text-sm">
                                    Already using Smart Shield? <span onClick={() => setIsLogin(true)} className="text-blue-400 font-bold cursor-pointer hover:underline underline-offset-4 decoration-2">Sign In</span>
                                </p>
                            )}
                        </div>
                    </div>
                </div>

                <p className="mt-8 text-center text-gray-600 text-[10px] font-bold uppercase tracking-[0.2em]">
                    Enterprise-Grade Safety Infrastructure &copy; 2026
                </p>
            </div>
        </div>
    );
};

export default Auth;
