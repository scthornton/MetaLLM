"""
Target Definitions

Classes representing different types of attack targets.
"""

from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, field


class TargetType(str, Enum):
    """Types of targets"""
    LLM = "llm"
    RAG = "rag"
    AGENT = "agent"
    MLOPS = "mlops"
    API = "api"
    NETWORK = "network"


@dataclass
class Target:
    """
    Base target class

    Example:
        target = Target(
            type=TargetType.LLM,
            endpoint="https://api.openai.com/v1/chat/completions",
            metadata={"model": "gpt-4"}
        )
    """
    type: TargetType
    endpoint: str
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing"""
        if self.name is None:
            self.name = self.endpoint

    def __str__(self) -> str:
        return f"{self.type.value}://{self.endpoint}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "name": self.name,
            "endpoint": self.endpoint,
            "description": self.description,
            "metadata": self.metadata,
        }


@dataclass
class LLMTarget(Target):
    """
    Large Language Model target

    Example:
        target = LLMTarget(
            endpoint="https://api.openai.com/v1/chat/completions",
            model_name="gpt-4",
            provider="openai",
            api_key="sk-...",
            system_prompt="You are a helpful assistant"
        )
    """
    model_name: Optional[str] = None
    provider: Optional[str] = None  # openai, anthropic, local, etc.
    api_key: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    def __post_init__(self):
        """Set type and initialize"""
        self.type = TargetType.LLM
        super().__post_init__()
        if self.model_name:
            self.metadata["model"] = self.model_name
        if self.provider:
            self.metadata["provider"] = self.provider


@dataclass
class RAGTarget(Target):
    """
    Retrieval-Augmented Generation target

    Example:
        target = RAGTarget(
            endpoint="http://localhost:8000",
            vector_db_type="chromadb",
            vector_db_endpoint="http://localhost:8001",
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            ingestion_endpoint="http://localhost:8000/ingest"
        )
    """
    vector_db_type: Optional[str] = None  # chromadb, pinecone, weaviate
    vector_db_endpoint: Optional[str] = None
    embedding_model: Optional[str] = None
    ingestion_endpoint: Optional[str] = None
    collection_name: Optional[str] = None

    def __post_init__(self):
        """Set type and initialize"""
        self.type = TargetType.RAG
        super().__post_init__()
        if self.vector_db_type:
            self.metadata["vector_db"] = self.vector_db_type


@dataclass
class AgentTarget(Target):
    """
    AI Agent framework target

    Example:
        target = AgentTarget(
            endpoint="http://localhost:8080",
            framework="langchain",
            agent_type="react",
            tools=["calculator", "search", "terminal"]
        )
    """
    framework: Optional[str] = None  # langchain, crewai, autogpt, custom
    agent_type: Optional[str] = None
    tools: list = field(default_factory=list)
    memory_type: Optional[str] = None

    def __post_init__(self):
        """Set type and initialize"""
        self.type = TargetType.AGENT
        super().__post_init__()
        if self.framework:
            self.metadata["framework"] = self.framework


@dataclass
class MLOpsTarget(Target):
    """
    MLOps infrastructure target

    Example:
        target = MLOpsTarget(
            endpoint="http://localhost:5000",
            platform="mlflow",
            version="2.8.0",
            features=["tracking", "registry", "serving"]
        )
    """
    platform: Optional[str] = None  # jupyter, mlflow, wandb, registry
    version: Optional[str] = None
    auth_required: bool = False
    features: list = field(default_factory=list)

    def __post_init__(self):
        """Set type and initialize"""
        self.type = TargetType.MLOPS
        super().__post_init__()
        if self.platform:
            self.metadata["platform"] = self.platform


@dataclass
class Auth:
    """
    Authentication credentials for targets

    Example:
        auth = Auth(
            type="bearer",
            token="sk-...",
            username="admin",
            password="password123"
        )
    """
    type: str  # bearer, basic, api_key, custom
    token: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        headers = self.headers.copy()

        if self.type == "bearer" and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.type == "api_key" and self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.type == "basic" and self.username and self.password:
            import base64
            credentials = f"{self.username}:{self.password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"

        return headers
