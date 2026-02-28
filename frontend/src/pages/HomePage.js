import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendContactMessage } from '../api';

// High-quality Unsplash landscape images (free, no API key needed)
const LANDSCAPE_IMAGES = [
    {
        url: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80',
        label: 'Mountains',
    },
    {
        url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=80',
        label: 'Beaches',
    },
    {
        url: 'https://images.unsplash.com/photo-1518684079-3c830dcef090?w=400&q=80',
        label: 'Deserts',
    },
    {
        url: 'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?w=400&q=80',
        label: 'Forests',
    },
    {
        url: 'https://images.unsplash.com/photo-1506197603052-3cc9c3a201bd?w=400&q=80',
        label: 'Islands',
    },
];

const HOW_IT_WORKS = [
    {
        icon: '🎯',
        step: 'Step 01',
        title: 'Tell Us Your Preferences',
        desc: 'Share your budget, travel style, group size & destination preferences using our smart filters.',
    },
    {
        icon: '🤖',
        step: 'Step 02',
        title: 'AI Analyzes Instantly',
        desc: 'Our AI scans current 2026 travel data, prices, and tourism trends from across the internet.',
    },
    {
        icon: '🗺️',
        step: 'Step 03',
        title: 'Get Smart Recommendations',
        desc: 'Receive curated destination recommendations with real costs, places to see, and travel tips.',
    },
    {
        icon: '✈️',
        step: 'Step 04',
        title: 'Plan Your Dream Trip',
        desc: 'Explore detailed destination guides and plan your perfect adventure with confidence.',
    },
];

