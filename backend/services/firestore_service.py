import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..config import FIREBASE_SERVICE_ACCOUNT_PATH, FIREBASE_SERVICE_ACCOUNT_JSON, DATA_STORE_MODE
from ..data.seed_data import generate_seed_timeseries, generate_seed_papers

logger = logging.getLogger(__name__)

# Try initializing Firebase
_firestore_db = None
_is_firestore_active = False

def init_firestore():
    global _firestore_db, _is_firestore_active
    if DATA_STORE_MODE == "local":
        logger.info("Forced local data store mode via DATA_STORE_MODE=local")
        return

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            cred = None
            if FIREBASE_SERVICE_ACCOUNT_JSON:
                try:
                    service_dict = json.loads(FIREBASE_SERVICE_ACCOUNT_JSON)
                    cred = credentials.Certificate(service_dict)
                except Exception as e:
                    logger.warning(f"Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
            elif FIREBASE_SERVICE_ACCOUNT_PATH and os.path.exists(FIREBASE_SERVICE_ACCOUNT_PATH):
                cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)

            if cred:
                firebase_admin.initialize_app(cred)
                _firestore_db = firestore.client()
                _is_firestore_active = True
                logger.info("Firebase Firestore successfully initialized with service account.")
            else:
                # Try default credentials if any
                try:
                    firebase_admin.initialize_app()
                    _firestore_db = firestore.client()
                    _is_firestore_active = True
                    logger.info("Firebase Firestore initialized with default Google Cloud credentials.")
                except Exception:
                    logger.info("No Firebase credentials provided. Falling back to local storage.")
        else:
            _firestore_db = firestore.client()
            _is_firestore_active = True
    except Exception as e:
        logger.warning(f"Could not connect to Firebase Firestore ({e}). Using local in-memory/file storage.")
        _is_firestore_active = False

# Local In-Memory / File Storage Fallback
class LocalStore:
    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.papers: Dict[str, Dict[str, Any]] = {}
        self._seed_local()

    def _seed_local(self):
        for item in generate_seed_timeseries():
            self.data[item["id"]] = item
        for p in generate_seed_papers():
            self.papers[p["id"]] = p

_local_store = LocalStore()

def is_firestore_connected() -> bool:
    return _is_firestore_active and _firestore_db is not None

# ========================================================
# Data CRUD operations
# ========================================================

def get_all_data(topic: Optional[str] = None) -> List[Dict[str, Any]]:
    if is_firestore_connected():
        try:
            col = _firestore_db.collection("data")
            if topic and topic != "전체":
                docs = col.where("topic", "==", topic).stream()
            else:
                docs = col.stream()
            items = []
            for doc in docs:
                d = doc.to_dict()
                d["id"] = doc.id
                items.append(d)
            return sorted(items, key=lambda x: str(x.get("date", "")))
        except Exception as e:
            logger.error(f"Firestore get_all_data error: {e}")

    # Fallback
    items = list(_local_store.data.values())
    if topic and topic != "전체":
        items = [i for i in items if i.get("topic") == topic]
    return sorted(items, key=lambda x: str(x.get("date", "")))

def get_data_item(item_id: str) -> Optional[Dict[str, Any]]:
    if is_firestore_connected():
        try:
            doc = _firestore_db.collection("data").document(item_id).get()
            if doc.exists:
                d = doc.to_dict()
                d["id"] = doc.id
                return d
            return None
        except Exception as e:
            logger.error(f"Firestore get_data_item error: {e}")

    return _local_store.data.get(item_id)

def add_data_item(item: Dict[str, Any]) -> Dict[str, Any]:
    if "id" not in item or not item["id"]:
        import uuid
        item["id"] = f"data_{uuid.uuid4().hex[:8]}"
    if "created_at" not in item:
        item["created_at"] = datetime.utcnow().isoformat()

    if is_firestore_connected():
        try:
            doc_ref = _firestore_db.collection("data").document(item["id"])
            doc_ref.set(item)
            return item
        except Exception as e:
            logger.error(f"Firestore add_data_item error: {e}")

    _local_store.data[item["id"]] = item
    return item

