import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    FiUser, FiLock, FiMail, FiCheckCircle, FiShield,
    FiTruck, FiNavigation, FiPhone, FiCreditCard, FiList,
    FiBriefcase, FiShoppingBag
} from 'react-icons/fi';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const Auth = ({ setAuth }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [role, setRole] = useState('rider'); // 'rider' or 'delivery_person'
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        full_name: '',
        phone: '',
        email: '',
        license_number: '',
        vehicle_type: 'motorcycle',
        company_name: '',
        gender: 'female',
        emergency_contact_name: '',
        emergency_contact_phone: '',
        emergency_contact_email: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleInputChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const endpoint = isLogin ? '/auth/login' : '/auth/signup';
            const payload = isLogin
                ? { username: formData.username, password: formData.password }
                : { ...formData, role };

            const response = await axios.post(`${API_URL}${endpoint}`, payload);

            if (isLogin) {
                localStorage.setItem('token', response.data.access_token);
                localStorage.setItem('user', response.data.username);
                localStorage.setItem('user_id', response.data.user_id);
                localStorage.setItem('role', response.data.role);

                // Auto-set rider_id for SOS system
                if (response.data.role === 'rider' || response.data.role === 'delivery_person') {
                    localStorage.setItem('rider_id', response.data.user_id);
                }

                setAuth(true);
                navigate('/dashboard');
            } else {
                setIsLogin(true);
                setError('Account created successfully! Please login.');
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4 py-12">
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0 pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[120px]"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-[120px]"></div>
            </div>

            <div className="max-w-xl w-full z-10">
                <div className="text-center mb-10">
                    <div className="inline-flex items-center justify-center p-3 bg-blue-600 rounded-2xl mb-4 shadow-lg shadow-blue-500/20">
                        <FiShield size={32} className="text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-white tracking-tight">Smart Shield</h1>
                    <p className="text-gray-400 mt-2">AI-Powered Trust Route Security</p>
                </div>

                <div className="bg-gray-800/50 backdrop-blur-xl border border-gray-700/50 p-8 rounded-3xl shadow-2xl">
                    <div className="flex bg-gray-900/50 p-1 rounded-xl mb-8">
                        <button
                            onClick={() => setIsLogin(true)}
                            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${isLogin ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            Sign In
                        </button>
                        <button
                            onClick={() => setIsLogin(false)}
                            className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${!isLogin ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20' : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            Sign Up
                        </button>
                    </div>

                    {!isLogin && (
                        <div className="mb-8">
                            <label className="block text-sm font-medium text-gray-400 mb-4 text-center">I am a...</label>
                            <div className="grid grid-cols-2 gap-3">
                                <button
                                    type="button"
                                    onClick={() => setRole('rider')}
                                    className={`flex flex-col items-center gap-2 p-3 rounded-2xl border-2 transition-all ${role === 'rider'
                                        ? 'border-blue-500 bg-blue-500/10 text-white'
                                        : 'border-gray-700 bg-gray-900/30 text-gray-500 hover:border-gray-600'
                                        }`}
                                >
                                    <FiUser size={20} />
                                    <span className="font-semibold text-xs">Rider</span>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setRole('delivery_person')}
                                    className={`flex flex-col items-center gap-2 p-3 rounded-2xl border-2 transition-all ${role === 'delivery_person'
                                        ? 'border-blue-500 bg-blue-500/10 text-white'
                                        : 'border-gray-700 bg-gray-900/30 text-gray-500 hover:border-gray-600'
                                        }`}
                                >
                                    <FiTruck size={20} />
                                    <span className="font-semibold text-xs">Delivery Partner</span>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setRole('customer')}
                                    className={`flex flex-col items-center gap-2 p-3 rounded-2xl border-2 transition-all ${role === 'customer'
                                        ? 'border-purple-500 bg-purple-500/10 text-white'
                                        : 'border-gray-700 bg-gray-900/30 text-gray-500 hover:border-gray-600'
                                        }`}
                                >
                                    <FiShoppingBag size={20} />
                                    <span className="font-semibold text-xs">Customer</span>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setRole('admin')}
                                    className={`flex flex-col items-center gap-2 p-3 rounded-2xl border-2 transition-all ${role === 'admin'
                                        ? 'border-red-500 bg-red-500/10 text-white'
                                        : 'border-gray-700 bg-gray-900/30 text-gray-500 hover:border-gray-600'
                                        }`}
                                >
                                    <FiBriefcase size={20} />
                                    <span className="font-semibold text-xs">Admin</span>
                                </button>
                            </div>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className={!isLogin ? "md:col-span-1" : "md:col-span-2"}>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Username</label>
                                <div className="relative">
                                    <FiUser className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                    <input
                                        type="text"
                                        name="username"
                                        value={formData.username}
                                        onChange={handleInputChange}
                                        required
                                        placeholder="Username"
                                        className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-600"
                                    />
                                </div>
                            </div>

                            {!isLogin && (
                                <div className="md:col-span-1">
                                    <label className="block text-sm font-medium text-gray-400 mb-2">Full Name</label>
                                    <div className="relative">
                                        <FiList className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                        <input
                                            type="text"
                                            name="full_name"
                                            value={formData.full_name}
                                            onChange={handleInputChange}
                                            required
                                            placeholder="John Doe"
                                            className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-600"
                                        />
                                    </div>
                                </div>
                            )}

                            <div className={!isLogin ? "md:col-span-1" : "md:col-span-2"}>
                                <label className="block text-sm font-medium text-gray-400 mb-2">Password</label>
                                <div className="relative">
                                    <FiLock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                    <input
                                        type="password"
                                        name="password"
                                        value={formData.password}
                                        onChange={handleInputChange}
                                        required
                                        placeholder="••••••••"
                                        className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-600"
                                    />
                                </div>
                            </div>

                            {!isLogin && (
                                <>
                                    <div className="md:col-span-1">
                                        <label className="block text-sm font-medium text-gray-400 mb-2">Phone</label>
                                        <div className="relative">
                                            <FiPhone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                            <input
                                                type="text"
                                                name="phone"
                                                value={formData.phone}
                                                onChange={handleInputChange}
                                                required
                                                placeholder="+1 234 567 890"
                                                className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-600"
                                            />
                                        </div>
                                    </div>
                                    <div className="md:col-span-1">
                                        <label className="block text-sm font-medium text-gray-400 mb-2">Email</label>
                                        <div className="relative">
                                            <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                            <input
                                                type="email"
                                                name="email"
                                                value={formData.email}
                                                onChange={handleInputChange}
                                                required
                                                placeholder="john@example.com"
                                                className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-600"
                                            />
                                        </div>
                                    </div>

                                    {role === 'delivery_person' ? (
                                        <>
                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-400 mb-2">License #</label>
                                                <div className="relative">
                                                    <FiCreditCard className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                                    <input
                                                        type="text"
                                                        name="license_number"
                                                        value={formData.license_number}
                                                        onChange={handleInputChange}
                                                        required
                                                        placeholder="AB-12345"
                                                        className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-600"
                                                    />
                                                </div>
                                            </div>
                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-400 mb-2">Vehicle Type</label>
                                                <div className="relative">
                                                    <FiTruck className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                                    <select
                                                        name="vehicle_type"
                                                        value={formData.vehicle_type}
                                                        onChange={handleInputChange}
                                                        className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all appearance-none"
                                                    >
                                                        <option value="motorcycle">Motorcycle</option>
                                                        <option value="scooter">Scooter</option>
                                                        <option value="bicycle">Bicycle</option>
                                                        <option value="car">Car</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-400 mb-2">Emergency Email (Optional)</label>
                                                <div className="relative">
                                                    <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                                    <input
                                                        type="email"
                                                        name="emergency_contact_email"
                                                        value={formData.emergency_contact_email}
                                                        onChange={handleInputChange}
                                                        placeholder="sos@example.com"
                                                        className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-600"
                                                    />
                                                </div>
                                            </div>
                                        </>
                                    ) : (
                                        <>
                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-400 mb-2">Gender</label>
                                                <div className="relative">
                                                    <FiUser className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                                    <select
                                                        name="gender"
                                                        value={formData.gender}
                                                        onChange={handleInputChange}
                                                        className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all appearance-none"
                                                    >
                                                        <option value="female">Female</option>
                                                        <option value="male">Male</option>
                                                        <option value="other">Other</option>
                                                    </select>
                                                </div>
                                            </div>
                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-400 mb-2">Emergency Contact</label>
                                                <div className="relative">
                                                    <FiPhone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                                    <input
                                                        type="text"
                                                        name="emergency_contact_phone"
                                                        value={formData.emergency_contact_phone}
                                                        onChange={handleInputChange}
                                                        required
                                                        placeholder="Emergency Phone"
                                                        className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-600"
                                                    />
                                                </div>
                                            </div>
                                            <div className="md:col-span-1">
                                                <label className="block text-sm font-medium text-gray-400 mb-2">Emergency Email (Optional)</label>
                                                <div className="relative">
                                                    <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                                                    <input
                                                        type="email"
                                                        name="emergency_contact_email"
                                                        value={formData.emergency_contact_email}
                                                        onChange={handleInputChange}
                                                        placeholder="sos@example.com"
                                                        className="w-full bg-gray-900/50 border border-gray-700 rounded-xl py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-600"
                                                    />
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </>
                            )}
                        </div>

                        {error && (
                            <div className={`p-4 rounded-xl text-sm flex items-start gap-3 ${error.includes('successfully') ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                                }`}>
                                {error.includes('successfully') ? <FiCheckCircle className="mt-0.5 shrink-0" /> : <FiShield className="mt-0.5 shrink-0 rotate-180" />}
                                <span>{error}</span>
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition-all shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2 group disabled:opacity-50 disabled:cursor-not-allowed mt-4"
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                            ) : (
                                <>
                                    {isLogin ? 'Sign In' : 'Complete Registration'}
                                    <FiShield className="group-hover:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </form>

                    <div className="mt-8 text-center text-sm text-gray-500">
                        {isLogin ? (
                            <p>Don't have an account? <span onClick={() => setIsLogin(false)} className="text-blue-400 cursor-pointer hover:underline">Sign up for free</span></p>
                        ) : (
                            <p>Already have an account? <span onClick={() => setIsLogin(true)} className="text-blue-400 cursor-pointer hover:underline">Sign in now</span></p>
                        )}
                    </div>
                </div>

                <p className="mt-10 text-center text-gray-600 text-xs tracking-widest uppercase">
                    &copy; 2025 Smart Shield Protection
                </p>
            </div>
        </div>
    );
};

export default Auth;
