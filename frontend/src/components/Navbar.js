import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
    const navigate = useNavigate();
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToSection = (id) => {
        const isHome = window.location.pathname === '/';
        if (!isHome) {
            navigate('/');
            setTimeout(() => {
                const el = document.getElementById(id);
                if (el) el.scrollIntoView({ behavior: 'smooth' });
            }, 300);
        } else {
            const el = document.getElementById(id);
            if (el) el.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
            {/* Logo + Brand */}
            <div className="navbar-brand" onClick={() => navigate('/')}>
                <div className="navbar-logo">🧭</div>
                <span className="navbar-title">GypsyCompass</span>
            </div>

            {/* Nav Links */}
            <div className="navbar-nav">
                <button className="nav-link" onClick={() => scrollToSection('about')}>
                    About
                </button>
                <button className="nav-link" onClick={() => scrollToSection('contact')}>
                    Contact
                </button>
                <button
                    id="nav-create-trip-btn"
                    className="nav-btn-primary"
                    onClick={() => navigate('/plan')}
                >
                    ✈️ Create Your Trip
                </button>
            </div>
        </nav>
    );
};

export default Navbar;
