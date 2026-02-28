import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Map destination names to beautiful Unsplash images (verified working URLs)
const DESTINATION_IMAGES = {
    default: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=600&q=80',
    // Mountains & Hill Stations
    'manali': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=600&q=80',
    'shimla': 'https://images.unsplash.com/photo-1597074866923-dc0589150358?w=600&q=80',
    'ladakh': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80',
    'leh': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80',
    'darjeeling': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=600&q=80',
    'coorg': 'https://images.unsplash.com/photo-1591017403286-fd8493524e1e?w=600&q=80',
    'kodagu': 'https://images.unsplash.com/photo-1591017403286-fd8493524e1e?w=600&q=80',
    'munnar': 'https://images.unsplash.com/photo-1587974928442-77dc3e0dba72?w=600&q=80',
    'ooty': 'https://images.unsplash.com/photo-1582131503261-fca1d1c0589f?w=600&q=80',
    'mussoorie': 'https://images.unsplash.com/photo-1597074866923-dc0589150358?w=600&q=80',
    'meghalaya': 'https://images.unsplash.com/photo-1519655377407-b66b59b93e45?w=600&q=80',
    'cherrapunji': 'https://images.unsplash.com/photo-1519655377407-b66b59b93e45?w=600&q=80',
    'spiti': 'https://images.unsplash.com/photo-1609587312208-cea54be969e7?w=600&q=80',
    'nainital': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
    'kodaikanal': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
    // Beaches & Water
    'goa': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=600&q=80',
    'andaman': 'https://images.unsplash.com/photo-1559628233-100c798642d4?w=600&q=80',
    'lakshadweep': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80',
    'pondicherry': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80',
    'varkala': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80',
    // Deserts & Heritage
    'jaisalmer': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&q=80',
    'rajasthan': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&q=80',
    'jaipur': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&q=80',
    'udaipur': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&q=80',
    'jodhpur': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&q=80',
    'rann': 'https://images.unsplash.com/photo-1518684079-3c830dcef090?w=600&q=80',
    'kutch': 'https://images.unsplash.com/photo-1518684079-3c830dcef090?w=600&q=80',
    // Culture & Heritage
    'varanasi': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=600&q=80',
    'hampi': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=600&q=80',
    'agra': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=600&q=80',
    'taj': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=600&q=80',
    'amritsar': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=600&q=80',
    'golden temple': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=600&q=80',
    'tamil nadu': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=600&q=80',
    'madurai': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=600&q=80',
    'tirupati': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=600&q=80',
    // Backwaters & Nature
    'kerala': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=600&q=80',
    'backwaters': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=600&q=80',
    'alleppey': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=600&q=80',
    'wayanad': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=600&q=80',
    'sundarbans': 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=600&q=80',
    // Wildlife
    'ranthambore': 'https://images.unsplash.com/photo-1549366021-9f761d450615?w=600&q=80',
    'corbett': 'https://images.unsplash.com/photo-1549366021-9f761d450615?w=600&q=80',
    'kaziranga': 'https://images.unsplash.com/photo-1549366021-9f761d450615?w=600&q=80',
    // Adventure
    'rishikesh': 'https://images.unsplash.com/photo-1590073242678-70ee3fc28f8e?w=600&q=80',
    // Cities
    'mumbai': 'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=600&q=80',
    'delhi': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=600&q=80',
    'kolkata': 'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=600&q=80',
    'chennai': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=600&q=80',
    'bangalore': 'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=600&q=80',
    'hyderabad': 'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=600&q=80',
    // International
    'bali': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&q=80',
    'thailand': 'https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=600&q=80',
    'bangkok': 'https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=600&q=80',
    'phuket': 'https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=600&q=80',
    'dubai': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&q=80',
    'maldives': 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=600&q=80',
    'nepal': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=600&q=80',
    'sri lanka': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&q=80',
    'srilanka': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&q=80',
    'singapore': 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=600&q=80',
    'vietnam': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&q=80',
    'paris': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&q=80',
    'france': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&q=80',
    'japan': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600&q=80',
    'tokyo': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600&q=80',
    'london': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=600&q=80',
    'switzerland': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
    'italy': 'https://images.unsplash.com/photo-1534445867742-43195f401b6c?w=600&q=80',
    'rome': 'https://images.unsplash.com/photo-1534445867742-43195f401b6c?w=600&q=80',
    'turkey': 'https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=600&q=80',
    'istanbul': 'https://images.unsplash.com/photo-1541432901042-2d8bd64b4a9b?w=600&q=80',
    'australia': 'https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?w=600&q=80',
    'new zealand': 'https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=600&q=80',
    'egypt': 'https://images.unsplash.com/photo-1539768942893-daf53e736b68?w=600&q=80',
    'greece': 'https://images.unsplash.com/photo-1533105079780-92b9be482077?w=600&q=80',
    'spain': 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=600&q=80',
    'malaysia': 'https://images.unsplash.com/photo-1508444845599-5c89863b1c44?w=600&q=80',
    'cambodia': 'https://images.unsplash.com/photo-1539367628448-4bc5c9d171c8?w=600&q=80',
    // Generic keywords (used as fallback matching)
    'mountain': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
    'hill': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
    'beach': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80',
    'coastal': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&q=80',
    'desert': 'https://images.unsplash.com/photo-1518684079-3c830dcef090?w=600&q=80',
    'forest': 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=600&q=80',
    'island': 'https://images.unsplash.com/photo-1559628233-100c798642d4?w=600&q=80',
    'heritage': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=600&q=80',
    'waterfall': 'https://images.unsplash.com/photo-1519655377407-b66b59b93e45?w=600&q=80',
    'temple': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=600&q=80',
    'city': 'https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=600&q=80',
    'lake': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&q=80',
    'wildlife': 'https://images.unsplash.com/photo-1549366021-9f761d450615?w=600&q=80',
    'safari': 'https://images.unsplash.com/photo-1549366021-9f761d450615?w=600&q=80',
    'adventure': 'https://images.unsplash.com/photo-1590073242678-70ee3fc28f8e?w=600&q=80',
    'backwater': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=600&q=80',
    'snow': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=80',
    'river': 'https://images.unsplash.com/photo-1590073242678-70ee3fc28f8e?w=600&q=80',
    'palace': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&q=80',
    'fort': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&q=80',
};

