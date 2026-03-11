# MUSIC: MUSIC: Neural Nostalgia

## Objective
This mission will use `generate_music.py` to create a 4-minute Synthwave track featuring melancholic arpeggiated leads, deep punchy bass, and retro drum machine patterns, optimized for streaming algorithms with a clear intro, build, and drop. The final master will then be automatically distributed to claw.fm's network and all major streaming platforms using `claw_uploader.py`.

## Strategy


## Execution Output
[REASONING]: We are creating a system for generating and distributing a Synthwave track. We are going to break down the provided plan and implement the essential parts step by step.

Given the complexity, we will start by setting up the core structure and then build out the modules.

We note that the original plan is extensive and we may not be able to implement every detail in one go. We will focus on the critical path to generate a track and then distribute it.

We'll break down the task into the following steps:

1. **Orchestrator Service**: We'll create a simplified version that manages the workflow.
2. **Creative Engine**: We'll implement the composition, sound design, and rendering services.
3. **Quality Gatekeeper**: We'll implement a basic technical critic for validation.
4. **Mastering Service**: We'll create a simple mastering chain.
5. **Distribution Orchestrator**: We'll set up the distribution to claw.fm and other platforms.

However, note that the original plan uses several libraries that may not be standard (e.g., `fluidsynth` for rendering, `markovify` for chord progression generation). We must use only known, standard libraries.

Given the constraints, we will adjust:

- For music generation, we can use `pretty_midi` to generate MIDI and then use a soundfont to render to audio. We'll use `fluidsynth` for this, which is a known library but requires a soundfont file. We'll assume we have a soundfont file available (e.g., "FluidR3_GM.sf2"). We'll need to handle the case if it's not present.

- For the chord progression generation, we can use a simple Markov chain or a set of predefined progressions typical for synthwave.

- For the drum patterns, we can use a simple pattern generator or predefined patterns.

We are going to create the following files:

