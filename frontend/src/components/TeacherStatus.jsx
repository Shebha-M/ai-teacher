import React from 'react';

/**
 * TeacherStatus Component
 * Displays the AI Educator's presence card, active emotional state,
 * gesture indicators, speech timing fidelity, and accessibility controls.
 */
export default function TeacherStatus({
  teacherName = 'Prof. Sophia',
  title = 'Adaptive Educational AI',
  emotion = 'explaining',
  gesture = 'explain',
  timingMode = 'word_cues',
  speaking = false,
  reducedMotion = false,
  onToggleReducedMotion = () => {},
}) {
  const getEmotionLabel = () => {
    switch (emotion) {
      case 'welcoming':
        return '🌟 Welcoming';
      case 'explaining':
        return '💡 Explaining';
      case 'encouraging':
        return '🤝 Encouraging';
      case 'thoughtful':
        return '🤔 Thoughtful';
      case 'celebrating':
        return '🎉 Celebrating';
      default:
        return '💡 Explaining';
    }
  };

  const getGestureLabel = () => {
    switch (gesture) {
      case 'welcome':
        return '👋 Welcoming';
      case 'point_visual':
      case 'point_right':
        return '👉 Pointing to Visual';
      case 'point_left':
        return '👈 Indicating Content';
      case 'think':
        return '🤔 Posing Question';
      case 'encourage':
        return '🤝 Encouraging Focus';
      case 'celebrate':
        return '🎉 Celebrating Mastery';
      case 'explain':
      default:
        return '💬 Lecturing';
    }
  };

  const getTimingFidelityBadge = () => {
    if (!speaking) return <span className="fidelity-badge idle">⏸️ Idle</span>;
    switch (timingMode) {
      case 'word_cues':
        return <span className="fidelity-badge word-sync" title="Sub-second word boundary synchronization">🟢 Word-Sync (Edge TTS)</span>;
      case 'sentence_cues':
        return <span className="fidelity-badge sentence-sync" title="Sentence timestamp pacing">🟡 Sentence-Sync</span>;
      case 'browser_speech':
        return <span className="fidelity-badge browser-speech" title="In-browser speech synthesis">🔵 Web Speech</span>;
      case 'deterministic':
      default:
        return <span className="fidelity-badge deterministic">⚪ Cadence Sync</span>;
    }
  };

  return (
    <div className="teacher-presence-card" id="teacher-presence-card">
      <div className="teacher-name-tag">{teacherName}</div>
      <div className="teacher-title-tag">{title}</div>

      <div className="status-badges-row">
        {/* Emotion Badge */}
        <div className="emotion-tag" id="badge-teacher-emotion">
          <span>{getEmotionLabel()}</span>
        </div>

        {/* Gesture Badge */}
        <div className="gesture-tag" id="badge-teacher-gesture">
          <span>{getGestureLabel()}</span>
        </div>
      </div>

      {/* Timing Fidelity */}
      <div className="timing-fidelity-container" id="container-timing-fidelity">
        {getTimingFidelityBadge()}
      </div>

      {/* Accessibility Control: Reduced Motion */}
      <div className="accessibility-row" style={{ marginTop: '10px' }}>
        <button
          type="button"
          className={`btn-subtle ${reducedMotion ? 'active' : ''}`}
          onClick={onToggleReducedMotion}
          id="btn-toggle-reduced-motion"
          title="Toggle animation intensity for reduced motion accessibility"
          aria-pressed={reducedMotion}
        >
          {reducedMotion ? '⚡ Motion: Reduced' : '✨ Motion: Normal'}
        </button>
      </div>
    </div>
  );
}