// Fallback gradient placeholder image (used when Unsplash image fails to load)
const FALLBACK_PLACEHOLDER = 'data:image/svg+xml,' + encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">' +
    '<defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">' +
    '<stop offset="0%" style="stop-color:#1a6b4a"/><stop offset="100%" style="stop-color:#2d9966"/>' +
    '</linearGradient></defs>' +
    '<rect width="600" height="400" fill="url(#g)"/>' +
    '<text x="300" y="190" text-anchor="middle" font-size="48">🌍</text>' +
    '<text x="300" y="240" text-anchor="middle" font-family="sans-serif" font-size="16" fill="rgba(255,255,255,0.8)">Destination</text>' +
    '</svg>'
);

const getDestinationImage = (name, imageKeyword) => {
    const combined = (name + ' ' + (imageKeyword || '')).toLowerCase();

    // 1. Direct name match
    for (const [k, url] of Object.entries(DESTINATION_IMAGES)) {
        if (k !== 'default' && combined.includes(k)) return url;
    }

    // 2. Try individual words from the combined string
    const words = combined.split(/[\s,\-/]+/).filter(w => w.length > 2);
    for (const word of words) {
        for (const [k, url] of Object.entries(DESTINATION_IMAGES)) {
            if (k !== 'default' && (k.includes(word) || word.includes(k))) return url;
        }
    }

    return DESTINATION_IMAGES.default;
};

const DestinationCard = ({ dest, userPrefs, onSelect }) => {
    const imgUrl = getDestinationImage(dest.name, dest.image_keyword);

    return (
        <div
            className="destination-card"
            onClick={() => onSelect(dest)}
        >
            <div className="destination-card-image">
                <img
                    src={imgUrl}
                    alt={dest.name}
                    loading="lazy"
                    onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = FALLBACK_PLACEHOLDER;
                    }}
                />
                <div className={`destination-card-badge ${dest.within_budget ? 'badge-within-budget' : 'badge-over-budget'}`}>
                    {dest.within_budget ? '✅ Within Budget' : '⚠️ Over Budget'}
                </div>
            </div>
            <div className="destination-card-content">
                <div className="destination-card-location">
                    📍 {dest.location}
                </div>
                <div className="destination-card-name">{dest.name}</div>
                <div className="destination-card-tagline">{dest.tagline}</div>
                <div className="destination-tags">
                    {(dest.best_for || []).slice(0, 3).map((tag, i) => (
                        <span key={i} className="destination-tag">{tag}</span>
                    ))}
                </div>
                <div className="destination-card-meta">
                    <span className="meta-item">
                        🛣️ {dest.distance_from_start}
                    </span>
                    <span className="meta-item">
                        ⏱️ {dest.travel_time}
                    </span>
                </div>
                <div className="destination-card-footer">
                    <div className="destination-cost">
                        <div className="cost-label">Estimated Total</div>
                        <div className={`cost-amount ${dest.within_budget ? '' : 'over'}`}>
                            {dest.currency || userPrefs?.currency || 'INR'}{' '}
                            {Number(dest.estimated_total_cost).toLocaleString()}
                        </div>
                    </div>
                    <button className="btn-view-details">
                        View Details →
                    </button>
                </div>
                {dest.over_budget_note && (
                    <div style={{ marginTop: '0.75rem', padding: '0.5rem 0.75rem', background: '#fef3c7', borderRadius: '8px', fontSize: '0.8rem', color: '#92400e', fontFamily: 'Inter, sans-serif' }}>
                        ⚠️ {dest.over_budget_note}
                    </div>
                )}
            </div>
        </div>
    );
};

