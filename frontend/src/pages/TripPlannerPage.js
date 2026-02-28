import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRecommendations, getLocationSuggestions } from '../api';

const CURRENCIES = [
    { code: 'INR', symbol: '₹', name: 'Indian Rupee' },
    { code: 'USD', symbol: '$', name: 'US Dollar' },
    { code: 'EUR', symbol: '€', name: 'Euro' },
    { code: 'GBP', symbol: '£', name: 'British Pound' },
    { code: 'AED', symbol: 'د.إ', name: 'UAE Dirham' },
    { code: 'SGD', symbol: 'S$', name: 'Singapore Dollar' },
];

const TRAVEL_MEDIUMS = [
    { id: 'travel_agency', label: 'Travel Agency', icon: '🏢' },
    { id: 'bus', label: 'Bus', icon: '🚌' },
    { id: 'flight', label: 'Flight', icon: '✈️' },
    { id: 'train', label: 'Train', icon: '🚆' },
];

const DESTINATION_STYLES = [
    {
        category: '🌿 Nature & Landscape',
        items: ['Hill Stations', 'Mountains', 'Forests & Wildlife', 'Waterfalls'],
    },
    {
        category: '🌊 Water-Based',
        items: ['Beaches', 'Backwaters & Lakes', 'Islands'],
    },
    {
        category: '🏛️ Culture & Heritage',
        items: ['Heritage Sites', 'Temples & Spiritual', 'Museums & Arts'],
    },
    {
        category: '🏜️ Unique Terrains',
        items: ['Deserts', 'Caves'],
    },
    {
        category: '🎯 Experience Based',
        items: ['Adventure', 'City Life', 'Village/Rural Tourism'],
    },
];

const STEPS = [
    { id: 1, label: 'Name', icon: '👤' },
    { id: 2, label: 'Budget', icon: '💰' },
    { id: 3, label: 'Group', icon: '👥' },
    { id: 4, label: 'Scope', icon: '🌍' },
    { id: 5, label: 'Days', icon: '📅' },
    { id: 6, label: 'Food', icon: '🍽️' },
    { id: 7, label: 'Location', icon: '📍' },
    { id: 8, label: 'Travel', icon: '🚀' },
    { id: 9, label: 'Style', icon: '🎨' },
];

