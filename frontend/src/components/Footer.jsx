/**
 * Footer Component - NyayaSahay Design with Lucide Icons
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Scale, Mail, Phone, MapPin, Shield } from 'lucide-react';
import '../styles/footer.css';

function Footer() {
    return (
        <footer className="footer">
            <div className="footer-container">
                <div className="footer-grid">
                    {/* Brand */}
                    <div className="footer-brand">
                        <div className="footer-logo">
                            <span className="footer-logo-icon">
                                <Scale size={20} />
                            </span>
                            <span className="footer-logo-text">NyayaSahay</span>
                        </div>
                        <p className="footer-tagline">
                            Empowering Indian citizens with AI-powered legal awareness.
                            Know your rights, protect your future.
                        </p>
                        <div className="footer-secure">
                            <Shield size={16} /> 100% Secure & Confidential
                        </div>
                    </div>

                    {/* Quick Links */}
                    <div className="footer-links">
                        <h4>Quick Links</h4>
                        <ul>
                            <li><Link to="/how-it-works">How It Works</Link></li>
                            <li><Link to="/your-rights">Know Your Rights</Link></li>
                            <li><Link to="/resources">IPC Sections</Link></li>
                            <li><Link to="/resources">CrPC Guide</Link></li>
                            <li><Link to="/faq">FAQs</Link></li>
                        </ul>
                    </div>

                    {/* Resources */}
                    <div className="footer-links">
                        <h4>Resources</h4>
                        <ul>
                            <li><Link to="/resources">Legal Dictionary</Link></li>
                            <li><Link to="/resources">Case Studies</Link></li>
                            <li><Link to="/resources">Rights During Arrest</Link></li>
                            <li><Link to="/resources">Bail Information</Link></li>
                            <li><Link to="/resources">Free Legal Aid</Link></li>
                        </ul>
                    </div>

                    {/* Contact */}
                    <div className="footer-links">
                        <h4>Contact</h4>
                        <ul className="footer-contact">
                            <li>
                                <Mail size={16} />
                                <a href="mailto:help@nyayasahay.in">help@nyayasahay.in</a>
                            </li>
                            <li>
                                <Phone size={16} />
                                <span>1800 XXX XXXX (Toll Free)</span>
                            </li>
                            <li>
                                <MapPin size={16} />
                                <span>New Delhi, India</span>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Disclaimer */}
                <div className="footer-disclaimer">
                    <p>
                        <strong>Disclaimer:</strong> NyayaSahay provides legal information for educational
                        purposes only and does not constitute legal advice. For specific legal matters,
                        please consult a qualified legal professional. The information provided is based
                        on Indian law and may not be applicable in all situations.
                    </p>
                </div>

                {/* Bottom Bar */}
                <div className="footer-bottom">
                    <p>© 2026 NyayaSahay. All rights reserved.</p>
                    <div className="footer-bottom-links">
                        <Link to="/privacy">Privacy Policy</Link>
                        <Link to="/terms">Terms of Service</Link>
                        <Link to="/accessibility">Accessibility</Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}

export default Footer;
