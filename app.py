import streamlit as st
import pandas as pd
import io
import json
from google.cloud import firestore
from google.oauth2 import service_account

# 1. إعدادات الصفحة والواجهة
st.set_page_config(
    page_title="Gestionnaire des Fournisseurs Cloud",
    page_icon="🏢",
    layout="wide"
)

st.markdown("""
    <style>
    .main-header { color: #1E293B; font-weight: 700; border-bottom: 3px solid #10B981; padding-bottom: 10px; margin-bottom: 20px; }
    .stAlert { direction: ltr; text-align: left; }
    </style>
    """, unsafe_allow_html=True)

# 2. وظيفة الاتصال السحابي مع معالجة أخطاء الـ JSON
def init_db():
    if "textkey" not in st.secrets:
        st.error("⚠️ مفتاح 'textkey' غير موجود في Secrets.")
        return None
    
    try:
        # قراءة المفتاح وتجاوز أخطاء التنسيق الشائعة
        raw_key = st.secrets["textkey"].strip()
        creds_info = json.loads(raw_key)
        creds = service_account.Credentials.from_service_account_info(creds_info)
        return firestore.Client(credentials=creds, project=creds_info['project_id'])
    except json.JSONDecodeError as je:
        st.error(f"❌ خطأ في تنسيق الـ JSON داخل Secrets: {je}")
        st.info("تأكد أنك وضعت النص بين ثلاث علامات تنصيص ''' ولا توجد حروف ناقصة.")
    except Exception as e:
        st.error(f"❌ خطأ غير متوقع في الاتصال: {e}")
    return None

db = init_db()
COLL = "suppliers_app"
DOC = "main_registry"

# وظائف المزامنة
def load_cloud():
    if db:
        try:
            res = db.collection(COLL).document(DOC).get()
            return res.to_dict().get("suppliers", []) if res.exists else []
        except: return []
    return []

def save_cloud(data):
    if db:
        try:
            db.collection(COLL).document(DOC).set({"suppliers": data})
            return True
        except: return False
    return False

# 3. إدارة الجلسة والبيانات
if 'data_list' not in st.session_state:
    st.session_state.data_list = load_cloud()

st.markdown("<h1 class='main-header'>🏢 Gestionnaire des Fournisseurs Cloud</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📥 Import Excel", "➕ Ajout Manuel"])

with tab1:
    up_file = st.file_uploader("Charger le fichier Excel (.xlsx)", type=['xlsx'])
    if up_file:
        xl = pd.ExcelFile(up_file)
        sheets = st.multiselect("Sélectionnez les feuilles :", xl.sheet_names, default=xl.sheet_names)
        if st.button("🚀 Fusionner و Mémoriser"):
            for s in sheets:
                df_raw = pd.read_excel(up_file, sheet_name=s, header=None)
                # معالجة بسيطة للبيانات (دمج مع كودك السابق)
                df_raw = df_raw.astype(str).replace('nan', '')
                for _, row in df_raw.iloc[1:].iterrows():
                    name = str(row.iloc[0]).strip()
                    if name:
                        exist = next((i for i, x in enumerate(st.session_state.data_list) if x['Nom'].lower() == name.lower()), None)
                        if exist is None:
                            st.session_state.data_list.append({"Nom": name, "Catégories": s, "Info": str(row.iloc[1]) if len(row)>1 else ""})
            save_cloud(st.session_state.data_list)
            st.success("Synchronisation réussie ✅")
            st.rerun()

with tab2:
    with st.form("manual"):
        name = st.text_input("Nom du Fournisseur *")
        cat = st.text_input("Catégorie")
        if st.form_submit_button("💾 Enregistrer"):
            if name:
                st.session_state.data_list.append({"Nom": name, "Catégories": cat, "Info": ""})
                save_cloud(st.session_state.data_list)
                st.rerun()

# العرض النهائي
st.divider()
if st.session_state.data_list:
    st.dataframe(pd.DataFrame(st.session_state.data_list), use_container_width=True, hide_index=True)
    if st.button("🗑️ Vider la base"):
        st.session_state.data_list = []
        save_cloud([])
        st.rerun()