const TripPlannerPage = ({ setRecommendations, setUserPrefs }) => {
    const navigate = useNavigate();
    const [currentStep, setCurrentStep] = useState(1);
    const [formData, setFormData] = useState({
        name: '',
        budget: '',
        currency: 'INR',
        travel_type: '',
        group_size: '',
        travel_scope: '',
        num_days: '',
        food_accommodation: '',
        from_location: '',
        travel_medium: '',
        destination_styles: [],
    });
    const [locationQuery, setLocationQuery] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const suggestionTimeout = useRef(null);
    const locationRef = useRef(null);

    useEffect(() => {
        document.title = 'Plan Your Trip — GypsyCompass';
    }, []);

    // Close suggestions on outside click
    useEffect(() => {
        const handleClick = (e) => {
            if (locationRef.current && !locationRef.current.contains(e.target)) {
                setShowSuggestions(false);
            }
        };
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, []);

    const fetchSuggestions = useCallback(async (q) => {
        if (q.length < 2) { setSuggestions([]); return; }
        try {
            const res = await getLocationSuggestions(q);
            setSuggestions(res.data.suggestions || []);
            setShowSuggestions(true);
        } catch {
            setSuggestions([]);
        }
    }, []);

    const handleLocationChange = (e) => {
        const val = e.target.value;
        setLocationQuery(val);
        setFormData((prev) => ({ ...prev, from_location: val }));
        clearTimeout(suggestionTimeout.current);
        suggestionTimeout.current = setTimeout(() => fetchSuggestions(val), 400);
    };

    const selectSuggestion = (suggestion) => {
        setLocationQuery(suggestion);
        setFormData((prev) => ({ ...prev, from_location: suggestion }));
        setShowSuggestions(false);
    };

    const toggleStyle = (style) => {
        setFormData((prev) => ({
            ...prev,
            destination_styles: prev.destination_styles.includes(style)
                ? prev.destination_styles.filter((s) => s !== style)
                : [...prev.destination_styles, style],
        }));
    };

    const canProceed = () => {
        switch (currentStep) {
            case 1: return formData.name.trim().length >= 2;
            case 2: return formData.budget > 0;
            case 3: return formData.travel_type !== '' && (formData.travel_type === 'solo' || formData.group_size > 0);
            case 4: return formData.travel_scope !== '';
            case 5: return formData.num_days > 0;
            case 6: return formData.food_accommodation !== '';
            case 7: return formData.from_location.trim().length >= 2;
            case 8: return formData.travel_medium !== '';
            case 9: return formData.destination_styles.length > 0;
            default: return true;
        }
    };

    const handleConfirm = async () => {
        setLoading(true);
        setError('');
        try {
            const payload = {
                ...formData,
                budget: parseFloat(formData.budget),
                group_size: formData.travel_type === 'solo' ? 1 : parseInt(formData.group_size),
                num_days: parseInt(formData.num_days),
            };
            setUserPrefs(payload);
            const res = await getRecommendations(payload);
            setRecommendations(res.data);
            navigate('/results');
        } catch (err) {
            setError('Failed to get recommendations. Please ensure the backend server is running.');
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="loading-screen">
                <div className="loading-animation">
                    <div className="loading-orbit">
                        <div className="loading-orbit-ring" />
                        <div className="loading-orbit-ring" />
                        <div className="loading-orbit-center">🧭</div>
                    </div>
                    <h2 className="loading-title">AI Is Analyzing Your Preferences...</h2>
                    <p className="loading-desc">Fetching real-time 2026 travel data just for you</p>
                    <ul className="loading-steps">
                        {[
                            'Understanding your travel preferences...',
                            'Scanning 2026 travel prices & data...',
                            'Matching destinations to your budget...',
                            'Preparing personalized recommendations...',
                        ].map((step, i) => (
                            <li key={i} className={`loading-step ${i < 2 ? 'done' : i === 2 ? 'active' : ''}`}>
                                <span className="loading-step-dot" />
                                {step}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        );
    }

    return (
        <div className="trip-planner-page">
            {/* Hero Banner */}
            <div className="planner-hero">
                <div className="planner-hero-content">
                    <h1>Plan Your Perfect Trip 🗺️</h1>
                    <p>Answer a few questions and let our AI curate your dream destinations</p>
                </div>
            </div>

            {/* Main Content */}
            <div style={{ padding: '0 1rem 80px', background: 'var(--bg-light)' }}>
                {/* Progress Steps */}
                <div className="progress-container">
                    <div className="progress-steps">
                        {STEPS.map((step) => (
                            <div
                                key={step.id}
                                className={`progress-step ${currentStep > step.id ? 'completed' : currentStep === step.id ? 'active' : ''
                                    }`}
                            >
                                <div className="step-circle">
                                    {currentStep > step.id ? '✓' : step.id}
                                </div>
                                <span className="step-label">{step.label}</span>
                            </div>
                        ))}
                    </div>

                    {/* ========== STEP CARDS ========== */}

                    {/* Step 1 — Name */}
                    {currentStep === 1 && (
                        <div className="planner-card">
                            <div className="planner-card-header">
                                <div className="planner-card-icon">👤</div>
                                <div>
                                    <h2>What's Your Name?</h2>
                                    <p>Let us personalise your travel experience</p>
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Your Full Name</label>
                                <input
                                    id="traveler-name-input"
                                    type="text"
                                    className="form-input"
                                    placeholder="Enter your name (e.g. Arjun Kumar)"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    autoFocus
                                />
                            </div>
                            <div className="planner-nav">
                                <div />
                                <button className="btn-next" onClick={() => setCurrentStep(2)} disabled={!canProceed()}>
                                    Continue →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 2 — Budget */}
                    {currentStep === 2 && (
                        <div className="planner-card">
                            <div className="planner-card-header">
                                <div className="planner-card-icon">💰</div>
                                <div>
                                    <h2>What's Your Budget?</h2>
                                    <p>Enter your total travel budget including all expenses</p>
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Total Budget</label>
                                <div className="budget-row">
                                    <input
                                        id="budget-input"
                                        type="number"
                                        className="form-input"
                                        placeholder="Enter amount (e.g. 50000)"
                                        value={formData.budget}
                                        onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                                        min="0"
                                    />
                                    <select
                                        id="currency-select"
                                        className="currency-select"
                                        value={formData.currency}
                                        onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                                    >
                                        {CURRENCIES.map((c) => (
                                            <option key={c.code} value={c.code}>
                                                {c.symbol} {c.code}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                {formData.budget > 0 && (
                                    <p style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: 'var(--primary)', fontFamily: 'Inter, sans-serif' }}>
                                        ✅ Budget set to {CURRENCIES.find((c) => c.code === formData.currency)?.symbol}
                                        {Number(formData.budget).toLocaleString()} {formData.currency}
                                    </p>
                                )}
                            </div>
                            <div className="planner-nav">
                                <button className="btn-back" onClick={() => setCurrentStep(1)}>← Back</button>
                                <button className="btn-next" onClick={() => setCurrentStep(3)} disabled={!canProceed()}>
                                    Continue →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 3 — Solo or Group */}
                    {currentStep === 3 && (
                        <div className="planner-card">
                            <div className="planner-card-header">
                                <div className="planner-card-icon">👥</div>
                                <div>
                                    <h2>Solo or Group Trip?</h2>
                                    <p>This helps us recommend the best options for your group size</p>
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Travel Type</label>
                                <div className="option-cards">
                                    {[
                                        { id: 'solo', label: 'Solo', icon: '🧍', desc: 'Just me, myself & I' },
                                        { id: 'group', label: 'Group', icon: '👨‍👩‍👧‍👦', desc: 'Travelling with others' },
                                    ].map((opt) => (
                                        <div
                                            key={opt.id}
                                            id={`travel-type-${opt.id}`}
                                            className={`option-card ${formData.travel_type === opt.id ? 'selected' : ''}`}
                                            onClick={() => setFormData({ ...formData, travel_type: opt.id, group_size: opt.id === 'solo' ? '1' : '' })}
                                        >
                                            <div className="option-card-icon">{opt.icon}</div>
                                            <div className="option-card-label">{opt.label}</div>
                                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px', fontFamily: 'Inter, sans-serif' }}>{opt.desc}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            {formData.travel_type === 'group' && (
                                <div className="form-group">
                                    <label className="form-label">Number of Members (including you)</label>
                                    <input
                                        id="group-size-input"
                                        type="number"
                                        className="form-input"
                                        placeholder="e.g. 4"
                                        value={formData.group_size}
                                        onChange={(e) => setFormData({ ...formData, group_size: e.target.value })}
                                        min="2"
                                        max="100"
                                        style={{ maxWidth: '200px' }}
                                    />
                                </div>
                            )}
                            <div className="planner-nav">
                                <button className="btn-back" onClick={() => setCurrentStep(2)}>← Back</button>
                                <button className="btn-next" onClick={() => setCurrentStep(4)} disabled={!canProceed()}>
                                    Continue →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 4 — Scope */}
                    {currentStep === 4 && (
                        <div className="planner-card">
                            <div className="planner-card-header">
                                <div className="planner-card-icon">🌍</div>
                                <div>
                                    <h2>Within Country or International?</h2>
                                    <p>Select the scope of your travel adventure</p>
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Travel Scope</label>
                                <div className="option-cards">
                                    {[
                                        { id: 'within_country', label: 'Within Country', icon: '🇮🇳', desc: 'Explore India' },
                                        { id: 'outside_country', label: 'International', icon: '🌐', desc: 'Explore the world' },
                                    ].map((opt) => (
                                        <div
                                            key={opt.id}
                                            id={`scope-${opt.id}`}
                                            className={`option-card ${formData.travel_scope === opt.id ? 'selected' : ''}`}
                                            onClick={() => setFormData({ ...formData, travel_scope: opt.id })}
                                        >
                                            <div className="option-card-icon">{opt.icon}</div>
                                            <div className="option-card-label">{opt.label}</div>
                                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px', fontFamily: 'Inter, sans-serif' }}>{opt.desc}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <div className="planner-nav">
                                <button className="btn-back" onClick={() => setCurrentStep(3)}>← Back</button>
                                <button className="btn-next" onClick={() => setCurrentStep(5)} disabled={!canProceed()}>
                                    Continue →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 5 — Days */}
                    {currentStep === 5 && (
                        <div className="planner-card">
                            <div className="planner-card-header">
                                <div className="planner-card-icon">📅</div>
                                <div>
                                    <h2>How Many Days?</h2>
                                    <p>Enter the number of travel days you have planned</p>
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Number of Days</label>
                                <input
                                    id="num-days-input"
                                    type="number"
                                    className="form-input"
                                    placeholder="e.g. 7"
                                    value={formData.num_days}
                                    onChange={(e) => setFormData({ ...formData, num_days: e.target.value })}
                                    min="1"
                                    max="365"
                                    style={{ maxWidth: '200px' }}
                                />
                                {formData.num_days > 0 && (
                                    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginTop: '1rem' }}>
                                        {[3, 5, 7, 10, 14, 21].map((day) => (
                                            <button
                                                key={day}
                                                className={`style-tag ${formData.num_days === day ? 'selected' : ''}`}
                                                onClick={() => setFormData({ ...formData, num_days: day })}
                                            >
                                                {day} days
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                            <div className="planner-nav">
                                <button className="btn-back" onClick={() => setCurrentStep(4)}>← Back</button>
                                <button className="btn-next" onClick={() => setCurrentStep(6)} disabled={!canProceed()}>
                                    Continue →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 6 — Food & Accommodation */}
                    {currentStep === 6 && (
                        <div className="planner-card">
                            <div className="planner-card-header">
                                <div className="planner-card-icon">🍽️</div>
                                <div>
                                    <h2>Food & Accommodation</h2>
                                    <p>Should we include food & stay in our recommendations?</p>
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Food & Stay Preference</label>
                                <div className="option-cards">
                                    {[
                                        {
                                            id: 'with',
                                            label: 'Included',
                                            icon: '🏨',
                                            desc: 'Include food & hotel in budget calculation',
                                        },
                                        {
                                            id: 'without',
                                            label: 'Arrange by Own',
                                            icon: '🎒',
                                            desc: "I'll arrange my own food & stay",
                                        },
                                    ].map((opt) => (
                                        <div
                                            key={opt.id}
                                            id={`food-${opt.id}`}
                                            className={`option-card ${formData.food_accommodation === opt.id ? 'selected' : ''}`}
                                            onClick={() => setFormData({ ...formData, food_accommodation: opt.id })}
                                        >
                                            <div className="option-card-icon">{opt.icon}</div>
                                            <div className="option-card-label">{opt.label}</div>
                                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px', fontFamily: 'Inter, sans-serif' }}>{opt.desc}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <div className="planner-nav">
                                <button className="btn-back" onClick={() => setCurrentStep(5)}>← Back</button>
                                <button className="btn-next" onClick={() => setCurrentStep(7)} disabled={!canProceed()}>
                                    Continue →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 7 — From Location */}
                    {currentStep === 7 && (
                        <div className="planner-card">
                            <div className="planner-card-header">
                                <div className="planner-card-icon">📍</div>
                                <div>
                                    <h2>Where Will You Depart From?</h2>
                                    <p>Your start location helps us calculate travel time and costs</p>
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Departure Location</label>
                                <div className="location-wrapper" ref={locationRef}>
                                    <input
                                        id="from-location-input"
                                        type="text"
                                        className="form-input"
                                        placeholder="Type your city (e.g. Chennai, Mumbai...)"
                                        value={locationQuery}
                                        onChange={handleLocationChange}
                                        onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                                        autoComplete="off"
                                    />
                                    {showSuggestions && suggestions.length > 0 && (
                                        <div className="location-suggestions">
                                            {suggestions.map((s, i) => (
                                                <div
                                                    key={i}
                                                    className="location-suggestion-item"
                                                    onClick={() => selectSuggestion(s)}
                                                >
                                                    📍 {s}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.5rem', fontFamily: 'Inter, sans-serif' }}>
                                    💡 Start typing to see city suggestions
                                </p>
                            </div>
                            <div className="planner-nav">
                                <button className="btn-back" onClick={() => setCurrentStep(6)}>← Back</button>
                                <button className="btn-next" onClick={() => setCurrentStep(8)} disabled={!canProceed()}>
                                    Continue →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 8 — Travel Medium */}
                    {currentStep === 8 && (
                        <div className="planner-card">
                            <div className="planner-card-header">
                                <div className="planner-card-icon">🚀</div>
                                <div>
                                    <h2>How Will You Travel?</h2>
                                    <p>Select your preferred mode of transport to the destination</p>
                                </div>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Travel Medium</label>
                                <div className="option-cards">
                                    {TRAVEL_MEDIUMS.map((mode) => (
                                        <div
                                            key={mode.id}
                                            id={`travel-medium-${mode.id}`}
                                            className={`option-card ${formData.travel_medium === mode.id ? 'selected' : ''}`}
                                            onClick={() => setFormData({ ...formData, travel_medium: mode.id })}
                                        >
                                            <div className="option-card-icon">{mode.icon}</div>
                                            <div className="option-card-label">{mode.label}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <div className="planner-nav">
                                <button className="btn-back" onClick={() => setCurrentStep(7)}>← Back</button>
                                <button className="btn-next" onClick={() => setCurrentStep(9)} disabled={!canProceed()}>
                                    Continue →
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step 9 — Destination Style */}
                    {currentStep === 9 && (
                        <div className="planner-card">
                            <div className="planner-card-header">
                                <div className="planner-card-icon">🎨</div>
                                <div>
                                    <h2>Your Destination Style</h2>
                                    <p>Select all that excite you — choose multiple!</p>
                                </div>
                            </div>
                            {DESTINATION_STYLES.map((cat, i) => (
                                <div key={i} className="style-category">
                                    <div className="style-category-title">{cat.category}</div>
                                    <div className="style-tags">
                                        {cat.items.map((item) => (
                                            <button
                                                key={item}
                                                id={`style-tag-${item.replace(/\s+/g, '-').toLowerCase()}`}
                                                className={`style-tag ${formData.destination_styles.includes(item) ? 'selected' : ''}`}
                                                onClick={() => toggleStyle(item)}
                                            >
                                                {formData.destination_styles.includes(item) ? '✓ ' : ''}{item}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            ))}
                            {formData.destination_styles.length > 0 && (
                                <div style={{ background: 'var(--primary-pale)', borderRadius: '12px', padding: '1rem', marginBottom: '1.5rem' }}>
                                    <p style={{ fontSize: '0.88rem', color: 'var(--primary)', fontFamily: 'Inter, sans-serif', fontWeight: 600 }}>
                                        ✅ {formData.destination_styles.length} style(s) selected:{' '}
                                        {formData.destination_styles.join(', ')}
                                    </p>
                                </div>
                            )}
                            {error && (
                                <div style={{ background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: '12px', padding: '1rem', marginBottom: '1.5rem', color: '#dc2626', fontSize: '0.9rem', fontFamily: 'Inter, sans-serif' }}>
                                    ⚠️ {error}
                                </div>
                            )}
                            <div className="planner-nav">
                                <button className="btn-back" onClick={() => setCurrentStep(8)}>← Back</button>
                                <button
                                    id="confirm-trip-btn"
                                    className="btn-confirm"
                                    onClick={handleConfirm}
                                    disabled={!canProceed()}
                                >
                                    🎯 Find My Destinations!
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Summary Preview below step 9 */}
                    {currentStep === 9 && (
                        <div
                            style={{
                                maxWidth: '800px',
                                margin: '1.5rem auto 0',
                                background: 'white',
                                borderRadius: '16px',
                                padding: '1.5rem 2rem',
                                border: '1px solid var(--border)',
                                boxShadow: 'var(--shadow-sm)',
                            }}
                        >
                            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '1rem', fontFamily: 'Inter, sans-serif', color: 'var(--text-dark)' }}>
                                📋 Your Trip Summary
                            </h4>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '0.75rem' }}>
                                {[
                                    { label: 'Traveler', value: formData.name },
                                    { label: 'Budget', value: `${formData.currency} ${Number(formData.budget).toLocaleString()}` },
                                    { label: 'Travel', value: formData.travel_type === 'solo' ? 'Solo' : `Group of ${formData.group_size}` },
                                    { label: 'Scope', value: formData.travel_scope === 'within_country' ? 'Within India' : 'International' },
                                    { label: 'Duration', value: `${formData.num_days} days` },
                                    { label: 'Food & Stay', value: formData.food_accommodation === 'with' ? 'Included' : 'Own arrangement' },
                                    { label: 'From', value: formData.from_location },
                                    { label: 'Transport', value: TRAVEL_MEDIUMS.find(m => m.id === formData.travel_medium)?.label || formData.travel_medium },
                                ].map((item, i) => (
                                    <div key={i} style={{ background: 'var(--bg-light)', borderRadius: '10px', padding: '0.6rem 1rem' }}>
                                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', fontFamily: 'Inter, sans-serif' }}>{item.label}</div>
                                        <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-dark)', fontFamily: 'Inter, sans-serif' }}>{item.value || '—'}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TripPlannerPage;