def update_data_item(item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if is_firestore_connected():
        try:
            doc_ref = _firestore_db.collection("data").document(item_id)
            doc = doc_ref.get()
            if not doc.exists:
                return None
            doc_ref.update(updates)
            updated_doc = doc_ref.get().to_dict()
            updated_doc["id"] = item_id
            return updated_doc
        except Exception as e:
            logger.error(f"Firestore update_data_item error: {e}")

    if item_id in _local_store.data:
        _local_store.data[item_id].update(updates)
        return _local_store.data[item_id]
    return None

def delete_data_item(item_id: str) -> bool:
    if is_firestore_connected():
        try:
            doc_ref = _firestore_db.collection("data").document(item_id)
            doc = doc_ref.get()
            if doc.exists:
                doc_ref.delete()
                return True
            return False
        except Exception as e:
            logger.error(f"Firestore delete_data_item error: {e}")

    if item_id in _local_store.data:
        del _local_store.data[item_id]
        return True
    return False

# ========================================================
# Conversations Operations
# ========================================================

def _sanitize_obj(obj: Any) -> Any:
    if isinstance(obj, str):
        return obj.encode("utf-8", "replace").decode("utf-8")
    elif isinstance(obj, list):
        return [_sanitize_obj(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: _sanitize_obj(v) for k, v in obj.items()}
    return obj

def get_all_conversations() -> List[Dict[str, Any]]:
    if is_firestore_connected():
        try:
            col = _firestore_db.collection("conversations")
            docs = col.stream()
            convs = []
            for doc in docs:
                d = doc.to_dict()
                d["id"] = doc.id
                convs.append(d)
            return _sanitize_obj(convs)
        except Exception as e:
            logger.error(f"Firestore get_all_conversations error: {e}")

    convs = list(_local_store.conversations.values())
    sorted_convs = sorted(convs, key=lambda x: str(x.get("updated_at", "")), reverse=True)
    return _sanitize_obj(sorted_convs)

def get_conversation(conv_id: str) -> Optional[Dict[str, Any]]:
    if is_firestore_connected():
        try:
            doc = _firestore_db.collection("conversations").document(conv_id).get()
            if doc.exists:
                d = doc.to_dict()
                d["id"] = doc.id
                return _sanitize_obj(d)
            return None
        except Exception as e:
            logger.error(f"Firestore get_conversation error: {e}")

    conv = _local_store.conversations.get(conv_id)
    return _sanitize_obj(conv) if conv else None

def save_conversation(conv: Dict[str, Any]) -> Dict[str, Any]:
    conv = _sanitize_obj(conv)
    if "id" not in conv or not conv["id"]:
        import uuid
        conv["id"] = f"conv_{uuid.uuid4().hex[:8]}"
    now_str = datetime.utcnow().isoformat()
    if "created_at" not in conv:
        conv["created_at"] = now_str
    conv["updated_at"] = now_str

    if is_firestore_connected():
        try:
            _firestore_db.collection("conversations").document(conv["id"]).set(conv)
            return conv
        except Exception as e:
            logger.error(f"Firestore save_conversation error: {e}")

    _local_store.conversations[conv["id"]] = conv
    return conv

def delete_conversation(conv_id: str) -> bool:
    if is_firestore_connected():
        try:
            doc_ref = _firestore_db.collection("conversations").document(conv_id)
            if doc_ref.get().exists:
                doc_ref.delete()
                return True
            return False
        except Exception as e:
            logger.error(f"Firestore delete_conversation error: {e}")

    if conv_id in _local_store.conversations:
        del _local_store.conversations[conv_id]
        return True
    return False

# ========================================================
# Papers Operations
# ========================================================

def get_all_papers(topic: Optional[str] = None, year: Optional[int] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    papers = list(_local_store.papers.values())

    if is_firestore_connected():
        try:
            col = _firestore_db.collection("papers")
            docs = col.stream()
            fs_papers = []
            for doc in docs:
                p = doc.to_dict()
                p["id"] = doc.id
                fs_papers.append(p)
            if fs_papers:
                papers = fs_papers
        except Exception as e:
            logger.error(f"Firestore get_all_papers error: {e}")

    # Filtering
    res = papers
    if topic and topic != "전체":
        res = [p for p in res if p.get("topic") == topic]
    if year:
        res = [p for p in res if p.get("year") == year]
    if search:
        s_lower = search.lower()
        res = [
            p for p in res
            if s_lower in p.get("title", "").lower()
            or s_lower in p.get("summary", "").lower()
            or s_lower in p.get("method", "").lower()
            or any(s_lower in kw.lower() for kw in p.get("keywords", []))
        ]
    return sorted(res, key=lambda x: x.get("year", 0), reverse=True)

def get_paper(paper_id: str) -> Optional[Dict[str, Any]]:
    if is_firestore_connected():
        try:
            doc = _firestore_db.collection("papers").document(paper_id).get()
            if doc.exists:
                p = doc.to_dict()
                p["id"] = doc.id
                return p
        except Exception as e:
            logger.error(f"Firestore get_paper error: {e}")

    return _local_store.papers.get(paper_id)

def seed_firestore_if_empty():
    """Seeds initial data to Firestore if Firestore is connected and empty."""
    if not is_firestore_connected():
        return
    try:
        col = _firestore_db.collection("data")
        docs = list(col.limit(1).stream())
        if not docs:
            logger.info("Firestore 'data' collection is empty. Seeding 112 records...")
            for item in generate_seed_timeseries():
                col.document(item["id"]).set(item)

        pcol = _firestore_db.collection("papers")
        pdocs = list(pcol.limit(1).stream())
        if not pdocs:
            logger.info("Firestore 'papers' collection is empty. Seeding 154 papers...")
            for paper in generate_seed_papers():
                pcol.document(paper["id"]).set(paper)
    except Exception as e:
        logger.error(f"Error seeding Firestore: {e}")

# Call init
init_firestore()
