import React, { useState, useRef, useEffect } from 'react';
import { GlobeIcon, ChevronDownIcon, CheckIcon } from './Icons';

export const LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English (US)', tag: 'en-US' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', tag: 'ta-IN' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', tag: 'hi-IN' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', tag: 'te-IN' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', tag: 'ml-IN' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', tag: 'kn-IN' },
];

export default function LanguageSwitcher({
  currentLanguage = 'en',
  onLanguageChange,
  languageMode = 'bilingual',
  onModeChange,
  isLoading = false,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const activeLang = LANGUAGES.find((l) => l.code === currentLanguage) || LANGUAGES[0];

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectLang = (code) => {
    setIsOpen(false);
    if (onLanguageChange && code !== currentLanguage) {
      onLanguageChange(code);
    }
  };

  return (
    <div className="language-switcher-container" ref={dropdownRef}>
      {/* Hidden standard select for E2E automated testing compatibility */}
      <select
        id="top-language-select"
        className="form-select sr-only-hidden"
        value={currentLanguage}
        onChange={(e) => handleSelectLang(e.target.value)}
        aria-hidden="true"
        tabIndex={-1}
        style={{ position: 'absolute', opacity: 0, pointerEvents: 'none', width: 0, height: 0 }}
      >
        {LANGUAGES.map((l) => (
          <option key={l.code} value={l.code}>
            {l.name} ({l.nativeName})
          </option>
        ))}
      </select>

      {/* Modern Floating Trigger Button */}
      <button
        type="button"
        className={`lang-trigger-btn ${isOpen ? 'open' : ''} ${isLoading ? 'loading' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title="Switch Session Presentation Language & Speech Voice"
        aria-expanded={isOpen}
      >
        <span className="lang-icon">
          <GlobeIcon />
        </span>
        <span className="lang-label">{activeLang.name}</span>
        <span className="lang-native-tag">{activeLang.nativeName}</span>
        {isLoading ? (
          <span className="lang-spinner"></span>
        ) : (
          <span className="lang-chevron">
            <ChevronDownIcon />
          </span>
        )}
      </button>

      {/* Glassmorphic Dropdown Panel */}
      {isOpen && (
        <div className="lang-dropdown-panel animate-scale-in">
          <div className="lang-dropdown-header">
            <span>Select Teaching Language</span>
            <span className="lang-badge-count">{LANGUAGES.length} Languages</span>
          </div>

          <div className="lang-options-list">
            {LANGUAGES.map((lang) => {
              const isSelected = lang.code === currentLanguage;
              return (
                <button
                  key={lang.code}
                  type="button"
                  className={`lang-option-item ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleSelectLang(lang.code)}
                >
                  <div className="lang-option-info">
                    <span className="lang-option-name">{lang.name}</span>
                    <span className="lang-option-native">{lang.nativeName}</span>
                  </div>
                  {isSelected && (
                    <span className="lang-check-icon">
                      <CheckIcon />
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Mode Selector Option inside Dropdown */}
          {onModeChange && (
            <div className="lang-mode-section">
              <div className="lang-mode-title">STEM Presentation Mode:</div>
              <div className="lang-mode-pills">
                <button
                  type="button"
                  className={`lang-mode-pill ${languageMode === 'bilingual' ? 'active' : ''}`}
                  onClick={() => onModeChange('bilingual')}
                  title="Native narrative with global English technical terms"
                >
                  Bilingual
                </button>
                <button
                  type="button"
                  className={`lang-mode-pill ${languageMode === 'full' ? 'active' : ''}`}
                  onClick={() => onModeChange('full')}
                  title="Full native language immersion"
                >
                  Full Native
                </button>
                <button
                  type="button"
                  className={`lang-mode-pill ${languageMode === 'mixed' ? 'active' : ''}`}
                  onClick={() => onModeChange('mixed')}
                  title="Conversational code switching"
                >
                  Mixed
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
