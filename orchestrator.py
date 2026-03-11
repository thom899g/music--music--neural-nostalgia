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