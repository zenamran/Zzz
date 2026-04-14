import streamlit as st
import pandas as pd
import io
import json
from google.cloud import firestore
from google.oauth2 import service_account

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Système Pro - Gestion des Fournisseurs",
    page_icon="🏢",
    layout="wide"
)

# تصميم الواجهة وتنسيق الاتجاه (RTL للدعم العربي)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    .main-header { color: #1E293B; font-weight: 700; border-bottom: 3px solid #10B981; padding-bottom: 10px; margin-bottom: 20px; }
    .stButton>button { background-color: #10B981; color: white; border-radius: 5px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. وظيفة الاتصال السحابي (Firestore)
def init_db():
    try:
        # استخراج البيانات من Secrets
        if "textkey" in st.secrets:
            creds_info = json.loads(st.secrets["textkey"])
            creds = service_account.Credentials.from_service_account_info(creds_info)
            return firestore.Client(credentials=creds, project=creds_info['project_id'])
    except Exception as e:
        st.error(f"خطأ في الاتصال السحابي: {e}")
    return None

db = init_db()
DOC_PATH = ("suppliers_app", "main_registry")

def load_data():
    if db:
        try:
            doc = db.collection(DOC_PATH[0]).document(DOC_PATH[1]).get()
            if doc.exists:
                return doc.to_dict().get("suppliers", [])
        except:
            pass
    return []

def save_data(data_list):
    if db:
        try:
            db.collection(DOC_PATH[0]).document(DOC_PATH[1]).set({"suppliers": data_list})
            return True
        except Exception as e:
            st.error(f"فشل الحفظ: {e}")
    return False

# 3. معالجة البيانات (المنطق الخاص بك)
def get_clean_records(df_raw, category_name):
    if df_raw.empty: return []
    df = df_raw.astype(str).replace(['nan', 'None', 'NaN', 'null'], '')
    mapping = {
        'Nom du Fournisseur': ['nom', 'fournisseur', 'designation', 'désignation', 'société', 'company', 'اسم', 'المورد'],
        'Adresse': ['adresse', 'address', 'lieu', 'عنوان', 'مقر'],
        'Téléphone': ['tél', 'tel', 'phone', 'هاتف'],
        'Mobile': ['mobile', 'mob', 'محمول', 'جوال'],
        'E-mail': ['email', 'mail', 'البريد']
    }
    header_idx, col_map = -1, {}
    for i in range(min(20, len(df))):
        row = [str(x).lower() for x in df.iloc[i].values]
        current_map, matches = {}, 0
        for target, keys in mapping.items():
            for idx, cell in enumerate(row):
                if any(k in cell for k in keys):
                    current_map[idx] = target
                    matches += 1
                    break
        if matches >= 1:
            header_idx, col_map = i, current_map
            break
    
    records = []
    if header_idx != -1:
        for _, row in df.iloc[header_idx + 1:].iterrows():
            record = {'Catégories': category_name}
            for col_idx, target_name in col_map.items():
                record[target_name] = str(row.iloc[col_idx]).strip()
            if record.get('Nom du Fournisseur'): records.append(record)
    return records

# 4. إدارة الحالة والواجهة
if 'data_list' not in st.session_state:
    st.session_state.data_list = load_data()

st.markdown("<h1 class='main-header'>🏢 Gestionnaire des Fournisseurs Cloud</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📥 Import Excel", "➕ Ajout Manuel"])

with tab1:
    up_file = st.file_uploader("Charger Excel", type=['xlsx'])
    if up_file:
        xl = pd.ExcelFile(up_file)
        sheets = st.multiselect("Sélectionnez les feuilles :", xl.sheet_names, default=xl.sheet_names)
        if st.button("🚀 Fusionner و Mémoriser"):
            for s in sheets:
                recs = get_clean_records(pd.read_excel(up_file, sheet_name=s, header=None), s)
                for r in recs:
                    name = r['Nom du Fournisseur'].lower().strip()
                    exist = next((i for i, x in enumerate(st.session_state.data_list) if x['Nom du Fournisseur'].lower().strip() == name), None)
                    if exist is None: st.session_state.data_list.append(r)
                    else:
                        cur = str(st.session_state.data_list[exist]['Catégories'])
                        if s not in cur: st.session_state.data_list[exist]['Catégories'] = f"{cur} / {s}"
            save_data(st.session_state.data_list)
            st.success("Données synchronisées avec le Cloud ✅")
            st.rerun()

with tab2:
    with st.form("manual"):
        n = st.text_input("Nom *")
        c = st.text_input("Catégorie")
        t = st.text_input("Téléphone")
        if st.form_submit_button("💾 Enregistrer"):
            if n:
                st.session_state.data_list.append({"Nom du Fournisseur": n, "Catégories": c, "Téléphone": t})
                save_data(st.session_state.data_list)
                st.rerun()

# العرض
st.divider()
if st.session_state.data_list:
    df = pd.DataFrame(st.session_state.data_list)
    st.dataframe(df, use_container_width=True, hide_index=True)
    if st.button("🗑️ Vider la base"):
        st.session_state.data_list = []
        save_data([])
        st.rerun()
else:
    st.info("La base de données est vide.")
