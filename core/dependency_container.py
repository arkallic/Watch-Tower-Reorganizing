# core/dependency_container.py
import os  # You correctly added this!
from typing import Dict, Any
from colorama import Fore, Style

# Import all components
from .config_manager import ConfigManager
from utils.logger import Logger
from utils.report_generator import ReportGenerator
from utils.data_persistence import DataPersistence
from integrations.ollama_client import OllamaClient
from integrations.modstring_manager import ModStringManager
from managers.moderation import ModerationManager
from managers.psychosis_manager import PsychosisManager
from managers.deleted_message_logger import DeletedMessageLogger
from managers.activity_tracker import ActivityTracker
from commands.bot_commands import BotCommands
from managers.audit_logger import AuditLogger

class DependencyContainer:
    """Centralized dependency injection container"""

    def __init__(self):
        self.dependencies = {}
        self.initialized = False
        # --- THIS IS THE FIX ---
        # This code runs when a DependencyContainer object is created.
        # It defines the file paths needed by the managers.
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.script_dir, "data")
        # ------------------------

    def initialize_all_dependencies(self):
        """Initialize all core dependencies"""
        try:
            print(f"{Fore.CYAN}🔧 Initializing dependencies...{Style.RESET_ALL}")

            # Core systems
            self.dependencies['config'] = ConfigManager()
            self.dependencies['logger'] = Logger()
            self.dependencies['data_persistence'] = DataPersistence()

            # Import and store bot_settings
            try:
                from core.settings import bot_settings
                self.dependencies['bot_settings'] = bot_settings
                print(f"{Fore.GREEN}✅ bot_settings imported and stored{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ Failed to import bot_settings: {e}{Style.RESET_ALL}")

            # Integrations
            self.dependencies['ollama'] = OllamaClient()
            self.dependencies['modstring_manager'] = ModStringManager(
                None,  # Bot will be injected later
                self.dependencies['data_persistence']
            )

            # --- THIS SECTION IS ALSO CORRECTED ---
            # Managers
            # 1. Create the AuditLogger instance first, using the self.data_dir we just defined.
            self.dependencies['audit_logger'] = AuditLogger(data_dir=self.data_dir)

            # 2. Now create the ModerationManager.
            self.dependencies['moderation_manager'] = ModerationManager(
                self.dependencies['config'],
                self.dependencies['logger']
            )
            # ------------------------------------

            self.dependencies['psychosis_manager'] = PsychosisManager(
                self.dependencies['config'],
                self.dependencies['logger']
            )

            self.dependencies['deleted_message_logger'] = DeletedMessageLogger()
            self.dependencies['activity_tracker'] = ActivityTracker()

            # Report generator (depends on moderation manager)
            self.dependencies['report_generator'] = ReportGenerator(
                self.dependencies['moderation_manager']
            )

            self.initialized = True
            print(f"{Fore.GREEN}✅ Core dependencies initialized{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}❌ Dependency initialization failed: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            raise

    def initialize_bot_dependent_components(self, bot):
        """Initialize components that require the bot instance"""
        try:
            # Update ModString manager with bot reference
            self.dependencies['modstring_manager'].bot = bot

            # Initialize commands system
            self.dependencies['bot_commands'] = BotCommands(
                bot,
                self.dependencies['config'],
                self.dependencies['logger'],
                self.dependencies['moderation_manager'],
                self.dependencies['report_generator'],
                self.dependencies['psychosis_manager'],
                self.dependencies['deleted_message_logger']
            )

            print(f"{Fore.GREEN}✅ Bot-dependent components initialized{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}❌ Bot-dependent initialization failed: {e}{Style.RESET_ALL}")
            raise

    def get_dependency(self, name: str):
        """Get a specific dependency"""
        return self.dependencies.get(name)

    def get_all_dependencies(self) -> Dict[str, Any]:
        """Get all dependencies"""
        return self.dependencies.copy()

    def is_initialized(self) -> bool:
        """Check if container is initialized"""
        return self.initialized