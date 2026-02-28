import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getDestinationDetails } from '../api';

// Dynamic image mapping
const DESTINATION_IMAGES = {
    default: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1200&q=85',
    'manali': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=1200&q=85',
    'goa': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=1200&q=85',
    'rajasthan': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1200&q=85',
    'jaisalmer': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1200&q=85',
    'kerala': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=1200&q=85',
    'ladakh': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&q=85',
    'andaman': 'https://images.unsplash.com/photo-1604138042739-c0a2e26e1f4f?w=1200&q=85',
    'coorg': 'https://images.unsplash.com/photo-1591017403286-fd8493524e1e?w=1200&q=85',
    'rishikesh': 'https://images.unsplash.com/photo-1590073242678-70ee3fc28f8e?w=1200&q=85',
    'meghalaya': 'https://images.unsplash.com/photo-1519655377407-b66b59b93e45?w=1200&q=85',
    'mountain': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&q=85',
    'beach': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&q=85',
    'desert': 'https://images.unsplash.com/photo-1518684079-3c830dcef090?w=1200&q=85',
    'forest': 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=1200&q=85',
    'island': 'https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?w=1200&q=85',
    'heritage': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=1200&q=85',
};

const getHeroImage = (name) => {
    const key = name.toLowerCase();
    for (const [k, url] of Object.entries(DESTINATION_IMAGES)) {
        if (k !== 'default' && key.includes(k)) return url;
    }
    return DESTINATION_IMAGES.default;
};

const SectionCard = ({ icon, title, children }) => (
    <div className="details-section-card">
        <div className="details-section-title">
            <div className="details-section-title-icon">{icon}</div>
            {title}
        </div>
        {children}
    </div>
);

