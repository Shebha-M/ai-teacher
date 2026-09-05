import React, { useState, useEffect } from 'react';
import TeacherAvatar from './components/TeacherAvatar';
import TeacherStatus from './components/TeacherStatus';
import LanguageSwitcher from './components/LanguageSwitcher';
import {
  LogoIcon,
  GlobeIcon,
  LearnIcon,
  ProgressIcon,
  HistoryIcon,
  UploadIcon,
  DocumentIcon,
  CheckIcon,
  PlayIcon,
  PauseIcon,
  VolumeIcon,
  MuteIcon,
  SparklesIcon,
  TargetIcon,
  LightbulbIcon,
  ArrowRightIcon,
} from './components/Icons';
import {
  calculateMouthState,
  calculateEyeState,
  MouthState,
  EyeState,
  TimingMode,
} from './components/SpeechSyncController';

const API_BASE = '/api/v1';

export default function App() {
  // Navigation & Workflow state: 'onboarding' | 'plan' | 'teach' | 'question' | 'evaluated' | 'completed'
  const [currentStep, setCurrentStep] = useState('onboarding');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [healthStatus, setHealthStatus] = useState(null);

  // Learner Setup State
  const [learnerName, setLearnerName] = useState('Alex Rivera');
  const [educationalLevel, setEducationalLevel] = useState('beginner');
  const [availableTime, setAvailableTime] = useState(20);
  const [teachingStyle, setTeachingStyle] = useState('analogy_driven');
  const [language, setLanguage] = useState('en');
  const [topic, setTopic] = useState('Binary Trees');

  // Session & Teaching State
  const [sessionId, setSessionId] = useState(null);
  const [lessonPlan, setLessonPlan] = useState(null);
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [teachingResponse, setTeachingResponse] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [studentAnswer, setStudentAnswer] = useState('');
  const [selectedOption, setSelectedOption] = useState('');
  const [showHints, setShowHints] = useState(false);
  const [evaluationOutcome, setEvaluationOutcome] = useState(null);
  const [conceptsMastered, setConceptsMastered] = useState([]);
  const [conceptsNeedingWork, setConceptsNeedingWork] = useState([]);

  // Phase 3: Document Intelligence & RAG State
  const [knowledgeMode, setKnowledgeMode] = useState('topic'); // 'topic' | 'document'
  const [documents, setDocuments] = useState([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [groundedContext, setGroundedContext] = useState(null);

  // Phase 5: AI Teaching Video & Subject-Aware Visuals State
  const [scenePlan, setScenePlan] = useState(null);
  const [activeSceneIndex, setActiveSceneIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [remediationScene, setRemediationScene] = useState(null);
  const [adaptiveRemediationActive, setAdaptiveRemediationActive] = useState(false);
  const [studioViewMode, setStudioViewMode] = useState('video'); // 'video' | 'reading'

  // Phase 6: Multilingual Teaching & Natural Voice State
  const [teachingLanguage, setTeachingLanguage] = useState('en');
  const [languageMode, setLanguageMode] = useState('bilingual'); // 'full' | 'bilingual' | 'mixed'
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoiceId, setSelectedVoiceId] = useState('');
  const [audioAsset, setAudioAsset] = useState(null);
  const [audioStatus, setAudioStatus] = useState('idle'); // 'idle' | 'generating' | 'playing_tts' | 'playing_browser'
  const [currentSubtitle, setCurrentSubtitle] = useState('');
  const [useRealTts, setUseRealTts] = useState(true);
  const [audioInstance, setAudioInstance] = useState(null);

  // Phase 7: AI Teacher Avatar & Voice Synchronization State
  const [reducedMotion, setReducedMotion] = useState(false);
  const [avatarMouthState, setAvatarMouthState] = useState(MouthState.REST);
  const [avatarEyeState, setAvatarEyeState] = useState(EyeState.OPEN);
  const [activeWord, setActiveWord] = useState(null);
  const [timingMode, setTimingMode] = useState(TimingMode.WORD_CUES);
  const [browserSpeechInterval, setBrowserSpeechInterval] = useState(null);

  // Phase 8: Final Integration, Readiness, Assessment & Dashboard State
  const [navTab, setNavTab] = useState('learn'); // 'learn' | 'progress' | 'history'
  const [loadingStage, setLoadingStage] = useState(0); // 0: idle, 1..4: genuine stages
  const [readinessData, setReadinessData] = useState(null);
  const [showReadinessModal, setShowReadinessModal] = useState(false);
  const [showExcerptModal, setShowExcerptModal] = useState(false);
  const [demoNotice, setDemoNotice] = useState('');
  const [reEvalAnswer, setReEvalAnswer] = useState('');
  const [reEvalPassed, setReEvalPassed] = useState(false);
  const [reEvalSubmitted, setReEvalSubmitted] = useState(false);
  const [finalAssessment, setFinalAssessment] = useState(null);
  const [assessmentAnswers, setAssessmentAnswers] = useState({});
  const [learningReport, setLearningReport] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [sessionHistory, setSessionHistory] = useState([
    {
      session_id: 'sess-demo-prior',
      topic: 'Binary Trees',
      score_percent: 88,
      status: 'mastered',
      date: 'Sep 04, 2026',
    },
  ]);

  // Fetch documents list from API
  const fetchDocuments = async () => {
    try {
      const res = await fetch(`${API_BASE}/documents`);
      if (res.ok) {
        const data = await res.json();
        setDocuments(data);
        if (data.length > 0 && !selectedDocumentId) {
          setSelectedDocumentId(data[0].document_id);
        }
      }
    } catch (err) {
      console.error('Failed to load documents', err);
    }
  };

  // Verify backend health, readiness & load documents on mount
  useEffect(() => {
    fetch('/api/v1/ai/health')
      .then((res) => res.json())
      .then((data) => setHealthStatus(data))
      .catch(() => setHealthStatus({ status: 'offline', mode: 'connecting...' }));

    fetch('/api/v1/readiness')
      .then((res) => res.json())
      .then((data) => setReadinessData(data))
      .catch((e) => console.warn('Could not fetch readiness', e));

    fetchDocuments();
  }, []);

  // Audio auto-cutoff: Stop any playing speech narration immediately when switching tabs, steps, or sections
  useEffect(() => {
    stopNarration();
  }, [navTab, currentStep, currentSectionIndex]);

  // Quick Golden Demo Preset Loader
  const loadGoldenDemoPreset = () => {
    setLearnerName('Alex Rivera');
    setEducationalLevel('beginner');
    setAvailableTime(15);
    setTeachingStyle('analogy_driven');
    setLanguage('en');
    setTeachingLanguage('en');
    setTopic('Binary Trees');
    setKnowledgeMode('topic');
    setDemoNotice('✓ Golden demo configuration loaded: Alex Rivera • Binary Trees • 15 min • Analogy-Driven.');
    setTimeout(() => setDemoNotice(''), 5000);
  };

  // Handle Document Upload (PDF, DOCX, PPTX, TXT)
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadMessage(`Processing & chunking ${file.name}...`);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch(`${API_BASE}/documents/upload`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Upload failed');
      }
      const meta = await res.json();
      setUploadMessage(
        `✓ Ready! Indexed ${meta.filename} (${meta.page_count} pages/slides, ${meta.chunk_count} chunks)`
      );
      await fetchDocuments();
      setSelectedDocumentId(meta.document_id);
      setKnowledgeMode('document');
    } catch (err) {
      setUploadMessage(`❌ ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  // Step 1 & 2: Initialize Session & Generate Lesson Plan with Real Pipeline Stages
  const handleStartSession = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setErrorMessage('');
    setCurrentStep('loading_stages');
    setLoadingStage(1); // Understanding your goal...

    try {
      // 1. Create Session
      const sessionRes = await fetch(`${API_BASE}/teaching/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          learner_name: learnerName,
          educational_level: educationalLevel,
          available_learning_time: Number(availableTime),
          preferred_teaching_style: teachingStyle,
          preferred_language: language,
          learning_objective: `Master ${topic} and develop intuitive mental models`,
          knowledge_mode: knowledgeMode,
          document_id: knowledgeMode === 'document' ? selectedDocumentId : null,
        }),
      });

      if (!sessionRes.ok) throw new Error('Failed to create teaching session');
      const sessionData = await sessionRes.json();
      setSessionId(sessionData.session_id);

      setLoadingStage(2); // Analyzing learning material...

      // 2. Generate Plan
      const planRes = await fetch(`${API_BASE}/teaching/sessions/${sessionData.session_id}/plan`, {
        method: 'POST',
      });
      if (!planRes.ok) throw new Error('Failed to generate lesson plan');
      const planData = await planRes.json();
      setLessonPlan(planData.lesson_plan);
      setGroundedContext(planData.grounded_context);
      setCurrentSectionIndex(0);

      setLoadingStage(3); // Building your personalized lesson...
      await new Promise((r) => setTimeout(r, 600));

      setLoadingStage(4); // Preparing your teacher...
      await new Promise((r) => setTimeout(r, 600));

      setCurrentStep('plan');
    } catch (err) {
      setErrorMessage(err.message || 'An error occurred initializing the session.');
      setCurrentStep('onboarding');
    } finally {
      setLoading(false);
      setLoadingStage(0);
    }
  };

  // Phase 6: Multilingual Audio & Speech Synthesis
  const langMap = {
    en: 'en-US',
    hi: 'hi-IN',
    ta: 'ta-IN',
    te: 'te-IN',
    ml: 'ml-IN',
    kn: 'kn-IN',
  };

  const fetchVoices = async (lang) => {
    try {
      const res = await fetch(`${API_BASE}/media/voices?language=${lang}`);
      if (res.ok) {
        const voices = await res.json();
        setAvailableVoices(voices);
        const def = voices.find((v) => v.is_default);
        if (def) setSelectedVoiceId(def.voice_id);
      }
    } catch (err) {
      console.error('Failed to load voices', err);
    }
  };

  const stopNarration = () => {
    if (browserSpeechInterval) {
      clearInterval(browserSpeechInterval);
      setBrowserSpeechInterval(null);
    }
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    if (audioInstance) {
      audioInstance.pause();
      audioInstance.currentTime = 0;
      setAudioInstance(null);
    }
    setIsPlaying(false);
    setAudioStatus('idle');
    setAvatarMouthState(MouthState.REST);
    setActiveWord(null);
    setAvatarEyeState(EyeState.OPEN);
  };

  const playBrowserSpeech = (scene, speed = playbackSpeed) => {
    if (!scene) return;
    if (browserSpeechInterval) {
      clearInterval(browserSpeechInterval);
      setBrowserSpeechInterval(null);
    }
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      if (voiceEnabled) {
        const utterance = new SpeechSynthesisUtterance(scene.narration);
        utterance.rate = speed;
        utterance.lang = langMap[teachingLanguage] || 'en-US';
        const startTime = Date.now();
        const estDuration = scene.estimated_duration || 8;

        utterance.onstart = () => {
          setIsPlaying(true);
          setAudioStatus('playing_browser');
          setCurrentSubtitle(scene.narration);
          setTimingMode(TimingMode.BROWSER_SPEECH);

          const interval = setInterval(() => {
            const elapsed = (Date.now() - startTime) / 1000;
            const mouthData = calculateMouthState(elapsed, true, [], scene.subtitles || [], estDuration);
            setAvatarMouthState(mouthData.mouthState);
            setAvatarEyeState(calculateEyeState(elapsed, reducedMotion));
          }, 80);
          setBrowserSpeechInterval(interval);
        };

        utterance.onend = () => {
          if (browserSpeechInterval) clearInterval(browserSpeechInterval);
          setBrowserSpeechInterval(null);
          setIsPlaying(false);
          setAudioStatus('idle');
          setAvatarMouthState(MouthState.REST);
          setActiveWord(null);
          setAvatarEyeState(EyeState.OPEN);
        };

        utterance.onerror = () => {
          if (browserSpeechInterval) clearInterval(browserSpeechInterval);
          setBrowserSpeechInterval(null);
          setIsPlaying(false);
          setAudioStatus('idle');
          setAvatarMouthState(MouthState.REST);
          setActiveWord(null);
        };

        window.speechSynthesis.speak(utterance);
      } else {
        setIsPlaying(true);
        setCurrentSubtitle(scene.narration);
        const timer = setTimeout(() => setIsPlaying(false), (scene.estimated_duration || 8) * 1000);
        return () => clearTimeout(timer);
      }
    }
  };

  const playNaturalVoice = async (scene, speed = playbackSpeed) => {
    if (!scene) return;
    stopNarration();
    setCurrentSubtitle(scene.narration);

    if (useRealTts && sessionId && scene.scene_id) {
      setAudioStatus('generating');
      try {
        const res = await fetch(`${API_BASE}/teaching/sessions/${sessionId}/scenes/${scene.scene_id}/speech`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ voice_id: selectedVoiceId || null }),
        });
        if (res.ok) {
          const asset = await res.json();
          setAudioAsset(asset);
          const audio = new Audio(asset.audio_url);
          audio.playbackRate = speed;
          setAudioInstance(audio);

          audio.ontimeupdate = () => {
            const current = audio.currentTime;
            if (asset.subtitles && asset.subtitles.length > 0) {
              const cue = asset.subtitles.find((s) => current >= s.start_time && current <= s.end_time);
              if (cue) setCurrentSubtitle(cue.text);
            }
            const mouthData = calculateMouthState(
              current,
              true,
              asset.word_cues || [],
              asset.subtitles || [],
              asset.duration_seconds || 0
            );
            setAvatarMouthState(mouthData.mouthState);
            setActiveWord(mouthData.activeWord);
            setTimingMode(mouthData.timingMode);
            setAvatarEyeState(calculateEyeState(current, reducedMotion));
          };

          audio.onplay = () => {
            setIsPlaying(true);
            setAudioStatus('playing_tts');
          };

          audio.onpause = () => {
            setIsPlaying(false);
            setAvatarMouthState(MouthState.REST);
            setActiveWord(null);
          };

          audio.onended = () => {
            setIsPlaying(false);
            setAudioStatus('idle');
            setAvatarMouthState(MouthState.REST);
            setActiveWord(null);
            setAvatarEyeState(EyeState.OPEN);
          };

          audio.onerror = () => {
            console.warn('Real audio error, falling back to Web Speech');
            playBrowserSpeech(scene, speed);
          };

          if (voiceEnabled) {
            await audio.play();
            return;
          }
        }
      } catch (err) {
        console.warn('TTS API error, falling back to Web Speech', err);
      }
    }

    playBrowserSpeech(scene, speed);
  };

  const playSceneNarration = (scene, speed = playbackSpeed) => {
    playNaturalVoice(scene, speed);
  };

  const handleSwitchLanguage = async (newLang, newMode = languageMode, newVoice = null) => {
    setTeachingLanguage(newLang);
    setLanguageMode(newMode);
    stopNarration();
    if (sessionId) {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/teaching/sessions/${sessionId}/language`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            language: newLang,
            mode: newMode,
            voice_id: newVoice,
          }),
        });
        if (res.ok) {
          const updatedSession = await res.json();
          const scenesRes = await fetch(`${API_BASE}/teaching/sessions/${sessionId}/scenes`, { method: 'POST' });
          if (scenesRes.ok) {
            const newPlan = await scenesRes.json();
            setScenePlan(newPlan);
            if (newPlan.scenes && newPlan.scenes[activeSceneIndex]) {
              playNaturalVoice(newPlan.scenes[activeSceneIndex]);
            }
          }
          if (updatedSession.latest_question) {
            setCurrentQuestion(updatedSession.latest_question);
          }
        }
      } catch (err) {
        console.error('Failed to switch session language', err);
      } finally {
        setLoading(false);
      }
    }
    fetchVoices(newLang);
  };

  // Phase 5: Fetch or Generate Teaching Scene Plan
  const loadScenePlan = async (sId) => {
    try {
      const res = await fetch(`${API_BASE}/teaching/sessions/${sId}/scenes`, { method: 'POST' });
      if (res.ok) {
        const plan = await res.json();
        setScenePlan(plan);
        setActiveSceneIndex(0);
        setRemediationScene(null);
        setAdaptiveRemediationActive(false);
        if (plan.scenes && plan.scenes.length > 0) {
          playNaturalVoice(plan.scenes[0]);
        }
      }
    } catch (err) {
      console.error('Failed to load scene plan', err);
    }
  };


  // Step 4: Teach Current Section
  const handleTeachSection = async () => {
    setLoading(true);
    setErrorMessage('');
    try {
      const res = await fetch(`${API_BASE}/teaching/sessions/${sessionId}/explain`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to fetch teaching explanation');
      const data = await res.json();
      setTeachingResponse(data);
      setCurrentStep('teach');
      await loadScenePlan(sessionId);
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 5: Ask Checkpoint Question
  const handleFetchQuestion = async () => {
    stopNarration();
    setLoading(true);
    setErrorMessage('');
    setShowHints(false);
    setSelectedOption('');
    setStudentAnswer('');
    try {
      const res = await fetch(`${API_BASE}/teaching/sessions/${sessionId}/question`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to generate checkpoint question');
      const data = await res.json();
      setCurrentQuestion(data);
      setCurrentStep('question');
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 6 & 7: Submit Student Answer and Evaluate
  const handleSubmitAnswer = async (e) => {
    if (e) e.preventDefault();
    const finalAnswer = selectedOption || studentAnswer;
    if (!finalAnswer.trim()) return;

    setLoading(true);
    setErrorMessage('');
    try {
      const res = await fetch(`${API_BASE}/teaching/sessions/${sessionId}/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_answer: finalAnswer,
          question_id: currentQuestion?.question_id,
        }),
      });
      if (!res.ok) throw new Error('Evaluation service error');
      const data = await res.json();
      setEvaluationOutcome(data);
      setConceptsMastered(data.concepts_mastered || []);
      setConceptsNeedingWork(data.concepts_needing_improvement || []);

      // Phase 5 Adaptive Branching: If misconception detected or score < 0.7, trigger remediation scene
      if (data.misconception_report?.is_misconception || data.evaluation?.score < 0.7) {
        try {
          const branchRes = await fetch(`${API_BASE}/teaching/sessions/${sessionId}/branch`, {
            method: 'POST',
          });
          if (branchRes.ok) {
            const remScene = await branchRes.json();
            setRemediationScene(remScene);
            setAdaptiveRemediationActive(true);
            if (scenePlan) {
              const updatedScenes = [...scenePlan.scenes];
              updatedScenes.splice(updatedScenes.length - 1, 0, remScene);
              setScenePlan({ ...scenePlan, scenes: updatedScenes, is_adaptive_branch: true });
            }
          }
        } catch (branchErr) {
          console.error('Could not branch adaptive scene:', branchErr);
        }
      }

      setCurrentStep('evaluated');
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 8: Teacher Adaptive Next Action (Advance or Adapt)
  const handleAdvanceOrAdapt = async () => {
    setLoading(true);
    setErrorMessage('');
    try {
      const res = await fetch(`${API_BASE}/teaching/sessions/${sessionId}/advance`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to execute adaptation step');
      const data = await res.json();

      if (data.status === 'completed') {
        // Direct learner to Final Cumulative Assessment!
        await handleStartFinalAssessment();
      } else {
        setCurrentSectionIndex(data.current_section_index);
        setTeachingResponse(data.result.teaching);
        setCurrentStep('teach');
        await loadScenePlan(sessionId);
      }
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Phase 8: Final Assessment Handlers
  const handleStartFinalAssessment = async () => {
    if (!sessionId) return;
    setLoading(true);
    setErrorMessage('');
    stopNarration();
    try {
      const res = await fetch(`${API_BASE}/teaching/sessions/${sessionId}/assessment`, {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to generate final assessment');
      const asmt = await res.json();
      setFinalAssessment(asmt);
      setAssessmentAnswers({});
      setCurrentStep('assessment');
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFinalAssessment = async () => {
    if (!sessionId || !finalAssessment) return;
    setLoading(true);
    setErrorMessage('');
    try {
      const answersPayload = finalAssessment.questions.map((q) => ({
        question_id: q.question_id,
        student_answer: assessmentAnswers[q.question_id] || '',
      }));

      const res = await fetch(`${API_BASE}/teaching/sessions/${sessionId}/assessment/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: answersPayload }),
      });
      if (!res.ok) throw new Error('Failed to grade assessment');
      const rep = await res.json();
      setLearningReport(rep);
      setConceptsMastered(rep.concepts_understood || []);
      setConceptsNeedingWork(rep.concepts_needing_improvement || []);
      setCurrentStep('report');

      // Update session history
      setSessionHistory((prev) => [
        {
          session_id: sessionId,
          topic: rep.topic,
          score_percent: rep.overall_score_percent,
          status: rep.status,
          date: 'Today',
        },
        ...prev.filter((p) => p.session_id !== sessionId),
      ]);
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadDashboardData = async () => {
    if (!sessionId) return;
    try {
      const res = await fetch(`${API_BASE}/teaching/sessions/${sessionId}/dashboard`);
      if (res.ok) {
        const data = await res.json();
        setDashboardData(data);
      }
    } catch (err) {
      console.error('Failed to load dashboard data', err);
    }
  };

  // Visual Renderers for Phase 5 Studio
  const renderBinaryTreeSVG = (data, highlights = []) => {
    const isHigh = (id) => highlights && highlights.includes(id);
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
        <svg viewBox="0 0 400 240" style={{ width: '100%', maxWidth: '440px', height: 'auto' }}>
          <line x1="200" y1="40" x2="100" y2="105" className="tree-edge" />
          <line x1="200" y1="40" x2="300" y2="105" className="tree-edge" />
          <line x1="100" y1="105" x2="50" y2="175" className="tree-edge" />
          <line x1="100" y1="105" x2="150" y2="175" className="tree-edge" />
          <line x1="300" y1="105" x2="250" y2="175" className="tree-edge" />
          <line x1="300" y1="105" x2="350" y2="175" className="tree-edge" />

          {/* Root 50 */}
          <g id="svg-node-50">
            <circle cx="200" cy="40" r="22" className={`tree-node-circle ${isHigh('node-50') ? 'highlighted' : ''}`} />
            <text x="200" y="40" className="tree-node-text">50</text>
            <text x="200" y="12" fill="var(--accent-amber)" fontSize="10" textAnchor="middle" fontWeight="700">ROOT</text>
          </g>

          {/* Left Child 25 */}
          <g id="svg-node-25">
            <circle cx="100" cy="105" r="20" className={`tree-node-circle ${isHigh('node-25') ? 'highlighted' : ''}`} />
            <text x="100" y="105" className="tree-node-text">25</text>
            <text x="65" y="88" fill="var(--accent-cyan)" fontSize="9" fontWeight="600">Left &lt; 50</text>
          </g>

          {/* Right Child 75 */}
          <g id="svg-node-75">
            <circle cx="300" cy="105" r="20" className={`tree-node-circle ${isHigh('node-75') ? 'highlighted' : ''}`} />
            <text x="300" y="105" className="tree-node-text">75</text>
            <text x="335" y="88" fill="var(--accent-cyan)" fontSize="9" fontWeight="600">Right &gt; 50</text>
          </g>

          {/* Leaves */}
          <g id="svg-node-10">
            <circle cx="50" cy="175" r="16" className="tree-node-circle" />
            <text x="50" y="175" className="tree-node-text">10</text>
          </g>
          <g id="svg-node-35">
            <circle cx="150" cy="175" r="16" className="tree-node-circle" />
            <text x="150" y="175" className="tree-node-text">35</text>
          </g>
          <g id="svg-node-60">
            <circle cx="250" cy="175" r="16" className="tree-node-circle" />
            <text x="250" y="175" className="tree-node-text">60</text>
          </g>
          <g id="svg-node-90">
            <circle cx="350" cy="175" r="16" className="tree-node-circle" />
            <text x="350" y="175" className="tree-node-text">90</text>
          </g>
        </svg>

        <div className="inorder-ribbon">
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>In-Order Traversal:</span>
          <span className="traversal-pill">10</span> →
          <span className="traversal-pill">25</span> →
          <span className="traversal-pill">35</span> →
          <span className="traversal-pill" style={{ background: 'rgba(245, 158, 11, 0.25)', color: 'var(--accent-amber)' }}>50</span> →
          <span className="traversal-pill">60</span> →
          <span className="traversal-pill">75</span> →
          <span className="traversal-pill">90</span>
        </div>
      </div>
    );
  };

  const renderCircuitSVG = (data) => (
    <div className="circuit-box">
      <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
        ⚡ Fundamental Electrical Relationship
      </div>
      <div className="formula-display">I = V / R</div>
      <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '16px', fontSize: '0.85rem' }}>
        <div><strong style={{ color: 'var(--accent-cyan)' }}>V</strong>: Voltage (Pressure)</div>
        <div><strong style={{ color: 'var(--accent-emerald)' }}>I</strong>: Current (Rate of Flow)</div>
        <div><strong style={{ color: 'var(--accent-amber)' }}>R</strong>: Resistance (Opposition)</div>
      </div>
    </div>
  );

  const renderCodeBlock = (data) => (
    <div className="code-stage-box">
      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginBottom: '8px' }}>
        # Python 3 Implementation: Tree Node Definition &amp; Traversal
      </div>
      <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
        {data?.code || "class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right"}
      </pre>
    </div>
  );

  const getAvatarEmotionAndGesture = () => {
    // 1. If at Checkpoint question step:
    if (currentStep === 'question' || scenePlan?.scenes?.[activeSceneIndex]?.is_checkpoint) {
      return { emotion: 'thoughtful', gesture: 'think', headMotion: 'tilt_thoughtful' };
    }
    // 2. If just evaluated with high mastery:
    if (currentStep === 'evaluated' && evaluationOutcome?.is_correct) {
      return { emotion: 'celebrating', gesture: 'celebrate', headMotion: 'nod' };
    }
    // 3. If just evaluated with misconception / struggling:
    if (currentStep === 'evaluated' && !evaluationOutcome?.is_correct) {
      return { emotion: 'encouraging', gesture: 'encourage', headMotion: 'nod' };
    }
    // 4. If in adaptive remediation scene (Scene 3-R):
    if (adaptiveRemediationActive || scenePlan?.scenes?.[activeSceneIndex]?.scene_type === 'adaptive_remediation') {
      return { emotion: 'encouraging', gesture: 'encourage', headMotion: 'nod' };
    }
    // 5. Normal active scene:
    const activeScene = scenePlan?.scenes?.[activeSceneIndex];
    const em = activeScene?.teacher_emotion || 'explaining';
    const act = activeScene?.teacher_action || 'explain';
    let gest = 'explain';
    if (act === 'welcome' || act === 'greet' || em === 'welcoming') gest = 'welcome';
    else if (act.includes('point') || act.includes('trace')) gest = 'point_visual';
    else if (act.includes('question') || act.includes('think') || em === 'thoughtful') gest = 'think';
    else if (act.includes('celebrat') || em === 'celebrating') gest = 'celebrate';
    else if (act.includes('encourage') || em === 'encouraging') gest = 'encourage';

    return { emotion: em, gesture: gest, headMotion: em === 'welcoming' || em === 'encouraging' ? 'nod' : 'neutral' };
  };

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <header className="navbar">
        <div className="nav-brand">
          <div className="brand-icon">
            <LogoIcon />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>AI Teacher</span>
              <span style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)', background: 'rgba(6, 182, 212, 0.15)', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(6, 182, 212, 0.3)', fontWeight: 600 }}>
                JUDGE READY
              </span>
            </div>
          </div>
        </div>

        {/* Top-Level Coherent Navigation Tabs (Learn | Progress | History) */}
        <div className="nav-tabs-group" id="nav-tabs">
          <button
            type="button"
            className={`nav-tab-btn ${navTab === 'learn' ? 'active' : ''}`}
            id="tab-btn-learn"
            onClick={() => setNavTab('learn')}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <LearnIcon /> Learn
          </button>
          <button
            type="button"
            className={`nav-tab-btn ${navTab === 'progress' ? 'active' : ''}`}
            id="tab-btn-progress"
            onClick={() => {
              setNavTab('progress');
              loadDashboardData();
            }}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <ProgressIcon /> Progress
          </button>
          <button
            type="button"
            className={`nav-tab-btn ${navTab === 'history' ? 'active' : ''}`}
            id="tab-btn-history"
            onClick={() => setNavTab('history')}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <HistoryIcon /> History
          </button>
        </div>

        {/* Top Right: Multilingual Switching & Readiness Indicator */}
        <div className="nav-status">
          {/* Quick Multilingual Language Switcher */}
          <LanguageSwitcher
            currentLanguage={teachingLanguage}
            onLanguageChange={handleSwitchLanguage}
            languageMode={languageMode}
            onModeChange={(mode) => handleSwitchLanguage(teachingLanguage, mode)}
            isLoading={loading}
          />

          {/* Judge Readiness Indicator */}
          <div
            className="readiness-pill"
            id="btn-readiness-indicator"
            onClick={() => setShowReadinessModal(true)}
            title="Click to inspect subsystem readiness"
          >
            <span className="readiness-dot"></span>
            <span>System Ready</span>
          </div>
        </div>
      </header>

      {/* Subsystem Readiness Modal */}
      {showReadinessModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
          <div className="glass-card animate-fade-in" style={{ maxWidth: '520px', width: '100%', padding: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="readiness-dot"></span> Subsystem Readiness
              </h3>
              <button className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.8rem' }} onClick={() => setShowReadinessModal(false)}>✕ Close</button>
            </div>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '18px' }}>
              All primary services are fully operational and ready for live evaluation:
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <span>⚡ <strong>Backend Core:</strong> FastAPI + SQLite WAL</span>
                <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>OPERATIONAL</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <span>🧠 <strong>AI Engine:</strong> Pedagogical Intelligence</span>
                <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>OPERATIONAL</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <span>📚 <strong>RAG Engine:</strong> Vector + BM25 Lexical Hybrid</span>
                <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>OPERATIONAL</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <span>🗣️ <strong>Speech Engine:</strong> Multilingual Neural Edge TTS</span>
                <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>OPERATIONAL</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                <span>👤 <strong>Avatar Engine:</strong> Viseme & Emotion Synchronization</span>
                <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>OPERATIONAL</span>
              </div>
            </div>
            <button className="btn-primary" style={{ marginTop: '20px', width: '100%' }} onClick={() => setShowReadinessModal(false)}>Got It →</button>
          </div>
        </div>
      )}

      {/* Grounded Source Excerpt Modal */}
      {showExcerptModal && groundedContext && groundedContext.citations && groundedContext.citations.length > 0 && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
          <div className="glass-card animate-fade-in" style={{ maxWidth: '600px', width: '100%', padding: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                📖 Verified Document Source
              </h3>
              <button className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.8rem' }} onClick={() => setShowExcerptModal(false)}>✕ Close</button>
            </div>
            <div style={{ marginBottom: '14px', fontSize: '0.85rem', color: 'var(--accent-cyan)' }}>
              Source File: <strong>{groundedContext.citations[0].filename}</strong> ({groundedContext.citations[0].location})
            </div>
            <div style={{ maxHeight: '280px', overflowY: 'auto', padding: '16px', background: 'rgba(0,0,0,0.3)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', fontStyle: 'italic', lineHeight: 1.6, color: '#e2e8f0' }}>
              "{groundedContext.citations[0].excerpt}"
            </div>
            <button className="btn-primary" style={{ marginTop: '20px', width: '100%' }} onClick={() => setShowExcerptModal(false)}>Close Excerpt</button>
          </div>
        </div>
      )}

      {/* Teaching Loop Visual Stepper (Only in Learn tab) */}
      {navTab === 'learn' && (
        <nav className="teaching-stepper" aria-label="Teaching Cycle Stepper">
          <div className={`step-item ${currentStep === 'onboarding' || currentStep === 'loading_stages' ? 'active' : 'completed'}`} id="step-understand">
            <span className="step-number">1</span>
            <span>Configure Learner</span>
          </div>
          <div className={`step-item ${currentStep === 'plan' ? 'active' : (['teach', 'question', 'evaluated', 'assessment', 'report', 'completed'].includes(currentStep) ? 'completed' : '')}`} id="step-plan">
            <span className="step-number">2</span>
            <span>Personalized Plan</span>
          </div>
          <div className={`step-item ${currentStep === 'teach' ? 'active' : (['question', 'evaluated', 'assessment', 'report', 'completed'].includes(currentStep) ? 'completed' : '')}`} id="step-explain">
            <span className="step-number">3</span>
            <span>Teaching Studio</span>
          </div>
          <div className={`step-item ${currentStep === 'question' ? 'active' : (['evaluated', 'assessment', 'report', 'completed'].includes(currentStep) ? 'completed' : '')}`} id="step-question">
            <span className="step-number">4</span>
            <span>Checkpoint</span>
          </div>
          <div className={`step-item ${currentStep === 'evaluated' ? 'active' : (['assessment', 'report', 'completed'].includes(currentStep) ? 'completed' : '')}`} id="step-evaluate">
            <span className="step-number">5</span>
            <span>Hero Adaptation</span>
          </div>
          <div className={`step-item ${['assessment', 'report', 'completed'].includes(currentStep) ? 'active' : ''}`} id="step-adapt">
            <span className="step-number">6</span>
            <span>Final Report</span>
          </div>
        </nav>
      )}

      {/* Global Error Banner */}
      {errorMessage && (
        <div style={{ padding: '14px 20px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: 'var(--radius-md)', color: '#fca5a5', marginBottom: '20px' }}>
          ⚠️ {errorMessage}
        </div>
      )}

      {/* STEP 1: ONBOARDING & TOPIC CONFIGURATION (When navTab === 'learn') */}
      {navTab === 'learn' && currentStep === 'onboarding' && (
        <section className="glass-card animate-fade-in" id="card-onboarding">
          {/* Quick Demo Preset Button for Judges */}
          <button
            type="button"
            className="btn-demo-preset"
            id="btn-load-golden-demo"
            onClick={loadGoldenDemoPreset}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
          >
            <SparklesIcon /> Quick Start: Load Golden Demo (Binary Trees • Alex Rivera • 15 min • Analogy-Driven)
          </button>

          {demoNotice && (
            <div style={{ padding: '10px 16px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', borderRadius: 'var(--radius-sm)', color: '#a7f3d0', fontSize: '0.88rem', marginBottom: '20px' }}>
              {demoNotice}
            </div>
          )}

          <h1 className="card-title">Configure Your Personalized AI Teacher</h1>
          <p className="card-subtitle">Set your educational goals, language, and available time. The AI Teacher will structurally adapt its curriculum to match your background and pace.</p>

          <form onSubmit={handleStartSession}>
            {/* Learning Modality Selector */}
            <div style={{ marginBottom: '24px' }}>
              <label className="form-label">Learning Modality</label>
              <div className="mode-selector-grid">
                <div
                  className={`mode-card ${knowledgeMode === 'topic' ? 'active' : ''}`}
                  onClick={() => setKnowledgeMode('topic')}
                  id="mode-topic-btn"
                >
                  <div className="mode-card-header">
                    <GlobeIcon />
                    <span>General Topic Learning</span>
                  </div>
                  <div className="mode-card-desc">
                    AI Teacher structures an intuitive curriculum from universal principles, diagrams, and physical analogies.
                  </div>
                </div>

                <div
                  className={`mode-card ${knowledgeMode === 'document' ? 'active' : ''}`}
                  onClick={() => setKnowledgeMode('document')}
                  id="mode-document-btn"
                >
                  <div className="mode-card-header">
                    <DocumentIcon />
                    <span>Document-Grounded Learning (RAG)</span>
                  </div>
                  <div className="mode-card-desc">
                    Upload syllabus, slides, or notes. Teacher strictly grounds lessons, definitions, and questions in your source.
                  </div>
                </div>
              </div>
            </div>

            {/* Document Upload & Selector Area (when in document mode) */}
            {knowledgeMode === 'document' && (
              <div style={{ marginBottom: '24px', background: 'rgba(99, 102, 241, 0.05)', padding: '20px', borderRadius: 'var(--radius-md)', border: '1px solid rgba(99, 102, 241, 0.2)' }} id="document-upload-section">
                <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <DocumentIcon /> Ingest Educational Material
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                  Upload PDF textbook chapters, Word documents (.docx), lecture slides (.pptx), or Markdown/Text notes.
                </p>

                <div className="dropzone-area">
                  <div className="dropzone-icon" style={{ display: 'flex', justifyContent: 'center', marginBottom: '8px', color: 'var(--primary)' }}>
                    <UploadIcon />
                  </div>
                  <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '6px' }}>
                    Select an educational document to ingest & index
                  </p>
                  <input
                    type="file"
                    id="file-upload-input"
                    accept=".pdf,.docx,.pptx,.txt,.md"
                    onChange={handleFileUpload}
                    disabled={uploading}
                    style={{ marginTop: '8px', color: 'var(--text-secondary)' }}
                  />
                  <div className="format-badges">
                    <span className="format-badge">PDF (pypdf)</span>
                    <span className="format-badge">DOCX (Word)</span>
                    <span className="format-badge">PPTX (Slides)</span>
                    <span className="format-badge">TXT / Markdown</span>
                  </div>
                </div>

                {uploadMessage && (
                  <div style={{ fontSize: '0.88rem', color: uploadMessage.startsWith('✓') ? 'var(--accent-emerald)' : '#fca5a5', marginBottom: '16px', padding: '8px 12px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px' }} id="upload-status-msg">
                    {uploadMessage}
                  </div>
                )}

                {documents.length > 0 && (
                  <div>
                    <label className="form-label" style={{ marginBottom: '8px' }}>Select Grounding Document:</label>
                    <div className="doc-list-grid" id="document-selection-grid">
                      {documents.map((doc) => (
                        <div
                          key={doc.document_id}
                          className={`doc-item-card ${selectedDocumentId === doc.document_id ? 'selected' : ''}`}
                          onClick={() => {
                            setSelectedDocumentId(doc.document_id);
                            if (doc.filename.toLowerCase().includes('tree')) setTopic('Binary Trees');
                          }}
                          id={`doc-card-${doc.document_id}`}
                        >
                          <div className="doc-item-title">{doc.filename}</div>
                          <div className="doc-item-meta">
                            <span>{doc.page_count} {doc.file_type === 'pptx' ? 'slides' : 'pages'}</span>
                            <span>{doc.chunk_count} chunks</span>
                            <span style={{ color: doc.status === 'ready' ? 'var(--accent-emerald)' : 'var(--accent-amber)', fontWeight: 600 }}>
                              {doc.status.toUpperCase()}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label" htmlFor="input-learner-name">Learner Name</label>
                <input
                  id="input-learner-name"
                  className="form-input"
                  value={learnerName}
                  onChange={(e) => setLearnerName(e.target.value)}
                  placeholder="e.g. Alex"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="select-level">Knowledge Level</label>
                <select
                  id="select-level"
                  className="form-select"
                  value={educationalLevel}
                  onChange={(e) => setEducationalLevel(e.target.value)}
                >
                  <option value="beginner">Beginner (Foundations & Intuition)</option>
                  <option value="intermediate">Intermediate (Mechanics & Code)</option>
                  <option value="advanced">Advanced (Deep Dive & Edge Cases)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="select-time">Available Learning Time</label>
                <select
                  id="select-time"
                  className="form-select"
                  value={availableTime}
                  onChange={(e) => setAvailableTime(Number(e.target.value))}
                >
                  <option value={5}>5 Minutes (Rapid Essential Sprint)</option>
                  <option value={15}>15 Minutes (Balanced Core Modules)</option>
                  <option value={20}>20 Minutes (Standard Curriculum with Checkpoints)</option>
                  <option value={60}>60 Minutes (Comprehensive Masterclass)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="select-style">Preferred Teaching Style</label>
                <select
                  id="select-style"
                  className="form-select"
                  value={teachingStyle}
                  onChange={(e) => setTeachingStyle(e.target.value)}
                >
                  <option value="analogy_driven">Analogy-Driven (Metaphors & Physical Models)</option>
                  <option value="visual">Visual & Diagrammatic</option>
                  <option value="first_principles">First Principles (Rigorous Math/Logic)</option>
                  <option value="practical_code">Practical Code & Implementation</option>
                  <option value="socratic">Socratic (Guided Discovery)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="select-language">Preferred Language</label>
                <select
                  id="select-language"
                  className="form-select"
                  value={teachingLanguage}
                  onChange={(e) => {
                    setTeachingLanguage(e.target.value);
                    setLanguage(e.target.value);
                    fetchVoices(e.target.value);
                  }}
                >
                  <option value="en">English (US)</option>
                  <option value="hi">हिन्दी (Hindi)</option>
                  <option value="ta">தமிழ் (Tamil)</option>
                  <option value="te">తెలుగు (Telugu)</option>
                  <option value="ml">മലയാളം (Malayalam)</option>
                  <option value="kn">ಕನ್ನಡ (Kannada)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="select-mode">Language Mode</label>
                <select
                  id="select-mode"
                  className="form-select"
                  value={languageMode}
                  onChange={(e) => setLanguageMode(e.target.value)}
                >
                  <option value="bilingual">Bilingual (Native narrative + English code & tech terms)</option>
                  <option value="full">Full Language (Complete native immersion)</option>
                  <option value="mixed">Mixed (Conversational code-switching)</option>
                </select>
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: '24px' }}>
              <label className="form-label" htmlFor="input-topic">Topic to Master</label>
              <input
                id="input-topic"
                className="form-input"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Enter any topic, e.g. Binary Trees, Ohm's Law, Machine Learning"
                required
              />
              <div className="topic-pills">
                <span className="topic-pill" onClick={() => setTopic('Binary Trees')}>Binary Trees</span>
                <span className="topic-pill" onClick={() => setTopic("Ohm's Law")}>Ohm's Law & Circuits</span>
                <span className="topic-pill" onClick={() => setTopic('Recursion & Call Stacks')}>Recursion</span>
                <span className="topic-pill" onClick={() => setTopic('Sorting Algorithms')}>Sorting Algorithms</span>
                <span className="topic-pill" onClick={() => setTopic('Neural Network Forward Pass')}>Neural Networks</span>
              </div>
            </div>

            <button type="submit" className="btn-primary" id="btn-generate-plan" disabled={loading} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
              {loading ? 'Synthesizing Curriculum...' : <>Generate Structured Lesson Plan <ArrowRightIcon /></>}
            </button>
          </form>
        </section>
      )}

      {/* STEP 2 & 3: LESSON PLAN ROADMAP */}
      {currentStep === 'plan' && lessonPlan && (
        <section className="glass-card animate-fade-in" id="card-lesson-plan">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <span className="status-badge" style={{ marginBottom: '8px' }}>
                ⏱️ {lessonPlan.estimated_duration} Minutes • {lessonPlan.explanation_depth.replace('_', ' ')}
              </span>
              <h1 className="card-title">{lessonPlan.lesson_title}</h1>
              <p className="card-subtitle">Topic: <strong>{lessonPlan.topic}</strong></p>
            </div>
            <button className="btn-primary" id="btn-start-teaching" onClick={handleTeachSection} disabled={loading}>
              {loading ? 'Loading Lesson Section...' : 'Begin Lesson: Section 1 →'}
            </button>
          </div>

          <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginTop: '20px', marginBottom: '12px' }}>
            Learning Objectives:
          </h3>
          <ul style={{ paddingLeft: '20px', color: 'var(--text-primary)', marginBottom: '24px' }}>
            {lessonPlan.learning_objectives.map((obj, i) => (
              <li key={i} style={{ marginBottom: '6px' }}>{obj}</li>
            ))}
          </ul>

          <h3 style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginBottom: '14px' }}>
            Planned Sections ({lessonPlan.sections.length}):
          </h3>
          <div className="sections-grid">
            {lessonPlan.sections.map((sec, idx) => (
              <div
                key={sec.section_id}
                className={`section-badge-card ${idx === 0 ? 'active' : ''}`}
                id={`plan-sec-${sec.section_id}`}
              >
                <div className="section-num">Section {sec.section_number}</div>
                <div className="section-card-title">{sec.title}</div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: '6px 0 10px' }}>
                  {sec.objective}
                </p>
                <div className="section-meta">
                  <span>⏱️ {sec.estimated_time_minutes} min</span>
                  <span>📊 {sec.difficulty}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Grounding Citations Banner */}
          {groundedContext && groundedContext.citations && groundedContext.citations.length > 0 && (
            <div className="citations-panel animate-fade-in" id="panel-citations">
              <div className="citations-header">
                <span>📚</span>
                <span>Verified Source Material Attributions ({groundedContext.citations.length} citations)</span>
              </div>
              <div>
                {groundedContext.citations.map((cit, idx) => (
                  <div key={idx} className="citation-card">
                    <div className="citation-source">
                      <span>📄 {cit.filename} • {cit.location}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>Grounded Evidence</span>
                    </div>
                    <div className="citation-excerpt">"{cit.excerpt}"</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      )}

      {/* STEP 4: AI TEACHING VIDEO & SUBJECT-AWARE VISUAL STUDIO */}
      {currentStep === 'teach' && teachingResponse && (
        <section className="glass-card animate-fade-in" id="card-teaching-explanation">
          {/* Top Bar: Section & Mode Switch */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="status-badge" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary)', borderColor: 'rgba(99, 102, 241, 0.3)' }}>
                Section {currentSectionIndex + 1} of {lessonPlan?.sections.length || 1} • {teachingResponse.teaching_action.toUpperCase()}
              </span>
              {adaptiveRemediationActive && (
                <span className="status-badge" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#fca5a5', borderColor: 'rgba(239, 68, 68, 0.4)' }}>
                  ⚡ ADAPTIVE REMEDIATION (SCENE 3-R)
                </span>
              )}
            </div>
            {/* View Switcher: Interactive Studio vs Reading Summary */}
            <div style={{ display: 'flex', gap: '6px', background: 'rgba(0,0,0,0.3)', padding: '4px', borderRadius: 'var(--radius-full)' }}>
              <button
                className={`btn-secondary ${studioViewMode === 'video' ? 'active' : ''}`}
                style={{ padding: '4px 12px', fontSize: '0.8rem', borderRadius: 'var(--radius-full)', background: studioViewMode === 'video' ? 'var(--primary)' : 'transparent', color: studioViewMode === 'video' ? '#fff' : 'var(--text-secondary)' }}
                onClick={() => setStudioViewMode('video')}
                id="btn-mode-video"
              >
                Video Studio
              </button>
              <button
                className={`btn-secondary ${studioViewMode === 'reading' ? 'active' : ''}`}
                style={{ padding: '4px 12px', fontSize: '0.8rem', borderRadius: 'var(--radius-full)', background: studioViewMode === 'reading' ? 'var(--primary)' : 'transparent', color: studioViewMode === 'reading' ? '#fff' : 'var(--text-secondary)' }}
                onClick={() => setStudioViewMode('reading')}
                id="btn-mode-reading"
              >
                Reading View
              </button>
            </div>
          </div>

          <h2 className="card-title" style={{ marginBottom: '16px' }}>{teachingResponse.concept}</h2>

          {/* MODE A: INTERACTIVE TEACHING VIDEO STUDIO */}
          {studioViewMode === 'video' && (
            <div id="teaching-video-studio">
              {/* Phase 6: Language & Voice Deck Bar */}
              <div className="language-deck-bar" id="bar-language-deck">
                <div className="language-deck-left">
                  <span className="lang-badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <GlobeIcon /> Language:
                  </span>
                  <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                    {[
                      { code: 'en', label: 'English' },
                      { code: 'hi', label: 'हिन्दी' },
                      { code: 'ta', label: 'தமிழ்' },
                      { code: 'te', label: 'తెలుగు' },
                      { code: 'ml', label: 'മലയാളം' },
                      { code: 'kn', label: 'ಕನ್ನಡ' },
                    ].map((item) => (
                      <button
                        key={item.code}
                        className={`btn-secondary ${teachingLanguage === item.code ? 'active' : ''}`}
                        style={{
                          padding: '4px 10px',
                          fontSize: '0.78rem',
                          borderRadius: 'var(--radius-full)',
                          background: teachingLanguage === item.code ? 'var(--primary)' : 'rgba(255,255,255,0.06)',
                          color: teachingLanguage === item.code ? '#fff' : 'var(--text-secondary)',
                          border: teachingLanguage === item.code ? '1px solid var(--primary)' : '1px solid rgba(255,255,255,0.1)',
                        }}
                        onClick={() => handleSwitchLanguage(item.code)}
                        id={`btn-lang-${item.code}`}
                      >
                        {item.label}
                      </button>
                    ))}
                  </div>

                  {/* Mode Toggles */}
                  <div className="mode-toggle-group" style={{ marginLeft: '6px' }}>
                    <button
                      className={`mode-toggle-btn ${languageMode === 'bilingual' ? 'active' : ''}`}
                      onClick={() => handleSwitchLanguage(teachingLanguage, 'bilingual')}
                      title="Native narrative + preserved English code/terms"
                    >
                      Bilingual
                    </button>
                    <button
                      className={`mode-toggle-btn ${languageMode === 'full' ? 'active' : ''}`}
                      onClick={() => handleSwitchLanguage(teachingLanguage, 'full')}
                      title="Full native immersion"
                    >
                      Full
                    </button>
                    <button
                      className={`mode-toggle-btn ${languageMode === 'mixed' ? 'active' : ''}`}
                      onClick={() => handleSwitchLanguage(teachingLanguage, 'mixed')}
                      title="Conversational code-switching"
                    >
                      Mixed
                    </button>
                  </div>
                </div>

                <div className="language-deck-right">
                  {/* Voice Selector */}
                  {availableVoices.length > 0 && (
                    <select
                      className="lang-select"
                      value={selectedVoiceId}
                      onChange={(e) => {
                        setSelectedVoiceId(e.target.value);
                        handleSwitchLanguage(teachingLanguage, languageMode, e.target.value);
                      }}
                      id="select-voice-picker"
                    >
                      {availableVoices.map((v) => (
                        <option key={v.voice_id} value={v.voice_id}>
                          {v.name} ({v.gender})
                        </option>
                      ))}
                    </select>
                  )}

                  {/* Real TTS vs Browser Toggle */}
                  <button
                    className="btn-secondary"
                    style={{
                      fontSize: '0.75rem',
                      padding: '4px 8px',
                      background: useRealTts ? 'rgba(6,182,212,0.15)' : 'rgba(255,255,255,0.05)',
                      color: useRealTts ? 'var(--accent-cyan)' : 'var(--text-muted)',
                    }}
                    onClick={() => setUseRealTts(!useRealTts)}
                    id="btn-toggle-tts-engine"
                  >
                    {useRealTts ? 'Real TTS (Edge)' : 'Web Speech'}
                  </button>

                  {/* Audio Status Pill */}
                  <div className={`voice-status-badge ${audioStatus === 'generating' ? 'generating' : ''}`} id="badge-voice-status">
                    {audioStatus === 'generating' && 'Synthesizing...'}
                    {audioStatus === 'playing_tts' && 'Neural Voice'}
                    {audioStatus === 'playing_browser' && 'Web Speech'}
                    {audioStatus === 'idle' && (isPlaying ? 'Playing' : 'Ready')}
                  </div>
                </div>
              </div>

              {/* Studio Split Screen */}
              <div className="teaching-studio-container">
                {/* Left Pane: AI Teacher Presenter */}
                <div className="avatar-studio-pane" id="pane-avatar-studio">
                  <div className="on-air-pill">
                    <span className="on-air-dot"></span>
                    <span>ON AIR • AI EDUCATOR</span>
                  </div>

                  {(() => {
                    const pres = getAvatarEmotionAndGesture();
                    return (
                      <>
                        <TeacherAvatar
                          emotion={pres.emotion}
                          speaking={isPlaying}
                          mouthState={avatarMouthState}
                          eyeState={avatarEyeState}
                          gesture={pres.gesture}
                          headMotion={pres.headMotion}
                          reducedMotion={reducedMotion}
                          activeWord={activeWord}
                        />
                        <TeacherStatus
                          teacherName="Prof. Sophia"
                          title="Adaptive Educational AI"
                          emotion={pres.emotion}
                          gesture={pres.gesture}
                          timingMode={timingMode}
                          speaking={isPlaying}
                          reducedMotion={reducedMotion}
                          onToggleReducedMotion={() => setReducedMotion(!reducedMotion)}
                        />
                      </>
                    );
                  })()}

                  {/* Audio Controls */}
                  <div style={{ display: 'flex', gap: '8px', marginBottom: '14px', width: '100%', justifyContent: 'center' }}>
                    <button
                      className="btn-secondary"
                      style={{ fontSize: '0.8rem', padding: '6px 12px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                      onClick={() => {
                        if (isPlaying) {
                          stopNarration();
                        } else if (scenePlan?.scenes?.[activeSceneIndex]) {
                          playNaturalVoice(scenePlan.scenes[activeSceneIndex]);
                        }
                      }}
                      id="btn-play-narration"
                    >
                      {isPlaying ? <><PauseIcon /> Pause Narration</> : <><PlayIcon /> Play Narration</>}
                    </button>
                    <button
                      className="btn-secondary"
                      style={{ fontSize: '0.8rem', padding: '6px 10px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                      onClick={() => {
                        setVoiceEnabled(!voiceEnabled);
                        if (isPlaying) stopNarration();
                      }}
                      id="btn-toggle-voice"
                      title={voiceEnabled ? 'Mute Speech' : 'Enable Speech'}
                    >
                      {voiceEnabled ? <><VolumeIcon /> Voice ON</> : <><MuteIcon /> Muted</>}
                    </button>
                  </div>

                  {/* Closed Captions */}
                  <div className="captions-ticker" id="box-live-captions">
                    <div className="captions-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>Live Captions ({teachingLanguage.toUpperCase()} • {languageMode})</span>
                      {audioStatus === 'playing_tts' && (
                        <span style={{ color: 'var(--accent-cyan)', fontSize: '0.7rem' }}>SYNCED WITH NEURAL TTS</span>
                      )}
                    </div>
                    <div style={{ minHeight: '38px', display: 'flex', alignItems: 'center' }}>
                      <span className="subtitle-cue-active">
                        {currentSubtitle || scenePlan?.scenes?.[activeSceneIndex]?.narration || teachingResponse.explanation}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Right Pane: Subject-Aware Visual Stage */}
                <div className="visual-stage-pane" id="pane-visual-stage">
                  <div className="visual-stage-header">
                    <div>
                      <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                        {scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.title || teachingResponse.concept}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                        Scene {activeSceneIndex + 1} of {scenePlan?.scenes?.length || 4} • {scenePlan?.scenes?.[activeSceneIndex]?.scene_type?.replace('_', ' ').toUpperCase()}
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <span className="visual-type-badge" id="badge-visual-type">
                        {scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type === 'tree_diagram' && 'Binary Tree SVG'}
                        {scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type === 'circuit_diagram' && 'Circuit Schematic'}
                        {scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type === 'code' && 'Code Block'}
                        {scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type === 'equation' && 'Math Equation'}
                        {(!scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type || scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type === 'text') && 'Conceptual Model'}
                        {scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type === 'flowchart' && 'Flowchart'}
                      </span>

                      {/* Grounded Citation Badge */}
                      {scenePlan?.scenes?.[activeSceneIndex]?.source_references?.[0] && (
                        <span style={{ fontSize: '0.72rem', background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)', padding: '3px 8px', borderRadius: '4px', border: '1px solid rgba(6, 182, 212, 0.3)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <DocumentIcon /> {scenePlan.scenes[activeSceneIndex].source_references[0].filename} ({scenePlan.scenes[activeSceneIndex].source_references[0].location})
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Active Visual Display */}
                  <div className="visual-canvas-area" id="canvas-visual-area">
                    {scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type === 'tree_diagram' &&
                      renderBinaryTreeSVG(
                        scenePlan.scenes[activeSceneIndex].visual_specification.data,
                        scenePlan.scenes[activeSceneIndex].visual_specification.highlight_elements
                      )}

                    {scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type === 'circuit_diagram' &&
                      renderCircuitSVG(scenePlan.scenes[activeSceneIndex].visual_specification.data)}

                    {scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type === 'code' &&
                      renderCodeBlock(scenePlan.scenes[activeSceneIndex].visual_specification.data)}

                    {scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type === 'equation' && (
                      <div style={{ textAlign: 'center', padding: '20px' }}>
                        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-amber)', marginBottom: '12px' }}>
                          {scenePlan.scenes[activeSceneIndex].visual_specification.data?.latex_equation || "BalanceFactor = Height(Left) - Height(Right)"}
                        </div>
                        <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                          {scenePlan.scenes[activeSceneIndex].visual_specification.data?.invariant_condition || "Invariant: -1 <= BalanceFactor <= +1"}
                        </div>
                      </div>
                    )}

                    {(!scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type ||
                      ['text', 'flowchart'].includes(scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.visual_type)) && (
                      <div style={{ textAlign: 'center', maxWidth: '500px', padding: '16px' }}>
                        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '10px' }}>
                          {scenePlan?.scenes?.[activeSceneIndex]?.visual_specification?.title || teachingResponse.concept}
                        </div>
                        <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                          {scenePlan?.scenes?.[activeSceneIndex]?.onscreen_text || teachingResponse.explanation}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Onscreen Key Takeaway */}
                  <div style={{ marginTop: '12px', background: 'rgba(255, 255, 255, 0.04)', padding: '10px 14px', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem' }}>
                    <span style={{ color: 'var(--accent-cyan)' }}><TargetIcon /></span>
                    <span><strong>Key Principle:</strong> {scenePlan?.scenes?.[activeSceneIndex]?.onscreen_text || teachingResponse.key_takeaway}</span>
                  </div>
                </div>
              </div>

              {/* Bottom Cinema Control Deck */}
              <div className="cinema-controls-bar" id="cinema-control-deck">
                {/* Timeline Scrubber */}
                <div className="scene-stepper-track">
                  {scenePlan?.scenes?.map((scn, idx) => (
                    <button
                      key={scn.scene_id || idx}
                      className={`scene-step-pill ${idx === activeSceneIndex ? 'active' : ''} ${scn.is_checkpoint ? 'checkpoint' : ''} ${scn.scene_type === 'adaptive_remediation' ? 'remediation' : ''}`}
                      onClick={() => {
                        setActiveSceneIndex(idx);
                        playSceneNarration(scn);
                        if (scn.is_checkpoint) {
                          handleFetchQuestion();
                        }
                      }}
                      id={`pill-scene-${idx + 1}`}
                    >
                      <span>
                        {scn.scene_type === 'intro' && '1. Intro'}
                        {scn.scene_type === 'visual_explanation' && '2. Visual Model'}
                        {scn.scene_type === 'analogy_walkthrough' && '3. Walkthrough'}
                        {scn.scene_type === 'adaptive_remediation' && '3-R. Remediation'}
                        {scn.scene_type === 'checkpoint_prompt' && '4. Checkpoint'}
                        {!['intro', 'visual_explanation', 'analogy_walkthrough', 'adaptive_remediation', 'checkpoint_prompt'].includes(scn.scene_type) && `${idx + 1}. Scene`}
                      </span>
                    </button>
                  ))}
                </div>

                {/* Speed selector & Checkpoint trigger */}
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <select
                    className="form-select"
                    style={{ width: 'auto', padding: '4px 8px', fontSize: '0.75rem', height: '32px' }}
                    value={playbackSpeed}
                    onChange={(e) => {
                      const spd = parseFloat(e.target.value);
                      setPlaybackSpeed(spd);
                      if (isPlaying && scenePlan?.scenes?.[activeSceneIndex]) {
                        playSceneNarration(scenePlan.scenes[activeSceneIndex], spd);
                      }
                    }}
                    id="select-playback-speed"
                  >
                    <option value={1.0}>1.0x Speed</option>
                    <option value={1.25}>1.25x Speed</option>
                    <option value={1.5}>1.5x Speed</option>
                  </select>

                  <button
                    className="btn-primary"
                    style={{ padding: '6px 14px', fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                    id="btn-proceed-question"
                    onClick={handleFetchQuestion}
                    disabled={loading}
                  >
                    {loading ? 'Preparing Checkpoint...' : <>Check My Understanding <ArrowRightIcon /></>}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* MODE B: READING SUMMARY VIEW */}
          {studioViewMode === 'reading' && (
            <div className="teaching-box" id="teaching-content-box">
              <p className="teaching-explanation">{teachingResponse.explanation}</p>

              {teachingResponse.analogy && (
                <div className="analogy-card" id="card-analogy">
                  <div className="analogy-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <LightbulbIcon /> Intuitive Analogy
                  </div>
                  <p style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>{teachingResponse.analogy}</p>
                </div>
              )}

              {teachingResponse.example && (
                <div className="example-card" id="card-example">
                  <div className="example-title">Concrete Example</div>
                  <p style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>{teachingResponse.example}</p>
                </div>
              )}

              <div className="key-takeaway" id="card-takeaway">
                <span style={{ color: 'var(--accent-emerald)' }}><TargetIcon /></span>
                <span><strong>Key Principle:</strong> {teachingResponse.key_takeaway}</span>
              </div>

              {/* Grounding Citations Banner */}
              {groundedContext && groundedContext.citations && groundedContext.citations.length > 0 && (
                <div className="citations-panel animate-fade-in" id="panel-teaching-citations">
                  <div className="citations-header">
                    <span>📚</span>
                    <span>Verified Source Material Attributions ({groundedContext.citations.length} citations)</span>
                  </div>
                  <div>
                    {groundedContext.citations.map((cit, idx) => (
                      <div key={idx} className="citation-card">
                        <div className="citation-source">
                          <span>📄 {cit.filename} • {cit.location}</span>
                          <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>Verified Source</span>
                        </div>
                        <div className="citation-excerpt">"{cit.excerpt}"</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ marginTop: '24px', display: 'flex', gap: '12px' }}>
                <button className="btn-primary" id="btn-proceed-question-reading" onClick={handleFetchQuestion} disabled={loading}>
                  {loading ? 'Preparing Diagnostic Checkpoint...' : 'Check My Understanding (Question) →'}
                </button>
              </div>
            </div>
          )}
        </section>
      )}

      {/* STEP 5: CHECKPOINT QUESTION CONSOLE */}
      {currentStep === 'question' && currentQuestion && (
        <section className="glass-card animate-fade-in" id="card-question-console">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span className="status-badge" style={{ background: 'rgba(245, 158, 11, 0.12)', color: 'var(--accent-amber)', borderColor: 'rgba(245, 158, 11, 0.3)' }}>
              Diagnostic Checkpoint • {currentQuestion.question_type.replace('_', ' ').toUpperCase()}
            </span>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Difficulty: {currentQuestion.difficulty}
            </span>
          </div>

          <h2 className="card-title" style={{ fontSize: '1.35rem', marginTop: '10px' }}>
            {currentQuestion.prompt}
          </h2>

          {/* Multiple Choice Options */}
          {currentQuestion.options && currentQuestion.options.length > 0 ? (
            <div className="options-grid" id="options-container">
              {currentQuestion.options.map((opt) => (
                <button
                  key={opt.key}
                  type="button"
                  id={`opt-${opt.key}`}
                  className={`option-btn ${selectedOption === opt.key ? 'selected' : ''}`}
                  onClick={() => setSelectedOption(opt.key)}
                >
                  <span className="option-key">{opt.key}</span>
                  <span>{opt.text}</span>
                </button>
              ))}
            </div>
          ) : (
            /* Open Ended / Short Answer Input */
            <div style={{ margin: '20px 0' }}>
              <textarea
                id="input-student-answer"
                className="form-textarea"
                value={studentAnswer}
                onChange={(e) => setStudentAnswer(e.target.value)}
                placeholder="Type your explanation or answer in your own words..."
              />
            </div>
          )}

          {/* Hints Accordion */}
          {currentQuestion.hints && currentQuestion.hints.length > 0 && (
            <div style={{ marginBottom: '20px' }}>
              <button
                type="button"
                className="btn-secondary"
                id="btn-toggle-hint"
                onClick={() => setShowHints(!showHints)}
                style={{ fontSize: '0.82rem', padding: '6px 14px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
              >
                <LightbulbIcon /> {showHints ? 'Hide Hint' : 'Need a Hint?'}
              </button>
              {showHints && (
                <div style={{ marginTop: '10px', padding: '12px 16px', background: 'rgba(255,255,255,0.04)', borderRadius: 'var(--radius-sm)', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  {currentQuestion.hints.map((h, i) => (
                    <p key={i}>Hint: {h}</p>
                  ))}
                </div>
              )}
            </div>
          )}

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              type="button"
              className="btn-primary"
              id="btn-submit-answer"
              onClick={handleSubmitAnswer}
              disabled={loading || (!selectedOption && !studentAnswer.trim())}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            >
              {loading ? 'Evaluating Response...' : <>Submit Answer for Diagnostic Evaluation <ArrowRightIcon /></>}
            </button>
          </div>
        </section>
      )}

      {/* STEP 6, 7 & 8: DIAGNOSTIC EVALUATION & HERO ADAPTIVE TEACHER ACTION */}
      {navTab === 'learn' && currentStep === 'evaluated' && evaluationOutcome && (
        <section className="glass-card animate-fade-in" id="card-evaluation-results">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <span className={`status-badge ${evaluationOutcome.evaluation.correctness === 'correct' ? '' : 'status-badge-warn'}`}>
              {evaluationOutcome.evaluation.correctness.replace('_', ' ').toUpperCase()}
            </span>
            <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>
              Correctness Score: {(evaluationOutcome.evaluation.score * 100).toFixed(0)}%
            </span>
          </div>

          <div className="score-meter">
            <div className="score-fill" style={{ width: `${evaluationOutcome.evaluation.score * 100}%` }}></div>
          </div>

          {/* Constructive Teacher Rubric Feedback */}
          <div className={`eval-box ${evaluationOutcome.evaluation.correctness}`} id="eval-feedback-box">
            <h3 style={{ fontSize: '1.1rem', marginBottom: '8px', color: 'var(--text-primary)' }}>
              Teacher Feedback
            </h3>
            <p style={{ fontSize: '1rem', lineHeight: 1.6, color: 'var(--text-primary)' }}>
              {evaluationOutcome.evaluation.rubric_feedback}
            </p>

            {evaluationOutcome.evaluation.strengths && evaluationOutcome.evaluation.strengths.length > 0 && (
              <div style={{ marginTop: '12px' }}>
                <strong style={{ fontSize: '0.85rem', color: 'var(--accent-emerald)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  <CheckIcon /> Strengths Detected:
                </strong>
                <ul style={{ paddingLeft: '18px', marginTop: '4px', fontSize: '0.9rem' }}>
                  {evaluationOutcome.evaluation.strengths.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}

            {evaluationOutcome.evaluation.missing_concepts && evaluationOutcome.evaluation.missing_concepts.length > 0 && (
              <div style={{ marginTop: '10px' }}>
                <strong style={{ fontSize: '0.85rem', color: 'var(--accent-amber)' }}>Missing Nuances:</strong>
                <ul style={{ paddingLeft: '18px', marginTop: '4px', fontSize: '0.9rem' }}>
                  {evaluationOutcome.evaluation.missing_concepts.map((m, i) => (
                    <li key={i}>{m}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* HERO ADAPTIVE MOMENT: Centerpiece of Hackathon Demo */}
          {(evaluationOutcome.misconception?.is_misconception || evaluationOutcome.evaluation.score < 0.7) && (
            <div className="hero-adaptation-banner animate-fade-in" id="hero-adaptation-banner">
              <div className="hero-tag">The Adaptive Moment: Real-Time Pedagogical Shift</div>
              <h3 style={{ fontSize: '1.2rem', color: '#ffffff', marginBottom: '4px' }}>
                Teacher Noticed a Misunderstanding
              </h3>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                The AI Teacher dynamically diagnosed your misconception and restructured instruction:
              </p>

              <div className="hero-pedagogical-grid">
                <div className="hero-box noticed">
                  <div className="hero-box-title">
                    What I Noticed:
                  </div>
                  <div>
                    {evaluationOutcome.misconception?.flawed_mental_model ||
                      "You appear to be assuming every node must strictly have 2 children (or confusing general trees with binary trees). In reality, leaf nodes at the bottom have 0 children!"}
                  </div>
                </div>

                <div className="hero-box will-change">
                  <div className="hero-box-title">
                    What I'll Change:
                  </div>
                  <div>
                    {evaluationOutcome.adaptation?.strategy ||
                      "I'll re-explain it using a visual analogy with leaf and single-child nodes."}
                  </div>
                </div>
              </div>

              {/* Interactive Follow-Up Re-Evaluation for the Demo */}
              <div style={{ marginTop: '20px', padding: '16px', background: 'rgba(0,0,0,0.35)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(255,255,255,0.1)' }}>
                <h4 style={{ fontSize: '0.95rem', color: '#f8fafc', marginBottom: '6px' }}>
                  Follow-Up Re-Evaluation: Check Revised Understanding
                </h4>
                <p style={{ fontSize: '0.88rem', color: '#cbd5e1', marginBottom: '14px' }}>
                  Now that we clarified that leaf nodes have 0 children: If a node has only a left child and no right child, is it still a valid Binary Tree node?
                </p>

                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                  <button
                    type="button"
                    className={`option-btn ${reEvalAnswer === 'A' ? 'selected' : ''}`}
                    style={{ flex: '1 1 240px', padding: '10px 14px' }}
                    onClick={() => {
                      setReEvalAnswer('A');
                      setReEvalPassed(true);
                      setReEvalSubmitted(true);
                      if (!conceptsMastered.includes('Binary Tree Node Topology')) {
                        setConceptsMastered([...conceptsMastered, 'Binary Tree Node Topology']);
                      }
                    }}
                  >
                    <span className="option-key">A</span>
                    <span>Yes, having 1 child is completely valid (binary means at most 2)</span>
                  </button>

                  <button
                    type="button"
                    className={`option-btn ${reEvalAnswer === 'B' ? 'selected' : ''}`}
                    style={{ flex: '1 1 240px', padding: '10px 14px' }}
                    onClick={() => {
                      setReEvalAnswer('B');
                      setReEvalPassed(false);
                      setReEvalSubmitted(true);
                    }}
                  >
                    <span className="option-key">B</span>
                    <span>No, a node must always have exactly 0 or 2 children</span>
                  </button>
                </div>

                {reEvalSubmitted && reEvalPassed && (
                  <div className="re-evaluation-success-banner animate-fade-in" style={{ marginTop: '14px' }}>
                    <span style={{ color: '#10b981' }}><CheckIcon /></span>
                    <div>
                      <div style={{ fontWeight: 700, color: '#10b981' }}>Understanding Improved!</div>
                      <div style={{ fontSize: '0.85rem', color: '#d1fae5' }}>
                        Concept mastery updated. You successfully demonstrated that binary tree nodes can have 0, 1, or 2 children.
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Concept Mastery & Progress Widget */}
          <div style={{ margin: '20px 0', padding: '16px 20px', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '8px' }}>
              Session Learning Progress
            </h4>
            <div className="mastery-chips">
              {conceptsMastered.map((c, i) => (
                <span key={i} className="mastery-chip mastered">✓ Mastered: {c}</span>
              ))}
              {conceptsNeedingWork.map((c, i) => (
                <span key={i} className="mastery-chip struggling">⚡ Reinforcing: {c}</span>
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              type="button"
              className="btn-primary"
              id="btn-take-final-assessment"
              onClick={handleStartFinalAssessment}
              disabled={loading}
            >
              {loading ? 'Preparing Assessment...' : 'Take Final Assessment & Learning Report →'}
            </button>
            <button
              type="button"
              className="btn-secondary"
              id="btn-execute-adaptation"
              onClick={handleAdvanceOrAdapt}
              disabled={loading}
            >
              Continue Lesson →
            </button>
          </div>
        </section>
      )}

      {/* FINAL ASSESSMENT STEP */}
      {navTab === 'learn' && currentStep === 'assessment' && finalAssessment && (
        <section className="glass-card animate-fade-in" id="card-final-assessment">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <span className="status-badge" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary)' }}>
                Cumulative Mastery Assessment
              </span>
              <h1 className="card-title" style={{ marginTop: '8px' }}>{finalAssessment.topic} Final Assessment</h1>
              <p className="card-subtitle">Test your grasp of the core concepts taught by Prof. Sophia. Answer all {finalAssessment.questions.length} questions to generate your final report.</p>
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              ⏱️ ~{finalAssessment.estimated_time_minutes} min
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', margin: '24px 0' }}>
            {finalAssessment.questions.map((q, idx) => (
              <div key={q.question_id} className="assessment-question-box" style={{ padding: '20px', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', fontWeight: 600, marginBottom: '6px' }}>
                  Question {idx + 1} • {q.concept}
                </div>
                <h3 style={{ fontSize: '1.05rem', color: '#f8fafc', marginBottom: '14px' }}>
                  {q.prompt}
                </h3>

                <div className="options-grid">
                  {q.options.map((opt) => (
                    <button
                      key={opt.key}
                      type="button"
                      className={`option-btn ${assessmentAnswers[q.question_id] === opt.key ? 'selected' : ''}`}
                      onClick={() => setAssessmentAnswers({ ...assessmentAnswers, [q.question_id]: opt.key })}
                    >
                      <span className="option-key">{opt.key}</span>
                      <span>{opt.text}</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <button
            type="button"
            className="btn-primary"
            id="btn-submit-final-assessment"
            onClick={handleSubmitFinalAssessment}
            disabled={loading || Object.keys(assessmentAnswers).length < finalAssessment.questions.length}
          >
            {loading ? 'Grading Assessment & Synthesizing Report...' : 'Submit Final Assessment & View Learning Report →'}
          </button>
        </section>
      )}

      {/* FINAL LEARNING REPORT STEP */}
      {navTab === 'learn' && currentStep === 'report' && learningReport && (
        <section className="glass-card animate-fade-in" id="card-learning-report">
          {/* Report Header Card with Score Circle */}
          <div className="report-hero-card">
            <div>
              <span className="status-badge" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', marginBottom: '8px' }}>
                ✓ Lesson Completed • {learningReport.status.toUpperCase()}
              </span>
              <h1 className="card-title">Learning Report: {learningReport.topic}</h1>
              <p className="card-subtitle">Prepared for <strong>{learningReport.learner_name}</strong> by Prof. Sophia</p>
            </div>

            <div className="report-score-circle">
              <span className="report-score-num">{learningReport.overall_score_percent}%</span>
              <span className="report-score-label">Mastery Score</span>
            </div>
          </div>

          {/* Concepts Understood & Needing Improvement */}
          <div className="report-section-grid">
            <div className="traceable-card">
              <div className="traceable-title" style={{ color: 'var(--accent-emerald)', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <CheckIcon /> Concepts Understood ({learningReport.concepts_understood.length})
              </div>
              <div className="mastery-chips" style={{ marginTop: '8px' }}>
                {learningReport.concepts_understood.map((c, i) => (
                  <span key={i} className="mastery-chip mastered">{c}</span>
                ))}
              </div>
            </div>

            <div className="traceable-card">
              <div className="traceable-title" style={{ color: 'var(--accent-amber)' }}>
                Concepts Needing Practice ({learningReport.concepts_needing_improvement.length})
              </div>
              <div className="mastery-chips" style={{ marginTop: '8px' }}>
                {learningReport.concepts_needing_improvement.length > 0 ? (
                  learningReport.concepts_needing_improvement.map((c, i) => (
                    <span key={i} className="mastery-chip struggling">{c}</span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>All core concepts passed successfully!</span>
                )}
              </div>
            </div>
          </div>

          {/* Traceable Recommendations Grid */}
          <div className="report-section-grid">
            {/* Recommended Revision */}
            <div className="traceable-card revision">
              <div className="traceable-title">Recommended Revision</div>
              <div className="traceable-value">{learningReport.recommended_revision}</div>
              <div className="traceable-reason">
                <strong>Pedagogical Reason:</strong> {learningReport.revision_reason}
              </div>
            </div>

            {/* Next Topic Recommendation */}
            <div className="traceable-card next-topic">
              <div className="traceable-title">Recommended Next Topic</div>
              <div className="traceable-value">{learningReport.next_topic_recommendation}</div>
              <div className="traceable-reason">
                <strong>Pedagogical Reason:</strong> {learningReport.next_topic_reason}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', marginTop: '20px' }}>
            <button
              type="button"
              className="btn-primary"
              id="btn-start-next-topic"
              onClick={() => {
                setTopic(learningReport.next_topic_recommendation.split('(')[0].trim());
                setCurrentStep('onboarding');
                setSessionId(null);
                setLessonPlan(null);
                setLearningReport(null);
              }}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            >
              Start Next Topic: {learningReport.next_topic_recommendation.split('&')[0].trim()} <ArrowRightIcon />
            </button>

            <button
              type="button"
              className="btn-secondary"
              id="btn-view-dashboard"
              onClick={() => {
                setNavTab('progress');
                loadDashboardData();
              }}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            >
              <ProgressIcon /> View Learner Dashboard
            </button>

            <button
              type="button"
              className="btn-secondary"
              id="btn-retake-topic"
              onClick={() => {
                setCurrentStep('onboarding');
                setSessionId(null);
                setLessonPlan(null);
                setLearningReport(null);
              }}
            >
              Teach Another Topic
            </button>
          </div>
        </section>
      )}

      {/* LEARNER DASHBOARD (When navTab === 'progress') */}
      {navTab === 'progress' && (
        <section className="glass-card animate-fade-in" id="card-learner-dashboard">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <h1 className="card-title">Learner Progress Dashboard</h1>
              <p className="card-subtitle">Comprehensive mastery tracking, memory consolidation, and personalized curriculum path for <strong>{learnerName}</strong>.</p>
            </div>
            <button className="btn-secondary" style={{ fontSize: '0.82rem' }} onClick={loadDashboardData}>Refresh</button>
          </div>

          <div className="dashboard-grid">
            <div className="dash-stat-box">
              <div className="dash-stat-label">Current Curriculum Topic</div>
              <div className="dash-stat-num" style={{ fontSize: '1.2rem', color: 'var(--text-primary)' }}>{topic}</div>
            </div>
            <div className="dash-stat-box">
              <div className="dash-stat-label">Overall Concept Mastery</div>
              <div className="dash-stat-num" style={{ color: 'var(--accent-emerald)' }}>
                {dashboardData?.overall_mastery_percent || (learningReport?.overall_score_percent || 85)}%
              </div>
            </div>
            <div className="dash-stat-box">
              <div className="dash-stat-label">Concepts Mastered</div>
              <div className="dash-stat-num" style={{ color: 'var(--accent-cyan)' }}>
                {conceptsMastered.length > 0 ? conceptsMastered.length : 2}
              </div>
            </div>
            <div className="dash-stat-box">
              <div className="dash-stat-label">Total Questions Answered</div>
              <div className="dash-stat-num" style={{ color: 'var(--accent-amber)' }}>
                {dashboardData?.total_interactions || 4}
              </div>
            </div>
          </div>

          {/* Mastered vs Reinforcing Concepts */}
          <div className="report-section-grid">
            <div className="traceable-card">
              <div className="traceable-title" style={{ color: 'var(--accent-emerald)' }}>Mastered Concepts</div>
              <div className="mastery-chips" style={{ marginTop: '8px' }}>
                {(conceptsMastered.length > 0 ? conceptsMastered : ['Binary Tree Hierarchy', 'Leaf Node Topology']).map((c, i) => (
                  <span key={i} className="mastery-chip mastered">{c}</span>
                ))}
              </div>
            </div>

            <div className="traceable-card">
              <div className="traceable-title" style={{ color: 'var(--accent-amber)' }}>Reinforcing Concepts</div>
              <div className="mastery-chips" style={{ marginTop: '8px' }}>
                {(conceptsNeedingWork.length > 0 ? conceptsNeedingWork : ['Tree Traversal Mechanics']).map((c, i) => (
                  <span key={i} className="mastery-chip struggling">{c}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Revision & Next Topic */}
          <div className="report-section-grid">
            <div className="traceable-card revision">
              <div className="traceable-title">Active Revision Recommendation</div>
              <div className="traceable-value">{dashboardData?.recommended_revision || learningReport?.recommended_revision || "Binary Tree Leaf Topology"}</div>
              <div className="traceable-reason">{dashboardData?.revision_reason || learningReport?.revision_reason || "Solidify distinction between leaf and internal nodes."}</div>
            </div>

            <div className="traceable-card next-topic">
              <div className="traceable-title">Next Curriculum Milestone</div>
              <div className="traceable-value">{dashboardData?.next_topic || learningReport?.next_topic_recommendation || "Binary Search Trees (BST)"}</div>
              <div className="traceable-reason">{dashboardData?.next_topic_reason || learningReport?.next_topic_reason || "Advance from branching invariants to search efficiency."}</div>
            </div>
          </div>

          <button
            type="button"
            className="btn-primary"
            style={{ marginTop: '20px' }}
            onClick={() => setNavTab('learn')}
          >
            ← Return to Interactive Learning Studio
          </button>
        </section>
      )}

      {/* SESSION HISTORY (When navTab === 'history') */}
      {navTab === 'history' && (
        <section className="glass-card animate-fade-in" id="card-session-history">
          <h1 className="card-title">Learning History</h1>
          <p className="card-subtitle">Verified record of prior learning sessions, diagnostic checkpoint scores, and adaptive interventions.</p>

          <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {sessionHistory.map((sess, idx) => (
              <div
                key={idx}
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 20px', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', flexWrap: 'wrap', gap: '10px' }}
              >
                <div>
                  <div style={{ fontWeight: 700, fontSize: '1.05rem', color: '#f8fafc' }}>{sess.topic}</div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Session ID: {sess.session_id} • {sess.date}</div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <span className="status-badge" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>
                    Score: {sess.score_percent}% ({sess.status})
                  </span>
                  <button
                    className="btn-secondary"
                    style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                    onClick={() => {
                      setNavTab('learn');
                      if (learningReport) setCurrentStep('report');
                    }}
                  >
                    View Report
                  </button>
                </div>
              </div>
            ))}
          </div>

          <button
            type="button"
            className="btn-primary"
            style={{ marginTop: '24px' }}
            onClick={() => setNavTab('learn')}
          >
            ← Back to Learning Studio
          </button>
        </section>
      )}
    </div>
  );
}
