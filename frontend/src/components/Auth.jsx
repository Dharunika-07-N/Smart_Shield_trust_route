import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    FiUser, FiLock, FiMail, FiCheckCircle, FiShield,
    FiTruck, FiPhone, FiCreditCard, FiList,
    FiBriefcase, FiShoppingBag, FiKey, FiAlertTriangle, FiEye, FiEyeOff
} from 'react-icons/fi';

import { API_BASE_URL as API_URL } from '../utils/constants';

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
        gender: 'female',
        emergency_contact_phone: '',
        emergency_contact_email: ''
    });
    const [errors, setErrors] = useState({});
    const [globalError, setGlobalError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

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


            // Map frontend roles to backend roles
            const backendRole = role; // Using actual role values now


            const payload = isLogin
                ? {
                    username: formData.email, // Use email as username
                    password: formData.password
                }
                : {
                    ...formData,
                    username: formData.email, // Use email as username
                    role: backendRole
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

                // Auto-set rider_id for SOS system
                if (response.data.role === 'rider') {
                    localStorage.setItem('rider_id', response.data.user_id);
                }


                setAuth(true);
                navigate('/dashboard');
            } else {
                setIsLogin(true);
                setGlobalError('Account created successfully! Please sign in.');
            }
        } catch (err) {
            setGlobalError(err.response?.data?.detail || 'An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const roleOptions = [
        { value: 'rider', label: 'Rider', icon: FiUser, color: '#2563EB', gradient: 'from-blue-600 to-blue-500' },
        { value: 'dispatcher', label: 'Dispatcher', icon: FiTruck, color: '#10B981', gradient: 'from-green-600 to-emerald-500' },
        { value: 'admin', label: 'Admin', icon: FiBriefcase, color: '#EF4444', gradient: 'from-red-600 to-red-500' }
    ];


    const selectedRole = roleOptions.find(r => r.value === role);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0F172A] via-slate-900 to-[#0F172A] px-4 py-12 relative overflow-hidden">
            {/* Animated Background */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
                <div className="absolute top-[-20%] left-[-15%] w-[500px] h-[500px] bg-[#2563EB]/20 rounded-full blur-[150px] animate-pulse"></div>
                <div className="absolute bottom-[-20%] right-[-15%] w-[500px] h-[500px] bg-[#10B981]/20 rounded-full blur-[150px] animate-pulse" style={{ animationDelay: '1s' }}></div>
                <div className="absolute top-[40%] right-[20%] w-[300px] h-[300px] bg-[#2563EB]/10 rounded-full blur-[100px] animate-pulse" style={{ animationDelay: '0.5s' }}></div>
            </div>

            <div className="max-w-2xl w-full z-10">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center p-4 bg-gradient-to-br from-[#2563EB] to-[#1e40af] rounded-3xl mb-5 shadow-2xl shadow-[#2563EB]/30 relative group">
                        <div className="absolute inset-0 bg-gradient-to-br from-[#3b82f6] to-[#2563EB] rounded-3xl blur opacity-50 group-hover:opacity-75 transition-opacity"></div>
                        <FiShield size={40} className="text-white relative z-10" />
                    </div>
                    <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-[#2563EB] via-[#3b82f6] to-[#2563EB] mb-3 tracking-tight">
                        Smart Shield
                    </h1>
                    <p className="text-gray-400 text-lg font-light">AI-Powered Trust Route Security</p>
                </div>

                <div className="bg-white/5 backdrop-blur-2xl border border-white/10 p-10 rounded-3xl shadow-2xl relative">
                    <div className="absolute inset-0 bg-gradient-to-br from-[#2563EB]/5 to-[#10B981]/5 rounded-3xl pointer-events-none"></div>

                    {/* Login/Signup Toggle */}
                    <div className="flex bg-gray-900/50 p-1.5 rounded-2xl mb-8 relative">
                        <button
                            onClick={() => setIsLogin(true)}
                            className={`flex-1 py-3 text-sm font-semibold rounded-xl transition-all duration-300 relative ${isLogin
                                ? 'bg-gradient-to-r from-[#2563EB] to-[#1e40af] text-white shadow-lg shadow-[#2563EB]/30'
                                : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            Sign In
                        </button>
                        <button
                            onClick={() => setIsLogin(false)}
                            className={`flex-1 py-3 text-sm font-semibold rounded-xl transition-all duration-300 relative ${!isLogin
                                ? 'bg-gradient-to-r from-[#2563EB] to-[#1e40af] text-white shadow-lg shadow-[#2563EB]/30'
                                : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            Sign Up
                        </button>
                    </div>

                    {/* Role Selection (Signup only) */}
                    {!isLogin && (
                        <div className="mb-8 relative">
                            <label className="block text-sm font-medium text-gray-300 mb-4 text-center">Select Your Role</label>
                            <div className="grid grid-cols-3 gap-4">
                                {roleOptions.map((option) => {
                                    const Icon = option.icon;
                                    const isSelected = role === option.value;
                                    return (
                                        <button
                                            key={option.value}
                                            type="button"
                                            onClick={() => setRole(option.value)}
                                            className={`relative flex flex-col items-center gap-3 p-5 rounded-2xl border-2 transition-all duration-300 group ${isSelected
                                                ? `bg-gradient-to-br ${option.gradient} bg-opacity-10 shadow-lg border-opacity-100`
                                                : 'border-gray-700/50 bg-gray-800/30 hover:border-gray-600 hover:bg-gray-800/50'
                                                }`}
                                            style={isSelected ? { borderColor: option.color } : {}}
                                        >
                                            <div className={`p-3 rounded-xl ${isSelected ? 'bg-white/10' : 'bg-gray-700/30'} transition-all group-hover:scale-110`}>
                                                <Icon size={24} className={isSelected ? 'text-white' : 'text-gray-400'} />
                                            </div>
                                            <span className={`font-semibold text-sm ${isSelected ? 'text-white' : 'text-gray-400'}`}>
                                                {option.label}
                                            </span>
                                            {isSelected && (
                                                <div className="absolute -top-2 -right-2 p-1 bg-gradient-to-br from-[#10B981] to-[#059669] rounded-full">
                                                    <FiCheckCircle size={16} className="text-white" />
                                                </div>
                                            )}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5 relative">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                            {/* Email */}
                            <div className={!isLogin ? "md:col-span-1" : "md:col-span-2"}>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                                <div className="relative group">
                                    <FiMail className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors ${errors.email ? 'text-[#EF4444]' : 'text-gray-500 group-focus-within:text-[#2563EB]'}`} />
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleInputChange}
                                        required
                                        placeholder="john@example.com"
                                        className={`w-full bg-gray-900/50 border rounded-xl py-3 pl-12 pr-4 text-white focus:ring-2 focus:border-transparent outline-none transition-all placeholder:text-gray-600 hover:border-gray-600 ${errors.email ? 'border-[#EF4444] focus:ring-[#EF4444]' : 'border-gray-700/50 focus:ring-[#2563EB]'
                                            }`}
                                    />
                                </div>
                                {errors.email && <p className="mt-1 text-xs text-[#EF4444] flex items-center gap-1"><FiAlertTriangle size={12} />{errors.email}</p>}
                            </div>

                            {/* Full Name (Signup only) */}
                            {!isLogin && (
                                <div className="md:col-span-1">
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Full Name</label>
                                    <div className="relative group">
                                        <FiList className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-[#2563EB] transition-colors" />
                                        <input
                                            type="text"
                                            name="full_name"
                                            value={formData.full_name}
                                            onChange={handleInputChange}
                                            required
                                            placeholder="John Doe"
                                            className="w-full bg-gray-900/50 border border-gray-700/50 rounded-xl py-3 pl-12 pr-4 text-white focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition-all placeholder:text-gray-600 hover:border-gray-600"
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Password */}
                            <div className={!isLogin ? "md:col-span-1" : "md:col-span-2"}>
                                <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                                <div className="relative group">
                                    <FiLock className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors ${errors.password ? 'text-[#EF4444]' : 'text-gray-500 group-focus-within:text-[#2563EB]'}`} />
                                    <input
                                        type={showPassword ? "text" : "password"}
                                        name="password"
                                        value={formData.password}
                                        onChange={handleInputChange}
                                        required
                                        placeholder="••••••••"
                                        className={`w-full bg-gray-900/50 border rounded-xl py-3 pl-12 pr-12 text-white focus:ring-2 focus:border-transparent outline-none transition-all placeholder:text-gray-600 hover:border-gray-600 ${errors.password ? 'border-[#EF4444] focus:ring-[#EF4444]' : 'border-gray-700/50 focus:ring-[#2563EB]'
                                            }`}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-[#2563EB] transition-colors"
                                    >
                                        {showPassword ? <FiEyeOff size={18} /> : <FiEye size={18} />}
                                    </button>
                                </div>
                                {errors.password && <p className="mt-1 text-xs text-[#EF4444] flex items-center gap-1"><FiAlertTriangle size={12} />{errors.password}</p>}
                            </div>

                            {/* Confirm Password (Signup only) */}
                            {!isLogin && (
                                <div className="md:col-span-2">
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
                                    <div className="relative group">
                                        <FiLock className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors ${errors.confirmPassword ? 'text-[#EF4444]' : 'text-gray-500 group-focus-within:text-[#2563EB]'}`} />
                                        <input
                                            type={showConfirmPassword ? "text" : "password"}
                                            name="confirmPassword"
                                            value={formData.confirmPassword}
                                            onChange={handleInputChange}
                                            required
                                            placeholder="••••••••"
                                            className={`w-full bg-gray-900/50 border rounded-xl py-3 pl-12 pr-12 text-white focus:ring-2 focus:border-transparent outline-none transition-all placeholder:text-gray-600 hover:border-gray-600 ${errors.confirmPassword ? 'border-[#EF4444] focus:ring-[#EF4444]' : 'border-gray-700/50 focus:ring-[#2563EB]'
                                                }`}
                                        />
                                        <button
                                            type="button"
                                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-[#2563EB] transition-colors"
                                        >
                                            {showConfirmPassword ? <FiEyeOff size={18} /> : <FiEye size={18} />}
                                        </button>
                                    </div>
                                    {errors.confirmPassword && <p className="mt-1 text-xs text-[#EF4444] flex items-center gap-1"><FiAlertTriangle size={12} />{errors.confirmPassword}</p>}
                                </div>
                            )}

                            {!isLogin && (
                                <>
                                    {/* Phone */}
                                    <div className="md:col-span-1">
                                        <label className="block text-sm font-medium text-gray-300 mb-2">Phone</label>
                                        <div className="relative group">
                                            <FiPhone className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors ${errors.phone ? 'text-[#EF4444]' : 'text-gray-500 group-focus-within:text-[#2563EB]'}`} />
                                            <input
                                                type="text"
                                                name="phone"
                                                value={formData.phone}
                                                onChange={handleInputChange}
                                                required
                                                placeholder="+1 234 567 890"
                                                className={`w-full bg-gray-900/50 border rounded-xl py-3 pl-12 pr-4 text-white focus:ring-2 focus:border-transparent outline-none transition-all placeholder:text-gray-600 hover:border-gray-600 ${errors.phone ? 'border-[#EF4444] focus:ring-[#EF4444]' : 'border-gray-700/50 focus:ring-[#2563EB]'
                                                    }`}
                                            />
                                        </div>
                                        {errors.phone && <p className="mt-1 text-xs text-[#EF4444] flex items-center gap-1"><FiAlertTriangle size={12} />{errors.phone}</p>}
                                    </div>

                                    {/* Admin Code (Admin only) */}
                                    {role === 'admin' && (
                                        <div className="md:col-span-2">
                                            <label className="block text-sm font-medium text-[#F59E0B] mb-2 flex items-center gap-2">
                                                <FiKey size={16} />
                                                Admin Access Code (Required)
                                            </label>
                                            <div className="relative group">
                                                <FiLock className="absolute left-4 top-1/2 -translate-y-1/2 text-[#F59E0B] group-focus-within:text-[#F59E0B] transition-colors" />
                                                <input
                                                    type="password"
                                                    name="admin_code"
                                                    value={formData.admin_code}
                                                    onChange={handleInputChange}
                                                    required
                                                    placeholder="Enter admin code"
                                                    className="w-full bg-orange-900/20 border border-[#F59E0B]/50 rounded-xl py-3 pl-12 pr-4 text-white focus:ring-2 focus:ring-[#F59E0B] focus:border-transparent outline-none transition-all placeholder:text-orange-900 hover:border-[#F59E0B]/70"
                                                />
                                            </div>
                                            <p className="mt-2 text-xs text-[#F59E0B]/70 flex items-center gap-1">
                                                <FiAlertTriangle size={12} />
                                                Contact system administrator for access code
                                            </p>
                                        </div>
                                    )}

                                    {/* Driver-specific fields */}
                                    {role === 'driver' && (
                                        <>
                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-300 mb-2">License Number</label>
                                                <div className="relative group">
                                                    <FiCreditCard className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-[#2563EB] transition-colors" />
                                                    <input
                                                        type="text"
                                                        name="license_number"
                                                        value={formData.license_number}
                                                        onChange={handleInputChange}
                                                        required
                                                        placeholder="AB-12345"
                                                        className="w-full bg-gray-900/50 border border-gray-700/50 rounded-xl py-3 pl-12 pr-4 text-white focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition-all placeholder:text-gray-600 hover:border-gray-600"
                                                    />
                                                </div>
                                            </div>
                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-300 mb-2">Vehicle Type</label>
                                                <div className="relative group">
                                                    <FiTruck className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-[#2563EB] transition-colors z-10" />
                                                    <select
                                                        name="vehicle_type"
                                                        value={formData.vehicle_type}
                                                        onChange={handleInputChange}
                                                        className="w-full bg-gray-900/50 border border-gray-700/50 rounded-xl py-3 pl-12 pr-4 text-white focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition-all appearance-none hover:border-gray-600"
                                                    >
                                                        <option value="motorcycle">Motorcycle</option>
                                                        <option value="scooter">Scooter</option>
                                                        <option value="bicycle">Bicycle</option>
                                                        <option value="car">Car</option>
                                                    </select>
                                                </div>
                                            </div>
                                        </>
                                    )}

                                    {/* User/Driver Emergency Contacts */}
                                    {(role === 'rider' || role === 'dispatcher') && (
                                        <>
                                            {role === 'rider' && (

                                                <div className="md:col-span-1">
                                                    <label className="block text-sm font-medium text-gray-300 mb-2">Gender</label>
                                                    <div className="relative group">
                                                        <FiUser className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-[#2563EB] transition-colors z-10" />
                                                        <select
                                                            name="gender"
                                                            value={formData.gender}
                                                            onChange={handleInputChange}
                                                            className="w-full bg-gray-900/50 border border-gray-700/50 rounded-xl py-3 pl-12 pr-4 text-white focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition-all appearance-none hover:border-gray-600"
                                                        >
                                                            <option value="female">Female</option>
                                                            <option value="male">Male</option>
                                                            <option value="other">Other</option>
                                                        </select>
                                                    </div>
                                                </div>
                                            )}
                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-300 mb-2">Emergency Contact</label>
                                                <div className="relative group">
                                                    <FiPhone className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-[#2563EB] transition-colors" />
                                                    <input
                                                        type="text"
                                                        name="emergency_contact_phone"
                                                        value={formData.emergency_contact_phone}
                                                        onChange={handleInputChange}
                                                        required
                                                        placeholder="Emergency Phone"
                                                        className="w-full bg-gray-900/50 border border-gray-700/50 rounded-xl py-3 pl-12 pr-4 text-white focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition-all placeholder:text-gray-600 hover:border-gray-600"
                                                    />
                                                </div>
                                            </div>
                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-300 mb-2">Emergency Email</label>
                                                <div className="relative group">
                                                    <FiMail className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-[#2563EB] transition-colors" />
                                                    <input
                                                        type="email"
                                                        name="emergency_contact_email"
                                                        value={formData.emergency_contact_email}
                                                        onChange={handleInputChange}
                                                        required
                                                        placeholder="emergency@example.com"
                                                        className="w-full bg-gray-900/50 border border-gray-700/50 rounded-xl py-3 pl-12 pr-4 text-white focus:ring-2 focus:ring-[#2563EB] focus:border-transparent outline-none transition-all placeholder:text-gray-600 hover:border-gray-600"
                                                    />
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </>
                            )}
                        </div>

                        {/* Remember Me & Forgot Password (Login only) */}
                        {isLogin && (
                            <div className="flex items-center justify-between">
                                <label className="flex items-center gap-2 cursor-pointer group">
                                    <input
                                        type="checkbox"
                                        checked={rememberMe}
                                        onChange={(e) => setRememberMe(e.target.checked)}
                                        className="w-4 h-4 rounded border-gray-700 bg-gray-900/50 text-[#2563EB] focus:ring-2 focus:ring-[#2563EB] cursor-pointer"
                                    />
                                    <span className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors">Remember me</span>
                                </label>
                                <button
                                    type="button"
                                    className="text-sm text-[#2563EB] hover:text-[#3b82f6] transition-colors font-medium"
                                >
                                    Forgot Password?
                                </button>
                            </div>
                        )}

                        {/* Error Message */}
                        {globalError && (
                            <div className={`p-4 rounded-xl text-sm flex items-start gap-3 backdrop-blur-sm ${globalError.includes('successfully')
                                ? 'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30'
                                : 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/30'
                                }`}>
                                {globalError.includes('successfully') ? (
                                    <FiCheckCircle className="mt-0.5 shrink-0" size={20} />
                                ) : (
                                    <FiAlertTriangle className="mt-0.5 shrink-0" size={20} />
                                )}
                                <span>{globalError}</span>
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={loading || Object.keys(errors).length > 0}
                            className="w-full bg-gradient-to-r from-[#2563EB] to-[#1e40af] hover:from-[#1e40af] hover:to-[#1e3a8a] text-white font-semibold py-4 rounded-xl transition-all shadow-lg shadow-[#2563EB]/30 hover:shadow-[#2563EB]/50 flex items-center justify-center gap-3 group disabled:opacity-50 disabled:cursor-not-allowed mt-6 relative overflow-hidden"
                        >
                            <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
                            {loading ? (
                                <div className="w-6 h-6 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                            ) : (
                                <>
                                    <span className="text-lg relative z-10">{isLogin ? 'Sign In' : 'Complete Registration'}</span>
                                    <FiShield className="group-hover:scale-110 transition-transform relative z-10" size={20} />
                                </>
                            )}
                        </button>
                    </form>

                    {/* Toggle Link */}
                    <div className="mt-8 text-center text-sm text-gray-400">
                        {isLogin ? (
                            <p>
                                Don't have an account?{' '}
                                <span
                                    onClick={() => setIsLogin(false)}
                                    className="text-[#2563EB] cursor-pointer hover:text-[#3b82f6] font-semibold hover:underline transition-colors"
                                >
                                    Sign up for free
                                </span>
                            </p>
                        ) : (
                            <p>
                                Already have an account?{' '}
                                <span
                                    onClick={() => setIsLogin(true)}
                                    className="text-[#2563EB] cursor-pointer hover:text-[#3b82f6] font-semibold hover:underline transition-colors"
                                >
                                    Sign in now
                                </span>
                            </p>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <p className="mt-10 text-center text-gray-600 text-xs tracking-widest uppercase">
                    &copy; 2026 Smart Shield Protection
                </p>
            </div>
        </div>
    );
};

export default Auth;