const DestinationDetailsPage = ({ destination, userPrefs }) => {
    const { name } = useParams();
    const navigate = useNavigate();
    const [details, setDetails] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const destinationName = destination?.name || decodeURIComponent(name);

    useEffect(() => {
        document.title = `${destinationName} — GypsyCompass`;
        const fetchDetails = async () => {
            setLoading(true);
            setError('');
            try {
                const res = await getDestinationDetails(destinationName, userPrefs || {});
                setDetails(res.data.details);
            } catch (err) {
                setError('Failed to load destination details. Please ensure the backend server is running.');
            } finally {
                setLoading(false);
            }
        };
        fetchDetails();
    }, [destinationName]); // eslint-disable-line react-hooks/exhaustive-deps

    const heroImage = getHeroImage(destinationName);

    if (loading) {
        return (
            <div className="loading-screen">
                <div className="loading-animation">
                    <div className="loading-orbit">
                        <div className="loading-orbit-ring" />
                        <div className="loading-orbit-ring" />
                        <div className="loading-orbit-center">🗺️</div>
                    </div>
                    <h2 className="loading-title">Loading {destinationName}...</h2>
                    <p className="loading-desc">Fetching complete travel guide with 2026 data</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="details-page">
                <div style={{ maxWidth: '600px', margin: '120px auto 0', padding: '2rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>⚠️</div>
                    <h2 style={{ marginBottom: '1rem' }}>Oops!</h2>
                    <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', fontFamily: 'Inter, sans-serif' }}>{error}</p>
                    <button className="btn-next" onClick={() => navigate('/results')}>← Back to Results</button>
                </div>
            </div>
        );
    }

    if (!details) return null;

    return (
        <div className="details-page">
            {/* Hero Image */}
            <div className="details-hero">
                <img src={heroImage} alt={destinationName} className="details-hero-img" />
                <div className="details-hero-overlay" />
                <div style={{ position: 'absolute', top: '88px', left: '2rem', zIndex: 2 }}>
                    <button className="back-btn" onClick={() => navigate('/results')} style={{ background: 'rgba(255,255,255,0.9)' }}>
                        ← Back to Results
                    </button>
                </div>
                <div className="details-hero-content" style={{ maxWidth: '1200px', left: '50%', transform: 'translateX(-50%)' }}>
                    <h1>{details.name || destinationName}</h1>
                    <p>📍 {details.full_location}</p>
                </div>
            </div>

            {/* Body */}
            <div className="details-body">
                <div className="container">
                    {/* Quick Info Chips */}
                    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2.5rem' }}>
                        {[
                            { icon: '🛣️', text: details.distance_from_start },
                            { icon: '☀️', text: `Best: ${details.best_season}` },
                            { icon: '🚌', text: details.local_transport },
                        ].map((chip, i) => (
                            <span key={i} className="chip">
                                {chip.icon} {chip.text}
                            </span>
                        ))}
                    </div>

                    <div className="details-grid">
                        {/* Left Column */}
                        <div>
                            {/* Overview */}
                            <SectionCard icon="ℹ️" title="About This Destination">
                                <p style={{ color: 'var(--text-muted)', lineHeight: 1.7, fontFamily: 'Inter, sans-serif', marginBottom: '1.25rem' }}>
                                    {details.overview}
                                </p>
                                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                    {(details.famous_for || []).map((item, i) => (
                                        <span key={i} className="destination-tag">{item}</span>
                                    ))}
                                </div>
                            </SectionCard>

                            {/* Tourist Spots */}
                            {details.tourist_spots && details.tourist_spots.length > 0 && (
                                <SectionCard icon="🏛️" title="Tourist Attractions">
                                    <div className="spots-list">
                                        {details.tourist_spots.map((spot, i) => (
                                            <div key={i} className="spot-item">
                                                <span className="spot-icon">
                                                    {['🏔️', '⛩️', '🌊', '🌿', '🏰', '🎭'][i % 6]}
                                                </span>
                                                <div>
                                                    <div className="spot-name">{spot.name}</div>
                                                    <div className="spot-desc">{spot.description}</div>
                                                    <div className="spot-fee">Entry: {spot.entry_fee}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </SectionCard>
                            )}

                            {/* Food Spots */}
                            {details.food_spots && details.food_spots.length > 0 && (
                                <SectionCard icon="🍽️" title="Best Food Spots">
                                    <div className="food-grid">
                                        {details.food_spots.map((food, i) => (
                                            <div key={i} className="food-item">
                                                <div style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>
                                                    {['🍛', '🥘', '🍜', '🫛', '🍲'][i % 5]}
                                                </div>
                                                <div className="food-name">{food.name}</div>
                                                <div className="food-specialty">{food.specialty}</div>
                                                <div className="food-cost">{food.avg_cost}</div>
                                            </div>
                                        ))}
                                    </div>
                                </SectionCard>
                            )}

                            {/* Travel Options */}
                            {details.travel_options && details.travel_options.length > 0 && (
                                <SectionCard icon="🚀" title="How to Get There">
                                    <div className="travel-options-list">
                                        {details.travel_options.map((opt, i) => (
                                            <div key={i} className="travel-option">
                                                <span className="travel-option-mode">
                                                    {opt.mode === 'Flight' ? '✈️' : opt.mode === 'Train' ? '🚆' : opt.mode === 'Bus' ? '🚌' : '🚗'}{' '}
                                                    {opt.mode}
                                                </span>
                                                <div className="travel-option-info">
                                                    ⏱️ {opt.duration} from {opt.from}
                                                </div>
                                                <div className="travel-option-cost">{opt.cost}</div>
                                            </div>
                                        ))}
                                    </div>
                                </SectionCard>
                            )}

                            {/* Events & Festivals */}
                            {details.events_festivals && details.events_festivals.length > 0 && (
                                <SectionCard icon="🎊" title="Events & Festivals">
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                        {details.events_festivals.map((event, i) => (
                                            <div key={i} style={{ display: 'flex', gap: '1rem', padding: '1rem', background: 'var(--bg-light)', borderRadius: '12px' }}>
                                                <div style={{ fontSize: '1.6rem', flexShrink: 0 }}>🎪</div>
                                                <div>
                                                    <div style={{ fontWeight: 600, fontSize: '0.95rem', fontFamily: 'Inter, sans-serif', color: 'var(--text-dark)', marginBottom: '2px' }}>
                                                        {event.name}
                                                    </div>
                                                    <div style={{ fontSize: '0.8rem', color: 'var(--primary)', fontWeight: 600, fontFamily: 'Inter, sans-serif', marginBottom: '4px' }}>
                                                        📅 {event.month}
                                                    </div>
                                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontFamily: 'Inter, sans-serif' }}>
                                                        {event.description}
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </SectionCard>
                            )}

                            {/* Travel Tips */}
                            {details.travel_tips && details.travel_tips.length > 0 && (
                                <SectionCard icon="💡" title="Travel Tips">
                                    <ul className="tips-list">
                                        {details.travel_tips.map((tip, i) => (
                                            <li key={i} className="tip-item">
                                                <span className="tip-number">{i + 1}</span>
                                                {tip}
                                            </li>
                                        ))}
                                    </ul>
                                </SectionCard>
                            )}

                            {/* Emergency */}
                            {details.emergency_contacts && (
                                <SectionCard icon="🆘" title="Emergency Information">
                                    <div style={{ background: '#fef2f2', border: '1px solid #fca5a5', borderRadius: '10px', padding: '1rem 1.25rem' }}>
                                        <p style={{ fontSize: '0.9rem', color: '#dc2626', fontFamily: 'Inter, sans-serif', display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
                                            <span>📞</span>
                                            <span>{details.emergency_contacts}</span>
                                        </p>
                                    </div>
                                </SectionCard>
                            )}
                        </div>

                        {/* Right Column — Cost Card & Accommodation */}
                        <div>
                            {/* Cost Breakdown */}
                            {details.cost_breakdown && (
                                <div className="cost-card" style={{ marginBottom: '2rem' }}>
                                    <div className="cost-card-title">
                                        💰 Cost Breakdown
                                    </div>
                                    {Object.entries(details.cost_breakdown).map(([key, value]) => {
                                        const isTotal = key === 'grand_total';
                                        return (
                                            <div key={key} className={`cost-row ${isTotal ? 'total' : ''}`}>
                                                <span className="cost-row-label">
                                                    {key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                                                </span>
                                                <span className="cost-row-value">{value}</span>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}

                            {/* Accommodation */}
                            {details.accommodation && details.accommodation.length > 0 && (
                                <div className="details-section-card">
                                    <div className="details-section-title">
                                        <div className="details-section-title-icon">🏨</div>
                                        Accommodation Options
                                    </div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                        {details.accommodation.map((acc, i) => (
                                            <div
                                                key={i}
                                                style={{
                                                    background: 'var(--bg-light)',
                                                    borderRadius: '12px',
                                                    padding: '1rem 1.25rem',
                                                    borderLeft: `3px solid ${['var(--primary)', 'var(--accent)', '#7c3aed'][i % 3]}`,
                                                }}
                                            >
                                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                                                    <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-dark)', fontFamily: 'Inter, sans-serif' }}>
                                                        {acc.type}
                                                    </span>
                                                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--primary)', fontFamily: 'Inter, sans-serif' }}>
                                                        {acc.cost_per_night}/night
                                                    </span>
                                                </div>
                                                <div style={{ fontSize: '0.83rem', color: 'var(--text-muted)', fontFamily: 'Inter, sans-serif' }}>
                                                    {acc.name}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Plan CTA */}
                            <div style={{ background: 'linear-gradient(135deg, var(--primary-pale), #d5f0e4)', borderRadius: '16px', padding: '1.5rem', textAlign: 'center', border: '1px solid rgba(26,107,74,0.15)' }}>
                                <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>✈️</div>
                                <h4 style={{ fontSize: '1rem', fontFamily: 'Inter, sans-serif', color: 'var(--text-dark)', marginBottom: '0.5rem' }}>
                                    Ready to Visit {destinationName}?
                                </h4>
                                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.25rem', fontFamily: 'Inter, sans-serif' }}>
                                    Start planning your perfect trip today
                                </p>
                                <button className="btn-next" onClick={() => navigate('/plan')} style={{ width: '100%', justifyContent: 'center' }}>
                                    Plan Another Trip 🗺️
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DestinationDetailsPage;
