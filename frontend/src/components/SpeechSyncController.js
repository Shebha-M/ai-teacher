/**
 * SpeechSyncController: Browser-side timing calculator for the AI Teacher Avatar.
 * Computes instantaneous mouth visemes, eye blinking, and active word metadata
 * from audio playback clocks and subtitle/word cues.
 */

export const MouthState = {
  REST: 'rest',
  OPEN: 'open',
  HALF_OPEN: 'half_open',
  NARROW: 'narrow',
};

export const EyeState = {
  OPEN: 'open',
  BLINK: 'blink',
};

export const TimingMode = {
  WORD_CUES: 'word_cues',
  SENTENCE_CUES: 'sentence_cues',
  BROWSER_SPEECH: 'browser_speech',
  DETERMINISTIC: 'deterministic',
};

/**
 * Calculates current mouth viseme state from audio playback time.
 */
export function calculateMouthState(playbackTime, isPlaying, wordCues = [], subtitles = [], totalDuration = 0) {
  if (!isPlaying || playbackTime < 0) {
    return {
      mouthState: MouthState.REST,
      activeWord: null,
      speakingProgress: 0,
      timingMode: TimingMode.DETERMINISTIC,
    };
  }

  if (totalDuration > 0 && playbackTime >= totalDuration) {
    return {
      mouthState: MouthState.REST,
      activeWord: null,
      speakingProgress: 1.0,
      timingMode: TimingMode.DETERMINISTIC,
    };
  }

  // 1. High precision: Word Cues
  if (wordCues && wordCues.length > 0) {
    for (let i = 0; i < wordCues.length; i++) {
      const cue = wordCues[i];
      if (playbackTime >= cue.start && playbackTime <= cue.end) {
        const duration = Math.max(0.01, cue.end - cue.start);
        const progress = (playbackTime - cue.start) / duration;

        let mouth = MouthState.REST;
        if (progress < 0.25) {
          mouth = MouthState.OPEN;
        } else if (progress < 0.65) {
          mouth = MouthState.HALF_OPEN;
        } else if (progress < 0.90) {
          mouth = MouthState.NARROW;
        } else {
          mouth = MouthState.REST;
        }

        return {
          mouthState: mouth,
          activeWord: cue.text,
          speakingProgress: Math.min(1.0, Math.max(0.0, progress)),
          timingMode: TimingMode.WORD_CUES,
        };
      }
    }

    // Inter-word pause
    return {
      mouthState: MouthState.REST,
      activeWord: null,
      speakingProgress: 0,
      timingMode: TimingMode.WORD_CUES,
    };
  }

  // 2. Medium precision: Sentence Cues
  if (subtitles && subtitles.length > 0) {
    for (let i = 0; i < subtitles.length; i++) {
      const sub = subtitles[i];
      if (playbackTime >= sub.start_time && playbackTime <= sub.end_time) {
        const cycle = (playbackTime - sub.start_time) % 0.28;
        let mouth = MouthState.REST;
        if (cycle < 0.08) {
          mouth = MouthState.OPEN;
        } else if (cycle < 0.18) {
          mouth = MouthState.HALF_OPEN;
        } else if (cycle < 0.24) {
          mouth = MouthState.NARROW;
        } else {
          mouth = MouthState.REST;
        }

        const duration = Math.max(0.01, sub.end_time - sub.start_time);
        const progress = (playbackTime - sub.start_time) / duration;

        return {
          mouthState: mouth,
          activeWord: null,
          speakingProgress: Math.min(1.0, Math.max(0.0, progress)),
          timingMode: TimingMode.SENTENCE_CUES,
        };
      }
    }
  }

  // 3. Fallback: Deterministic syllabic oscillation
  const cycle = playbackTime % 0.32;
  let mouth = MouthState.REST;
  if (cycle < 0.10) {
    mouth = MouthState.OPEN;
  } else if (cycle < 0.22) {
    mouth = MouthState.HALF_OPEN;
  } else if (cycle < 0.28) {
    mouth = MouthState.NARROW;
  } else {
    mouth = MouthState.REST;
  }

  return {
    mouthState: mouth,
    activeWord: null,
    speakingProgress: cycle / 0.32,
    timingMode: TimingMode.DETERMINISTIC,
  };
}

/**
 * Natural non-periodic eye blinking: blinks for 150ms every 3.5 seconds.
 */
export function calculateEyeState(playbackTime, reducedMotion = false) {
  if (reducedMotion) return EyeState.OPEN;
  const cycle = playbackTime % 3.5;
  if (cycle >= 3.35) {
    return EyeState.BLINK;
  }
  return EyeState.OPEN;
}