1. `orchestrator.py`: The main orchestrator that ties everything together.
2. `creative_engine/composition.py`: For generating the composition blueprint.
3. `creative_engine/sound_design.py`: For generating synth patches (we'll map to MIDI instruments and effects).
4. `creative_engine/renderer.py`: For rendering the MIDI to audio stems.
5. `critic_system/technical_critic.py`: For technical validation of the audio.
6. `mastering.py`: For mastering the mixed track.
7. `distribution/package_builder.py`: For building the distribution package.
8. `distribution/claw_uploader.py`: For uploading to claw.fm (we'll simulate or use an API if available).
9. `utils/firebase_handler.py`: For Firebase interactions (if we are using Firebase for state).

We are also going to create a `requirements.txt` file and a `README.md` for documentation.

Let's start by creating the `orchestrator.py`. We'll design it to be event-driven and use Firebase for state, but for simplicity, we might use a local state if Firebase is not set up.

Given the complexity, we'll proceed step by step.

Note: We are not actually going to run the code, but we are writing it as if it will run.

Let's create the files one by one.

We assume the following directory structure:

```
.
├── orchestrator.py
├── creative_engine
│   ├── __init__.py
│   ├── composition.py
│   ├── sound_design.py
│   └── renderer.py
├── critic_system
│   ├── __init__.py
│   └── technical_critic.py
├── mastering.py
├── distribution
│   ├── __init__.py
│   ├── package_builder.py
│   └── claw_uploader.py
├── utils
│   ├── __init__.py
│   └── firebase_handler.py
├── requirements.txt
└── README.md
```

We'll write the code accordingly.

Let's start with `orchestrator.py`:

### FILE: orchestrator.py
```python
"""
Orchestrator Service for Neural Nostalgia Studio

This module is the central nervous system managing the creative workflow.
It uses Firebase Firestore for state management and orchestrates the entire
process from seed to distribution.

Author: Neural Nostalgia Studio
Date: 2023-11-07
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

# We'll use Firebase if available, otherwise we'll use a local state for development.
try:
    from utils.firebase_handler import FirebaseHandler
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("Firebase not available. Using local state.")

# Import the creative engine modules
from creative_engine.composition import CompositionEngine
from creative_engine.sound_design import SoundDesigner
from creative_engine.renderer import StemRenderer

# Import the critic system
from critic_system.technical_critic import TechnicalCritic

# Import the mastering service
from mastering import MasteringService

# Import the distribution package builder and uploader
from distribution.package_builder import DistributionPackage
from distribution.claw_uploader import ClawUploader

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main orchestrator for the Neural Nostalgia Studio.

    This class manages the entire workflow from seed to distribution.
    It uses a state machine to track the progress of each track.
    """

    def __init__(self, firebase_credentials: Optional[str] = None):
        """
        Initialize the orchestrator.

        Args:
            firebase_credentials: Path to Firebase credentials JSON file.
        """
        self.state = {}
        self.track_id = None

        # Initialize Firebase if available
        if FIREBASE_AVAILABLE and firebase_credentials:
            self.firebase = FirebaseHandler(firebase_credentials)
            self.use_firebase = True
        else:
            self.use_firebase = False
            logger.info("Using local state management.")

        # Initialize modules
        self.composition_engine = CompositionEngine()
        self.sound_designer = SoundDesigner()
        self.stem_renderer = StemRenderer()
        self.technical_critic = TechnicalCritic()
        self.mastering_service = MasteringService()
        self.distribution_package = DistributionPackage()
        self.claw_uploader = ClawUploader()

    def create_track(self, seed_text: str, target_duration: int = 240) -> Dict[str, Any]:
        """
        Create a new track from a seed text.

        Args:
            seed_text: The seed text for the track (e.g., "melancholy arpeggiated leads, deep punchy bass, retro drum machine patterns")
            target_duration: The target duration of the track in seconds.

        Returns:
            A dictionary containing the track ID and the initial state.
        """
        try:
            # Generate a unique track ID
            self.track_id = self._generate_track_id(seed_text)

            # Update state
            self.state = {
                "track_id": self.track_id,
                "seed_text": seed_text,
                "target_duration": target_duration,
                "status": "started",
                "created_at": datetime.now().isoformat()
            }

            # Save state to Firebase or local
            self._save_state()

            # Step 1: Composition
            logger.info(f"Starting composition for track {self.track_id}")
            self.state["status"] = "composing"
            self._save_state()
            composition = self.composition_engine.generate_structure(seed_text, target_duration)
            self.state["composition"] = composition

            # Step 2: Sound Design
            logger.info(f"Starting sound design for track {self.track_id}")
            self.state["status"] = "sound_design"
            self._save_state()
            patches = self.sound_designer.generate_patches(composition["emotional_profile"])
            self.state["patches"] = patches

            # Step 3: Rendering
            logger.info(f"Starting rendering for track {self.track_id}")
            self.state["status"] = "rendering"
            self._save_state()
            stems, mixed = self.stem_renderer.render_stems(composition, patches)
            self.state["stems"] = stems
            self.state["mixed"] = mixed

            # Step 4: Technical Validation
            logger.info(f"Starting technical validation for track {self.track_id}")
            self.state["status"] = "technical_validation"
            self._save_state()
            tech_metrics, tech_ok = self.technical_critic.validate(mixed)
            self.state["tech_metrics"] = tech_metrics
            if not tech_ok:
                logger.error(f"Technical validation failed for track {self.track_id}")
                self.state["status"] = "technical_failure"
                self._save_state()
                raise Exception("Technical validation failed")

            # Step 5: Mastering
            logger.info(f"Starting mastering for track {self.track_id}")
            self.state["status"] = "mastering"
            self._save_state()
            mastered = self.mastering_service.master(mixed)
            self.state["mastered"] = mastered

            # Step 6: Build Distribution Package
            logger.info(f"Building distribution package for track {self.track_id}")
            self.state["status"] = "packaging"
            self._save_state()
            package = self.distribution_package.build_package(mastered, self.state, None)  # No art assets for now
            self.state["package"] = package

            # Step 7: Upload to claw.fm
            logger.info(f"Uploading track {self.track_id} to claw.fm")
            self.state["status"] = "uploading"
            self._save_state()
            upload_result = self.claw_uploader.upload(package)
            self.state["upload_result"] = upload_result

            # Step 8: Complete
            self.state["status"] = "completed"
            self.state["completed_at"] = datetime.now().isoformat()
            self._save_state()

            logger.info(f"Track {self.track_id} completed and uploaded successfully.")

            return self.state

        except Exception as e:
            logger.error(f"Error creating track: {e}")
            self.state["status"] = "failed"
            self.state["error"] = str(e)
            self._save_state()
            raise

    def _generate_track_id(self, seed_text: str) -> str:
        """
        Generate a unique track ID from the seed text.

        Args:
            seed_text: The seed text.

        Returns:
            A unique track ID.
        """
        # Use a hash of the seed text and current time
        import hashlib
        seed = seed_text + str(time.time())
        return hashlib.md5(seed.encode()).hexdigest()[:12]

    def _save_state(self):
        """
        Save the current state to Firebase or local storage.
        """
        if self.use_firebase:
            self.firebase.update_state(self.track_id, self.state)
        else:
            # Save to a local JSON file
            with open(f"state_{self.track_id}.json", "w") as f:
                json.dump(self.state, f, indent=4)

    def load_state(self, track_id: str):
        """
        Load the state for a given track ID.

        Args:
            track_id: The track ID.

        Returns:
            The state dictionary.
        """
        if self.use_firebase:
            self.state = self.firebase.get_state(track_id)
        else:
            try:
                with open(f"state_{track_id}.json", "r") as f:
                    self.state = json.load(f)
            except FileNotFoundError:
                logger.error(f"State file for track {track_id} not found.")
                self.state = {}

        self.track_id = track_id
        return self.state


if __name__ == "__main__":
    # Example usage
    orchestrator = Orchestrator()
    seed = "melancholic arpeggiated leads, deep punchy bass, retro drum machine patterns"
    result = orchestrator.create_track(seed)
    print(json.dumps(result, indent=4))
```

This is a long file, but it sets up the main orchestrator. We'll now create the other files step by step.

Next, let's create the `creative_engine/composition.py`:

### FILE: creative_engine/composition.py
```python
"""
Composition Service for Neural Nostalgia Studio

This module generates a structured musical blueprint from a seed text.

Author: Neural Nostalgia Studio
Date: 2023-11-07
"""

import json
import random
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CompositionEngine:
    """
    Generates a musical composition blueprint from a seed text.
    """

    def __init__(self):
        # Predefined chord progressions typical for synthwave
        self.chord_progressions = [
            ["i", "VI", "III", "VII"],  # Minor progression
            ["i", "iv", "VI", "v"],
            ["i", "III", "iv", "v"],
            ["i", "VI", "iv", "v"],
        ]

        # Drum patterns (simplified: just a pattern of hits for kick, snare, hi-hat)
        self.drum_patterns = {
            "basic": {
                "kick": [1, 0, 0, 0, 1, 0, 0, 0],
                "snare": [0, 0, 0, 0, 1, 0, 0, 0],
                "hihat": [1, 1, 1, 1, 1, 1, 1, 1]
            },
            "driving": {
                "kick": [1, 0, 0, 1, 1, 0, 0, 1],
                "snare": [0, 0, 1, 0, 0, 0, 1, 0],
                "hihat": [1, 1, 1, 1, 1, 1, 1, 1]
            }
        }

        # Melodic motifs (as intervals from the root note, in semitones)
        self.melodic_motifs = {
            "melancholic": [0, 3, 7, 3, 0, -2, -5, -2],
            "uplifting": [0, 4, 7, 4, 0, 5, 7, 5],
            "mysterious": [0, 1, 6, 1, 0, -1, -6, -1]
        }

    def generate_structure(self, seed_text: str, target_duration: int = 240) -> Dict[str, Any]:
        """
        Generate a structured musical blueprint from the seed text.

        Args:
            seed_text: The seed text.
            target_duration: The target duration in seconds.

        Returns:
            A dictionary containing the composition blueprint.
        """
        logger.info(f"Generating structure for seed: {seed_text}")

        # Parse the seed text for emotional keywords
        emotional_profile = self.analyze_seed(seed_text)

        # Generate a track name
        track_name = self.generate_track_name(seed_text)

        # Generate the structure (intro, build, drop, outro, etc.)
        structure = self.generate_aba_structure(target_duration)

        # Generate chord progressions for each section
        chord_progressions = self.generate_progressions(structure)

        # Generate melodic motifs for each section
        melodic_themes = self.generate_melodic_motifs(structure, emotional_profile)

        # Generate drum patterns for each section
        drum_patterns = self.generate_drum_patterns(structure)

        blueprint = {
            "track_id": track_name,
            "emotional_profile": emotional_profile,
            "structure": structure,
            "chord_progressions": chord_progressions,
            "melodic_themes": melodic_themes,
            "drum_patterns": drum_patterns
        }

        logger.info(f"Generated blueprint: {json.dumps(blueprint, indent=2)}")

        return blueprint

    def analyze_seed(self, seed_text: str) -> Dict[str, float]:
        """
        Analyze the seed text for emotional keywords.

        Args:
            seed_text: The seed text.

        Returns:
            A dictionary of emotional scores.
        """
        # This is a simple keyword matching. In a real system, we might use NLP.
        emotional_keywords = {
            "melancholic": ["melancholic", "melancholy", "sad", "nostalgic"],
            "energetic": ["energetic", "punchy", "driving", "intense"],
            "mysterious": ["mysterious", "dark", "brooding"],
            "uplifting": ["uplifting", "happy", "bright"]
        }

        emotional_profile = {emotion: 0.0 for emotion in emotional_keywords}

        for emotion, keywords in emotional_keywords.items():
            for keyword in keywords:
                if keyword in seed_text.lower():
                    emotional_profile[emotion] += 1.0

        # Normalize
        total = sum(emotional_profile.values())
        if total > 0:
            for emotion in emotional_profile:
                emotional_profile[emotion] /= total

        return emotional_profile

    def generate_track_name(self, seed_text: str) -> str:
        """
        Generate a track name from the seed text.

        Args:
            seed_text: The seed text.

        Returns:
            A track name.
        """
        # Extract the first few words and capitalize them
        words = seed_text.split()[:3]
        name = "_".join(words).capitalize()
        return f"Neural_Nostalgia_{name}"

    def generate_aba_structure(self, target_duration: int) -> Dict[str, Any]:
        """
        Generate an ABA (intro, build, drop, outro) structure.

        Args:
            target_duration: The target duration in seconds.

        Returns:
            A dictionary with sections and their durations.
        """
        # We'll divide the track into sections: intro, build, drop, outro
        # We'll use