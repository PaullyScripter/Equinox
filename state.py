import discord
from discord.ui import View, Modal, Button, Select, TextInput
from typing import Optional, Any, Dict, List, Tuple
from collections import deque

# ── Bot / Client ──
client: discord.Client = None
PREFIX: str = "/"

# ── Config / Constants ──
devs: List[int] = []
IGNORED_USER_IDS: set = set()
SUB_FILES: Dict[str, str] = {}
PRIVACY_SET: set[int] = set()
STATUS_PRIVACY_SET: set[int] = set()
SUPPORTED_FIAT: set = set()
SYMBOL_TO_ID: Dict[str, str] = {}
SUPPORTED_CHAINS: set = set()
COLOR_OK: int = 0x57F287
COLOR_WARN: int = 0xFEE75C
COLOR_BAD: int = 0xED4245
COLOR_INFO: int = 0xFFFFFF
CODEBLOCK_CLOSED_RE: re.Pattern = None
CODEBLOCK_UNTERMINATED_RE: re.Pattern = None
DURATION_RE: re.Pattern = None

# ── Data ──
pending_alerts: Dict = {}
user_graph_data: Dict = {}
dictionary: object = None
char1: List[str] = []

# ── View / UI Classes (set by main.py at startup) ──
FlexButton: type[View] = None
BuyPremium: type[View] = None
DaysBetweenButton: type[View] = None
myInvite: type[View] = None
Mymodal: type[Modal] = None
AuthButton: type[View] = None
LoginModal: type[Modal] = None
ResetButton: type[View] = None
NumbersButton: type[View] = None
VerifyButton: type[View] = None
DeleteVerifySystem: type[View] = None
EmailCheck: type[View] = None
EmailCode: type[View] = None
UnbanButton: type[View] = None
DefineButton: type[View] = None
RawCopyButton: type[View] = None
WikipediaButton: type[View] = None
CloneButton: type[View] = None
rrSelectGames: type[View] = None
rrSelectGender: type[View] = None
rrSelectPing: type[View] = None
rrSelectServer: type[View] = None
Paginator: type[View] = None
mySelect: type[View] = None
CurrencyView: type[View] = None
PaginationView: type[View] = None
PromptModal: type[Modal] = None
PromptButtonView: type[View] = None
GeminiView: type[View] = None
RemoveGeminiView: type[View] = None
DeployView: type[View] = None
DropView: type[View] = None
GraphView: type[View] = None
FunctionInputModal: type[Modal] = None
DeleteFunctionModal: type[Modal] = None
ZoomModal: type[Modal] = None
UpdateButton: type[View] = None
ScamFeedbackView: type[View] = None
YoungestView: type[View] = None
MemberStatsView: type[View] = None
PresencePaginator: type[View] = None
ReactionRoleView: type[View] = None
BuyPremium2: type[View] = None

# ── Functions (set by main.py at startup) ──
def read_json(filename): raise RuntimeError("state not initialized")
def write_json(data, filename): raise RuntimeError("state not initialized")
def refresh(): raise RuntimeError("state not initialized")
async def is_premium(discord_id): raise RuntimeError("state not initialized")
def format_expires(expires): raise RuntimeError("state not initialized")
def load_json(path): raise RuntimeError("state not initialized")
def save_json(path, data): raise RuntimeError("state not initialized")
def load_stats(): raise RuntimeError("state not initialized")
def save_stats(data): raise RuntimeError("state not initialized")
def _log_command(user_id, command_name): raise RuntimeError("state not initialized")
def load_autoping_channels(guild_id): raise RuntimeError("state not initialized")
def save_autoping_channels(guild_id, channels): raise RuntimeError("state not initialized")
def load_autorole(guild_id): raise RuntimeError("state not initialized")
def save_autorole(guild_id, role_id): raise RuntimeError("state not initialized")
def remove_autorole(guild_id): raise RuntimeError("state not initialized")
def load_privacy_settings(): raise RuntimeError("state not initialized")
def save_privacy_settings(data): raise RuntimeError("state not initialized")
def reload_privacy_sets(): raise RuntimeError("state not initialized")
def load_server_data(guild_id): raise RuntimeError("state not initialized")
def save_server_data(guild_id, data): raise RuntimeError("state not initialized")
def load_gemini_servers(): raise RuntimeError("state not initialized")
def save_gemini_servers(data): raise RuntimeError("state not initialized")
def load_actions(): raise RuntimeError("state not initialized")
def save_actions(data): raise RuntimeError("state not initialized")
def append_audit_log(guild_id, entry): raise RuntimeError("state not initialized")
def read_audit_log(guild_id): raise RuntimeError("state not initialized")
def load_audit_config(): raise RuntimeError("state not initialized")
def save_audit_config(data): raise RuntimeError("state not initialized")
def get_guild_cfg(guild_id): raise RuntimeError("state not initialized")
def update_guild_cfg(guild_id, **patch): raise RuntimeError("state not initialized")
def embed_basic(title, description, color): raise RuntimeError("state not initialized")
def admin_or_manage_guild(interaction): raise RuntimeError("state not initialized")
def normalize_phrase(text): raise RuntimeError("state not initialized")
def extract_domains(text): raise RuntimeError("state not initialized")
def scan_message_for_scams(content, cfg): raise RuntimeError("state not initialized")
def try_python_syntax_check(code): raise RuntimeError("state not initialized")
def parse_duration_to_timedelta(s): raise RuntimeError("state not initialized")
def fmt_discord_time(dt): raise RuntimeError("state not initialized")
def _chunk_lines(lines, size): raise RuntimeError("state not initialized")
def build_overview_embed(guild, members): raise RuntimeError("state not initialized")
def is_scam_whitelisted(member, cfg): raise RuntimeError("state not initialized")
def fetch_tx_data(chain, txid): raise RuntimeError("state not initialized")
def parse_tx_data(chain, data): raise RuntimeError("state not initialized")
def fetch_word_example(word): raise RuntimeError("state not initialized")
def generate_graph(user_id, zoom_factor): raise RuntimeError("state not initialized")
def replenish_codes(tier, count): raise RuntimeError("state not initialized")
def _load_codes_for_tier(t): raise RuntimeError("state not initialized")
def _as_txt_file(filename, codes): raise RuntimeError("state not initialized")
def remove_subscription(user_id, tier): raise RuntimeError("state not initialized")
def add_subscription(user_id, tier, code): raise RuntimeError("state not initialized")
def build_top_roles_embed(guild, members, page): raise RuntimeError("state not initialized")
def build_age_graph(members): raise RuntimeError("state not initialized")
def init_db_pool(min_size, max_size): raise RuntimeError("state not initialized")
def load_data(): raise RuntimeError("state not initialized")
