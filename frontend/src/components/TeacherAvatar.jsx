import React from 'react';
import { MouthState, EyeState } from './SpeechSyncController';

/**
 * TeacherAvatar Component
 * Professional, vector-rendered AI Educator Presenter.
 * Renders state-synchronized visemes, natural eye-blinks, emotion-driven expressions,
 * and pedagogical gestures pointing directly toward interactive lesson visuals.
 */
export default function TeacherAvatar({
  emotion = 'explaining',
  speaking = false,
  mouthState = MouthState.REST,
  eyeState = EyeState.OPEN,
  gesture = 'explain',
  headMotion = 'neutral',
  reducedMotion = false,
  activeWord = null,
}) {
  // Eyebrow geometry based on emotion
  const renderEyebrows = () => {
    switch (emotion) {
      case 'welcoming':
        return (
          <>
            <path d="M 46 50 Q 55 45 64 49" stroke="#475569" strokeWidth="2.5" fill="none" strokeLinecap="round" />
            <path d="M 76 49 Q 85 45 94 50" stroke="#475569" strokeWidth="2.5" fill="none" strokeLinecap="round" />
          </>
        );
      case 'thoughtful':
        return (
          <>
            <path d="M 46 48 Q 55 52 64 50" stroke="#475569" strokeWidth="2.5" fill="none" strokeLinecap="round" />
            <path d="M 76 47 Q 85 44 94 48" stroke="#475569" strokeWidth="2.5" fill="none" strokeLinecap="round" />
          </>
        );
      case 'encouraging':
        return (
          <>
            <path d="M 46 49 Q 55 44 64 48" stroke="#475569" strokeWidth="2.5" fill="none" strokeLinecap="round" />
            <path d="M 76 48 Q 85 44 94 49" stroke="#475569" strokeWidth="2.5" fill="none" strokeLinecap="round" />
          </>
        );
      case 'celebrating':
        return (
          <>
            <path d="M 46 46 Q 55 41 64 45" stroke="#475569" strokeWidth="2.5" fill="none" strokeLinecap="round" />
            <path d="M 76 45 Q 85 41 94 46" stroke="#475569" strokeWidth="2.5" fill="none" strokeLinecap="round" />
          </>
        );
      case 'explaining':
      default:
        return (
          <>
            <path d="M 46 49 Q 55 47 64 50" stroke="#475569" strokeWidth="2.5" fill="none" strokeLinecap="round" />
            <path d="M 76 50 Q 85 47 94 49" stroke="#475569" strokeWidth="2.5" fill="none" strokeLinecap="round" />
          </>
        );
    }
  };

  // Eyes rendering: open vs blinking
  const renderEyes = () => {
    if (eyeState === EyeState.BLINK) {
      return (
        <>
          <path d="M 49 63 Q 55 68 61 63" stroke="#1e293b" strokeWidth="2.5" fill="none" strokeLinecap="round" />
          <path d="M 79 63 Q 85 68 91 63" stroke="#1e293b" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        </>
      );
    }
    return (
      <>
        {/* Left Eye */}
        <circle cx="55" cy="62" r="4" fill="#0f172a" />
        <circle cx="56.5" cy="60.5" r="1.3" fill="#ffffff" />
        {/* Right Eye */}
        <circle cx="85" cy="62" r="4" fill="#0f172a" />
        <circle cx="86.5" cy="60.5" r="1.3" fill="#ffffff" />
      </>
    );
  };

  // Mouth viseme rendering
  const renderMouth = () => {
    if (!speaking || mouthState === MouthState.REST) {
      if (emotion === 'celebrating') {
        return <path d="M 61 82 Q 70 94 79 82" stroke="#be123c" strokeWidth="2.5" fill="#fecdd3" strokeLinecap="round" />;
      }
      if (emotion === 'encouraging' || emotion === 'welcoming') {
        return <path d="M 63 83 Q 70 90 77 83" stroke="#be123c" strokeWidth="2.2" fill="none" strokeLinecap="round" />;
      }
      if (emotion === 'thoughtful') {
        return <path d="M 64 84 Q 70 82 76 84" stroke="#be123c" strokeWidth="2.2" fill="none" strokeLinecap="round" />;
      }
      return <path d="M 64 83 Q 70 87 76 83" stroke="#be123c" strokeWidth="2" fill="none" strokeLinecap="round" />;
    }

    switch (mouthState) {
      case MouthState.OPEN:
        // Wide vowel articulation (ah, oh)
        return (
          <g>
            <ellipse cx="70" cy="85" rx="8.5" ry="6.5" fill="#9f1239" stroke="#be123c" strokeWidth="1.5" />
            <path d="M 64 82 Q 70 84 76 82" stroke="#ffffff" strokeWidth="2" fill="none" />
          </g>
        );
      case MouthState.HALF_OPEN:
        // Rounded mid articulation (eh, ih)
        return (
          <g>
            <ellipse cx="70" cy="84.5" rx="7" ry="4.5" fill="#be123c" stroke="#9f1239" strokeWidth="1" />
            <line x1="65" y1="83" x2="75" y2="83" stroke="#ffffff" strokeWidth="1.5" strokeLinecap="round" />
          </g>
        );
      case MouthState.NARROW:
        // Narrow consonant articulation (oo, ee, m, p)
        return (
          <ellipse cx="70" cy="84" rx="4.5" ry="3" fill="#be123c" stroke="#9f1239" strokeWidth="1" />
        );
      case MouthState.REST:
      default:
        return <path d="M 64 83 Q 70 87 76 83" stroke="#be123c" strokeWidth="2" fill="none" strokeLinecap="round" />;
    }
  };

  // Body gestures
  const renderGesture = () => {
    switch (gesture) {
      case 'welcome':
        return (
          <g id="gesture-welcome" className="avatar-gesture-layer">
            {/* Right hand waving hello */}
            <path d="M 105 130 Q 120 105 122 88" stroke="#312e81" strokeWidth="7" strokeLinecap="round" fill="none" />
            <circle cx="122" cy="84" r="7" fill="#fed7aa" stroke="#fbbf24" strokeWidth="1.5" />
            <path d="M 119 78 L 123 75 M 123 78 L 126 76" stroke="#fbbf24" strokeWidth="1.5" strokeLinecap="round" />
          </g>
        );
      case 'point_visual':
      case 'point_right':
        return (
          <g id="gesture-point-visual" className="avatar-gesture-layer">
            {/* Arm pointing firmly rightward toward the visual stage */}
            <path d="M 102 130 Q 124 118 132 110" stroke="#312e81" strokeWidth="8" strokeLinecap="round" fill="none" />
            <path d="M 130 110 L 138 106" stroke="#fed7aa" strokeWidth="4.5" strokeLinecap="round" />
            <circle cx="132" cy="110" r="5" fill="#fed7aa" />
          </g>
        );
      case 'point_left':
        return (
          <g id="gesture-point-left" className="avatar-gesture-layer">
            {/* Arm pointing leftward */}
            <path d="M 38 130 Q 16 118 8 110" stroke="#312e81" strokeWidth="8" strokeLinecap="round" fill="none" />
            <path d="M 10 110 L 2 106" stroke="#fed7aa" strokeWidth="4.5" strokeLinecap="round" />
            <circle cx="8" cy="110" r="5" fill="#fed7aa" />
          </g>
        );
      case 'think':
        return (
          <g id="gesture-think" className="avatar-gesture-layer">
            {/* Hand resting thoughtfully under chin */}
            <path d="M 98 135 Q 92 112 80 96" stroke="#312e81" strokeWidth="6" strokeLinecap="round" fill="none" />
            <circle cx="78" cy="94" r="6" fill="#fed7aa" />
          </g>
        );
      case 'encourage':
        return (
          <g id="gesture-encourage" className="avatar-gesture-layer">
            {/* Warm open palms */}
            <path d="M 36 135 Q 24 120 32 112" stroke="#312e81" strokeWidth="6" strokeLinecap="round" fill="none" />
            <circle cx="32" cy="110" r="5.5" fill="#fed7aa" />
            <path d="M 104 135 Q 116 120 108 112" stroke="#312e81" strokeWidth="6" strokeLinecap="round" fill="none" />
            <circle cx="108" cy="110" r="5.5" fill="#fed7aa" />
          </g>
        );
      case 'celebrate':
        return (
          <g id="gesture-celebrate" className="avatar-gesture-layer">
            {/* Both arms raised in joy */}
            <path d="M 34 135 Q 18 105 18 85" stroke="#312e81" strokeWidth="7" strokeLinecap="round" fill="none" />
            <circle cx="18" cy="81" r="6" fill="#fed7aa" stroke="#fbbf24" strokeWidth="1" />
            <path d="M 106 135 Q 122 105 122 85" stroke="#312e81" strokeWidth="7" strokeLinecap="round" fill="none" />
            <circle cx="122" cy="81" r="6" fill="#fed7aa" stroke="#fbbf24" strokeWidth="1" />
          </g>
        );
      case 'explain':
      default:
        return (
          <g id="gesture-explain" className="avatar-gesture-layer">
            {/* Presenter hand gesture */}
            <path d="M 100 135 Q 112 122 116 118" stroke="#312e81" strokeWidth="6" strokeLinecap="round" fill="none" />
            <circle cx="118" cy="116" r="5" fill="#fed7aa" />
          </g>
        );
    }
  };

  // Determine head tilt class
  const getHeadTransform = () => {
    if (reducedMotion) return '';
    if (headMotion === 'tilt_thoughtful') return 'rotate(3deg) translate(2px, -1px)';
    if (headMotion === 'nod' && speaking) return 'translate(0px, 1.5px)';
    return '';
  };

  return (
    <div
      className={`avatar-viewport ${speaking ? 'speaking' : ''} ${reducedMotion ? 'reduced-motion' : ''}`}
      id="avatar-presenter-viewport"
      data-emotion={emotion}
      data-gesture={gesture}
      data-mouth={mouthState}
      data-eye={eyeState}
    >
      <svg
        viewBox="0 0 140 140"
        style={{
          width: '140px',
          height: '140px',
          overflow: 'visible',
          transform: getHeadTransform(),
          transition: reducedMotion ? 'none' : 'transform 0.3s ease',
        }}
        aria-label={`AI Teacher Avatar: ${emotion} emotion, ${gesture} gesture`}
      >
        <defs>
          <linearGradient id="avatarGlowGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#6366f1" stopOpacity="0.45" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.35" />
          </linearGradient>
          <radialGradient id="faceShade" cx="50%" cy="40%" r="50%">
            <stop offset="0%" stopColor="#ffedd5" />
            <stop offset="100%" stopColor="#fed7aa" />
          </radialGradient>
        </defs>

        {/* Ambient Halo */}
        <circle cx="70" cy="70" r="64" fill="url(#avatarGlowGrad)" />

        {/* Torso & Professor Blazer */}
        <path d="M 24 140 Q 70 98 116 140 Z" fill="#1e1b4b" stroke="#6366f1" strokeWidth="2.5" />
        {/* Shirt & Tie */}
        <path d="M 58 116 L 70 138 L 82 116 Z" fill="#312e81" />
        <line x1="70" y1="116" x2="70" y2="138" stroke="#06b6d4" strokeWidth="2.5" />

        {/* Dynamic Arms / Gestures */}
        {renderGesture()}

        {/* Neck */}
        <rect x="63" y="90" width="14" height="20" rx="4" fill="#fed7aa" />

        {/* Head Base */}
        <ellipse cx="70" cy="65" rx="30" ry="34" fill="url(#faceShade)" />

        {/* Professional Hair */}
        <path
          d="M 38 60 Q 40 28 70 24 Q 100 28 102 60 Q 92 36 70 36 Q 48 36 38 60 Z"
          fill="#334155"
        />

        {/* Eyebrows */}
        {renderEyebrows()}

        {/* Designer Glasses Frame */}
        <rect x="45" y="55" width="20" height="14" rx="4" fill="rgba(99, 102, 241, 0.08)" stroke="#6366f1" strokeWidth="2.2" />
        <rect x="75" y="55" width="20" height="14" rx="4" fill="rgba(99, 102, 241, 0.08)" stroke="#6366f1" strokeWidth="2.2" />
        <line x1="65" y1="62" x2="75" y2="62" stroke="#6366f1" strokeWidth="2.2" />

        {/* Eyes (Open or Blinking) */}
        {renderEyes()}

        {/* Nose */}
        <path d="M 70 66 L 68 74 L 72 74" stroke="#f59e0b" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />

        {/* Speaking / Reactive Mouth */}
        {renderMouth()}
      </svg>

      {/* Active Word Viseme Tooltip if available */}
      {speaking && activeWord && !reducedMotion && (
        <div className="active-word-pill" aria-hidden="true">
          "{activeWord}"
        </div>
      )}
    </div>
  );
}
