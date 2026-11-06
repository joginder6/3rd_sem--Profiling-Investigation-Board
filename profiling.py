import sqlite3
import random
import streamlit as st
from abc import ABC, abstractmethod
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="NULLTRACER // INVESTIGATION BOARD",
    page_icon="📌",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HANDLE EVIDENCE DELETION VIA QUERY PARAM ---
if "delete_log" in st.query_params:
    try:
        del_log_id = int(st.query_params["delete_log"])
        conn = sqlite3.connect("nulltracer.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM evidence_logs WHERE log_id = ?", (del_log_id,))
        conn.commit()
        conn.close()
        st.query_params.clear()
        st.rerun()
    except Exception:
        pass

# --- DARK CORKBOARD & NETFLIX FORENSIC STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Courier+Prime:wght@400;700&family=Permanent+Marker&display=swap');

    /* Balanced Dark Corkboard Background */
    .stApp {
        background-color: #613e24 !important;
        background-image: 
            radial-gradient(#4a2e19 15%, transparent 16%), 
            radial-gradient(#382212 15%, transparent 16%),
            radial-gradient(circle at center, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.55) 100%);
        background-size: 20px 20px, 20px 20px, 100% 100%;
        background-position: 0 0, 10px 10px, 0 0;
        color: #e2e8f0;
        font-family: 'Courier Prime', monospace;
    }

    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding: 1rem 1.5rem 1.5rem 1.5rem !important; max-width: 100% !important; }

    /* Distinct Corkboard Section Column Containers */
    [data-testid="column"] {
        background: rgba(18, 11, 6, 0.65);
        border: 1px solid rgba(133, 92, 54, 0.3);
        border-radius: 4px;
        padding: 12px;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.8), 0 8px 25px rgba(0,0,0,0.6);
    }

    /* Top Spanning Banner */
    .cork-banner {
        background: #e6dcbf;
        background-image: linear-gradient(to bottom, rgba(255,255,255,0.2), rgba(0,0,0,0.1));
        border: 2px solid #573a21;
        padding: 12px 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        display: flex;
        justify-content: space-between;
        align-items: center;
        transform: rotate(-0.1deg);
        position: relative;
    }
    .cork-banner h1 {
        font-family: 'Special Elite', cursive;
        color: #991b1b;
        margin: 0;
        font-size: 23px;
        letter-spacing: 1.5px;
        text-shadow: 1px 1px 0px rgba(0,0,0,0.15);
    }
    .cork-banner p {
        font-family: 'Special Elite', cursive;
        color: #453322;
        margin: 2px 0 0 0;
        font-size: 11px;
    }

    /* Pinned Polaroid Card */
    .polaroid-card {
        background: #f2e9d2;
        border: 1px solid #d4c5a9;
        box-shadow: 6px 8px 22px rgba(0,0,0,0.7);
        padding: 14px;
        position: relative;
        transform: rotate(-0.8deg);
        margin-bottom: 15px;
    }

    /* Physical Red Pushpin */
    .pin {
        width: 14px;
        height: 14px;
        background: radial-gradient(circle at 35% 35%, #ef4444, #7f1d1d);
        border-radius: 50%;
        position: absolute;
        top: -7px;
        left: 50%;
        transform: translateX(-50%);
        box-shadow: 0 3px 6px rgba(0,0,0,0.8);
        z-index: 10;
    }

    /* Visual Masking Tape Effect */
    .tape {
        width: 70px;
        height: 20px;
        background: rgba(238, 225, 191, 0.65);
        border: 1px dashed rgba(180, 160, 120, 0.5);
        position: absolute;
        top: -10px;
        right: 15px;
        transform: rotate(5deg);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    .suspect-img {
        width: 100%;
        height: 210px;
        object-fit: cover;
        border: 1px solid #785a3c;
        filter: sepia(35%) contrast(115%) brightness(95%);
        margin-bottom: 10px;
    }

    /* Evidence Note Card */
    .paper-evidence {
        background: #ebdcb9;
        border: 1px solid #c7b591;
        box-shadow: 4px 5px 15px rgba(0,0,0,0.6);
        padding: 12px 28px 12px 14px;
        margin-bottom: 12px;
        position: relative;
        transform: rotate(0.4deg);
    }

    /* Forensic Stamp Badges */
    .stamp-badge {
        display: inline-block;
        padding: 3px 8px;
        font-family: 'Permanent Marker', cursive;
        font-size: 11px;
        border: 2px solid;
        border-radius: 3px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .stamp-red { color: #b91c1c; border-color: #b91c1c; transform: rotate(-3deg); }
    .stamp-amber { color: #d97706; border-color: #d97706; transform: rotate(2deg); }
    .stamp-blue { color: #1d4ed8; border-color: #1d4ed8; transform: rotate(-1deg); }

    /* Section Subheadings */
    .section-title {
        font-family: 'Special Elite', cursive;
        color: #fef08a;
        font-size: 14px;
        margin-bottom: 12px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
        letter-spacing: 0.5px;
    }

    /* Aged Input Fields */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #e6dcbf !important;
        color: #1c140d !important;
        border: 1px dashed #785a3c !important;
        font-family: 'Courier Prime', monospace !important;
        font-size: 11px !important;
        font-weight: bold;
    }

    /* Red Marker Action Buttons */
    .stButton button {
        background-color: #b91c1b !important;
        border: 2px solid #fef08a !important;
        border-radius: 2px !important;
        box-shadow: 3px 4px 10px rgba(0,0,0,0.6) !important;
        padding: 6px 12px !important;
        width: 100%;
    }

    .stButton button * {
        color: #ffffff !important;
        font-family: 'Special Elite', cursive !important;
        font-size: 13px !important;
        font-weight: bold !important;
        letter-spacing: 1px !important;
    }

    .stButton button:hover {
        background-color: #dc2626 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 1. DBMS CORE ---
def init_db():
    conn = sqlite3.connect("nulltracer.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            alibi TEXT,
            risk_score REAL,
            image_url TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            evidence_type TEXT,
            payload TEXT,
            timestamp TEXT,
            FOREIGN KEY(profile_id) REFERENCES profiles(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- 2. MAX-HEAP PRIORITY ENGINE ---
class MaxHeap:
    def __init__(self): self.heap = []
    def parent(self, i): return (i - 1) // 2
    def left_child(self, i): return 2 * i + 1
    def right_child(self, i): return 2 * i + 2

    def insert(self, profile_data):
        self.heap.append(profile_data)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, i):
        while i > 0 and self.heap[self.parent(i)]['score'] < self.heap[i]['score']:
            self.heap[self.parent(i)], self.heap[i] = self.heap[i], self.heap[self.parent(i)]
            i = self.parent(i)

    def extract_max(self):
        if not self.heap: return None
        if len(self.heap) == 1: return self.heap.pop()
        max_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return max_val

    def _heapify_down(self, i):
        max_index = i
        left = self.left_child(i)
        right = self.right_child(i)
        if left < len(self.heap) and self.heap[left]['score'] > self.heap[max_index]['score']: max_index = left
        if right < len(self.heap) and self.heap[right]['score'] > self.heap[max_index]['score']: max_index = right
        if i != max_index:
            self.heap[i], self.heap[max_index] = self.heap[max_index], self.heap[i]
            self._heapify_down(max_index)

# --- 3. OOP POLYMORPHIC VERIFICATION ---
class EvidenceItem(ABC):
    def __init__(self, log_id, payload, timestamp):
        self.log_id = log_id
        self.payload = payload
        self.timestamp = timestamp

    @abstractmethod
    def verify_match(self): pass

class CCTVLog(EvidenceItem):
    def verify_match(self): return f"Camera footage check: timeline conflicts at {self.timestamp}"

class AccessLog(EvidenceItem):
    def verify_match(self): return f"Security swipe check: unauthorized entry at {self.timestamp}"

class FinancialLog(EvidenceItem):
    def verify_match(self): return f"Bank ledger check: unusual activity at {self.timestamp}"

# --- HEADER BANNER ---
st.markdown("""
    <div class="cork-banner">
        <div>
            <h1>📌 NULLTRACER // FIELD INVESTIGATION BOARD</h1>
            <p>CASE DOSSIER // EVIDENCE CORRELATION & SUSPECT PROFILING SYSTEM</p>
        </div>
        <div style="text-align: right; font-family: 'Special Elite', cursive; font-size: 11px; color: #7f1d1d;">
            STATUS: ACTIVE INVESTIGATION<br>DATABASE: CONNECTED
        </div>
    </div>
""", unsafe_allow_html=True)

# Fetch all profiles from DB & build Max-Heap
conn = sqlite3.connect("nulltracer.db")
cursor = conn.cursor()
cursor.execute("SELECT id, name, alibi, risk_score, image_url FROM profiles")
profiles = cursor.fetchall()
conn.close()

max_heap = MaxHeap()
for p in profiles:
    max_heap.insert({"id": p[0], "name": p[1], "alibi": p[2], "score": p[3], "image_url": p[4]})

# Extract highest priority suspect automatically via Max-Heap root
top_priority_target = max_heap.extract_max()

# --- 3-COLUMN INVESTIGATION LAYOUT ---
col1, col2, col3 = st.columns([1.1, 1.3, 1], gap="medium")

with col1:
    st.markdown("<div class='section-title'>[ACTIVE TARGET DOSSIER]</div>", unsafe_allow_html=True)
    
    if profiles:
        profile_options = {p[1]: p for p in profiles}
        selected_name = st.selectbox("📂 SELECT ACTIVE CASE FILE", list(profile_options.keys()))
        selected_profile = profile_options[selected_name]
        
        target_id, target_name, target_alibi, target_score, target_image = selected_profile

        # Display selected suspect polaroid with full properties
        st.markdown(f"""
            <div class="polaroid-card">
                <div class="pin"></div>
                <div class="tape"></div>
                <span class="stamp-badge stamp-red">SELECTED TARGET</span>
                <img src="{target_image}" class="suspect-img">
                <div style="font-family: 'Special Elite', cursive; font-size: 15px; color: #111;">{target_name}</div>
                <div style="font-size: 11px; color: #4b5563; margin-top: 4px;"><b>Alibi Notes:</b> {target_alibi}</div>
                <div style="font-size: 12px; color: #991b1b; font-weight: bold; margin-top: 6px; font-family: 'Special Elite', cursive;">Suspicion Level: {target_score:.1f}/100</div>
            </div>
        """, unsafe_allow_html=True)

        # --- EDIT ACTIVE TARGET DOSSIER FORM ---
        with st.expander("✏️ EDIT ACTIVE DOSSIER (IMAGE & THREAT SLIDER)"):
            with st.form(f"edit_profile_{target_id}"):
                new_image_url = st.text_input("Update Image URL", value=target_image)
                new_score = st.slider("Adjust Suspicion Index", 0.0, 100.0, float(target_score))
                update_submitted = st.form_submit_button("SAVE CHANGES TO DATABASE")
                if update_submitted:
                    conn = sqlite3.connect("nulltracer.db")
                    cursor = conn.cursor()
                    cursor.execute("UPDATE profiles SET image_url = ?, risk_score = ? WHERE id = ?", (new_image_url, new_score, target_id))
                    conn.commit()
                    conn.close()
                    st.success("Dossier updated and saved successfully!")
                    st.rerun()

        if st.button("🗑️ SHRED / DELETE THIS DOSSIER"):
            conn = sqlite3.connect("nulltracer.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evidence_logs WHERE profile_id = ?", (target_id,))
            cursor.execute("DELETE FROM profiles WHERE id = ?", (target_id,))
            conn.commit()
            conn.close()
            st.success(f"Successfully shredded dossier for {target_name}!")
            st.rerun()
    else:
        selected_profile = None
        st.markdown("""
            <div class="polaroid-card" style="text-align: center; padding: 40px 10px;">
                <div class="pin"></div>
                <b style="color: #991b1b; font-family: Special Elite;">NO ACTIVE SUSPECTS IN SYSTEM</b>
                <p style="font-size: 11px; color: #555;">Use the right panel to pin a target.</p>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("<div class='section-title'>[VERIFIED EVIDENCE LOGS // RED THREAD MAPPING]</div>", unsafe_allow_html=True)
    
    if selected_profile:
        conn = sqlite3.connect("nulltracer.db")
        cursor = conn.cursor()
        cursor.execute("SELECT p.name, e.evidence_type, e.payload, e.timestamp, e.log_id FROM profiles p JOIN evidence_logs e ON p.id = e.profile_id WHERE p.id = ?", (selected_profile[0],))
        active_evidence = cursor.fetchall()
        conn.close()

        if not active_evidence:
            st.markdown("<div class='paper-evidence' style='font-family: Special Elite; color: #333;'>No evidence logs found for this target. Pin items below.</div>", unsafe_allow_html=True)

        for item in active_evidence:
            log_id = item[4]
            if item[1] == "CCTV": obj = CCTVLog(log_id, item[2], item[3])
            elif item[1] == "ACCESS": obj = AccessLog(log_id, item[2], item[3])
            else: obj = FinancialLog(log_id, item[2], item[3])

            st.markdown(f"""
                <div class="paper-evidence">
                    <div style="position: absolute; top: 6px; right: 8px; z-index: 20;">
                        <a href="?delete_log={log_id}" title="Delete evidence" style="text-decoration: none; font-size: 11px; background: #991b1b; color: #ffffff; border: 1px solid #fef08a; padding: 1px 4px; border-radius: 2px;">❌</a>
                    </div>
                    <span class="stamp-badge stamp-amber">EVIDENCE LINKED</span>
                    <div style="color: #991b1b; font-weight: bold; font-family: 'Special Elite', cursive; font-size: 11px;">🔴 {item[0]} ──> {item[1]} [{item[3]}]</div>
                    <div style="color: #2c241d; margin: 4px 0; font-size: 11px;">{item[2]}</div>
                    <div style="color: #1d4ed8; font-size: 10px; border-top: 1px dashed #c7b591; padding-top: 3px; margin-top: 3px; font-family: Special Elite;">
                        ↳ Analysis: {obj.verify_match()}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='paper-evidence' style='font-family: Special Elite; color: #333;'>Select a suspect profile first.</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='section-title'>[MAX-HEAP PRIORITY ROOT & BUILDER]</div>", unsafe_allow_html=True)
    
    # Small Max-Priority Root Display Card on the side
    if top_priority_target:
        st.markdown(f"""
            <div style="background: #f2e9d2; border: 2px solid #b91c1b; padding: 10px; margin-bottom: 15px; box-shadow: 3px 4px 10px rgba(0,0,0,0.6); position: relative;">
                <div class="pin" style="top: -6px;"></div>
                <span class="stamp-badge stamp-red" style="font-size: 9px; padding: 1px 4px; margin-bottom: 4px;">🔥 MAX PRIORITY ROOT</span>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <img src="{top_priority_target['image_url']}" style="width: 55px; height: 55px; object-fit: cover; border: 1px solid #785a3c; filter: sepia(35%);">
                    <div>
                        <div style="font-family: 'Special Elite', cursive; font-size: 11px; color: #111;"><b>{top_priority_target['name']}</b></div>
                        <div style="font-size: 10px; color: #991b1b; font-weight: bold; font-family: 'Special Elite', cursive;">Score: {top_priority_target['score']:.1f}/100</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Form to register custom suspects
    with st.form("add_suspect_form", clear_on_submit=True):
        st.markdown("<b style='color: #fef08a; font-size: 11px; font-family: Special Elite;'>1. PIN NEW SUSPECT PROFILE</b>", unsafe_allow_html=True)
        custom_name = st.text_input("Suspect Name / Code", "SUBJECT // [NAME]")
        custom_alibi = st.text_input("Claimed Alibi Note", "Claims presence at...")
        custom_image = st.text_input("Image URL (Photo / CCTV)", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=60")
        custom_score = st.slider("Suspicion Index", 50.0, 99.9, 88.5)
        sub_suspect = st.form_submit_button("PIN TARGET TO BOARD")
        if sub_suspect:
            conn = sqlite3.connect("nulltracer.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO profiles (name, alibi, risk_score, image_url) VALUES (?, ?, ?, ?)", 
                           (custom_name, custom_alibi, custom_score, custom_image))
            conn.commit()
            conn.close()
            st.success("Target pinned successfully!")
            st.rerun()

    st.markdown("<div style='font-family: Special Elite; color: #fef08a; font-size: 11px; margin-top: 10px;'>PINNED DOSSIERS IN DB:</div>", unsafe_allow_html=True)
    for p in profiles:
        st.markdown(f"""
            <div style="background: #e6dcbf; border: 1px solid #c7b591; padding: 5px 8px; margin-bottom: 4px; font-size: 10px; color: #111; transform: rotate(0.4deg);">
                <span class="stamp-badge stamp-blue" style="font-size: 8px; padding: 1px 4px; margin-bottom: 2px;">SECURED</span><br>
                <b>{p[1]}</b><br><span style="color: #991b1b; font-weight: bold;">Suspicion Level: {p[3]:.1f}</span>
            </div>
        """, unsafe_allow_html=True)

# Form to pin custom evidence notes to the currently selected suspect in Column 2 dropdown
with col2:
    if selected_profile:
        st.markdown("<div class='section-title' style='margin-top: 15px;'>[PIN CUSTOM EVIDENCE & WITNESS NOTE]</div>", unsafe_allow_html=True)
        with st.form("add_evidence_form", clear_on_submit=True):
            custom_payload = st.text_input("Witness Note / Threat Log", "Observed near sector 4 at...")
            log_type = st.selectbox("Classification", ["CCTV", "ACCESS", "FINANCIAL"])
            custom_timestamp = st.text_input("Timestamp", "03:15:00")
            sub_evidence = st.form_submit_button("PIN EVIDENCE NOTE")
            if sub_evidence:
                conn = sqlite3.connect("nulltracer.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO evidence_logs (profile_id, evidence_type, payload, timestamp) VALUES (?, ?, ?, ?)",
                               (selected_profile[0], log_type, custom_payload, custom_timestamp))
                conn.commit()
                conn.close()
                st.success(f"Evidence pinned to {selected_name} successfully!")
                st.rerun()