const HomePage = () => {
    const navigate = useNavigate();
    const [contactForm, setContactForm] = useState({ name: '', email: '', message: '' });
    const [contactStatus, setContactStatus] = useState({ loading: false, success: '', error: '' });

    useEffect(() => {
        document.title = 'GypsyCompass — Find Your Perfect Travel Destination';
    }, []);

    const handleContactChange = (field, value) => {
        setContactForm(prev => ({ ...prev, [field]: value }));
        setContactStatus({ loading: false, success: '', error: '' });
    };

    const handleContactSubmit = async () => {
        if (!contactForm.name.trim() || !contactForm.email.trim() || !contactForm.message.trim()) {
            setContactStatus({ loading: false, success: '', error: 'Please fill in all fields.' });
            return;
        }
        setContactStatus({ loading: true, success: '', error: '' });
        try {
            const res = await sendContactMessage(contactForm);
            setContactStatus({ loading: false, success: res.data.message || 'Message sent successfully!', error: '' });
            setContactForm({ name: '', email: '', message: '' });
        } catch (err) {
            const msg = err.response?.data?.error || 'Failed to send message. Please try again.';
            setContactStatus({ loading: false, success: '', error: msg });
        }
    };

    return (
        <div>
            {/* ========== HERO SECTION ========== */}
            <section className="hero-section">
                <div className="hero-bg">
                    <img
                        src="https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=1920&q=85"
                        alt="Beautiful travel destination landscape"
                        className="hero-bg-image"
                    />
                    <div className="hero-overlay" />
                </div>
                <div className="hero-content">
                    <div className="hero-badge">
                        <span className="hero-badge-dot" />
                        AI-Powered Travel Discovery • 2026
                    </div>
                    <h1 className="hero-title">
                        Don't Know{' '}
                        <span>Where To Travel?</span>
                        <br />
                        Yeah, We Got It!
                    </h1>
                    <p className="hero-subtitle">
                        You have the money, we have the map. Tell us your travel style,
                        budget & preferences — our AI will find your perfect destination
                        with real-time prices and travel tips.
                    </p>
                    <div className="hero-cta-group">
                        <button
                            id="hero-find-destination-btn"
                            className="btn-hero-primary"
                            onClick={() => navigate('/plan')}
                        >
                            🗺️ Find Your Perfect Destination
                        </button>
                        <button
                            className="btn-hero-secondary"
                            onClick={() => {
                                document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' });
                            }}
                        >
                            How It Works ↓
                        </button>
                    </div>
                </div>
                <div className="hero-scroll">
                    <div className="scroll-line" />
                    Scroll to explore
                </div>
            </section>

            {/* ========== LANDSCAPE STRIP ========== */}
            <div className="landscape-strip">
                {LANDSCAPE_IMAGES.map((img, i) => (
                    <div key={i} className="landscape-strip-item" data-label={img.label}>
                        <img src={img.url} alt={img.label} loading="lazy" />
                    </div>
                ))}
            </div>

            {/* ========== HOW IT WORKS ========== */}
            <section id="how-it-works" className="section">
                <div className="container">
                    <div style={{ textAlign: 'center', marginBottom: '0' }}>
                        <span className="section-tag">How It Works</span>
                        <h2 className="section-title">Your Journey to the Perfect Trip</h2>
                        <p className="section-desc">
                            From preferences to paradise in minutes — powered by real-time AI analysis
                        </p>
                    </div>
                    <div className="how-it-works-grid">
                        {HOW_IT_WORKS.map((item, i) => (
                            <div key={i} className="how-card">
                                <div className="how-icon">{item.icon}</div>
                                <div className="how-step">{item.step}</div>
                                <div className="how-title">{item.title}</div>
                                <p className="how-desc">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ========== CTA SECTION ========== */}
            <section
                style={{
                    background: 'linear-gradient(135deg, #1a6b4a, #2d9966)',
                    padding: '80px 0',
                    textAlign: 'center',
                }}
            >
                <div className="container">
                    <h2
                        style={{
                            color: 'white',
                            fontSize: 'clamp(1.8rem, 3.5vw, 2.5rem)',
                            marginBottom: '1rem',
                        }}
                    >
                        Ready to Find Your Perfect Destination?
                    </h2>
                    <p
                        style={{
                            color: 'rgba(255,255,255,0.85)',
                            fontSize: '1.05rem',
                            marginBottom: '2rem',
                            fontFamily: 'Inter, sans-serif',
                        }}
                    >
                        Join travellers who discovered their dream trips through GypsyCompass
                    </p>
                    <button
                        id="cta-plan-trip-btn"
                        className="btn-hero-primary"
                        onClick={() => navigate('/plan')}
                        style={{ margin: '0 auto' }}
                    >
                        🚀 Start Planning Now — It's Free!
                    </button>
                </div>
            </section>

            {/* ========== ABOUT SECTION ========== */}
            <section id="about" className="section section-alt">
                <div className="container">
                    <div className="about-grid">
                        <div className="about-image-stack">
                            <img
                                src="https://images.unsplash.com/photo-1488085061387-422e29b40080?w=700&q=80"
                                alt="Travel planning"
                                className="about-img-main"
                            />
                            <img
                                src="https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=300&q=80"
                                alt="Beautiful destination"
                                className="about-img-secondary"
                            />
                            <div className="about-stats">
                                <div className="about-stat-number">500+</div>
                                <div className="about-stat-label">Destinations</div>
                            </div>
                        </div>

                        <div className="about-content">
                            <span className="section-tag">About GypsyCompass</span>
                            <h2 className="section-title" style={{ textAlign: 'left' }}>
                                We Solve the "Where to Go?" Problem
                            </h2>
                            <p style={{ color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: '1.5rem', fontFamily: 'Inter, sans-serif' }}>
                                We understand the struggle — you have time, money, and enthusiasm to travel,
                                but choosing the right destination is overwhelming. That's why we built
                                GypsyCompass, your AI-powered travel compass.
                            </p>
                            <ul className="about-features">
                                <li className="about-feature">
                                    <div className="about-feature-icon">🤖</div>
                                    <div className="about-feature-text">
                                        <h4>Real-Time AI Analysis</h4>
                                        <p>Our AI fetches current 2026 travel prices and tourism data from across the internet</p>
                                    </div>
                                </li>
                                <li className="about-feature">
                                    <div className="about-feature-icon">💰</div>
                                    <div className="about-feature-text">
                                        <h4>Budget-Smart Recommendations</h4>
                                        <p>Get destinations perfectly matched to your budget with transparent cost breakdowns</p>
                                    </div>
                                </li>
                                <li className="about-feature">
                                    <div className="about-feature-icon">🧠</div>
                                    <div className="about-feature-text">
                                        <h4>Personalized to Your Taste</h4>
                                        <p>From hill stations to beaches, deserts to heritage sites — filtered exactly for you</p>
                                    </div>
                                </li>
                                <li className="about-feature">
                                    <div className="about-feature-icon">📍</div>
                                    <div className="about-feature-text">
                                        <h4>Complete Trip Intelligence</h4>
                                        <p>Distance, food spots, tourist attractions, events, and travel agency costs all in one place</p>
                                    </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            {/* ========== DESTINATIONS PREVIEW STRIP ========== */}
            <section className="section" style={{ background: 'var(--bg-light)', paddingTop: '40px', paddingBottom: '60px' }}>
                <div className="container">
                    <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
                        <span className="section-tag">Destinations</span>
                        <h2 className="section-title">Explore Beautiful Destinations</h2>
                    </div>
                    <div
                        style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
                            gap: '1.5rem',
                        }}
                    >
                        {[
                            { name: 'Manali', tag: 'Hill Station', img: 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=400&q=80', color: '#1a6b4a' },
                            { name: 'Goa', tag: 'Beach', img: 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=400&q=80', color: '#0ea5e9' },
                            { name: 'Rajasthan', tag: 'Heritage', img: 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=400&q=80', color: '#d97706' },
                            { name: 'Kerala', tag: 'Backwaters', img: 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=400&q=80', color: '#059669' },
                            { name: 'Ladakh', tag: 'Mountains', img: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&q=80', color: '#7c3aed' },
                            { name: 'Andaman', tag: 'Islands', img: 'https://images.unsplash.com/photo-1559628233-100c798642d4?w=400&q=80', color: '#0891b2' },
                            { name: 'Tamil Nadu', tag: 'Temples', img: 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=400&q=80', color: '#b91c1c' },
                            { name: 'Paris', tag: 'City of Love', img: 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=400&q=80', color: '#e11d48' },
                        ].map((dest, i) => (
                            <div
                                key={i}
                                style={{
                                    borderRadius: '16px',
                                    overflow: 'hidden',
                                    position: 'relative',
                                    height: '200px',
                                    cursor: 'pointer',
                                    boxShadow: 'var(--shadow-md)',
                                }}
                                onClick={() => navigate('/plan')}
                            >
                                <img src={dest.img} alt={dest.name} style={{ width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.5s ease' }}
                                    onMouseOver={(e) => e.target.style.transform = 'scale(1.08)'}
                                    onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
                                />
                                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.75) 0%, transparent 60%)' }} />
                                <div style={{ position: 'absolute', bottom: '16px', left: '16px', right: '16px' }}>
                                    <span style={{ background: dest.color, color: 'white', padding: '3px 10px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: 700, fontFamily: 'Inter, sans-serif' }}>{dest.tag}</span>
                                    <div style={{ color: 'white', fontSize: '1.15rem', fontWeight: 700, marginTop: '4px', fontFamily: 'Playfair Display, serif' }}>{dest.name}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div style={{ textAlign: 'center', marginTop: '2.5rem' }}>
                        <button className="btn-next" onClick={() => navigate('/plan')} style={{ margin: '0 auto' }}>
                            Explore All Destinations ✨
                        </button>
                    </div>
                </div>
            </section>

            {/* ========== CONTACT SECTION ========== */}
            <section id="contact" className="section section-alt">
                <div className="container">
                    <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                        <span className="section-tag">Contact Us</span>
                        <h2 className="section-title">Get In Touch</h2>
                        <p className="section-desc">
                            Contact us for any queries, partnerships, or feedback
                        </p>
                    </div>
                    <div className="contact-grid">
                        <div className="contact-info-cards">
                            <div className="contact-card">
                                <div className="contact-icon">📧</div>
                                <div>
                                    <div className="contact-label">Email</div>
                                    <div className="contact-value">support@gypsycompass.com</div>
                                    <div className="contact-sub">We reply within 24 hours</div>
                                </div>
                            </div>
                            <div className="contact-card">
                                <div className="contact-icon">📱</div>
                                <div>
                                    <div className="contact-label">Phone</div>
                                    <div className="contact-value">+91 00000 00000</div>
                                    <div className="contact-sub">Mon–Sat, 9 AM – 6 PM IST</div>
                                </div>
                            </div>
                            <div className="contact-card">
                                <div className="contact-icon">📍</div>
                                <div>
                                    <div className="contact-label">Address</div>
                                    <div className="contact-value">GypsyCompass Travel Tech</div>
                                    <div className="contact-sub">Chennai, Tamil Nadu – 600001, India</div>
                                </div>
                            </div>
                            <div className="contact-card">
                                <div className="contact-icon">⏰</div>
                                <div>
                                    <div className="contact-label">Support Hours</div>
                                    <div className="contact-value">Monday – Saturday</div>
                                    <div className="contact-sub">9:00 AM to 6:00 PM, IST</div>
                                </div>
                            </div>
                        </div>

                        <div style={{ background: 'var(--bg-lighter)', borderRadius: 'var(--radius-xl)', padding: '2rem', border: '1px solid var(--border)' }}>
                            <h3 style={{ fontSize: '1.3rem', marginBottom: '1.5rem', fontFamily: 'Inter, sans-serif' }}>Send a Message</h3>
                            <div className="form-group">
                                <label className="form-label">Your Name</label>
                                <input
                                    type="text"
                                    placeholder="Enter your name"
                                    className="form-input"
                                    value={contactForm.name}
                                    onChange={(e) => handleContactChange('name', e.target.value)}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Email Address</label>
                                <input
                                    type="email"
                                    placeholder="Enter your email"
                                    className="form-input"
                                    value={contactForm.email}
                                    onChange={(e) => handleContactChange('email', e.target.value)}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Message</label>
                                <textarea
                                    placeholder="How can we help you?"
                                    className="form-input"
                                    rows={4}
                                    style={{ resize: 'vertical' }}
                                    value={contactForm.message}
                                    onChange={(e) => handleContactChange('message', e.target.value)}
                                />
                            </div>
                            {contactStatus.error && (
                                <div style={{ background: '#fef2f2', color: '#dc2626', padding: '10px 14px', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.9rem', fontFamily: 'Inter, sans-serif' }}>
                                    ❌ {contactStatus.error}
                                </div>
                            )}
                            {contactStatus.success && (
                                <div style={{ background: '#f0fdf4', color: '#16a34a', padding: '10px 14px', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.9rem', fontFamily: 'Inter, sans-serif' }}>
                                    ✅ {contactStatus.success}
                                </div>
                            )}
                            <button
                                className="btn-next"
                                style={{ width: '100%', justifyContent: 'center', opacity: contactStatus.loading ? 0.7 : 1 }}
                                onClick={handleContactSubmit}
                                disabled={contactStatus.loading}
                            >
                                {contactStatus.loading ? '⏳ Sending...' : '📤 Send Message'}
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* ========== FOOTER ========== */}
            <footer className="footer">
                <div className="container">
                    <div className="footer-grid">
                        <div>
                            <div className="footer-brand">
                                <div className="footer-logo">🧭</div>
                                <span className="footer-name">GypsyCompass</span>
                            </div>
                            <p className="footer-desc">
                                AI-powered travel destination discovery for explorers who have the money
                                but need the direction. Find your perfect trip today.
                            </p>
                        </div>
                        <div>
                            <div className="footer-heading">Quick Links</div>
                            <ul className="footer-links">
                                {['Home', 'Plan Your Trip', 'About Us', 'Contact'].map((link) => (
                                    <li key={link}>
                                        <span className="footer-link">{link}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div>
                            <div className="footer-heading">Destinations</div>
                            <ul className="footer-links">
                                {['Hill Stations', 'Beaches', 'Heritage Sites', 'Adventure', 'Islands', 'Deserts'].map((dest) => (
                                    <li key={dest}>
                                        <span className="footer-link">{dest}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                    <div className="footer-bottom">
                        <span>© 2026 GypsyCompass. All rights reserved.</span>
                        <span>Made with ❤️ for Explorers</span>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default HomePage;