const ResultsPage = ({ recommendations, userPrefs, setSelectedDestination }) => {
    const navigate = useNavigate();
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        document.title = 'Travel Recommendations — GypsyCompass';
        // If no recommendations, redirect to plan page
        if (!recommendations) {
            navigate('/plan');
        }
    }, [recommendations, navigate]);

    if (!recommendations) return null;

    const allDestinations = recommendations.recommendations || [];
    const withinBudget = allDestinations.filter((d) => d.within_budget);
    const overBudget = allDestinations.filter((d) => !d.within_budget);

    const handleDestinationSelect = (dest) => {
        setSelectedDestination(dest);
        navigate(`/destination/${encodeURIComponent(dest.name)}`);
    };

    return (
        <div className="results-page">
            {/* Header */}
            <div className="results-header">
                <div className="container">
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 16px', background: 'rgba(255,255,255,0.15)', borderRadius: '999px', fontSize: '0.82rem', color: 'rgba(255,255,255,0.9)', marginBottom: '1rem', fontFamily: 'Inter, sans-serif' }}>
                        <span>🎯</span> Personalized for {userPrefs?.name || 'You'}
                    </div>
                    <h1>Your Perfect Destinations Are Here! 🌍</h1>
                    <p>
                        Found {allDestinations.length} destinations based on your preferences •{' '}
                        {withinBudget.length} within your {userPrefs?.currency} {Number(userPrefs?.budget).toLocaleString()} budget
                    </p>

                    {recommendations.ai_summary && (
                        <div className="ai-summary-box" style={{ maxWidth: '900px', margin: '2rem auto 0' }}>
                            <span className="ai-icon">🤖</span>
                            <span>{recommendations.ai_summary}</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Quick Stats */}
            <div style={{ background: 'white', padding: '1.5rem 0', borderBottom: '1px solid var(--border)' }}>
                <div className="container">
                    <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', flexWrap: 'wrap' }}>
                        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontFamily: 'Inter, sans-serif' }}>Filter:</span>
                            {[
                                { id: 'all', label: `All (${allDestinations.length})` },
                                { id: 'within', label: `✅ Within Budget (${withinBudget.length})` },
                                { id: 'over', label: `⚠️ Over Budget (${overBudget.length})` },
                            ].map((f) => (
                                <button
                                    key={f.id}
                                    className={`style-tag ${filter === f.id ? 'selected' : ''}`}
                                    onClick={() => setFilter(f.id)}
                                >
                                    {f.label}
                                </button>
                            ))}
                        </div>
                        <button className="back-btn" onClick={() => navigate('/plan')} style={{ marginBottom: 0 }}>
                            ← Modify Preferences
                        </button>
                    </div>
                </div>
            </div>

            {/* Results Body */}
            <div className="results-section">
                <div className="container">
                    {/* Within Budget */}
                    {(filter === 'all' || filter === 'within') && withinBudget.length > 0 && (
                        <div style={{ marginBottom: '4rem' }}>
                            <h2 className="results-section-title">
                                ✅ Within Your Budget
                            </h2>
                            <p className="results-section-desc">
                                These destinations fit perfectly within your {userPrefs?.currency} {Number(userPrefs?.budget).toLocaleString()} budget
                            </p>
                            <div className="destinations-grid">
                                {withinBudget.map((dest, i) => (
                                    <DestinationCard
                                        key={i}
                                        dest={dest}
                                        userPrefs={userPrefs}
                                        onSelect={handleDestinationSelect}
                                    />
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Over Budget */}
                    {(filter === 'all' || filter === 'over') && overBudget.length > 0 && (
                        <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                                <h2 className="results-section-title over-budget-section-title">
                                    ⚠️ Beyond Budget — Worth It!
                                </h2>
                            </div>
                            <p className="results-section-desc" style={{ marginBottom: '2.5rem' }}>
                                These destinations are slightly over your budget but offer incredible experiences
                            </p>
                            <div className="destinations-grid">
                                {overBudget.map((dest, i) => (
                                    <DestinationCard
                                        key={i}
                                        dest={dest}
                                        userPrefs={userPrefs}
                                        onSelect={handleDestinationSelect}
                                    />
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Empty state */}
                    {allDestinations.length === 0 && (
                        <div className="no-results">
                            <div className="no-results-icon">🔍</div>
                            <h3>No destinations found</h3>
                            <p>Try adjusting your preferences for better results</p>
                            <button className="btn-next" onClick={() => navigate('/plan')} style={{ margin: '1.5rem auto 0', display: 'block' }}>
                                ← Go Back & Modify
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Landscape footer strip */}
            <div className="landscape-strip">
                {[
                    { url: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80', label: 'Mountains' },
                    { url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=80', label: 'Beaches' },
                    { url: 'https://images.unsplash.com/photo-1518684079-3c830dcef090?w=400&q=80', label: 'Deserts' },
                    { url: 'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=400&q=80', label: 'Forests' },
                    { url: 'https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?w=400&q=80', label: 'Islands' },
                ].map((img, i) => (
                    <div key={i} className="landscape-strip-item" data-label={img.label}>
                        <img src={img.url} alt={img.label} loading="lazy" />
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ResultsPage;
